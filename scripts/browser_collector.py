#!/usr/bin/env python3
"""
CDP Browser Collector - 블로그 테스트, 웹 스크래핑, 성능 모니터링 유틸리티

Usage:
    # 블로그 스크린샷 캡처
    python3 scripts/browser_collector.py screenshot --url https://tech.2twodragon.com

    # Lighthouse 성능 측정
    python3 scripts/browser_collector.py lighthouse --url https://tech.2twodragon.com

    # 웹 스크래핑 (기술 뉴스 수집)
    python3 scripts/browser_collector.py scrape --url https://example.com --selector ".article"

    # 블로그 전체 링크 검증
    python3 scripts/browser_collector.py check-links --url https://tech.2twodragon.com

    # CDP 엔드포인트 연결 (이미 실행 중인 Chrome)
    python3 scripts/browser_collector.py screenshot --cdp ws://localhost:9222
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "_site" / "browser-reports"


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_playwright_script(script_content: str, extra_args: list[str] | None = None):
    """Run a Playwright script via npx."""
    script_path = PROJECT_ROOT / "scripts" / "_tmp_browser_script.mjs"
    try:
        script_path.write_text(script_content, encoding="utf-8")
        cmd = ["npx", "playwright", "test", "--config=-"]
        if extra_args:
            cmd.extend(extra_args)
        result = subprocess.run(
            ["node", str(script_path)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=120,
        )
        if result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            return None
        return result.stdout
    finally:
        script_path.unlink(missing_ok=True)


def screenshot(url: str, output: str | None = None, cdp_endpoint: str | None = None):
    """Take a screenshot of the given URL."""
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output is None:
        sanitized = url.replace("https://", "").replace("http://", "").replace("/", "_")
        output = str(OUTPUT_DIR / f"screenshot_{sanitized}_{timestamp}.png")

    connect_code = ""
    if cdp_endpoint:
        connect_code = f'const browser = await chromium.connectOverCDP("{cdp_endpoint}");'
    else:
        connect_code = "const browser = await chromium.launch();"

    script = f"""
import {{ chromium }} from 'playwright';

(async () => {{
  {connect_code}
  const context = await browser.newContext({{
    viewport: {{ width: 1280, height: 720 }}
  }});
  const page = await context.newPage();
  await page.goto('{url}', {{ waitUntil: 'networkidle', timeout: 60000 }});
  await page.screenshot({{ path: '{output}', fullPage: true }});
  console.log(JSON.stringify({{ status: 'ok', path: '{output}' }}));
  await browser.close();
}})();
"""
    result = run_playwright_script(script)
    if result:
        print(f"Screenshot saved: {output}")
    return output


def lighthouse(url: str, output: str | None = None):
    """Run Lighthouse performance audit."""
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output is None:
        output = str(OUTPUT_DIR / f"lighthouse_{timestamp}.json")

    html_output = output.replace(".json", ".html")

    cmd = [
        "npx", "lighthouse", url,
        "--output=json,html",
        f"--output-path={output.replace('.json', '')}",
        "--chrome-flags=--headless --no-sandbox",
        "--only-categories=performance,accessibility,best-practices,seo",
        "--quiet",
    ]

    print(f"Running Lighthouse audit for {url}...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

    if result.returncode != 0:
        print(f"Lighthouse error: {result.stderr}", file=sys.stderr)
        return None

    # Parse and display summary
    json_file = output.replace(".json", ".report.json")
    if os.path.exists(json_file):
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
        categories = data.get("categories", {})
        print("\n--- Lighthouse Results ---")
        for name, cat in categories.items():
            score = cat.get("score", 0)
            emoji = "✅" if score and score >= 0.9 else "⚠️" if score and score >= 0.5 else "❌"
            print(f"  {emoji} {cat.get('title', name)}: {int((score or 0) * 100)}/100")

        # Core Web Vitals
        audits = data.get("audits", {})
        vitals = {
            "LCP": audits.get("largest-contentful-paint", {}).get("displayValue", "N/A"),
            "FID": audits.get("max-potential-fid", {}).get("displayValue", "N/A"),
            "CLS": audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A"),
            "TTFB": audits.get("server-response-time", {}).get("displayValue", "N/A"),
        }
        print("\n--- Core Web Vitals ---")
        for metric, value in vitals.items():
            print(f"  {metric}: {value}")

        print(f"\nFull report: {json_file}")
        print(f"HTML report: {html_output}")
    return output


def scrape(url: str, selector: str, output: str | None = None, cdp_endpoint: str | None = None):
    """Scrape content from a URL using CSS selector."""
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output is None:
        output = str(OUTPUT_DIR / f"scrape_{timestamp}.json")

    connect_code = ""
    if cdp_endpoint:
        connect_code = f'const browser = await chromium.connectOverCDP("{cdp_endpoint}");'
    else:
        connect_code = "const browser = await chromium.launch();"

    script = f"""
