# frozen_string_literal: true

require 'digest'
require 'base64'
require 'set'

# Jekyll plugin: inject Subresource Integrity (SRI) attributes into
# self-hosted <script src=...> and <link rel="stylesheet" href=...> tags.
#
# Scope (per .omc/plans/sri-injection-jekyll-plugin.md):
#   - Same-origin assets only: paths matching /assets/(js|css)/...
#   - External URLs (http://, https://, //) are untouched.
#   - Existing integrity= attributes are preserved (idempotent).
#   - Missing assets log a warning but do not break the build.
#
# Hook: :site, :post_write — runs after Jekyll has written _site/.
# Walks _site/**/*.html, rewrites matching tags in place.
#
# Hash format: sha384-<base64(SHA-384(file_bytes))>. Query strings
# (?v=...) and fragments (#...) are stripped before filesystem lookup.
# The site.baseurl prefix (e.g. /tech-blog on the GH Pages backup) is
# stripped before resolving the asset path under site.dest.

module Jekyll
  module SriInject
    ASSET_RE = %r{/assets/(?:js|css)/}.freeze

    # Match <script ... src="..."> and <link ... href="..."> opening tags.
    # Capture: $1 = tag name, $2 = attrs before src/href, $3 = src|href,
    # $4 = url value, $5 = attrs after.
    TAG_RE = /<(script|link)\b([^>]*?)\b(src|href)=(["'])([^"']+)\4([^>]*)>/i

    def self.same_origin_local?(url)
      return false if url.nil? || url.empty?
      return false if url.start_with?('http://', 'https://', '//', 'data:')
      url.include?('/assets/js/') || url.include?('/assets/css/')
    end

    def self.strip_query_and_fragment(url)
      # Drop ?... and #... — hash is over file bytes, not the URL.
      url.sub(/[?#].*\z/, '')
    end

    def self.resolve_asset_path(url, baseurl)
      path = strip_query_and_fragment(url)
      # Strip leading site.baseurl (e.g. "/tech-blog") if present —
      # GH Pages backup builds with --baseurl "/tech-blog", but on
      # disk the asset still lives at _site/assets/...
      if !baseurl.empty? && path.start_with?(baseurl)
        path = path[baseurl.length..]
      end
      # Ensure leading slash for File.join semantics later.
      path = "/#{path}" unless path.start_with?('/')
      path
    end

    def self.compute_sha384(file)
      raw = File.binread(file)
      digest = Digest::SHA384.digest(raw)
      "sha384-#{Base64.strict_encode64(digest)}"
    end

    # Memoised hash per (abs_path, mtime). Keyed within a single build.
    def self.cached_hash(file, cache)
      stat = File.stat(file)
      key = [file, stat.mtime.to_i, stat.size]
      cache[key] ||= compute_sha384(file)
    end

    # Link tags only get SRI if they are stylesheets. <link rel="prefetch">,
    # <link rel="preload">, <link rel="icon"> etc. are out of scope.
    def self.stylesheet_link?(attrs_before, attrs_after)
      combined = "#{attrs_before} #{attrs_after}"
      combined =~ /\brel=(["'])\s*stylesheet\s*\1/i ? true : false
    end

    def self.process_html(content, dest, baseurl, cache, warned)
      return content if content.nil? || content.empty?

      content.gsub(TAG_RE) do |match|
        tag        = Regexp.last_match(1).downcase
        attrs_pre  = Regexp.last_match(2)
        attr_name  = Regexp.last_match(3).downcase
        url        = Regexp.last_match(5)
        attrs_post = Regexp.last_match(6)

        # Tag/attribute pairing: script wants src, link wants href.
        next match if tag == 'script' && attr_name != 'src'
        next match if tag == 'link'   && attr_name != 'href'

        # Link tags: only stylesheets get SRI.
        next match if tag == 'link' && !stylesheet_link?(attrs_pre, attrs_post)

        # Skip external / data URIs.
        next match unless same_origin_local?(url)

        # Idempotency: skip if integrity already present anywhere in the tag.
        next match if "#{attrs_pre} #{attrs_post}".match?(/\bintegrity=/i)

        # Resolve URL → filesystem path under site.dest.
        rel_path = resolve_asset_path(url, baseurl)
        next match unless rel_path.match?(ASSET_RE)

        abs = File.join(dest, rel_path)
        unless File.file?(abs)
          unless warned.include?(abs)
            warned << abs
            Jekyll.logger.warn('SRI:', "asset missing, skipping: #{rel_path}")
          end
          next match
        end

        hash = begin
          cached_hash(abs, cache)
        rescue StandardError => e
          Jekyll.logger.warn('SRI:', "hash failed for #{rel_path}: #{e.message}")
          next match
        end

        injection = %( integrity="#{hash}" crossorigin="anonymous")
        # Append integrity + crossorigin just before the closing '>'.
        # Preserve original attrs_pre spacing (it already starts with the
        # whitespace that separated <tag from src/href) so we don't
        # introduce duplicate spaces. Trim trailing whitespace from
        # attrs_post so the injection sits cleanly before the closing
        # bracket.
        "<#{tag}#{attrs_pre}#{attr_name}=\"#{url}\"#{attrs_post.rstrip}#{injection}>"
      end
    end

    def self.run(site)
      t0 = Time.now
      dest = site.dest
      baseurl = (site.config['baseurl'] || '').to_s
      cache = {}
      warned = Set.new
      processed = 0
      injected = 0

      Dir.glob(File.join(dest, '**', '*.html')).each do |html_file|
        original = File.read(html_file)
        rewritten = process_html(original, dest, baseurl, cache, warned)
        next if rewritten == original

        # Count injected integrity attrs for this file (rough metric).
        injected += rewritten.scan(/integrity="sha384-/).length -
                    original.scan(/integrity="sha384-/).length
        File.write(html_file, rewritten)
        processed += 1
      end

      elapsed_ms = ((Time.now - t0) * 1000).round(1)
      Jekyll.logger.info(
        'SRI:',
        "processed=#{processed} html files, injected=#{injected} integrity attrs " \
        "(cache=#{cache.size} unique assets, #{elapsed_ms} ms)"
      )
    rescue StandardError => e
      Jekyll.logger.warn('SRI:', "plugin error (degrade-don't-crash): #{e.class}: #{e.message}")
    end
  end
end

Jekyll::Hooks.register :site, :post_write do |site|
  Jekyll::SriInject.run(site)
end
