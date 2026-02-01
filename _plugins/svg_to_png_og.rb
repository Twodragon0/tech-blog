# frozen_string_literal: true

# SVG to PNG OG Image Converter
#
# jekyll-seo-tag reads page.image and outputs og:image meta tags.
# SNS platforms (Facebook, Twitter, LinkedIn, KakaoTalk) cannot render SVG.
# This hook converts page.image from SVG to PNG path (if PNG exists)
# so jekyll-seo-tag outputs PNG URLs for og:image and twitter:image.

Jekyll::Hooks.register :pages, :pre_render do |page|
  convert_svg_image_to_png(page)
end

Jekyll::Hooks.register :posts, :pre_render do |post|
  convert_svg_image_to_png(post)
end

Jekyll::Hooks.register :documents, :pre_render do |doc|
  convert_svg_image_to_png(doc)
end

def convert_svg_image_to_png(page)
  image = page.data["image"]
  return unless image.is_a?(String) && image.end_with?(".svg")

  png_path = image.sub(/\.svg\z/, ".png")
  source_dir = page.site.source
  full_png_path = File.join(source_dir, png_path)

  page.data["image"] = png_path if File.exist?(full_png_path)
end
