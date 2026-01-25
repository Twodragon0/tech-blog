# OpenCode Configuration for Tech Blog

This directory contains OpenCode configuration for automated blog post improvement using Sisyphus mode and Ralph Loop.

## Configuration Files

- `opencode.json` - Main OpenCode configuration
- `commands/improve-posts.md` - Ralph Loop command documentation

## Quick Start

### Sisyphus Mode with Ralph Loop

```bash
# Start OpenCode in Sisyphus mode
opencode sisyphus

# Run Ralph Loop commands
/improve-posts
/collect-news
/validate-posts
/generate-images
```

## Agents

### Model Selection Strategy
**Cost-Optimized Approach**: Use high-quality models (Opus 4.5) only for complex tasks requiring code generation or high-quality content. Use cost-efficient models (Sonnet 4) for validation, analysis, and read-only tasks.

### Primary Agent
- **Purpose**: Main content improvement and generation (complex tasks)
- **Mode**: Primary (Sisyphus orchestrator)
- **Model**: Claude Opus 4.5 ⭐ (high-quality for content/code generation)
- **Permissions**: Full (write, edit, bash)
- **Max Steps**: 50
- **Temperature**: 0.3 (balanced creativity)
- **Use Cases**: Content generation, complex coding, image generation

### Explore Agent
- **Purpose**: Codebase analysis and discovery (read-only, cost-optimized)
- **Mode**: Subagent (read-only)
- **Model**: Claude Sonnet 4 💰 (cost-efficient for analysis)
- **Permissions**: None (read-only)
- **Max Steps**: 20
- **Temperature**: 0.2 (focused analysis)
- **Use Cases**: Codebase exploration, cost analysis, read-only tasks

### Validate Agent
- **Purpose**: Quality checks and security audits (rule-based, cost-optimized)
- **Mode**: Subagent (read-only)
- **Model**: Claude Sonnet 4 💰 (cost-efficient for validation)
- **Permissions**: None (read-only)
- **Max Steps**: 10
- **Temperature**: 0.1 (strict validation)
- **Use Cases**: Quality validation, security audits, compliance checks

### Code Agent
- **Purpose**: Complex coding tasks (high-quality for code work)
- **Mode**: Subagent
- **Model**: Claude Opus 4.5 ⭐ (high-quality for coding)
- **Permissions**: Write, edit, bash (with ask for bash)
- **Max Steps**: 30
- **Temperature**: 0.2 (focused coding)
- **Use Cases**: Code writing, refactoring, bug fixing

## Commands

### `/improve-posts`
Ralph Loop command for continuous post improvement.

**Workflow:**
1. Collect RSS news (24h default)
2. Generate draft posts
3. Validate quality (score >= 80)
4. Iteratively improve until threshold met
5. Generate images
6. Final validation

**Completion Promise**: `POSTS_IMPROVED`

### `/collect-news`
Cost-optimized news collection from RSS feeds.

**Model**: Sonnet 4 (cost-efficient) 💰
**Features:**
- Uses cached data when available (7-day TTL)
- Prioritizes local scripts (no API cost)
- Rate limiting enabled (15 req/min)
- Batch processing

**Completion Promise**: `NEWS_COLLECTED`

### `/validate-posts`
Comprehensive post validation.

**Model**: Sonnet 4 (cost-efficient) 💰
**Checks:**
- Front matter completeness
- Link validity
- Image naming (English only)
- Security compliance (secrets, XSS, injection)
- Quality thresholds

**Completion Promise**: `POSTS_VALIDATED`

### `/generate-images`
Generate missing post images.

**Model**: Opus 4.5 (high-quality) ⭐
**Requirements:**
- English filenames only
- SVG format preferred
- No Korean characters
- Local scripts preferred

**Completion Promise**: `IMAGES_GENERATED`

### `/security-audit`
Security audit and compliance check.

**Model**: Sonnet 4 (cost-efficient) 💰
**Checks:**
- Hardcoded secrets
- File permissions
- API usage patterns
- XSS/injection patterns
- Input validation
- Sensitive data exposure

**Completion Promise**: `SECURITY_AUDIT_COMPLETE`

### `/cost-optimize`
API usage optimization and cost analysis.

**Model**: Sonnet 4 (cost-efficient) 💰
**Priority:**
1. Gemini CLI (free) ⭐
2. Local templates
3. Cursor console
4. API calls (minimize)

**Completion Promise**: `COST_OPTIMIZED`

### `/write-code`
Write high-quality code with security best practices.

**Model**: Opus 4.5 (high-quality) ⭐
**Features:**
- Security-first approach
- Type hints and docstrings
- Error handling
- Tests included

**Completion Promise**: `CODE_WRITTEN`

### `/refactor`
Refactor code for better maintainability and security.

