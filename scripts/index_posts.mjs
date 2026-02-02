#!/usr/bin/env node

import { PrismaClient } from '@prisma/client';
import matter from 'gray-matter';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const postsDir = path.join(__dirname, '..', '_posts');

const args = process.argv.slice(2);
const DRY_RUN = args.includes('--dry-run');
const VERBOSE = args.includes('--verbose');

function stripHtml(html) {
  return html
    .replace(/<[^>]*>/g, '')
    .replace(/\{%.*?%\}/g, '')
    .replace(/\{\{.*?\}\}/g, '')
    .replace(/!\[.*?\]\(.*?\)/g, '')
    .replace(/\[([^\]]+)\]\(.*?\)/g, '$1')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/[*_~`]/g, '')
    .replace(/^[-*+]\s/gm, '')
    .replace(/^\d+\.\s/gm, '')
    .replace(/^>\s/gm, '')
    .replace(/```[\s\S]*?```/g, '')
    .replace(/\|[^\n]+\|/g, '')
    .replace(/[-|]+\s*\n/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function generateUrl(filename) {
  // Jekyll permalink: /posts/:year/:month/:day/:title/
  const match = filename.match(/^(\d{4})-(\d{2})-(\d{2})-(.+)\.md$/);
  if (match) {
    const [, year, month, day, titleSlug] = match;
    return `/posts/${year}/${month}/${day}/${titleSlug}/`;
  }
  const slug = filename.replace(/\.md$/, '');
  return `/posts/${slug}/`;
}

function parsePost(filePath) {
  const filename = path.basename(filePath);
  const raw = fs.readFileSync(filePath, 'utf-8');
  const { data, content } = matter(raw);

  const slug = filename.replace(/\.md$/, '');

  let category = null;
  if (data.category) {
    category = String(data.category);
  } else if (Array.isArray(data.categories) && data.categories.length > 0) {
    category = String(data.categories[0]);
  }

  let tags = [];
  if (Array.isArray(data.tags)) {
    tags = data.tags.map(String);
  }

  let publishedDate = new Date();
  if (data.date) {
    publishedDate = new Date(data.date);
  } else {
    const dateMatch = filename.match(/^(\d{4}-\d{2}-\d{2})/);
    if (dateMatch) publishedDate = new Date(dateMatch[1]);
  }

  const strippedContent = stripHtml(content);
  const contentPlain = strippedContent.substring(0, 500);

  return {
    slug,
    title: data.title || slug,
    excerpt: data.excerpt || null,
    content: strippedContent,
    contentPlain,
    category,
    tags,
    publishedDate,
    imageUrl: data.image || null,
    url: generateUrl(filename),
  };
}

async function main() {
  console.log('📚 Tech Blog Post Indexer');
  console.log('========================');

  if (DRY_RUN) console.log('🔍 DRY RUN - no database writes\n');

  if (!fs.existsSync(postsDir)) {
    console.error(`❌ Posts directory not found: ${postsDir}`);
    process.exit(1);
  }

  const files = fs.readdirSync(postsDir)
    .filter(f => f.endsWith('.md'))
    .sort();

  console.log(`Found ${files.length} posts in _posts/\n`);

  if (DRY_RUN) {
    for (const [i, file] of files.entries()) {
      try {
        const post = parsePost(path.join(postsDir, file));
        console.log(`[${i + 1}/${files.length}] ✓ ${file}`);
        if (VERBOSE) {
          console.log(`  Title: ${post.title}`);
          console.log(`  Category: ${post.category || 'none'}`);
          console.log(`  Tags: ${post.tags.join(', ') || 'none'}`);
          console.log(`  Content: ${post.content.length} chars`);
          console.log(`  URL: ${post.url}\n`);
        }
      } catch (err) {
        console.log(`[${i + 1}/${files.length}] ⚠ ${file} - ${err.message}`);
      }
    }
    console.log('\n========================');
    console.log('Dry run complete. No database changes.');
    return;
  }

  const prisma = new PrismaClient({ log: ['error'] });
  let created = 0, updated = 0, skipped = 0, errors = 0;

  try {
    for (const [i, file] of files.entries()) {
      try {
        const post = parsePost(path.join(postsDir, file));

        const existing = await prisma.blogPost.findUnique({
          where: { slug: post.slug },
          select: { id: true },
        });

        if (existing) {
          await prisma.blogPost.update({
            where: { slug: post.slug },
            data: {
              title: post.title,
              excerpt: post.excerpt,
              content: post.content,
              contentPlain: post.contentPlain,
              category: post.category,
              tags: post.tags,
              publishedDate: post.publishedDate,
              imageUrl: post.imageUrl,
              url: post.url,
            },
          });
          updated++;
        } else {
          await prisma.blogPost.create({ data: post });
          created++;
        }

        console.log(`[${i + 1}/${files.length}] ✓ ${file}`);
        if (VERBOSE) {
          console.log(`  ${existing ? 'Updated' : 'Created'}: ${post.title}`);
        }
      } catch (err) {
        errors++;
        console.log(`[${i + 1}/${files.length}] ✗ ${file} - ${err.message}`);
      }
    }

    console.log('\n========================');
    console.log('Results:');
    console.log(`  Created: ${created}`);
    console.log(`  Updated: ${updated}`);
    console.log(`  Skipped: ${skipped}`);
    console.log(`  Errors:  ${errors}`);
  } finally {
    await prisma.$disconnect();
  }
}

const startTime = Date.now();
main()
  .then(() => {
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log(`  Total time: ${elapsed}s`);
  })
  .catch((err) => {
    console.error('❌ Fatal error:', err.message);
    process.exit(1);
  });
