#!/usr/bin/env python3
"""Upgrade low-quality post thumbnail SVGs with richer visual elements."""

import os
import re
import json
from datetime import datetime

# Theme definitions with unique visual elements
THEMES = {
    "vulnerability": {
        "accent": "#ef4444", "accent2": "#f97316", "bg2": "#1a0a0a",
        "icon": """
    <g transform="translate(600,250)">
      <path d="M0,-130 L110,-85 L110,30 C110,90 55,135 0,160 C-55,135 -110,90 -110,30 L-110,-85 Z" fill="{accent}" opacity="0.12" stroke="{accent}" stroke-width="2"/>
      <path d="M0,-110 L90,-72 L90,22 C90,72 45,110 0,132 C-45,110 -90,72 -90,22 L-90,-72 Z" fill="none" stroke="{accent}" stroke-width="1.5" stroke-dasharray="8,4" opacity="0.3"/>
      <line x1="-40" y1="-50" x2="40" y2="50" stroke="{accent}" stroke-width="4" stroke-linecap="round" opacity="0.8"/>
      <line x1="40" y1="-50" x2="-40" y2="50" stroke="{accent}" stroke-width="4" stroke-linecap="round" opacity="0.8"/>
      <circle cx="0" cy="0" r="20" fill="none" stroke="{accent}" stroke-width="2.5" opacity="0.6"/>
    </g>""",
        "extras": """
    <g opacity="0.5">
      <polygon points="150,420 165,395 180,420" fill="none" stroke="#fbbf24" stroke-width="1.5"/>
      <text x="165" y="416" font-family="Arial" font-size="10" fill="#fbbf24" text-anchor="middle">!</text>
      <polygon points="1020,150 1035,125 1050,150" fill="none" stroke="#fbbf24" stroke-width="1.5"/>
      <text x="1035" y="146" font-family="Arial" font-size="10" fill="#fbbf24" text-anchor="middle">!</text>
      <polygon points="950,450 965,425 980,450" fill="none" stroke="#fbbf24" stroke-width="1.5"/>
      <text x="965" y="446" font-family="Arial" font-size="10" fill="#fbbf24" text-anchor="middle">!</text>
    </g>""",
        "code_lines": ["CVE-2026-XXXX", "CVSS: 9.8 CRITICAL", "patch --apply fix", "vuln.scan(target)"],
    },
    "ransomware": {
        "accent": "#ef4444", "accent2": "#dc2626", "bg2": "#1a0505",
        "icon": """
    <g transform="translate(600,240)">
      <rect x="-50" y="-40" width="100" height="80" rx="10" fill="#1e293b" stroke="{accent}" stroke-width="2.5"/>
      <path d="M-25,-40 L-25,-65 C-25,-90 25,-90 25,-65 L25,-40" fill="none" stroke="{accent}" stroke-width="3.5" stroke-linecap="round"/>
      <circle cx="0" cy="0" r="12" fill="{accent}" opacity="0.7"/>
      <rect x="-3" y="2" width="6" height="18" rx="3" fill="{accent}" opacity="0.9"/>
      <path d="M-80,-10 L-55,-10 M-80,10 L-55,10" stroke="{accent}" stroke-width="2" stroke-dasharray="4,2" opacity="0.4"/>
      <path d="M55,-10 L80,-10 M55,10 L80,10" stroke="{accent}" stroke-width="2" stroke-dasharray="4,2" opacity="0.4"/>
    </g>""",
        "extras": """
    <g font-family="Courier New" font-size="12" fill="{accent}" opacity="0.15">
      <text x="80" y="150">ENCRYPTED</text>
      <text x="950" y="180">LOCKED</text>
      <text x="100" y="430">$$$ RANSOM $$$</text>
      <text x="920" y="450">decrypt.key</text>
    </g>""",
        "code_lines": ["encrypt(data)", "ransom_note.txt", "bitcoin: bc1q...", "key_exchange()"],
    },
    "supply_chain": {
        "accent": "#8b5cf6", "accent2": "#7c3aed", "bg2": "#0a0a1e",
        "icon": """
    <g transform="translate(600,240)">
      <rect x="-90" y="-30" width="60" height="60" rx="8" fill="#1e293b" stroke="{accent}" stroke-width="2"/>
      <rect x="-15" y="-30" width="60" height="60" rx="8" fill="#1e293b" stroke="{accent}" stroke-width="2"/>
      <rect x="60" y="-30" width="60" height="60" rx="8" fill="#1e293b" stroke="#ef4444" stroke-width="2"/>
      <line x1="-30" y1="0" x2="-15" y2="0" stroke="{accent}" stroke-width="2" marker-end="none"/>
      <line x1="45" y1="0" x2="60" y2="0" stroke="#ef4444" stroke-width="2"/>
      <text x="-60" y="6" font-family="Courier New" font-size="16" fill="{accent}" text-anchor="middle">OK</text>
      <text x="15" y="6" font-family="Courier New" font-size="16" fill="{accent}" text-anchor="middle">OK</text>
      <text x="90" y="6" font-family="Courier New" font-size="16" fill="#ef4444" text-anchor="middle">!!</text>
      <path d="M90,-30 L90,-55 C90,-55 90,-70 75,-70 L-75,-70 C-75,-70 -90,-70 -90,-55 L-90,-30" fill="none" stroke="{accent}" stroke-width="1" stroke-dasharray="4,3" opacity="0.3"/>
    </g>""",
        "extras": """
    <g opacity="0.4">
      <circle cx="200" cy="150" r="4" fill="{accent}"/><circle cx="220" cy="160" r="3" fill="{accent}"/>
      <line x1="200" y1="150" x2="220" y2="160" stroke="{accent}" stroke-width="1"/>
      <circle cx="1000" cy="420" r="4" fill="{accent}"/><circle cx="980" cy="410" r="3" fill="{accent}"/>
      <line x1="1000" y1="420" x2="980" y2="410" stroke="{accent}" stroke-width="1"/>
    </g>""",
        "code_lines": ["npm install pkg", "pip install lib", "verify(hash)", "dependency.lock"],
    },
    "ai_security": {
        "accent": "#3b82f6", "accent2": "#06b6d4", "bg2": "#0a0a1e",
        "icon": """
    <g transform="translate(600,240)">
      <circle cx="0" cy="0" r="60" fill="#1e293b" stroke="{accent}" stroke-width="2.5"/>
      <circle cx="0" cy="0" r="45" fill="none" stroke="{accent}" stroke-width="1" stroke-dasharray="6,3" opacity="0.3"/>
      <circle cx="-15" cy="-10" r="8" fill="{accent}" opacity="0.5"/>
      <circle cx="15" cy="-10" r="8" fill="{accent}" opacity="0.5"/>
      <path d="M-20,15 Q0,30 20,15" fill="none" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>
      <line x1="-60" y1="-30" x2="-95" y2="-55" stroke="{accent2}" stroke-width="1.5" opacity="0.4"/>
      <circle cx="-100" cy="-60" r="8" fill="#1e293b" stroke="{accent2}" stroke-width="1.5" opacity="0.5"/>
      <line x1="60" y1="-30" x2="95" y2="-55" stroke="{accent2}" stroke-width="1.5" opacity="0.4"/>
      <circle cx="100" cy="-60" r="8" fill="#1e293b" stroke="{accent2}" stroke-width="1.5" opacity="0.5"/>
      <line x1="-55" y1="30" x2="-85" y2="55" stroke="{accent2}" stroke-width="1.5" opacity="0.4"/>
      <circle cx="-90" cy="60" r="8" fill="#1e293b" stroke="{accent2}" stroke-width="1.5" opacity="0.5"/>
      <line x1="55" y1="30" x2="85" y2="55" stroke="{accent2}" stroke-width="1.5" opacity="0.4"/>
      <circle cx="90" cy="60" r="8" fill="#1e293b" stroke="{accent2}" stroke-width="1.5" opacity="0.5"/>
    </g>""",
        "extras": """
    <g font-family="Courier New" font-size="10" fill="{accent}" opacity="0.12">
      <text x="80" y="130">model.predict()</text>
      <text x="950" y="160">tensor.eval()</text>
      <text x="60" y="440">agent.run(task)</text>
      <text x="920" y="430">llm.generate()</text>
    </g>""",
        "code_lines": ["agent.execute()", "model.eval()", "prompt_inject()", "guardrail.check()"],
    },
    "cloud": {
        "accent": "#06b6d4", "accent2": "#3b82f6", "bg2": "#0a0a1e",
        "icon": """
    <g transform="translate(600,230)">
      <path d="M-80,20 C-80,-40 -40,-70 10,-70 C30,-70 50,-60 60,-45 C70,-55 90,-55 105,-40 C130,-40 140,-20 140,0 C140,25 125,40 100,40 L-60,40 C-80,40 -100,25 -100,5 C-100,-5 -90,-15 -80,-15 Z" fill="#1e293b" stroke="{accent}" stroke-width="2.5"/>
      <path d="M-60,20 C-60,-25 -25,-50 15,-50 C30,-50 45,-42 52,-30 C60,-38 75,-38 87,-27 C105,-27 115,-12 115,5 C115,22 103,33 82,33 L-42,33 C-58,33 -75,22 -75,5 C-75,-2 -68,-10 -60,-10 Z" fill="none" stroke="{accent}" stroke-width="1" stroke-dasharray="5,3" opacity="0.3"/>
      <rect x="-15" y="-15" width="30" height="25" rx="4" fill="none" stroke="{accent}" stroke-width="2"/>
      <path d="M-8,-15 L-8,-28 C-8,-38 8,-38 8,-28 L8,-15" fill="none" stroke="{accent}" stroke-width="2"/>
      <circle cx="0" cy="0" r="4" fill="{accent}" opacity="0.7"/>
    </g>""",
        "extras": """
    <g opacity="0.3">
      <rect x="100" y="130" width="80" height="50" rx="4" fill="none" stroke="{accent2}" stroke-width="1"/>
      <text x="140" y="160" font-family="Courier New" font-size="9" fill="{accent2}" text-anchor="middle">us-east-1</text>
      <rect x="1020" y="400" width="80" height="50" rx="4" fill="none" stroke="{accent2}" stroke-width="1"/>
      <text x="1060" y="430" font-family="Courier New" font-size="9" fill="{accent2}" text-anchor="middle">ap-ne-2</text>
    </g>""",
        "code_lines": ["aws configure", "kubectl apply", "terraform plan", "cloud.deploy()"],
    },
    "blockchain": {
        "accent": "#f59e0b", "accent2": "#f97316", "bg2": "#1a0f00",
        "icon": """
    <g transform="translate(600,240)">
      <rect x="-80" y="-35" width="50" height="50" rx="6" fill="#1e293b" stroke="{accent}" stroke-width="2"/>
      <rect x="-15" y="-35" width="50" height="50" rx="6" fill="#1e293b" stroke="{accent}" stroke-width="2"/>
      <rect x="50" y="-35" width="50" height="50" rx="6" fill="#1e293b" stroke="{accent}" stroke-width="2"/>
      <line x1="-30" y1="-10" x2="-15" y2="-10" stroke="{accent}" stroke-width="2"/>
      <line x1="35" y1="-10" x2="50" y2="-10" stroke="{accent}" stroke-width="2"/>
      <text x="-55" y="-4" font-family="Courier New" font-size="14" fill="{accent}" text-anchor="middle" opacity="0.7">#1</text>
      <text x="10" y="-4" font-family="Courier New" font-size="14" fill="{accent}" text-anchor="middle" opacity="0.7">#2</text>
      <text x="75" y="-4" font-family="Courier New" font-size="14" fill="{accent}" text-anchor="middle" opacity="0.7">#3</text>
      <text x="10" y="50" font-family="Arial" font-size="28" fill="{accent}" text-anchor="middle" font-weight="bold" opacity="0.3">B</text>
    </g>""",
        "extras": """
    <g opacity="0.2">
      <text x="130" y="180" font-family="Courier New" font-size="11" fill="{accent}">hash: 0x7f3a...</text>
      <text x="900" y="200" font-family="Courier New" font-size="11" fill="{accent}">nonce: 42981</text>
      <text x="100" y="420" font-family="Courier New" font-size="11" fill="{accent}">block.verify()</text>
      <text x="930" y="440" font-family="Courier New" font-size="11" fill="{accent}">tx.confirm()</text>
    </g>""",
        "code_lines": ["tx.sign(key)", "block.hash()", "BTC: $71,000", "ledger.verify()"],
    },
    "apt_malware": {
        "accent": "#ef4444", "accent2": "#8b5cf6", "bg2": "#1a0505",
        "icon": """
    <g transform="translate(600,240)">
      <circle cx="0" cy="0" r="50" fill="#1e293b" stroke="{accent}" stroke-width="2"/>
      <circle cx="0" cy="0" r="35" fill="none" stroke="{accent}" stroke-width="1" stroke-dasharray="4,3" opacity="0.4"/>
      <circle cx="-12" cy="-8" r="7" fill="{accent}" opacity="0.7"/>
      <circle cx="12" cy="-8" r="7" fill="{accent}" opacity="0.7"/>
      <circle cx="-12" cy="-8" r="3" fill="#0a0a1a"/>
      <circle cx="12" cy="-8" r="3" fill="#0a0a1a"/>
      <path d="M-12,15 L12,15" stroke="{accent}" stroke-width="2.5" stroke-linecap="round"/>
      <line x1="-50" y1="-25" x2="-80" y2="-50" stroke="{accent}" stroke-width="1.5" opacity="0.5"/>
      <line x1="50" y1="-25" x2="80" y2="-50" stroke="{accent}" stroke-width="1.5" opacity="0.5"/>
      <line x1="-50" y1="25" x2="-80" y2="50" stroke="{accent}" stroke-width="1.5" opacity="0.5"/>
      <line x1="50" y1="25" x2="80" y2="50" stroke="{accent}" stroke-width="1.5" opacity="0.5"/>
      <circle cx="-85" cy="-55" r="5" fill="{accent}" opacity="0.3"/>
      <circle cx="85" cy="-55" r="5" fill="{accent}" opacity="0.3"/>
      <circle cx="-85" cy="55" r="5" fill="{accent}" opacity="0.3"/>
      <circle cx="85" cy="55" r="5" fill="{accent}" opacity="0.3"/>
    </g>""",
        "extras": """
    <g opacity="0.4">
      <polygon points="150,420 165,395 180,420" fill="none" stroke="#fbbf24" stroke-width="1.5"/>
      <text x="165" y="416" font-family="Arial" font-size="10" fill="#fbbf24" text-anchor="middle">!</text>
      <polygon points="1030,160 1045,135 1060,160" fill="none" stroke="#fbbf24" stroke-width="1.5"/>
      <text x="1045" y="156" font-family="Arial" font-size="10" fill="#fbbf24" text-anchor="middle">!</text>
    </g>""",
        "code_lines": ["C2: connect()", "exfil(data)", "persist(rootkit)", "lateral_move()"],
    },
    "zero_day": {
        "accent": "#ef4444", "accent2": "#f59e0b", "bg2": "#1a0808",
        "icon": """
    <g transform="translate(600,240)">
      <rect x="-55" y="-65" width="110" height="110" rx="12" fill="#1e293b" stroke="{accent}" stroke-width="2.5"/>
      <line x1="-55" y1="-30" x2="55" y2="-30" stroke="{accent}" stroke-width="1.5" opacity="0.5"/>
      <text x="0" y="-40" font-family="Arial" font-size="16" fill="{accent}" text-anchor="middle" font-weight="bold" opacity="0.8">0-DAY</text>
      <text x="0" y="5" font-family="Courier New" font-size="36" fill="{accent}" text-anchor="middle" font-weight="bold" opacity="0.5">0</text>
      <line x1="-30" y1="-20" x2="30" y2="40" stroke="{accent2}" stroke-width="3" stroke-linecap="round" opacity="0.6"/>
      <line x1="30" y1="-20" x2="-30" y2="40" stroke="{accent2}" stroke-width="3" stroke-linecap="round" opacity="0.6"/>
    </g>""",
        "extras": """
    <g opacity="0.4">
      <polygon points="180,160 195,135 210,160" fill="none" stroke="#fbbf24" stroke-width="1.5"/>
      <text x="195" y="156" font-family="Arial" font-size="10" fill="#fbbf24" text-anchor="middle">!</text>
      <polygon points="990,420 1005,395 1020,420" fill="none" stroke="#fbbf24" stroke-width="1.5"/>
      <text x="1005" y="416" font-family="Arial" font-size="10" fill="#fbbf24" text-anchor="middle">!</text>
      <polygon points="1050,150 1065,125 1080,150" fill="none" stroke="#fbbf24" stroke-width="1.5"/>
      <text x="1065" y="146" font-family="Arial" font-size="10" fill="#fbbf24" text-anchor="middle">!</text>
    </g>""",
        "code_lines": ["CVE-2026-XXXX", "exploit(0day)", "patch: PENDING", "alert: CRITICAL"],
    },
    "docker": {
        "accent": "#06b6d4", "accent2": "#3b82f6", "bg2": "#0a0a1e",
        "icon": """
    <g transform="translate(600,235)">
      <rect x="-80" y="-20" width="160" height="80" rx="10" fill="#1e293b" stroke="{accent}" stroke-width="2.5"/>
      <g transform="translate(-50,-5)">
        <rect x="0" y="0" width="22" height="18" rx="2" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.6"/>
        <rect x="28" y="0" width="22" height="18" rx="2" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.6"/>
        <rect x="56" y="0" width="22" height="18" rx="2" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.6"/>
        <rect x="0" y="24" width="22" height="18" rx="2" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.6"/>
        <rect x="28" y="24" width="22" height="18" rx="2" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.6"/>
        <rect x="56" y="24" width="22" height="18" rx="2" fill="#ef4444" stroke="#ef4444" stroke-width="1.5" opacity="0.3"/>
      </g>
      <path d="M-80,-20 C-100,-40 -60,-55 -40,-50 C-20,-60 20,-60 40,-50 C60,-55 100,-40 80,-20" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.3"/>
    </g>""",
        "extras": """
    <g font-family="Courier New" font-size="10" fill="{accent}" opacity="0.15">
      <text x="80" y="140">docker build .</text>
      <text x="950" y="160">container.run()</text>
      <text x="60" y="430">FROM alpine:3.20</text>
      <text x="930" y="450">EXPOSE 8080</text>
    </g>""",
        "code_lines": ["docker pull img", "container.exec()", "Dockerfile", "compose up -d"],
    },
    "phishing": {
        "accent": "#ef4444", "accent2": "#f59e0b", "bg2": "#1a0808",
        "icon": """
    <g transform="translate(600,230)">
      <path d="M0,-100 L0,-20 C0,10 -25,30 -25,30 C-25,30 0,50 25,30 C25,30 50,10 50,-20 L50,-35" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>
      <circle cx="-25" cy="35" r="6" fill="{accent}" opacity="0.6"/>
      <line x1="0" y1="-100" x2="0" y2="-140" stroke="{accent}" stroke-width="2" opacity="0.3"/>
      <rect x="-50" y="60" width="100" height="65" rx="6" fill="#1e293b" stroke="{accent2}" stroke-width="2"/>
      <line x1="-50" y1="65" x2="0" y2="95" stroke="{accent2}" stroke-width="1.5" opacity="0.5"/>
      <line x1="50" y1="65" x2="0" y2="95" stroke="{accent2}" stroke-width="1.5" opacity="0.5"/>
      <line x1="-30" y1="105" x2="30" y2="105" stroke="{accent2}" stroke-width="1" opacity="0.3"/>
      <line x1="-25" y1="115" x2="25" y2="115" stroke="{accent2}" stroke-width="1" opacity="0.3"/>
    </g>""",
        "extras": """
    <g opacity="0.3">
      <text x="150" y="180" font-family="Courier New" font-size="10" fill="{accent}">From: admin@...</text>
      <text x="900" y="200" font-family="Courier New" font-size="10" fill="{accent}">Click here now</text>
      <text x="120" y="440" font-family="Courier New" font-size="10" fill="{accent}">credential.steal</text>
      <text x="920" y="430" font-family="Courier New" font-size="10" fill="{accent}">redirect(evil)</text>
    </g>""",
        "code_lines": ["phish.send()", "cred.capture()", "vishing_call()", "social_eng()"],
    },
    "code_security": {
        "accent": "#22c55e", "accent2": "#3b82f6", "bg2": "#0a1a0a",
        "icon": """
    <g transform="translate(600,235)">
      <rect x="-80" y="-55" width="160" height="110" rx="10" fill="#1e293b" stroke="{accent}" stroke-width="2"/>
      <rect x="-75" y="-50" width="150" height="20" rx="4" fill="{accent}" opacity="0.1"/>
      <circle cx="-60" cy="-40" r="4" fill="#ef4444" opacity="0.6"/>
      <circle cx="-48" cy="-40" r="4" fill="#fbbf24" opacity="0.6"/>
      <circle cx="-36" cy="-40" r="4" fill="#22c55e" opacity="0.6"/>
      <text x="-60" y="-15" font-family="Courier New" font-size="10" fill="{accent}" opacity="0.7">$ code --secure</text>
      <text x="-60" y="2" font-family="Courier New" font-size="10" fill="{accent2}" opacity="0.5">  scanning...</text>
      <text x="-60" y="19" font-family="Courier New" font-size="10" fill="#ef4444" opacity="0.5">  3 vulns found</text>
      <text x="-60" y="36" font-family="Courier New" font-size="10" fill="{accent}" opacity="0.7">$ fix --apply</text>
    </g>""",
        "extras": """
    <g opacity="0.3">
      <rect x="100" y="130" width="120" height="60" rx="6" fill="none" stroke="{accent2}" stroke-width="1"/>
      <text x="160" y="155" font-family="Courier New" font-size="9" fill="{accent2}" text-anchor="middle">main.go</text>
      <text x="160" y="175" font-family="Courier New" font-size="9" fill="{accent}" text-anchor="middle">SAFE</text>
      <rect x="980" y="400" width="120" height="60" rx="6" fill="none" stroke="#ef4444" stroke-width="1"/>
      <text x="1040" y="425" font-family="Courier New" font-size="9" fill="#ef4444" text-anchor="middle">api.py</text>
      <text x="1040" y="445" font-family="Courier New" font-size="9" fill="#ef4444" text-anchor="middle">VULN</text>
    </g>""",
        "code_lines": ["lint --fix", "test --coverage", "audit --strict", "deploy --safe"],
    },
}

