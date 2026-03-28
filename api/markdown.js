// Vercel Serverless Function - Markdown Agent API
// AI 에이전트가 블로그 포스트를 마크다운으로 효율적으로 스캔할 수 있는 엔드포인트
//
// Usage:
// GET /api/markdown?path=/posts/2026/02/25/Claude_Code_OpenCode_Best_Practices/
// GET /api/markdown?recent=10
// GET /api/markdown?category=devops
// GET /api/markdown?q=kubernetes
//
// Response: text/markdown

import { checkRateLimit, setRateLimitHeaders } from './lib/ratelimit.js';

const CONFIG = {
  MAX_RESULTS: 50,
  RECENT_DEFAULT: 10,
  MAX_CONTENT_LENGTH: 10000,
  CACHE_TTL: 3600,
  MAX_QUERY_LENGTH: 200,
};

// Dynamic import to prevent crash when @prisma/client is not installed
let prismaInstance = null;
async function getPrisma() {
  if (!prismaInstance) {
    try {
      const { PrismaClient } = await import('@prisma/client');
      prismaInstance = new PrismaClient({ log: ['error'] });
    } catch {
      return null;
    }
  }
  return prismaInstance;
}

// HTML to plain text using char-walking (avoids regex-based tag filter vulnerabilities)
function stripHtml(html) {
  if (!html) return '';
  let result = '';
  let depth = 0;
  for (let i = 0; i < html.length; i++) {
    if (html[i] === '<') { depth++; continue; }
    if (html[i] === '>') { if (depth > 0) depth--; continue; }
    if (depth === 0) result += html[i];
  }
  return result
    .replace(/&nbsp;/g, ' ')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

// Format a single post as markdown
function formatPostMarkdown(post) {
  const lines = [];
  lines.push(`## ${post.title}`);
  lines.push('');
  lines.push(`- **URL**: https://tech.2twodragon.com${post.url}`);
  lines.push(`- **Date**: ${formatDate(post.publishedDate)}`);
  if (post.category) lines.push(`- **Category**: ${post.category}`);
  if (post.tags && post.tags.length) lines.push(`- **Tags**: ${post.tags.join(', ')}`);
  if (post.excerpt) lines.push(`- **Excerpt**: ${stripHtml(post.excerpt)}`);
  lines.push('');

  if (post.content) {
    const content = stripHtml(post.content);
    lines.push(content.substring(0, CONFIG.MAX_CONTENT_LENGTH));
    if (content.length > CONFIG.MAX_CONTENT_LENGTH) {
      lines.push('');
      lines.push(`... [truncated, full content at https://tech.2twodragon.com${post.url}]`);
    }
  }

  return lines.join('\n');
}

function formatDate(date) {
  if (!date) return '';
  const d = new Date(date);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

export default async function handler(req, res) {
  // CORS headers for AI agents - explicit allowlist instead of wildcard
  const allowedOrigins = ['https://tech.2twodragon.com', 'https://twodragon0.github.io'];
  const origin = req.headers.origin;
  if (origin && allowedOrigins.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '0');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('X-Robots-Tag', 'noindex');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Rate Limiting (prevent abuse of database-backed endpoint)
    const clientIp = req.headers['x-forwarded-for']?.split(',')[0]?.trim()
      || req.headers['x-real-ip']
      || 'unknown';

    const rateLimitResult = await checkRateLimit(clientIp, 'anonymous');
    setRateLimitHeaders(res, rateLimitResult.headers);

    if (!rateLimitResult.success) {
      res.setHeader('Content-Type', 'text/markdown; charset=utf-8');
      return res.status(429).send('# Rate Limited\n\nToo many requests. Please try again later.');
    }

    const { path, recent, category, q } = req.query;

    // Input validation: limit query parameter lengths
    if (q && q.length > CONFIG.MAX_QUERY_LENGTH) {
      res.setHeader('Content-Type', 'text/markdown; charset=utf-8');
      return res.status(400).send('# Bad Request\n\nQuery parameter too long.');
    }
    if (path && path.length > 500) {
      res.setHeader('Content-Type', 'text/markdown; charset=utf-8');
      return res.status(400).send('# Bad Request\n\nPath parameter too long.');
    }
    if (category && category.length > 100) {
      res.setHeader('Content-Type', 'text/markdown; charset=utf-8');
      return res.status(400).send('# Bad Request\n\nCategory parameter too long.');
    }

    const prisma = await getPrisma();
    if (!prisma) {
      res.setHeader('Content-Type', 'text/markdown; charset=utf-8');
      return res.status(503).send('# Database Not Configured\n\nPostgreSQL/Prisma is not set up. Try [/llms.txt](/llms.txt) for static content index.');
    }
    let posts = [];
    let title = "Twodragon's Tech Blog";

    if (path) {
      // Single post by URL path
      const normalizedPath = path.endsWith('/') ? path : `${path}/`;
      posts = await prisma.blogPost.findMany({
        where: { url: { contains: normalizedPath.replace(/^\/posts/, '') } },
        take: 1,
      });
      if (posts.length === 0) {
        // Try partial match
        const slug = normalizedPath.split('/').filter(Boolean).pop();
        if (slug) {
          posts = await prisma.blogPost.findMany({
            where: { url: { contains: slug } },
            take: 1,
          });
        }
      }
      title = posts.length > 0 ? posts[0].title : 'Not Found';
    } else if (q) {
      // Search by keyword
      const searchTerm = `%${q}%`;
      posts = await prisma.$queryRaw`
        SELECT id, title, excerpt, url, category, tags, "publishedDate", content, "imageUrl"
        FROM "BlogPost"
        WHERE title ILIKE ${searchTerm}
          OR content ILIKE ${searchTerm}
          OR excerpt ILIKE ${searchTerm}
        ORDER BY "publishedDate" DESC
        LIMIT ${CONFIG.MAX_RESULTS}
      `;
      title = `Search: ${q}`;
    } else if (category) {
      // Filter by category
      posts = await prisma.blogPost.findMany({
        where: { category: { equals: category, mode: 'insensitive' } },
        orderBy: { publishedDate: 'desc' },
        take: CONFIG.MAX_RESULTS,
      });
      title = `Category: ${category}`;
    } else {
      // Recent posts
      const limit = Math.min(parseInt(recent) || CONFIG.RECENT_DEFAULT, CONFIG.MAX_RESULTS);
      posts = await prisma.blogPost.findMany({
        orderBy: { publishedDate: 'desc' },
        take: limit,
      });
      title = `Recent ${limit} Posts`;
    }

    // Build markdown response
    const lines = [];
    lines.push(`# ${title}`);
    lines.push('');
    lines.push(`> Twodragon's Tech Blog - DevSecOps, Cloud Security, Kubernetes`);
    lines.push(`> Generated: ${new Date().toISOString()}`);
    lines.push(`> Results: ${posts.length}`);
    lines.push('');

    if (posts.length === 0) {
      lines.push('No posts found.');
    } else {
      for (const post of posts) {
        lines.push(formatPostMarkdown(post));
        lines.push('');
        lines.push('---');
        lines.push('');
      }
    }

    // Navigation
    lines.push('## Navigation');
    lines.push('');
    lines.push('- [Site Index](/llms.txt)');
    lines.push('- [Full Content](/llms-full.txt)');
    lines.push('- [RSS Feed](/feed.xml)');
    lines.push('- [Sitemap](/sitemap.xml)');

    res.setHeader('Content-Type', 'text/markdown; charset=utf-8');
    res.setHeader('Cache-Control', 'public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400');
    return res.status(200).send(lines.join('\n'));
  } catch (error) {
    console.error('[Markdown API] Error:', error.message);
    res.setHeader('Content-Type', 'text/markdown; charset=utf-8');
    return res.status(503).send(`# Error\n\nService temporarily unavailable.\n\nTry [/llms.txt](/llms.txt) for static content index.`);
  }
}
