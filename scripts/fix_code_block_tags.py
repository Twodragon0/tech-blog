#!/usr/bin/env python3
"""
fix_code_block_tags.py - Add language tags to bare code blocks in Jekyll blog posts.

Scans all .md files in _posts/, detects the language of bare code blocks,
and adds appropriate language tags in place.
"""

import glob
import os
import re
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------


def detect_language(lines: list[str]) -> str:
    """Analyze code block lines and return the most appropriate language tag."""
    if not lines:
        return "text"

    text = "\n".join(lines)
    joined = text.lower()

    # --- Dockerfile ---
    first_nonempty = next((l.strip() for l in lines if l.strip()), "")
    dockerfile_keywords = {
        "FROM ",
        "RUN ",
        "COPY ",
        "CMD ",
        "EXPOSE ",
        "WORKDIR ",
        "ENV ",
        "ENTRYPOINT ",
        "ARG ",
        "LABEL ",
        "ADD ",
        "VOLUME ",
        "USER ",
        "HEALTHCHECK ",
        "SHELL ",
    }
    dockerfile_hits = sum(
        1 for l in lines if any(l.strip().startswith(k) for k in dockerfile_keywords)
    )
    if dockerfile_hits >= 2 or (
        dockerfile_hits >= 1 and first_nonempty.startswith("FROM ")
    ):
        return "dockerfile"

    # --- PowerShell ---
    ps_patterns = [
        r"\bGet-\w+",
        r"\bSet-\w+",
        r"\bNew-\w+",
        r"\bRemove-\w+",
        r"\$env:",
        r"-ErrorAction\b",
        r"\| Where-Object\b",
        r"\| Select-Object\b",
        r"\bWrite-Host\b",
        r"\bInvoke-\w+",
    ]
    if any(re.search(p, text) for p in ps_patterns):
        return "powershell"

    # --- Splunk SPL ---
    splunk_markers = [
        "sourcetype=",
        "index=",
        "| stats ",
        "| where ",
        "| table ",
        "| rex ",
        "| search ",
        "| eval ",
        "| transaction ",
    ]
    splunk_hits = sum(1 for m in splunk_markers if m in text)
    if splunk_hits >= 2:
        return "splunk"

    # --- KQL (Kusto / Azure) ---
    kql_tables = [
        "SecurityEvent",
        "AzureActivity",
        "SigninLogs",
        "AuditLogs",
        "CommonSecurityLog",
        "Heartbeat",
        "OfficeActivity",
        "DeviceEvents",
        "ThreatIntelligenceIndicator",
        "AlertEvidence",
    ]
    kql_ops = [
        "| project ",
        "| summarize ",
        "| extend ",
        "| where ",
        "| join ",
        "| union ",
        "| render ",
        "| count",
    ]
    kql_table_hit = any(t in text for t in kql_tables)
    kql_op_hits = sum(1 for op in kql_ops if op in text)
    if kql_table_hit and kql_op_hits >= 1:
        return "kql"

    # --- SQL ---
    sql_patterns = [
        r"\bSELECT\b",
        r"\bINSERT\b",
        r"\bUPDATE\b",
        r"\bDELETE\b",
        r"\bCREATE TABLE\b",
        r"\bALTER TABLE\b",
        r"\bDROP TABLE\b",
        r"\bINNER JOIN\b",
        r"\bLEFT JOIN\b",
        r"\bGROUP BY\b",
    ]
    sql_hits = sum(1 for p in sql_patterns if re.search(p, text, re.IGNORECASE))
    if sql_hits >= 2:
        return "sql"

    # --- HCL / Terraform ---
    hcl_keywords = [
        'resource "',
        'variable "',
        'module "',
        'provider "',
        'data "',
        'output "',
        "locals {",
        "terraform {",
    ]
    hcl_hits = sum(1 for k in hcl_keywords if k in text)
    if hcl_hits >= 1:
        return "hcl"

    # --- NGINX ---
    nginx_keywords = [
        "server {",
        "location ",
        "proxy_pass ",
        "add_header ",
        "listen ",
        "server_name ",
        "root ",
        "fastcgi_pass ",
    ]
    nginx_hits = sum(1 for k in nginx_keywords if k in text)
    if nginx_hits >= 2:
        return "nginx"

    # --- JSON ---
    stripped_text = text.strip()
    if (stripped_text.startswith("{") or stripped_text.startswith("[")) and re.search(
        r'"[^"]+"\s*:', text
    ):
        try:
            import json

            json.loads(text.strip())
            return "json"
        except Exception:
            # Looks like JSON even if not perfectly valid
            if re.search(r'"[^"]+"\s*:', text) and stripped_text.startswith(("{", "[")):
                return "json"

    # --- YAML ---
    yaml_hits = 0
    if stripped_text.startswith("---"):
        yaml_hits += 3
    for line in lines:
        stripped = line.strip()
        if re.match(r"^[\w\-]+\s*:\s+\S", stripped):
            yaml_hits += 1
        if re.match(r"^-\s+\w", stripped):
            yaml_hits += 0.5
    yaml_hits_total = int(yaml_hits)
    # Avoid misidentifying bash variable assignments as yaml
    bash_assign = sum(1 for l in lines if re.match(r"^\w+=\S", l.strip()))
    if yaml_hits_total >= 3 and bash_assign < yaml_hits_total:
        return "yaml"

    # --- XML / HTML ---
    xml_hits = 0
    for line in lines:
        stripped = line.strip()
        if re.match(r"^<[a-zA-Z/!?]", stripped):
            xml_hits += 1
    if xml_hits >= 2:
        if any(
            kw in joined for kw in ["<!doctype html", "<html", "<body", "<div", "<head"]
        ):
            return "html"
        return "xml"

    # --- Rust ---
    rust_patterns = [
        r"\bfn \w+",
        r"\blet mut\b",
        r"\bimpl \w+",
        r"\buse std::",
        r"\bpub fn\b",
    ]
    if any(re.search(p, text) for p in rust_patterns):
        return "rust"

    # --- Go ---
    go_patterns = [r"\bfunc \w+\(", r"\bpackage \w+\b", r"\bimport \(", r"\bfmt\."]
    if any(re.search(p, text) for p in go_patterns):
        return "go"

    # --- Java ---
    java_patterns = [
        r"\bpublic class\b",
        r"\bprivate\b.*\b(void|int|String)\b",
        r"\bSystem\.out\b",
        r"\bimport java\.",
        r"\bpublic static void main\b",
    ]
    if any(re.search(p, text) for p in java_patterns):
        return "java"

    # --- Python ---
    py_patterns = [
        r"^\s*import \w",
        r"^\s*from \w+ import",
        r"^\s*def \w+\s*\(",
        r"^\s*class \w+.*:",
        r"^\s*print\(",
        r"\bif __name__\s*==\s*['\"]__main__['\"]",
        r"^\s*@\w+",
        r"^\s*async def \w+",
    ]
    py_hits = sum(1 for p in py_patterns if re.search(p, text, re.MULTILINE))
    # Python indented function call style
    if py_hits == 0 and re.search(r"^\s{4}\w+\.\w+\(", text, re.MULTILINE):
        py_hits += 1
    if py_hits >= 2:
        return "python"

    # --- CSS ---
    css_hits = 0
    for line in lines:
        stripped = line.strip()
        if re.match(r"^[\.\#\w\-\[\]]+\s*\{", stripped):
            css_hits += 1
        if re.match(
            r"^\s*(color|margin|padding|display|font|background|border|width|height)\s*:",
            stripped,
        ):
            css_hits += 1
    if css_hits >= 3:
        return "css"

    # --- JavaScript / TypeScript ---
    js_patterns = [
        r"\bconst \w+\s*=",
        r"\blet \w+\s*=",
        r"\bvar \w+\s*=",
        r"\bfunction \w+\s*\(",
        r"=>",
        r"\bconsole\.log\(",
        r"\bimport \{",
        r"\bexport (default|const|function|class)\b",
        r"\bmodule\.exports\b",
        r"\basync function\b",
        r"\bawait \w+",
        r"\bnew \w+\(",
    ]
    js_hits = sum(1 for p in js_patterns if re.search(p, text))
    if js_hits >= 2:
        return "javascript"

    # --- Markdown (checklist / table) ---
    md_hits = 0
    for line in lines:
        stripped = line.strip()
        if re.match(r"^-\s+\[[ xX]\]", stripped):
            md_hits += 2
        if stripped.startswith("| ") and stripped.endswith(" |"):
            md_hits += 1
    if md_hits >= 3:
        return "markdown"

    # --- Shell / Bash ---
    bash_indicators = [
        r"^\s*\$\s+\S",  # $ prompt
        r"^#!/",  # shebang
        r"^\s*sudo\s+",
        r"^\s*(apt|apt-get|yum|dnf|brew|pip3?|npm|npx)\s+",
        r"^\s*(docker|kubectl|terraform|helm|git|curl|wget|ssh|scp|rsync)\s+",
        r"^\s*(cd|ls|cat|grep|echo|export|alias|chmod|mkdir|rm|mv|cp)\s+",
        r"^\s*dig\s+",
        r"^\s*openssl\s+",
        r"\|\s*\w+",  # pipes
        r"\\\s*$",  # line continuation
        r"^\s*#\s+\w",  # comment line
        r"^\s*(if|for|while|case|do|done|fi|then|else)\b",
        r"^\s*\w+=\$\(",  # var=$(cmd)
        r"^\s*\w+=\"",  # var="value"
        r"^\s*\w+=\`",  # var=`cmd`
    ]
    bash_hits = sum(1 for p in bash_indicators if re.search(p, text, re.MULTILINE))
    if bash_hits >= 1:
        return "bash"

    # Python fallback (single indicator is enough)
    if py_hits >= 1:
        return "python"

    # Single JS indicator
    if js_hits >= 1:
        return "javascript"

    # --- Single yaml match ---
    if yaml_hits_total >= 2:
        return "yaml"

    # --- JSON single brace ---
    if stripped_text.startswith("{") and stripped_text.endswith("}"):
        return "json"

    return "text"


