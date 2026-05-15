#!/usr/bin/env ruby
# Inject SRI integrity hashes into <script>/<link> tags in built HTML.
#
# Runs as a post-build step (called from build.sh AFTER terser
# minification), so the hashes match the FINAL bytes the browser will
# receive. A Jekyll `:post_write` plugin can't be used: it runs before
# terser, and was reverted in 90803aa8 after blocking all JS on prod
# with stale (pre-minify) hashes.
#
# Ruby instead of Python because Vercel's build env runs `bundle exec
# jekyll build` — Ruby is guaranteed available, python3 is not.
#
# Walks _site/**/*.html. For each tag matching one of:
#   <script src="/assets/{js,css}/foo.js[?v=...]" ...>
#   <link  rel="stylesheet" href="/assets/{js,css}/foo.css[?v=...]" ...>
# that does NOT already carry an integrity= attribute, and whose
# src/href points to a same-origin local file, the script:
#   1. Strips ?query and #fragment for filesystem lookup.
#   2. Strips a leading site.baseurl if path starts with it
#      (handles GH Pages backup --baseurl /tech-blog).
#   3. Computes SHA-384 of the file at _site/{path}.
#   4. Rewrites the tag to add integrity="sha384-..." crossorigin="anonymous".
# Missing or unreadable assets log a warning but never abort the build.
#
# Exit codes: always 0 (warnings only).

require 'digest'
require 'base64'
require 'optparse'
require 'pathname'
require 'set'

REPO_ROOT = Pathname.new(__FILE__).realpath.parent.parent.parent

# Matches <script ...> and <link ...>. Captures the element name and attrs
# blob so we can rewrite while preserving attribute order.
TAG_RE = /<(?<elem>script|link)(?<attrs>\s[^>]*?)\s*\/?>/i

def extract_attr(attrs, name)
  m = attrs.match(/\b#{Regexp.escape(name)}\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))/i)
  return nil unless m
  m[1] || m[2] || m[3]
end

def compute_sri(path, cache, warned)
  return cache[path.to_s] if cache.key?(path.to_s)
  unless File.readable?(path)
    unless warned.include?(path.to_s)
      warn "SRI: cannot read #{path} (skipping)"
      warned << path.to_s
    end
    return nil
  end
  digest = Digest::SHA384.digest(File.read(path, mode: 'rb'))
  sri = "sha384-#{Base64.strict_encode64(digest)}"
  cache[path.to_s] = sri
  sri
end

def rewrite_tag(match, site_dest, baseurl, cache, warned, stats)
  elem = match[:elem].downcase
  attrs = match[:attrs]
  full_tag = match[0]

  # Idempotent: skip if already has integrity.
  return full_tag if attrs =~ /\bintegrity\s*=/i

  if elem == 'link'
    rel = (extract_attr(attrs, 'rel') || '').downcase
    return full_tag unless rel.split.include?('stylesheet')
    url = extract_attr(attrs, 'href')
  else
    url = extract_attr(attrs, 'src')
  end
  return full_tag unless url

  # Skip external + protocol-relative + data URIs.
  return full_tag if url =~ %r{\A(?:https?:|//|data:|blob:)}

  # Strip query + fragment.
  clean = url.split('?', 2)[0].split('#', 2)[0]
  # Strip leading baseurl.
  clean = clean[baseurl.length..] if !baseurl.empty? && clean.start_with?("#{baseurl}/")
  rel_path = clean.sub(%r{\A/}, '')
  return full_tag unless rel_path.start_with?('assets/')

  abs_path = site_dest.join(rel_path)
  sri = compute_sri(abs_path, cache, warned)
  return full_tag unless sri

  stats[:injected] += 1
  "<#{match[:elem]}#{attrs.rstrip} integrity=\"#{sri}\" crossorigin=\"anonymous\">"
end

def process_file(html_path, site_dest, baseurl, cache, warned, stats)
  text = File.read(html_path, encoding: 'UTF-8')
  new_text = text.gsub(TAG_RE) do |_|
    rewrite_tag(Regexp.last_match, site_dest, baseurl, cache, warned, stats)
  end
  return false if new_text == text
  File.write(html_path, new_text, mode: 'wb')
  true
rescue => e
  warn "SRI: error processing #{html_path}: #{e.class}: #{e.message}"
  false
end

# CLI
site_dir = REPO_ROOT.join('_site').to_s
baseurl = ''

OptionParser.new do |opts|
  opts.on('--site PATH', 'Built site root (default: ./_site)') { |v| site_dir = v }
  opts.on('--baseurl URL', 'Jekyll site.baseurl to strip') { |v| baseurl = v }
end.parse!

site_dest = Pathname.new(site_dir)
unless site_dest.directory?
  warn "SRI: no _site at #{site_dest}, skipping"
  exit 0
end

cache = {}
warned = Set.new
stats = { injected: 0 }
html_files = Pathname.glob(site_dest.join('**/*.html'))
changed = 0
html_files.each do |p|
  changed += 1 if process_file(p, site_dest, baseurl, cache, warned, stats)
end

puts "SRI: scanned #{html_files.length} HTML files, rewrote #{changed}, " \
     "injected #{stats[:injected]} integrity attributes " \
     "(#{cache.length} unique asset hashes)"
