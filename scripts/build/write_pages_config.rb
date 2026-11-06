#!/usr/bin/env ruby
# Pages metadata may advertise HTTP even when the backup supports HTTPS.
require 'json'
require 'uri'

begin
  origin = URI.parse(ENV.fetch('PAGES_ORIGIN'))
  valid = origin.is_a?(URI::HTTP) && %w[http https].include?(origin.scheme) &&
          origin.host && !origin.host.empty? && origin.userinfo.nil? &&
          origin.query.nil? && origin.fragment.nil? &&
          ['', '/'].include?(origin.path) &&
          origin.port == (origin.scheme == 'http' ? 80 : 443)
  abort 'Invalid Pages origin' unless valid

  secure_origin = URI::HTTPS.build(host: origin.host).to_s
  output = File.join(ENV.fetch('RUNNER_TEMP'), 'jekyll-pages.yml')
  File.write(output, JSON.generate({ 'url' => secure_origin }))
rescue URI::InvalidURIError, KeyError
  abort 'Invalid Pages configuration environment'
end
