# Security Vendor News Collector

보안 벤더 블로그에서 뉴스를 수집하고 블로그 초안을 생성하는 스크립트입니다.

## 지원 벤더

### Endpoint Security
- **Jamf** - Apple device management and security
- **CrowdStrike** - Endpoint detection and response (EDR)
- **SentinelOne** - Autonomous endpoint security

### Network/Cloud Security
- **Zscaler** - Zero trust security platform
- **Zscaler ThreatLabz** - Threat research
- **Cloudflare** - CDN and security services
- **Palo Alto Networks** - Network security
- **Unit 42** - Palo Alto threat research

### Identity & Access Management
- **Okta** - Identity management
- **Okta Security** - Security research

### Observability & SIEM
- **Datadog** - Monitoring and security
- **Datadog Security Labs** - Security research
- **Splunk** - SIEM and observability
- **Elastic Security Labs** - Security research

### DevSecOps & Container Security
- **Snyk** - Developer security
- **Aqua Security** - Container security
- **Sysdig** - Container and cloud security
- **Wiz** - Cloud security posture
- **Lacework** - Cloud security

### Infrastructure
- **HashiCorp** - Infrastructure automation

### Threat Intelligence
- **Mandiant** - Threat intelligence (Google)
- **Tenable** - Vulnerability management
- **Rapid7** - Vulnerability and threat detection

## Usage

### Collect All Vendor News

```bash
# Last 7 days (default)
python3 scripts/generate_vendor_news_draft.py

# Last 30 days
python3 scripts/generate_vendor_news_draft.py --hours 720
```

### Collect Specific Vendors

```bash
# Only network security vendors
python3 scripts/generate_vendor_news_draft.py --vendors cloudflare,zscaler,paloalto

# Only DevSecOps vendors
python3 scripts/generate_vendor_news_draft.py --vendors snyk,aquasec,sysdig,wiz
```

### List Available Vendors

```bash
python3 scripts/generate_vendor_news_draft.py --list-vendors
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--vendors` | all | Comma-separated vendor list |
| `--hours` | 168 (7 days) | Hours to look back |
| `--max-items` | 30 | Maximum items per draft |
| `--output-dir` | `_drafts` | Output directory |

## Output

Draft posts are saved to `_drafts/` directory:

```
_drafts/
└── 2026-01-22-Security_Vendor_Blog_Weekly_Review.md
```

To publish, move to `_posts/`:

```bash
mv _drafts/2026-01-22-Security_Vendor_Blog_Weekly_Review.md _posts/
```

## collect_tech_news.py Updates

The following vendor sources were added to `collect_tech_news.py`:

```python
# Security Vendors
"jamf", "zscaler", "zscaler_research", "cloudflare", 
"okta", "okta_security", "datadog", "crowdstrike",
"paloalto", "unit42", "snyk", "hashicorp", "wiz",
"lacework", "sentinelone", "aquasec", "sysdig",
"tenable", "rapid7", "splunk", "mandiant", "elastic_security"
```

## Automation

### GitHub Actions

Add to `.github/workflows/daily-news.yml`:

```yaml
- name: Collect vendor news
  run: |
    python3 scripts/generate_vendor_news_draft.py --hours 168
```

### Cron Job

```bash
# Weekly on Monday at 9 AM
0 9 * * 1 cd /path/to/tech-blog && python3 scripts/generate_vendor_news_draft.py
```

## Related Scripts

| Script | Purpose |
|--------|---------|
| `collect_tech_news.py` | Base news collector (RSS feeds) |
| `collect_kisa_security.py` | KISA security notices |
| `generate_news_draft.py` | General news draft generator |
