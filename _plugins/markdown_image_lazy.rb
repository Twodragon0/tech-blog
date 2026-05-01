# frozen_string_literal: true

# Jekyll plugin: inject loading="lazy" decoding="async" into body <img> tags,
# and inject deterministic CSS class hooks based on src extension / path.
#
# Class hooks injected (when not already present):
#   is-svg-image      — src ends with .svg
#   is-raster-image   — src ends with .png / .jpg / .jpeg / .webp / .avif
#   is-section-image  — src path segment contains "section-"
#   is-news-card-image — src path contains "news-card"
#
# Behaviour:
# - Skips images that already have loading= (e.g. header image with loading="eager")
# - Skips images that already have decoding= only if they do NOT also need loading=
# - Skips data: URI images (base64 inline)

module Jekyll
  module ImageLazyLoading
    LAZY_ATTRS = ' loading="lazy" decoding="async"'.freeze
    LOADING_ONLY = ' loading="lazy"'.freeze

    # Determine class hooks to add based on the src attribute value.
    # Returns a space-separated string of class names (may be empty).
    def self.class_hooks_for_src(src)
      return '' if src.nil? || src.empty?

      hooks = []
      src_lower = src.downcase
      if src_lower.end_with?('.svg')
        hooks << 'is-svg-image'
      elsif src_lower =~ /\.(png|jpe?g|webp|avif)(\?|$|#)/i || src_lower.end_with?('.png', '.jpg', '.jpeg', '.webp', '.avif')
        hooks << 'is-raster-image'
      end
      hooks << 'is-section-image'  if src.include?('section-')
      hooks << 'is-news-card-image' if src.include?('news-card')
      hooks.join(' ')
    end

    # Inject class hooks into an existing class= attribute string, or add class= if absent.
    def self.inject_classes(attrs, new_hooks)
      return attrs if new_hooks.empty?

      if attrs =~ /\bclass=(["'])(.*?)\1/
        quote   = Regexp.last_match(1)
        current = Regexp.last_match(2).strip
        new_hooks_list = new_hooks.split
        missing = new_hooks_list.reject { |h| current.split.include?(h) }
        return attrs if missing.empty?

        merged = (current.split + missing).uniq.join(' ')
        attrs.sub(/\bclass=(["']).*?\1/, "class=#{quote}#{merged}#{quote}")
      else
        # No class attribute — append one before the end of the tag
        attrs + " class=\"#{new_hooks}\""
      end
    end

    def self.process(content)
      return content if content.nil? || content.empty?

      content.gsub(/<img(?![^>]*\bloading=)([^>]*?)(\s*\/)?>/i) do |match|
        attrs      = Regexp.last_match(1)
        self_close = Regexp.last_match(2)

        # Skip data URIs (base64 inline images — no benefit from lazy)
        next match if attrs.match?(/src=["']data:/i)

        # Extract src value for class hook computation
        src_value = attrs[/src=["']([^"']*)/i, 1].to_s
        hooks     = class_hooks_for_src(src_value)
        attrs     = inject_classes(attrs, hooks) unless hooks.empty?

        has_decoding = attrs.match?(/\bdecoding=/i)
        extra = has_decoding ? LOADING_ONLY : LAZY_ATTRS
        # Preserve self-closing slash after injected attrs
        self_close ? "<img#{attrs}#{extra} />" : "<img#{attrs}#{extra}>"
      end
    end
  end
end

Jekyll::Hooks.register [:posts, :pages, :documents], :post_render do |doc|
  next unless doc.output_ext == '.html'

  doc.output = Jekyll::ImageLazyLoading.process(doc.output)
end
