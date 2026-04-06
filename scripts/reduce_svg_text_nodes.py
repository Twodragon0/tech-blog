#!/usr/bin/env python3
"""
Reduce text node count in SVG files to 10 or fewer.
Removes decorative/redundant text nodes while keeping essential ones.
"""

import os
import sys
import xml.etree.ElementTree as ET

SVG_DIR = "/Users/yong/Desktop/personal/tech-blog/assets/images"

# SVG namespace
NS = "http://www.w3.org/2000/svg"

# Per-file removal targets: list of exact text content strings to remove.
# Each entry is either a plain string (remove ALL occurrences) or a dict
# {"text": "...", "max": N} to remove only the first N occurrences.
REMOVAL_TARGETS = {
    # 12 -> 10: remove both "!" nodes (they appear twice)
    "2026-03-18-Tech_Security_Weekly_Digest_AI_AWS_Data_Ransomware.svg": [
        "!",  # removes both occurrences -> -2 = 10
    ],
    # 21 -> 10: remove 11 decorative nodes
    "2026-03-21-Tech_Security_Weekly_Digest_Security_CVE_AI_Malware.svg": [
        "COMPLIANCE",
        "VERIFIED SECURE",
        "!",
        "9.8",
        "CRITICAL",
        "CVSS",
        "v3.1",
        "EXPLOITS",
        "Active",
        "CVE SCORING",
        "CVE DETECTED",
    ],
    # 15 -> 10: remove 5 decorative nodes
    "2026-03-22-Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple.svg": [
        "AI",  # standalone short label
        "CVE",  # standalone short label
        "01101100",  # binary string
        "10110010",  # binary string
        "11001011",  # binary string
    ],
    # 15 -> 10: remove 5 decorative nodes
    "2026-03-23-Tech_Security_Weekly_Digest_Ransomware.svg": [
        "COMPLIANCE",
        "VERIFIED SECURE",
        "!",
        "THREAT DETECTED",
        "THREAT LEVEL: CRITICAL",
    ],
    # 19 -> 10: remove 9 decorative nodes (two "!" nodes count as 2)
    "2026-03-24-Tech_Security_Weekly_Digest_Malware_Data_AWS_AI.svg": [
        "RANSOMWARE",
        "Threat Detection",
        "COMPLIANCE",
        "Security Verified",
        "!",  # removes both occurrences -> -2
        "DATA BREACH",
        "Alert Active",
        "CYBERSECURITY",
    ],
    # 14 -> 10: remove 4 decorative nodes
    # "APT" appears as standalone [9] AND inside "Zero-Day APT" [6].
    # We only want the standalone one removed -> use max:1 with index hint.
    # Since "APT" standalone comes AFTER "Zero-Day APT", we remove the last
    # occurrence by targeting only the exact standalone "APT" node.
    "2026-04-01-Tech_Security_Weekly_Digest_Zero-Day_Go_AI_AWS.svg": [
        "ISO 27001",
        "0-DAY",
        "TRUECONF CVE",
        {"text": "APT", "max": 1},  # only standalone "APT", not "Zero-Day APT"
    ],
    # 13 -> 10: remove 3 decorative nodes
    "2026-04-02-Tech_Security_Weekly_Digest_AI_Malware.svg": [
        "npm",
        "!",
        "UAC",
    ],
}


def get_text_content(elem):
    """Get the full text content of a text element including tspan children."""
    parts = []
    if elem.text and elem.text.strip():
        parts.append(elem.text.strip())
    for child in elem:
        local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if local == "tspan":
            if child.text and child.text.strip():
                parts.append(child.text.strip())
    return " ".join(parts).strip()


def count_text_nodes(tree_root):
    """Count all <text> elements in SVG."""
    count = 0
    for elem in tree_root.iter():
        local = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        if local == "text":
            count += 1
    return count


def remove_text_nodes(filepath, targets):
    """Remove text elements whose content matches any target string.

    targets: list of str (remove all occurrences) or dict {"text": str, "max": int}
    """
    ET.register_namespace("", NS)
    tree = ET.parse(filepath)
    root = tree.getroot()

    before_count = count_text_nodes(root)

    # Normalise targets into {"text": ..., "max": ..., "removed": 0}
    normalised = []
    for t in targets:
        if isinstance(t, dict):
            normalised.append(
                {"text": t["text"], "max": t.get("max", 9999), "removed": 0}
            )
        else:
            normalised.append({"text": t, "max": 9999, "removed": 0})

    removed = []
    to_remove = []  # (parent, child, label)

    for parent in root.iter():
        for child in list(parent):
            local = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if local == "text":
                content = get_text_content(child)
                for spec in normalised:
                    if content == spec["text"] and spec["removed"] < spec["max"]:
                        to_remove.append((parent, child, spec["text"]))
                        spec["removed"] += 1
                        break

    for parent, child, label in to_remove:
        parent.remove(child)
        removed.append(label)

    after_count = count_text_nodes(root)

    # Write back with UTF-8 and XML declaration
    tree.write(filepath, encoding="unicode", xml_declaration=False)

    # Re-read and add xml declaration if missing
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("<?xml"):
        content = '<?xml version="1.0" encoding="UTF-8"?>\n' + content

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return before_count, after_count, removed


def main():
    print("=" * 60)
    print("SVG Text Node Reducer")
    print("=" * 60)

    all_pass = True

    for filename, targets in REMOVAL_TARGETS.items():
        filepath = os.path.join(SVG_DIR, filename)

        if not os.path.exists(filepath):
            print(f"\n[MISSING] {filename}")
            continue

        print(f"\nProcessing: {filename}")
        before, after, removed = remove_text_nodes(filepath, targets)

        status = "PASS" if after <= 10 else "FAIL"
        if after > 10:
            all_pass = False

        print(f"  Before: {before} nodes  ->  After: {after} nodes  [{status}]")
        print(f"  Removed ({len(removed)}): {removed}")

    print("\n" + "=" * 60)

    # Final verification pass
    print("Final verification:")
    print("-" * 60)
    for filename in REMOVAL_TARGETS:
        filepath = os.path.join(SVG_DIR, filename)
        if not os.path.exists(filepath):
            continue
        tree = ET.parse(filepath)
        count = count_text_nodes(tree.getroot())
        status = "PASS" if count <= 10 else "FAIL"
        print(f"  {filename[-60:]}: {count} nodes [{status}]")

    print("=" * 60)
    if all_pass:
        print("All files pass (<=10 text nodes).")
    else:
        print("Some files still exceed 10 text nodes - manual review needed.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
