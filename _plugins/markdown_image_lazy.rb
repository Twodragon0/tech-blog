# frozen_string_literal: true

# Jekyll plugin: inject loading="lazy" decoding="async" into body <img> tags.
# - Skips images that already have loading= (e.g. header image with loading="eager")
# - Skips images that already have decoding= only if they do NOT also need loading=
# - Skips data: URI images (base64 inline)

module Jekyll
  module ImageLazyLoading
    LAZY_ATTRS = ' loading="lazy" decoding="async"'.freeze
    LOADING_ONLY = ' loading="lazy"'.freeze

    def self.process(content)
      return content if content.nil? || content.empty?

      content.gsub(/<img(?![^>]*\bloading=)([^>]*?)(\s*\/)?>/i) do |match|
        attrs      = Regexp.last_match(1)
        self_close = Regexp.last_match(2)

        # Skip data URIs (base64 inline images — no benefit from lazy)
        next match if attrs.match?(/src=["']data:/i)

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
