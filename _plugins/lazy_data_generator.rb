# frozen_string_literal: true

require 'json'
require 'fileutils'

# Generates /tags-data.json and /categories-data.json at build time.
#
# Replaces the Liquid versions whose `where_exp` filter ran once per
# tag/category × full site.posts scan. Pure-Ruby single-pass build is
# orders of magnitude faster on a 200+ post site, and it produces the
# same JSON shape consumed by tags-page.js / categories-page.js.
#
# Strategy:
#   - During the :site, :post_write hook, after Jekyll has produced
#     _site/, derive the data and write the two JSON files directly.
#   - Bypasses the Liquid render pipeline entirely (no template parse,
#     no `where_exp` recomputation).
#
# JSON shape (per-post payload, terse keys to keep transfer small):
#   t   : title
#   u   : URL (relative_url applied)
#   d   : human date "YYYY. MM. DD"
#   x   : ISO 8601 datetime
#   c   : primary category badge label
#   cs  : space-joined data-category string (categories.html only)
#   tags: up to 3 tag labels (categories.html only)
#   tn  : total tag count (categories.html only)
#   ex  : excerpt (160-char truncated, categories.html only)
#   img : front-matter image path with relative_url (categories.html only)
#   ip,ia,iw,ica,icw : 0/1 flags for which OG/card variants exist on disk

CLASSIFIER_KEYWORDS = {
  'devops'     => ['devops', 'ci/cd', 'cicd', 'pipeline', 'github actions', 'automation', 'terraform', 'ansible'],
  'kubernetes' => ['kubernetes', 'k8s', 'eks'],
  'blockchain' => ['blockchain', 'bitcoin', 'crypto', 'ethereum', 'web3']
}.freeze

Jekyll::Hooks.register :site, :post_write do |site|
  posts = site.posts.docs
  static_paths = collect_static_paths(site)

  tag_index = build_tag_index(posts)
  category_index = build_category_index(posts, site.config['category_list'] || [])

  baseurl = site.config['baseurl'].to_s
  tags_json = render_tags_json(tag_index, baseurl)
  cats_json = render_categories_json(site, category_index, static_paths)
  archive_json = render_archive_json(posts, baseurl)

  dest = site.dest
  File.write(File.join(dest, 'tags-data.json'), tags_json)
  File.write(File.join(dest, 'categories-data.json'), cats_json)
  File.write(File.join(dest, 'archive-data.json'), archive_json)

  Jekyll.logger.info('LazyData:',
    "tags=#{tag_index.count(&:itself)} categories=#{category_index.count { |_, v| !v.empty? }} " \
    "archive_posts=#{posts.length} " \
    "(tags=#{tags_json.bytesize / 1024}KB cats=#{cats_json.bytesize / 1024}KB " \
    "archive=#{archive_json.bytesize / 1024}KB)"
  )
end

def collect_static_paths(site)
  paths = {}
  site.static_files.each do |sf|
    rel = sf.relative_path.start_with?('/') ? sf.relative_path : "/#{sf.relative_path}"
    paths[rel] = true
  end
  paths
end

def build_tag_index(posts)
  idx = Hash.new { |h, k| h[k] = [] }
  posts.each do |post|
    next unless post.data['tags']
    Array(post.data['tags']).each do |tag|
      idx[tag.to_s] << post
    end
  end
  idx
end

def build_category_index(posts, category_list)
  idx = {}
  category_list.each do |cat|
    cat_name = cat['name'].to_s
    cat_key = cat_name.downcase.strip
    keywords = CLASSIFIER_KEYWORDS[cat_key]
    matched = []

    posts.each do |post|
      already = matched.any? { |p| p.equal?(post) }
      next if already

      if direct_match?(post, cat_key)
        matched << post
      elsif keywords && classifier_match?(post, keywords)
        matched << post
      end
    end

    idx[cat_name] = matched
  end
  idx
end

def direct_match?(post, cat_key)
  single = post.data['category']
  return true if single && !single.to_s.empty? && single.to_s.downcase.strip == cat_key
  cats = post.data['categories']
  return false unless cats
  Array(cats).any? { |c| c.to_s.downcase.strip == cat_key }
end

def classifier_match?(post, keywords)
  classifier = "#{post.data['title']} #{post.data['excerpt']} ".dup
  tags = post.data['tags']
  classifier << Array(tags).join(' ') if tags
  cl = classifier.downcase
  keywords.any? { |kw| cl.include?(kw) }
end

def render_tags_json(tag_index, baseurl)
  sorted = tag_index.keys.sort_by { |t| t.to_s.downcase }

  hash = {}
  sorted.each do |tag|
    posts = tag_index[tag]
    next if posts.empty?

    related = build_related_tags(posts, tag)
    slug = Jekyll::Utils.slugify(tag)

    hash[slug] = {
      'name' => tag.to_s,
      'related' => related,
      'posts' => posts.map { |p| simple_post_payload(p, baseurl) }
    }
  end

  JSON.generate(hash)
end

def render_categories_json(site, cat_index, static_paths)
  category_list = site.config['category_list'] || []
  baseurl = site.config['baseurl'].to_s

  hash = {}
  cat_index.each do |name, posts|
    next if posts.empty?
    entry = category_list.find { |c| c['name'].to_s == name.to_s }
    title = entry ? entry['title'].to_s : name.to_s

    hash[name.to_s] = {
      'name' => name.to_s,
      'title' => title,
      'posts' => posts.map { |p| full_post_payload(p, baseurl, static_paths) }
    }
  end

  JSON.generate(hash)