**Model**: Opus 4.5 (high-quality) ⭐
**Completion Promise**: `CODE_REFACTORED`

### `/fix-bugs`
Fix bugs and security issues.

**Model**: Opus 4.5 (high-quality) ⭐
**Completion Promise**: `BUGS_FIXED`

## Cost Optimization Strategy

### Model Selection Strategy
**Smart Model Selection**: Use the right model for each task to optimize costs while maintaining quality.

| Task Type | Model | Rationale |
|-----------|-------|-----------|
| Content/Code Generation | Opus 4.5 ⭐ | High-quality output required |
| Code Writing/Refactoring | Opus 4.5 ⭐ | Complex logic, best practices |
| Validation/Analysis | Sonnet 4 💰 | Rule-based, cost-efficient |
| Read-only Exploration | Sonnet 4 💰 | Analysis only, no generation |
| Security Audits | Sonnet 4 💰 | Pattern matching, cost-efficient |

### Pricing Comparison
- **Claude Opus 4.5**: $5/M input, $25/M output (high-quality)
- **Claude Sonnet 4**: ~$3/M input, ~$15/M output (cost-efficient)
- **Cost Savings**: Up to 90% with prompt caching, 50% with batch processing

### Cost Optimization Techniques
1. **Cache First**: Always check cache (7-day TTL) before API calls
2. **Local Scripts**: Use Python scripts (no API cost) when possible
3. **Batch Processing**: Group operations to reduce API calls
4. **Prompt Caching**: Reuse prompts for similar tasks (90% savings)
5. **Model Selection**: Use Sonnet 4 for validation, Opus 4.5 for generation
6. **Rate Limiting**: Respect API rate limits to avoid throttling

### API Usage Priority
1. **Gemini CLI** (OAuth 2.0) - Free ⭐ **First Choice**
2. **Local templates** - No cost
3. **Cursor/Claude Console** - Free allocation
4. **API calls** - Costs money (minimize, use caching)

### Best Practices
- Use cached data when available (7-day TTL)
- Batch operations to reduce API calls
- Use local scripts for preprocessing
- Monitor API usage regularly

## Security Best Practices

### Security-First Approach
All commands include security checks and follow best practices.

### Input Validation
- Always validate user inputs (XSS, injection patterns)
- Sanitize HTML content before rendering
- Validate URLs and file paths
- Check for malicious patterns

### Error Handling
- Never expose sensitive info in errors
- Log detailed errors server-side only
- Mask sensitive data in logs (automatic)
- Use environment variables for secrets
- Implement automatic retry with exponential backoff

### Permissions (Principle of Least Privilege)
- **Primary Agent**: Full permissions (content/code generation)
- **Code Agent**: Write/edit allowed, bash requires approval
- **Explore Agent**: Read-only (no write/edit/bash)
- **Validate Agent**: Read-only (no write/edit/bash)
- Audit file operations regularly

### Security Checks
- Hardcoded secrets detection
- File permission validation
- API usage pattern review
- XSS/injection pattern detection
- Input sanitization verification
- Sensitive data exposure prevention

## Operational Efficiency

### Monitoring
- Track improvement progress in `improvement_log.txt`
- Monitor processed news IDs in `_data/processed_news_ids.json`
- Use todo list for task tracking
- Check quality scores per post

### Error Recovery
- Automatic retry with exponential backoff
- Fallback to cached data on API failure
- Mark posts for manual review after 3 failures
- Use placeholder images on generation failure

### Automation
- Daily news collection (9:00 KST)
- Weekly digest generation (Sunday 10:00 KST)
- Automatic quality validation
- Image generation for new posts

## Quality Gates

### Post Quality Score Criteria

| Criterion | Weight | Threshold |
|-----------|--------|-----------|
| Content Length | 20% | >= 3000 chars |
| Tables | 15% | >= 2 tables |
| Code Blocks | 15% | >= 1 block |
| Checklist | 10% | >= 1 item |
| Front Matter | 20% | All required |
| English Images | 10% | No Korean |
| Valid Links | 10% | No broken |

**Minimum Score**: 80/100

## Troubleshooting

### Common Issues

**Issue**: OpenCode doesn't recognize commands
- **Solution**: Check `opencode.json` syntax and schema version

**Issue**: API rate limiting errors
- **Solution**: Use `/cost-optimize` to review usage, enable caching

**Issue**: Quality validation fails repeatedly
- **Solution**: Check quality gates configuration, review post content

**Issue**: Security audit finds issues
- **Solution**: Review `/security-audit` output, fix immediately

## MCP Servers

OpenCode is configured with popular MCP (Model Context Protocol) servers similar to Cursor. MCP servers provide additional tools and capabilities to the AI agents.

### Available MCP Servers