import {{ chromium }} from 'playwright';
import {{ writeFileSync }} from 'fs';

(async () => {{
  {connect_code}
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('{url}', {{ waitUntil: 'networkidle', timeout: 60000 }});

  const elements = await page.$$eval('{selector}', els => els.map(el => ({{
    text: el.textContent?.trim(),
    href: el.getAttribute('href') || null,
    html: el.innerHTML?.substring(0, 500)
  }})));

  const result = {{
    url: '{url}',
    selector: '{selector}',
    timestamp: new Date().toISOString(),
    count: elements.length,
    items: elements
  }};

  writeFileSync('{output}', JSON.stringify(result, null, 2));
  console.log(JSON.stringify({{ status: 'ok', count: elements.length, path: '{output}' }}));
  await browser.close();
}})();
"""
    result = run_playwright_script(script)
    if result:
        data = json.loads(result.strip().split("\n")[-1])
        print(f"Scraped {data.get('count', 0)} items → {output}")
    return output


def check_links(url: str, cdp_endpoint: str | None = None):
    """Check all links on the blog for broken links."""
    ensure_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = str(OUTPUT_DIR / f"link_check_{timestamp}.json")

    connect_code = ""
    if cdp_endpoint:
        connect_code = f'const browser = await chromium.connectOverCDP("{cdp_endpoint}");'
    else:
        connect_code = "const browser = await chromium.launch();"

    script = f"""
import {{ chromium }} from 'playwright';
import {{ writeFileSync }} from 'fs';

(async () => {{
  {connect_code}
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('{url}', {{ waitUntil: 'networkidle', timeout: 60000 }});

  const links = await page.$$eval('a[href]', els => els.map(el => ({{
    text: el.textContent?.trim()?.substring(0, 100),
    href: el.getAttribute('href')
  }})));

  const results = [];
  for (const link of links) {{
    if (!link.href || link.href.startsWith('#') || link.href.startsWith('javascript:')) continue;
    const fullUrl = link.href.startsWith('http') ? link.href : new URL(link.href, '{url}').href;
    try {{
      const resp = await page.request.head(fullUrl, {{ timeout: 10000 }});
      results.push({{ ...link, url: fullUrl, status: resp.status(), ok: resp.ok() }});
    }} catch (e) {{
      results.push({{ ...link, url: fullUrl, status: 0, ok: false, error: e.message }});
    }}
  }}

  const broken = results.filter(r => !r.ok);
  const report = {{
    url: '{url}',
    timestamp: new Date().toISOString(),
    total: results.length,
    broken: broken.length,
    brokenLinks: broken,
    allLinks: results
  }};

  writeFileSync('{output}', JSON.stringify(report, null, 2));
  console.log(JSON.stringify({{ status: 'ok', total: results.length, broken: broken.length }}));
  await browser.close();
}})();
"""
    result = run_playwright_script(script)
    if result:
        data = json.loads(result.strip().split("\n")[-1])
        total = data.get("total", 0)
        broken = data.get("broken", 0)
        status = "✅" if broken == 0 else "⚠️"
        print(f"{status} Checked {total} links, {broken} broken → {output}")
    return output


def main():
    parser = argparse.ArgumentParser(
        description="CDP Browser Collector for tech-blog",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # screenshot
    p_ss = subparsers.add_parser("screenshot", help="Capture screenshot")
    p_ss.add_argument("--url", required=True, help="URL to capture")
    p_ss.add_argument("--output", help="Output file path")
    p_ss.add_argument("--cdp", dest="cdp_endpoint", help="CDP endpoint (ws://...)")

    # lighthouse
    p_lh = subparsers.add_parser("lighthouse", help="Run Lighthouse audit")
    p_lh.add_argument("--url", required=True, help="URL to audit")
    p_lh.add_argument("--output", help="Output file path")

    # scrape
    p_sc = subparsers.add_parser("scrape", help="Scrape web content")
    p_sc.add_argument("--url", required=True, help="URL to scrape")
    p_sc.add_argument("--selector", required=True, help="CSS selector")
    p_sc.add_argument("--output", help="Output file path")
    p_sc.add_argument("--cdp", dest="cdp_endpoint", help="CDP endpoint (ws://...)")

    # check-links
    p_cl = subparsers.add_parser("check-links", help="Check for broken links")
    p_cl.add_argument("--url", required=True, help="URL to check")
    p_cl.add_argument("--cdp", dest="cdp_endpoint", help="CDP endpoint (ws://...)")

    args = parser.parse_args()

    if args.command == "screenshot":
        screenshot(args.url, args.output, args.cdp_endpoint)
    elif args.command == "lighthouse":
        lighthouse(args.url, args.output)
    elif args.command == "scrape":
        scrape(args.url, args.selector, args.output, args.cdp_endpoint)
    elif args.command == "check-links":
        check_links(args.url, args.cdp_endpoint)


if __name__ == "__main__":
    main()