# SVG data for each file to upgrade
UPGRADES = [
    {
        "file": "2025-05-09-Cloud_Security_Course_7Batch_-_4Week_AWS_Vulnerability_Inspection_and_ISMS_Response_Guide.svg",
        "theme": "cloud",
        "title": "AWS Vulnerability & ISMS",
        "subtitle": "Cloud Security Course 7th | Week 4 Practical Guide",
        "badge": "COURSE",
        "date": "May 9, 2025",
    },
    {
        "file": "2026-01-25-Tech_Security_Weekly_Digest.svg",
        "theme": "vulnerability",
        "title": "VMware vCenter KEV Patch",
        "subtitle": "Weekly Digest | Fortinet SSO Bypass + Sandworm DynoWiper",
        "badge": "WEEKLY DIGEST",
        "date": "Jan 25, 2026",
    },
    {
        "file": "2026-02-01-Tech_Security_Weekly_Digest_AI_OpenSSL_Zero_Day_OWASP_Agentic_Fortinet.svg",
        "theme": "zero_day",
        "title": "AI Finds 12 OpenSSL 0-Days",
        "subtitle": "Weekly Digest | OWASP Agentic AI + Fortinet Patch",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 1, 2026",
    },
    {
        "file": "2026-02-04-AI_vs_Claude_Code_AI_Coding_Assistant_Comparison.svg",
        "theme": "code_security",
        "title": "AI Coding Assistant Comparison",
        "subtitle": "Claude Code vs Copilot | Security + DevSecOps + FinOps",
        "badge": "DEEP DIVE",
        "date": "Feb 4, 2026",
    },
    {
        "file": "2026-02-04-Tech_Security_Weekly_Digest_AI_Docker_Data_Go.svg",
        "theme": "docker",
        "title": "Docker AI CVE-2025-11953",
        "subtitle": "Weekly Digest | CVSS 9.8 RCE + Data Pipeline Attack",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 4, 2026",
    },
    {
        "file": "2026-02-05-Tech_Security_Weekly_Digest_CVE_AI_Malware_Go.svg",
        "theme": "apt_malware",
        "title": "n8n RCE + NGINX Hijack",
        "subtitle": "Weekly Digest | AsyncRAT Campaign + CVE Analysis",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 5, 2026",
    },
    {
        "file": "2026-02-08-Tech_Security_Weekly_Digest_AI_Ransomware_Data.svg",
        "theme": "phishing",
        "title": "Signal Phishing + Ransomware",
        "subtitle": "Weekly Digest | State-Sponsored Attack + BlackField",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 8, 2026",
    },
    {
        "file": "2026-02-09-Blockchain_Tech_Digest_Bithumb_Bitcoin.svg",
        "theme": "blockchain",
        "title": "Bithumb $44B Incident",
        "subtitle": "Blockchain Digest | Bitcoin $71K + Operational Security",
        "badge": "BLOCKCHAIN",
        "date": "Feb 9, 2026",
    },
    {
        "file": "2026-02-09-Security_Cloud_Digest_AI_VirusTotal_AWS_Agentic.svg",
        "theme": "supply_chain",
        "title": "AI Supply Chain Security",
        "subtitle": "Security Digest | VirusTotal AI + AWS Agentic",
        "badge": "SECURITY",
        "date": "Feb 9, 2026",
    },
    {
        "file": "2026-02-10-AI_Cloud_Digest_Meta_Prometheus_Google_OTLP_AWS.svg",
        "theme": "ai_security",
        "title": "Meta Prometheus + OTLP",
        "subtitle": "AI Cloud Digest | Google Observability + AWS Update",
        "badge": "AI CLOUD",
        "date": "Feb 10, 2026",
    },
    {
        "file": "2026-02-10-Security_Digest_SolarWinds_UNC3886_LLM_Attack.svg",
        "theme": "apt_malware",
        "title": "SolarWinds RCE + UNC3886",
        "subtitle": "Security Digest | Telecom Espionage + LLM Attack",
        "badge": "SECURITY",
        "date": "Feb 10, 2026",
    },
    {
        "file": "2026-02-12-Tech_Security_Weekly_Digest_AI_Cloud_Security_Agent.svg",
        "theme": "supply_chain",
        "title": "Supply Chain + APT36 RAT",
        "subtitle": "Weekly Digest | Outlook Add-in Attack + Windows Update",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 12, 2026",
    },
    {
        "file": "2026-02-13-Tech_Security_Weekly_Digest_AI_Go_Security_Agent.svg",
        "theme": "supply_chain",
        "title": "Lazarus Supply Chain Attack",
        "subtitle": "Weekly Digest | Copilot Studio Vuln + FinOps Security",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 13, 2026",
    },
    {
        "file": "2026-02-14-Weekly_Security_Digest_Microsoft_Zero_Day_Apple_Ivanti_EPMM.svg",
        "theme": "zero_day",
        "title": "Microsoft 6x Zero-Day Patch",
        "subtitle": "Weekly Digest | Apple Emergency + Ivanti EPMM Attack",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 14, 2026",
    },
    {
        "file": "2026-02-17-Weekly_Tech_Security_Digest_AI_Cloud_Risk.svg",
        "theme": "ai_security",
        "title": "AI Agent + Patch Tuesday",
        "subtitle": "Weekly Digest | Cloud Cost Optimization + Kimwolf Botnet",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 17, 2026",
    },
    {
        "file": "2026-02-19-Tech_Security_Weekly_Digest_AWS_Security_Zero-Day_CVE.svg",
        "theme": "zero_day",
        "title": "Dell RecoverPoint 0-Day",
        "subtitle": "Weekly Digest | AWS Security Update + CVE-2026-2329",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 19, 2026",
    },
    {
        "file": "2026-02-20-Tech_Blog_Weekly_Digest_AI_Data_Cloud.svg",
        "theme": "cloud",
        "title": "AI Alignment + EKS Flyte",
        "subtitle": "Weekly Digest | Docker Security + Cloud Native Trends",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 20, 2026",
    },
    {
        "file": "2026-02-21-Tech_Security_Weekly_Digest_Data_Rust_AI_Threat.svg",
        "theme": "vulnerability",
        "title": "CVE-2025-49113 + Rust Supply",
        "subtitle": "Weekly Digest | Ransomware Response + Claude Security",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 21, 2026",
    },
    {
        "file": "2026-02-23-Tech_Security_Weekly_Digest_AI_Ransomware_Data_Bitcoin.svg",
        "theme": "ransomware",
        "title": "Vertical AI + BlackField",
        "subtitle": "Weekly Digest | Ransomware Defense + Data Protection",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 23, 2026",
    },
    {
        "file": "2026-02-24-Tech_Security_Weekly_Digest_Malware_AI_Docker_LLM.svg",
        "theme": "apt_malware",
        "title": "APT28 MacroMaze Campaign",
        "subtitle": "Weekly Digest | Docker Hardening + LLM Operations Risk",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 24, 2026",
    },
    {
        "file": "2026-02-26-Tech_Security_Weekly_Digest_AI_Go_AWS_API.svg",
        "theme": "apt_malware",
        "title": "UNC2814 GRIDTIDE Campaign",
        "subtitle": "Weekly Digest | Claude Code RCE + Vishing Trends",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 26, 2026",
    },
    {
        "file": "2026-02-28-Tech_Security_Weekly_Digest_Go_AI_Malware.svg",
        "theme": "phishing",
        "title": "Pig Butchering $61M Seized",
        "subtitle": "Weekly Digest | FreePBX Mass Breach + Go Crypto Backdoor",
        "badge": "WEEKLY DIGEST",
        "date": "Feb 28, 2026",
    },
]


