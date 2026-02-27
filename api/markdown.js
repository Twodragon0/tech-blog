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

import { PrismaClient } from '@prisma/client';

const CONFIG = {
  MAX_RESULTS: 50,
  RECENT_DEFAULT: 10,
  MAX_CONTENT_LENGTH: 10000,
  CACHE_TTL: 3600,
};

let prismaInstance = null;
function getPrisma() {
  if (!prismaInstance) {
    prismaInstance = new PrismaClient({ log: ['error'] });
  }
  return prismaInstance;
}

// HTML to plain text (iterative strip to prevent nested tag bypass)
function stripHtml(html) {
  if (!html) return '';
  let text = html;
  let prev;
  // Iteratively remove nested script/style blocks
  do {
    prev = text;
    text = text.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    text = text.replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '');
  } while (text !== prev);
  // Iteratively remove HTML tags (prevents <scr<script>ipt> bypass)
  do {
    prev = text;
    text = text.replace(/<[^>]*>/g, '');
  } while (text !== prev);
  // Decode entities only after all tags are fully removed
  text = text
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\n{3,}/g, '\n\n')
    .trim();
  return text;
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
  // CORS headers for AI agents
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Robots-Tag', 'noindex');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { path, recent, category, q } = req.query;
    const prisma = getPrisma();
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