# ---------------------------------------------------------------------------
# File processing
# ---------------------------------------------------------------------------


def process_file(filepath: str) -> dict:
    """Process a single markdown file, tagging bare code blocks in place."""
    with open(filepath, "r", encoding="utf-8") as fh:
        content = fh.read()

    lines = content.split("\n")
    result_lines = []
    changes = defaultdict(int)  # language -> count

    in_code_block = False
    block_lang = None
    block_lines = []
    block_open_idx = None  # index in result_lines where opening ``` sits

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not in_code_block:
            if stripped == "```":
                # Opening bare code block
                in_code_block = True
                block_lang = None
                block_lines = []
                block_open_idx = len(result_lines)
                result_lines.append(line)  # placeholder, will replace after detection
            elif stripped.startswith("```") and len(stripped) > 3:
                # Already has a language tag — skip
                lang = stripped[3:].strip()
                in_code_block = True
                block_lang = lang  # known lang, won't touch
                block_lines = []
                block_open_idx = None
                result_lines.append(line)
            else:
                result_lines.append(line)
        else:
            if stripped == "```":
                # Closing fence
                if block_open_idx is not None:
                    # Detect and patch opening fence
                    detected = detect_language(block_lines)
                    # Replace placeholder
                    result_lines[block_open_idx] = "```" + detected
                    changes[detected] += 1
                else:
                    pass  # already-tagged block, no patch needed
                result_lines.append(line)
                in_code_block = False
                block_lang = None
                block_lines = []
                block_open_idx = None
            else:
                block_lines.append(line)
                result_lines.append(line)

        i += 1

    # If file ended inside a code block (shouldn't happen in valid markdown)
    if in_code_block and block_open_idx is not None and block_lines:
        detected = detect_language(block_lines)
        result_lines[block_open_idx] = "```" + detected
        changes[detected] += 1

    new_content = "\n".join(result_lines)
    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write(new_content)

    return dict(changes)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    posts_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_posts"
    )
    md_files = sorted(
        glob.glob(os.path.join(posts_dir, "**", "*.md"), recursive=True)
        + glob.glob(os.path.join(posts_dir, "*.md"))
    )
    # deduplicate
    md_files = sorted(set(md_files))

    total_fixed = 0
    lang_totals = defaultdict(int)
    file_report = []

    print(f"Scanning {len(md_files)} files in {posts_dir} ...")
    print()

    for filepath in md_files:
        changes = process_file(filepath)
        if changes:
            count = sum(changes.values())
            total_fixed += count
            fname = os.path.basename(filepath)
            file_report.append((fname, changes))
            for lang, n in changes.items():
                lang_totals[lang] += n

    # --- Report ---
    print(f"{'=' * 60}")
    print(f"  Total code blocks fixed: {total_fixed}")
    print(f"{'=' * 60}")

    print("\nBreakdown by language:")
    for lang, n in sorted(lang_totals.items(), key=lambda x: -x[1]):
        bar = "#" * min(n, 50)
        print(f"  {lang:<15} {n:>4}   {bar}")

    text_count = lang_totals.get("text", 0)
    if text_count:
        print(f"\n  Note: {text_count} block(s) tagged as 'text' (could not classify).")

    print(f"\n{'=' * 60}")
    print("Per-file summary (files with changes):")
    print(f"{'=' * 60}")
    for fname, changes in file_report:
        parts = ", ".join(f"{lang}:{n}" for lang, n in sorted(changes.items()))
        print(f"  {fname[:60]:<62} [{parts}]")

    print(
        f"\nDone. {total_fixed} bare code blocks tagged across {len(file_report)} files."
    )


if __name__ == "__main__":
    main()
