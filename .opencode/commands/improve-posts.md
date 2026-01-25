# /improve-posts - Ralph Loop Post Improvement Command

## Description
Continuously improve blog posts using the Sisyphus Ralph Loop pattern. This command collects RSS news, generates drafts, validates quality, and iteratively improves content.

**Model**: Claude Opus 4.5 ⭐ (High-quality for content generation)

## Usage
```
/improve-posts [--hours=24] [--max-posts=5] [--quality-threshold=80]
```

## Arguments
- `--hours`: Hours of news to collect (default: 24)
- `--max-posts`: Maximum posts to process per iteration (default: 5)
- `--quality-threshold`: Minimum quality score required (default: 80)

## Ralph Loop Configuration
- **Completion Promise**: `POSTS_IMPROVED`
- **Max Iterations**: 50
- **Stop Condition**: All posts meet quality threshold or max iterations reached
- **Agent**: Primary (Opus 4.5)
- **Mode**: Sisyphus orchestrator

## Cost Optimization

**CRITICAL**: Follow these steps to minimize API costs:

1. **Check Cache First**: 
   - Verify `_data/collected_news.json` exists and is < 7 days old
   - Use cached data if available (no API cost)

2. **Use Local Scripts**:
   - `python3 scripts/collect_tech_news.py` (no API cost)
   - `python3 scripts/generate_news_draft.py` (no API cost)
   - `python3 scripts/check_posts.py` (no API cost)

3. **Prioritize Free Tools**:
   - Gemini CLI (OAuth 2.0, free) ⭐ First Choice
   - Cursor/Claude Console (free allocation)
   - API calls (minimize, use only when necessary)

4. **Batch Operations**:
   - Process multiple posts in single run
   - Group API calls together
   - Use prompt caching when possible (90% cost reduction)

## Security

**Security-First Approach**:
- Mask sensitive data in all logs
- Validate all inputs before processing
- Never expose API keys or secrets
- Check file permissions before operations
- Sanitize content before saving

## Workflow Steps

### Phase 1: News Collection (Cost-Optimized)
1. **Check Cache First**: Verify `_data/collected_news.json` exists and is < 7 days old
2. **If Cache Valid**: Use cached data (no API cost)
3. **If Cache Invalid/Missing**: 
   - Run `python3 scripts/collect_tech_news.py --hours {hours}` (local script, no API cost)
   - Verify `_data/collected_news.json` was created
4. Log statistics (total items, by category) with masked sensitive data

### Phase 2: Draft Generation
1. Run `python3 scripts/generate_news_draft.py --prepare --max-posts {max_posts}`
2. Check `_drafts/prompts/` for generated prompt files
3. For each prompt, use AI to generate full blog post

### Phase 3: Quality Validation
For each generated/improved post, validate:

| Criterion | Weight | Threshold |
|-----------|--------|-----------|
| Content Length | 20% | >= 3000 chars |
| Has Tables | 15% | >= 2 tables |
| Has Code Examples | 15% | >= 1 code block |
| Has Checklist | 10% | >= 1 checklist |
| Front Matter Valid | 20% | All required fields |
| Images English Only | 10% | No Korean chars |
| Links Valid | 10% | No broken links |

### Phase 4: Improvement Loop
If quality score < threshold:
1. Identify missing/weak areas
2. Generate improvement suggestions
3. Apply improvements
4. Re-validate
5. Repeat until threshold met or max iterations

### Phase 5: Finalization
1. Move approved posts from `_drafts/` to `_posts/`
2. Generate SVG images for posts
3. Run validation scripts
4. Update processed news IDs

## Quality Score Calculation

```python
def calculate_quality_score(post: dict) -> int:
    score = 0
    
    # Content Length (20%)
    if len(post['content']) >= 3000:
        score += 20
    elif len(post['content']) >= 2000:
        score += 15
    elif len(post['content']) >= 1000:
        score += 10
    
    # Tables (15%)
    table_count = post['content'].count('|---|')
    if table_count >= 3:
        score += 15
    elif table_count >= 2:
        score += 10
    elif table_count >= 1:
        score += 5
    
    # Code Examples (15%)
    code_count = post['content'].count('```')
    if code_count >= 4:  # 2+ code blocks
        score += 15
    elif code_count >= 2:
        score += 10
    
    # Checklist (10%)
    if '- [ ]' in post['content'] or '- [x]' in post['content']:
        score += 10
    
    # Front Matter (20%)
    required_fields = ['title', 'date', 'category', 'tags', 'excerpt']
    if all(f in post['front_matter'] for f in required_fields):
        score += 20
    
    # English Images (10%)
    if not has_korean_in_image_refs(post['content']):
        score += 10
    
    # Valid Links (10%)
    if not has_broken_links(post['content']):
        score += 10
    
    return score
```

## Example Invocation

```bash
# Standard daily improvement
/improve-posts

# Extended collection window
/improve-posts --hours=48 --max-posts=10

# High quality requirements
/improve-posts --quality-threshold=90
```

## Integration with Sisyphus Mode

When running in Sisyphus mode with Ralph Loop:

1. **Intent Recognition**: Sisyphus recognizes `/improve-posts` as a continuous task
2. **Background Execution**: Launches explore agents for codebase analysis
3. **Parallel Processing**: Multiple posts improved simultaneously
4. **Quality Gates**: Each post must pass validation before completion
5. **Progress Tracking**: Todo list updated in real-time
6. **Completion Signal**: Output `<promise>POSTS_IMPROVED</promise>` when done

## Error Handling

| Error | Recovery Action |
|-------|-----------------|
| RSS fetch failed | Use cached data from last 7 days |
| AI generation failed | Retry with alternative prompt |
| Quality validation failed 3x | Mark post for manual review |
| Image generation failed | Use placeholder, flag for later |

## Monitoring

Progress is tracked via:
- `improvement_log.txt` - Detailed operation log
- `_data/processed_news_ids.json` - Processed news tracking
- Todo list in OpenCode session

## Related Commands

| Command | Model | Description |
|---------|-------|-------------|
| `/collect-news` | Sonnet 4 💰 | Only collect news without processing (cost-optimized) |
| `/validate-posts` | Sonnet 4 💰 | Only validate existing posts (cost-optimized) |
| `/generate-images` | Opus 4.5 ⭐ | Generate missing post images (high-quality) |
| `/security-audit` | Sonnet 4 💰 | Security audit and compliance check (cost-optimized) |
| `/cost-optimize` | Sonnet 4 💰 | Analyze and optimize API usage (cost-optimized) |

## Model Selection Rationale

This command uses **Opus 4.5** because:
- High-quality content generation requires advanced reasoning
- Complex multi-step workflows benefit from superior model capabilities
- Content quality directly impacts user experience
- Cost is justified by the value of high-quality blog posts

For cost-optimized operations (validation, analysis), use:
- `/collect-news` (Sonnet 4)
- `/validate-posts` (Sonnet 4)
- `/security-audit` (Sonnet 4)