end

def render_archive_json(posts, baseurl)
  # Group by year → month → posts. Posts are already date-sorted DESC by
  # Jekyll, so sub-arrays come out newest-first within each month bucket.
  years = {}
  posts.each do |post|
    year = post.date.strftime('%Y')
    month = post.date.strftime('%m')
    years[year] ||= {}
    years[year][month] ||= []
    years[year][month] << archive_post_payload(post, baseurl)
  end

  # Emit years newest-first to match the visible archive page ordering.
  ordered = {}
  years.keys.sort.reverse.each do |y|
    months = years[y]
    ordered_months = {}
    months.keys.sort.reverse.each do |m|
      ordered_months[m] = months[m]
    end
    ordered[y] = ordered_months
  end
  JSON.generate(ordered)
end

def archive_post_payload(post, baseurl)
  tags = Array(post.data['tags'] || [])
  cats_str = build_category_string(post)
  excerpt_short = sanitize_excerpt_short(post.data['excerpt'])

  {
    't'    => post.data['title'].to_s,
    'u'    => prefix_with_baseurl(post.url, baseurl),
    'd'    => post.date.strftime('%m. %d'),
    'x'    => post.date.iso8601,
    'c'    => primary_category(post),
    'cs'   => cats_str,
    'tags' => tags.first(3).map(&:to_s),
    'ex'   => excerpt_short
  }
end

def sanitize_excerpt_short(excerpt)
  return '' unless excerpt
  stripped = excerpt.to_s.gsub(/<[^>]+>/, '').gsub(/\s+/, ' ').strip
  stripped.length > 80 ? "#{stripped[0, 77]}..." : stripped
end

def build_related_tags(posts, current_tag)
  seen = {}
  result = []
  posts.each do |post|
    next unless post.data['tags']
    Array(post.data['tags']).each do |t|
      ts = t.to_s
      next if ts == current_tag
      next if seen[ts]
      seen[ts] = true
      result << ts
      break if result.length >= 5
    end
    break if result.length >= 5
  end
  result
end

def simple_post_payload(post, baseurl)
  {
    't' => post.data['title'].to_s,
    'u' => prefix_with_baseurl(post.url, baseurl),
    'd' => post.date.strftime('%Y. %m. %d'),
    'x' => post.date.iso8601,
    'c' => primary_category(post)
  }
end

def full_post_payload(post, baseurl, static_paths)
  img_path = post.data['image'].to_s
  img_url = img_path.empty? ? '' : prefix_with_baseurl(img_path, baseurl)
  flags = compute_image_flags(img_path, static_paths)
  tags = Array(post.data['tags'] || [])

  {
    't'    => post.data['title'].to_s,
    'u'    => prefix_with_baseurl(post.url, baseurl),
    'd'    => post.date.strftime('%Y. %m. %d'),
    'x'    => post.date.iso8601,
    'c'    => primary_category(post),
    'cs'   => build_category_string(post),
    'tags' => tags.first(3).map(&:to_s),
    'tn'   => tags.length,
    'ex'   => sanitize_excerpt(post.data['excerpt']),
    'img'  => img_url,
    'ip'   => flags[:png],
    'ia'   => flags[:avif],
    'iw'   => flags[:webp],
    'ica'  => flags[:card_avif],
    'icw'  => flags[:card_webp]
  }
end

def prefix_with_baseurl(path, baseurl)
  path = path.to_s
  return path if path.start_with?('http://', 'https://')
  return path if !baseurl.empty? && path.start_with?(baseurl)
  "#{baseurl}#{path.start_with?('/') ? path : "/#{path}"}"
end

def primary_category(post)
  single = post.data['category']
  return single.to_s if single && !single.to_s.empty?
  cats = post.data['categories']
  return Array(cats).first.to_s if cats && !Array(cats).empty?
  ''
end

def build_category_string(post)
  seen = {}
  result = []
  single = post.data['category']
  if single && !single.to_s.empty?
    s = single.to_s.downcase.strip
    seen[s] = true
    result << s
  end
  cats = post.data['categories']
  Array(cats).each do |c|
    s = c.to_s.downcase.strip
    next if seen[s]
    seen[s] = true
    result << s
  end
  result.join(' ')
end

def sanitize_excerpt(excerpt)
  return '' unless excerpt
  raw = excerpt.to_s
  stripped = raw.gsub(/<[^>]+>/, '').gsub(/\s+/, ' ').strip
  stripped.length > 160 ? "#{stripped[0, 157]}..." : stripped
end

def compute_image_flags(img_path, static_paths)
  return { png: 0, avif: 0, webp: 0, card_avif: 0, card_webp: 0 } if img_path.empty?

  variants = {
    png:       img_path.sub(/\.svg\z/i, '_og.png'),
    avif:      img_path.sub(/\.svg\z/i, '_og.avif').sub(/\.png\z/i, '_og.avif'),
    webp:      img_path.sub(/\.svg\z/i, '_og.webp').sub(/\.png\z/i, '_og.webp'),
    card_avif: img_path.sub(/\.svg\z/i, '_card.avif').sub(/\.png\z/i, '_card.avif'),
    card_webp: img_path.sub(/\.svg\z/i, '_card.webp').sub(/\.png\z/i, '_card.webp')
  }

  variants.transform_values do |path|
    key = path.start_with?('/') ? path : "/#{path}"
    static_paths[key] ? 1 : 0
  end
end