def generate_svg(cfg):
    theme = THEMES[cfg["theme"]]
    accent = theme["accent"]
    accent2 = theme["accent2"]
    bg2 = theme["bg2"]
    icon = theme["icon"].replace("{accent}", accent).replace("{accent2}", accent2)
    extras = theme["extras"].replace("{accent}", accent).replace("{accent2}", accent2)
    code_lines = theme["code_lines"]

    # Badge color mapping
    badge_color = accent
    if cfg["badge"] in ("WEEKLY DIGEST", "WEEKLY"):
        badge_color = "#ef4444"
    elif cfg["badge"] in ("DEEP DIVE", "COURSE"):
        badge_color = "#8b5cf6"
    elif cfg["badge"] == "BLOCKCHAIN":
        badge_color = "#f59e0b"
    elif cfg["badge"] in ("SECURITY", "AI CLOUD"):
        badge_color = "#3b82f6"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0a0a1a"/>
      <stop offset="100%" style="stop-color:{bg2}"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{accent}"/>
      <stop offset="100%" style="stop-color:{accent2}"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="softglow">
      <feGaussianBlur stdDeviation="20" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="shadow">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000" flood-opacity="0.3"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" fill="url(#bg)"/>

  <!-- Subtle grid -->
  <g opacity="0.04">
    <line x1="60" y1="0" x2="60" y2="630" stroke="#fff" stroke-width="1"/>
    <line x1="120" y1="0" x2="120" y2="630" stroke="#fff" stroke-width="1"/>
    <line x1="180" y1="0" x2="180" y2="630" stroke="#fff" stroke-width="1"/>
    <line x1="240" y1="0" x2="240" y2="630" stroke="#fff" stroke-width="1"/>
    <line x1="960" y1="0" x2="960" y2="630" stroke="#fff" stroke-width="1"/>
    <line x1="1020" y1="0" x2="1020" y2="630" stroke="#fff" stroke-width="1"/>
    <line x1="1080" y1="0" x2="1080" y2="630" stroke="#fff" stroke-width="1"/>
    <line x1="1140" y1="0" x2="1140" y2="630" stroke="#fff" stroke-width="1"/>
  </g>

  <!-- Ambient glow -->
  <circle cx="600" cy="280" r="250" fill="{accent}" opacity="0.04" filter="url(#softglow)"/>
  <circle cx="300" cy="180" r="150" fill="{accent2}" opacity="0.05" filter="url(#softglow)"/>
  <circle cx="900" cy="400" r="180" fill="{accent}" opacity="0.03" filter="url(#softglow)"/>

  <!-- Central icon -->
  <g filter="url(#shadow)">
{icon}
  </g>

  <!-- Theme extras -->
{extras}

  <!-- Floating code fragments -->
  <g font-family="Courier New, monospace" font-size="11" opacity="0.12" fill="{accent}">
    <text x="50" y="100">{code_lines[0]}</text>
    <text x="950" y="120">{code_lines[1]}</text>
    <text x="70" y="480">{code_lines[2]}</text>
    <text x="920" y="500">{code_lines[3]}</text>
  </g>

  <!-- Title -->
  <text x="600" y="510" font-family="Arial, sans-serif" font-size="36" font-weight="bold" fill="white" text-anchor="middle" filter="url(#glow)">{cfg["title"]}</text>
  <text x="600" y="548" font-family="Arial, sans-serif" font-size="16" fill="#94a3b8" text-anchor="middle">{cfg["subtitle"]}</text>

  <!-- Top badges -->
  <rect x="40" y="25" width="160" height="32" rx="16" fill="{badge_color}" opacity="0.2" stroke="{badge_color}" stroke-width="1"/>
  <text x="120" y="47" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="{badge_color}" text-anchor="middle">{cfg["badge"]}</text>

  <rect x="1000" y="25" width="160" height="32" rx="16" fill="#3b82f6" opacity="0.2" stroke="#3b82f6" stroke-width="1"/>
  <text x="1080" y="47" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#93c5fd" text-anchor="middle">{cfg["date"]}</text>

  <!-- Footer -->
  <text x="1160" y="615" font-family="Arial, sans-serif" font-size="13" fill="#475569" text-anchor="end">tech.2twodragon.com</text>
</svg>'''
    return svg


def main():
    img_dir = "assets/images"
    updated = 0
    for cfg in UPGRADES:
        path = os.path.join(img_dir, cfg["file"])
        if not os.path.exists(path):
            print(f"  SKIP (not found): {cfg['file']}")
            continue
        svg = generate_svg(cfg)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(svg)
        updated += 1
        print(f"  UPGRADED: {cfg['file']} ({len(svg)}B, theme={cfg['theme']})")

    print(f"\nTotal upgraded: {updated}/{len(UPGRADES)}")


if __name__ == "__main__":
    main()
