source "https://rubygems.org"

# CI/Vercel: Ruby 2.7+ 필수 (google-protobuf >= 3.25.5 보안 패치)
ruby ">= 2.7.0"

gem "jekyll", "~> 4.3.4"

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.15"
  gem "jekyll-sitemap", "~> 1.4"
  gem "jekyll-seo-tag", "~> 2.8"
end

# Performance
gem "webrick", "~> 1.8"

# Security: CVE fix for protobuf DoS (Dependabot alert #8)
gem "google-protobuf", ">= 3.25.5"

# Fix: sass-embedded 1.58.3 breaks on Ruby 3.3+ (FileUtils::URI error)
gem "sass-embedded", "~> 1.85"