| Server | Status | Auth Method | Purpose | Configuration |
|--------|--------|-------------|---------|---------------|
| **Playwright** | ✅ Enabled | None | Browser automation and testing | None required |
| **Filesystem** | ✅ Enabled | None | File system operations | `ALLOWED_DIRECTORIES` |
| **Git** | ✅ Enabled | None | Git operations | None required |
| **Memory** | ✅ Enabled | None | Persistent memory storage | None required |
| **Notion** | ⚠️ Disabled | **OAuth 2.0** ⭐ | Notion workspace integration | Remote server (OAuth flow) |
| **YouTube** | ⚠️ Disabled | API Key / OAuth | YouTube video search and info | `YOUTUBE_API_KEY` or Google OAuth |
| **GitHub** | ⚠️ Disabled | OAuth 2.0 / PAT | GitHub repository operations | OAuth app or `GITHUB_TOKEN` |
| **Google Drive** | ⚠️ Disabled | **OAuth 2.0** ⭐ | Google Drive file operations | `gcp-oauth.keys.json` file |
| **Slack** | ⚠️ Disabled | OAuth / Bot Token | Slack workspace integration | `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID` |
| **Brave Search** | ⚠️ Disabled | API Key | Web search via Brave API | `BRAVE_API_KEY` |
| **Postgres** | ⚠️ Disabled | Connection String | PostgreSQL database operations | `POSTGRES_CONNECTION_STRING` |
| **SQLite** | ⚠️ Disabled | File Path | SQLite database operations | `SQLITE_DB_PATH` |
| **Puppeteer** | ⚠️ Disabled | None | Browser automation (alternative) | None required |

### OAuth 2.0 Setup (Recommended)

**⭐ OAuth 2.0 is the recommended authentication method** for Notion, Google Drive, and other services. It's more secure than API keys and provides better access control.

#### Notion OAuth Setup

Notion uses a **hosted MCP server** with OAuth 2.0 authentication:

1. **No API key needed** - OAuth flow handles authentication
2. **Connect via OpenCode**: When you enable the Notion MCP server, OpenCode will initiate the OAuth flow
3. **Authorization**: You'll be redirected to Notion to authorize access
4. **Automatic token management**: Tokens are managed automatically

**To enable:**
```json
{
  "mcp": {
    "notion": {
      "enabled": true
    }
  }
}
```

**Security benefits:**
- Your password is never shared
- Existing security policies apply (SSO, MFA)
- Access is limited to your permissions
- Tokens can be revoked anytime

#### Google Drive OAuth Setup

Google Drive MCP server uses OAuth 2.0 with a credentials file:

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable "Google Drive API"

2. **Configure OAuth Consent Screen**:
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" (or "Internal" for Workspace)
   - Add required scopes: `https://www.googleapis.com/auth/drive.readonly`

3. **Create OAuth Client ID**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the JSON file

4. **Setup Credentials**:
   ```bash
   # Rename downloaded file to gcp-oauth.keys.json
   mv ~/Downloads/client_secret_*.json gcp-oauth.keys.json
   
   # Set environment variable
   export GCP_OAUTH_KEYS_PATH="./gcp-oauth.keys.json"
   export GOOGLE_DRIVE_CREDENTIALS_PATH="./gcp-oauth.keys.json"
   ```

5. **Run Authentication**:
   ```bash
   # Install the MCP server package
   npx -y @modelcontextprotocol/server-google-drive
   
   # Run authentication (this will open browser for OAuth)
   # The credentials will be saved automatically
   ```

6. **Enable in OpenCode**:
   ```json
   {
     "mcp": {
       "google-drive": {
         "enabled": true,
         "environment": {
           "GCP_OAUTH_KEYS_PATH": "${GCP_OAUTH_KEYS_PATH}",
           "GOOGLE_DRIVE_CREDENTIALS_PATH": "${GOOGLE_DRIVE_CREDENTIALS_PATH}"
         }
       }
     }
   }
   ```

**Security notes:**
- Store `gcp-oauth.keys.json` securely (already in `.gitignore`)
- Use read-only scope (`drive.readonly`) for security
- Credentials are stored locally after first auth

#### GitHub OAuth Setup

GitHub MCP server supports both OAuth 2.0 and Personal Access Tokens (PAT):

