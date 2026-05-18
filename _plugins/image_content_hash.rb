# frozen_string_literal: true

# Jekyll plugin: image content-hash versioning.
#
# Computes SHA-256 (first 8 hex chars) of every file under
#   assets/images/**/*.{svg,png,webp,avif}
# at :site, :post_read (runs before page/post :pre_render) and caches the
# mapping in site.data['image_hashes'] keyed by the path WITHOUT the leading
# slash (e.g. 'assets/images/foo.svg').
#
# Exposes a Liquid filter `image_v` that appends `?v={hash}` to a local
# image URL. The filter:
#   - strips any pre-existing ?... query before re-appending (canonicalise)
#   - returns the URL unchanged for external URLs (http://, https://, //)
#   - returns the URL unchanged for non-/assets/ paths
#   - returns the URL unchanged when the file is missing on disk
#   - computes the hash on-demand and memoises it if it was missing from
#     the boot-time cache (defensive — should rarely trigger)
#
# Plan: .omc/plans/image-content-hash-versioning.md (Step 1).

require 'digest'
require 'pathname'

module Jekyll
  module ImageContentHash
    HASH_LEN = 8
    ALLOWED_EXTS = %w[.svg .png .webp .avif].freeze

    class << self
      attr_accessor :site_source

      def cache
        @cache ||= {}
      end

      def reset!(source)
        @site_source = source
        @cache = {}
      end

      # Compute the 8-char SHA-256 hex prefix of a file's bytes.
      # Returns nil when the file is missing or unreadable.
      def compute_hash(abs_path)
        return nil unless File.file?(abs_path)

        Digest::SHA256.file(abs_path).hexdigest[0, HASH_LEN]
      rescue StandardError
        nil
      end

      # Look up (or compute-and-memoise) the hash for a /assets/... URL path.
      # Accepts either a URL-style path with a leading slash or a relative
      # path without one. Returns nil when not resolvable.
      def lookup(url_path)
        return nil if url_path.nil? || url_path.empty?

        rel = url_path.sub(%r{\A/}, '')
        return cache[rel] if cache.key?(rel)
        return nil unless site_source

        abs = File.join(site_source, rel)
        h = compute_hash(abs)
        cache[rel] = h if h
        h
      end
    end
  end

  module ImageContentHashFilter
    # Liquid filter: pipe an image URL through to get `URL?v={hash}`.
    # Idempotent: a pre-existing ?... query is stripped before re-appending.
    def image_v(input)
      return input if input.nil?

      url = input.to_s
      return url if url.empty?

      # External / protocol-relative URLs — leave alone.
      return url if url.start_with?('http://', 'https://', '//')

      # Strip any existing query (we replace, not stack).
      path = url.split('?', 2).first.to_s
      return url unless path.start_with?('/assets/')

      ext = File.extname(path).downcase
      return url unless ImageContentHash::ALLOWED_EXTS.include?(ext)

      hash = ImageContentHash.lookup(path)
      return path unless hash # missing file → return clean path without ?v=

      "#{path}?v=#{hash}"
    end
  end
end

Liquid::Template.register_filter(Jekyll::ImageContentHashFilter)

Jekyll::Hooks.register :site, :post_read do |site|
  Jekyll::ImageContentHash.reset!(site.source)
  img_dir = File.join(site.source, 'assets', 'images')
  next unless File.directory?(img_dir)

  glob_pattern = File.join(img_dir, '**', '*.{svg,png,webp,avif,SVG,PNG,WEBP,AVIF}')
  source_pn = Pathname.new(site.source)
  Dir.glob(glob_pattern).each do |path|
    next unless File.file?(path)

    rel = Pathname.new(path).relative_path_from(source_pn).to_s
    h = Jekyll::ImageContentHash.compute_hash(path)
    Jekyll::ImageContentHash.cache[rel] = h if h
  end

  # Expose to Liquid templates for debugging / direct map access.
  site.data ||= {}
  site.data['image_hashes'] = Jekyll::ImageContentHash.cache.dup
end
