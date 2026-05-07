#!/usr/bin/env python3
"""Check for broken internal /posts/ links in _posts/*.md files."""
import re
import glob
import os

posts = glob.glob("_posts/*.md")
permalinks = set()
for p in posts:
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.md", os.path.basename(p))
    if m:
        y, mo, d, t = m.groups()
        permalinks.add(f"/posts/{y}/{mo}/{d}/{t}/")

broken = []
pattern = re.compile(r'(?:href=["\']|\]\(|\s)(/posts/[^\s\)\\\'"<>]+/)')
for p in posts:
    content = open(p, encoding="utf-8").read()
    for m in pattern.finditer(content):
        link = m.group(1)
        if link not in permalinks:
            broken.append((link, os.path.basename(p)))

print(f"broken={len(broken)}")
for link, fn in broken[:30]:
    print(f"  {fn}: {link}")