**Option 1: OAuth 2.0 (Recommended)**
1. Register OAuth app at [GitHub Developer Settings](https://github.com/settings/developers)
2. Set callback URL (if using hosted OAuth provider)
3. Use client ID and secret

**Option 2: Personal Access Token (Simpler)**
```bash
export GITHUB_TOKEN="ghp_your_personal_access_token"
```

### Security Best Practices

**⚠️ CRITICAL**: All API keys and tokens must be stored as environment variables. Never hardcode secrets in configuration files.

1. **OAuth First**: Prefer OAuth 2.0 over API keys when available
   - More secure (no long-lived tokens)
   - Better access control
   - Easier revocation

2. **Environment Variables**: Set required environment variables before enabling MCP servers:
   ```bash
   # For services that still require API keys
   export YOUTUBE_API_KEY="your-youtube-api-key"
   export BRAVE_API_KEY="your-brave-api-key"
   export GITHUB_TOKEN="your-github-token"
   
   # For OAuth-based services
   export GCP_OAUTH_KEYS_PATH="./gcp-oauth.keys.json"
   export GOOGLE_DRIVE_CREDENTIALS_PATH="./gcp-oauth.keys.json"
   ```

2. **Enable Only What You Need**: MCP servers add to your context window and can quickly accumulate tokens. Be selective about which servers you enable.

3. **File Permissions**: Review file permissions for filesystem and database MCP servers to ensure least privilege access.

4. **API Rate Limits**: Be aware of API rate limits for external services (Notion, GitHub, YouTube, etc.).

### Enabling MCP Servers

#### OAuth-Based Servers (Notion, Google Drive)

**Notion** (OAuth 2.0 - No setup needed):
```json
{
  "mcp": {
    "notion": {
      "enabled": true
    }
  }
}
```
When enabled, OpenCode will initiate the OAuth flow automatically. You'll be redirected to Notion to authorize.

**Google Drive** (OAuth 2.0 - Requires setup):
1. Follow the OAuth setup steps above
2. Ensure `gcp-oauth.keys.json` exists and is authenticated
3. Enable in config:
```json
{
  "mcp": {
    "google-drive": {
      "enabled": true,
      "environment": {
        "GCP_OAUTH_KEYS_PATH": "${GCP_OAUTH_KEYS_PATH}",
        "GOOGLE_DRIVE_CREDENTIALS_PATH": "${GOOGLE_DRIVE_CREDENTIALS_PATH}"
      }
    }
  }
}
```

#### API Key-Based Servers

For servers that still use API keys, set environment variables first:
```bash
export YOUTUBE_API_KEY="your-api-key"
export BRAVE_API_KEY="your-api-key"
```

Then enable in config:
```json
{
  "mcp": {
    "youtube": {
      "enabled": true,
      "environment": {
        "YOUTUBE_API_KEY": "${YOUTUBE_API_KEY}"
      }
    }
  }
}
```

### MCP Server Configuration

All MCP servers are configured in `opencode.json` under the `mcp` key. Each server has:
- `type`: `"local"` for npm-based servers
- `command`: Command to start the server (typically `npx -y @modelcontextprotocol/server-*`)
- `enabled`: Enable/disable the server
- `environment`: Environment variables (use `${VAR_NAME}` syntax)
- `timeout`: Timeout in milliseconds (default: 5000ms)

### Cost Considerations

- **Context Window**: Each enabled MCP server adds tools to the context, increasing token usage
- **API Costs**: External services (Notion, GitHub, YouTube) may have API rate limits or costs
- **Recommendation**: Enable only the MCP servers you actively use

### Troubleshooting

**Issue**: MCP server fails to start
- **Solution**: Check environment variables are set correctly
- **Solution**: Verify npm/npx is available and can install packages
- **Solution**: Check timeout settings (increase if needed)
- **OAuth Issue**: For OAuth-based servers, ensure OAuth flow completed successfully

**Issue**: OAuth authentication fails
- **Notion**: Ensure you're using the remote server URL (`https://mcp.notion.com/mcp`)
- **Google Drive**: Verify `gcp-oauth.keys.json` exists and run authentication: `node ./dist auth`
- **Google Drive**: Check OAuth consent screen is configured correctly in Google Cloud Console
- **Google Drive**: Ensure required scopes are added (`drive.readonly`)

**Issue**: API rate limiting errors
- **Solution**: Review API usage, implement rate limiting in your scripts
- **Solution**: Use caching to reduce API calls
- **OAuth Benefit**: OAuth tokens often have higher rate limits than API keys

**Issue**: Context window exceeded
- **Solution**: Disable unused MCP servers
- **Solution**: Use selective tool enabling per agent
- **Note**: OAuth-based servers (like Notion remote) may add less context than local servers

## Related Documentation

- `AGENTS.md` - AI agent coding guidelines
- `.cursorrules` - Cursor AI rules
- `docs/scripts/README_RALPH_LOOP.md` - Ralph Loop detailed guide
- `scripts/README.md` - Script documentation
- [OpenCode MCP Documentation](https://opencode.ai/docs/mcp-servers/) - Official MCP server guide

## Support

For issues or questions:
1. Check this README
2. Review command documentation in `commands/`
3. Check `AGENTS.md` for guidelines
4. Review OpenCode documentation: https://opencode.ai/docs/
