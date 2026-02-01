#!/usr/bin/env python3
"""
Code Block Visualization Analysis Tool

Analyzes all code blocks in blog posts and categorizes them into:
1. Mermaid diagram candidates (architecture, flowcharts, sequences)
2. Code image candidates (syntax highlighting)
3. Existing Mermaid diagrams (keep as-is)

Usage:
    python3 scripts/analyze_code_blocks_visualization.py
    python3 scripts/analyze_code_blocks_visualization.py --output report.json
"""

import re
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


# Keywords that suggest a block should be a Mermaid diagram
MERMAID_KEYWORDS = {
    'architecture': ['architecture', 'infrastructure', 'components', 'services', 'modules'],
    'flowchart': ['step', 'process', 'flow', 'workflow', 'pipeline', 'stage', 'phase'],
    'sequence': ['request', 'response', 'api call', 'authentication', 'authorization'],
    'relationship': ['→', '->', '=>', 'connects to', 'depends on', 'relationship'],
    'aws': ['vpc', 's3', 'ec2', 'lambda', 'api gateway', 'cloudfront', 'rds'],
    'k8s': ['pod', 'deployment', 'service', 'ingress', 'configmap', 'namespace'],
}

# Languages that should definitely be code images
CODE_IMAGE_LANGUAGES = {
    'python', 'javascript', 'typescript', 'java', 'go', 'rust', 'c', 'cpp',
    'ruby', 'php', 'swift', 'kotlin', 'scala', 'sql', 'solidity', 'spl'
}

# Languages that could be either Mermaid or images depending on content
FLEXIBLE_LANGUAGES = {
    'yaml', 'bash', 'shell', 'hcl', 'terraform', 'text', 'plaintext', ''
}


def extract_code_blocks(file_path: Path) -> List[Dict]:
    """Extract all code blocks from a markdown file."""
    blocks = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match code blocks with optional language
    pattern = r'```(\w*)\n(.*?)```'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        language = match.group(1).lower() if match.group(1) else ''
        code = match.group(2)
        
        blocks.append({
            'language': language,
            'code': code,
            'start_line': content[:match.start()].count('\n') + 1,
            'length': len(code.splitlines()),
            'file': file_path.name
        })
    
    return blocks


def analyze_block_content(block: Dict) -> str:
    """
    Analyze a code block and determine if it should be:
    - 'mermaid_diagram': Convert to Mermaid diagram
    - 'code_image': Convert to code image
    - 'existing_mermaid': Keep as-is (already Mermaid)
    - 'keep_code': Keep as plain code block
    """
    language = block['language']
    code = block['code'].lower()
    
    # Already a Mermaid diagram
    if language == 'mermaid':
        return 'existing_mermaid'
    
    # Definite code image languages
    if language in CODE_IMAGE_LANGUAGES:
        return 'code_image'
    
    # Flexible languages - analyze content
    if language in FLEXIBLE_LANGUAGES:
        # Check for Mermaid keywords
        mermaid_score = 0
        for category, keywords in MERMAID_KEYWORDS.items():
            for keyword in keywords:
                if keyword in code:
                    mermaid_score += 1
        
        # Check for code indicators
        code_indicators = [
            'import ', 'export ', 'function ', 'class ', 'def ',
            'const ', 'let ', 'var ', '#!/bin/', 'curl ', 'wget '
        ]
        code_score = sum(1 for indicator in code_indicators if indicator in code)
        
        # HCL/Terraform is often infrastructure diagrams
        if language in ['hcl', 'terraform']:
            if mermaid_score >= 2:
                return 'mermaid_diagram'
            else:
                return 'code_image'
        
        # YAML pipelines are often flowcharts
        if language == 'yaml':
            pipeline_keywords = ['stage', 'step', 'job', 'workflow', 'pipeline']
            if any(keyword in code for keyword in pipeline_keywords):
                if mermaid_score >= 3:
                    return 'mermaid_diagram'
            return 'code_image'
        
        # Bash workflows can be sequence diagrams
        if language in ['bash', 'shell']:
            if mermaid_score >= 3 and code_score < 5:
                return 'mermaid_diagram'
            return 'code_image'
        
        # Empty language tag - analyze deeply
        if language == '':
            # Short blocks with high Mermaid keywords
            if block['length'] < 20 and mermaid_score >= 3:
                return 'mermaid_diagram'
            # Code indicators suggest code image
            if code_score >= 3:
                return 'code_image'
            # Long blocks without code indicators might be diagrams
            if block['length'] > 10 and mermaid_score >= 2 and code_score == 0:
                return 'mermaid_diagram'
            # Default to code image for safety
            return 'code_image'
        
        # Default to code image
        return 'code_image'
    
    # Unknown languages - keep as code
    return 'keep_code'


def analyze_all_posts(posts_dir: Path = Path('_posts')) -> Dict:
    """Analyze all code blocks in all posts."""
    results = {
        'total_posts': 0,
        'total_blocks': 0,
        'categories': defaultdict(int),
        'languages': defaultdict(int),
        'recommendations': {
            'mermaid_diagram': [],
            'code_image': [],
            'existing_mermaid': [],
            'keep_code': []
        },
        'stats': {
            'avg_block_length': 0,
            'max_block_length': 0,
            'min_block_length': float('inf')
        }
    }
    
    all_lengths = []
    
    for post_file in sorted(posts_dir.glob('*.md')):
        results['total_posts'] += 1
        blocks = extract_code_blocks(post_file)
        results['total_blocks'] += len(blocks)
        
        for block in blocks:
            # Track language distribution
            lang = block['language'] if block['language'] else '(no language)'
            results['languages'][lang] += 1
            
            # Analyze and categorize
            category = analyze_block_content(block)
            results['categories'][category] += 1
            
            # Add detailed recommendation
            results['recommendations'][category].append({
                'file': block['file'],
                'line': block['start_line'],
                'language': block['language'],
                'length': block['length'],
                'preview': block['code'][:100].replace('\n', ' ')
            })
            
            # Track stats
            all_lengths.append(block['length'])
    
    # Calculate stats
    if all_lengths:
        results['stats']['avg_block_length'] = sum(all_lengths) / len(all_lengths)
        results['stats']['max_block_length'] = max(all_lengths)
        results['stats']['min_block_length'] = min(all_lengths)
    
    return results


def print_report(results: Dict):
    """Print a human-readable report."""
    print("=" * 80)
    print("CODE BLOCK VISUALIZATION ANALYSIS REPORT")
    print("=" * 80)
    print()
    
    print(f"📊 OVERVIEW:")
    print(f"  Total Posts: {results['total_posts']}")
    print(f"  Total Code Blocks: {results['total_blocks']}")
    print()
    
    print(f"📈 STATISTICS:")
    print(f"  Average Block Length: {results['stats']['avg_block_length']:.1f} lines")
    print(f"  Max Block Length: {results['stats']['max_block_length']} lines")
    print(f"  Min Block Length: {results['stats']['min_block_length']} lines")
    print()
    
    print(f"🎨 VISUALIZATION CATEGORIES:")
    total = sum(results['categories'].values())
    for category, count in sorted(results['categories'].items(), key=lambda x: -x[1]):
        percentage = (count / total * 100) if total > 0 else 0
        emoji = {
            'mermaid_diagram': '🔷',
            'code_image': '🖼️ ',
            'existing_mermaid': '✅',
            'keep_code': '📝'
        }.get(category, '❓')
        print(f"  {emoji} {category:20s}: {count:4d} ({percentage:5.1f}%)")
    print()
    
    print(f"🔤 LANGUAGE DISTRIBUTION:")
    for lang, count in sorted(results['languages'].items(), key=lambda x: -x[1])[:15]:
        percentage = (count / results['total_blocks'] * 100) if results['total_blocks'] > 0 else 0
        print(f"  {lang:20s}: {count:4d} ({percentage:5.1f}%)")
    print()
    
    print(f"💡 RECOMMENDATIONS:")
    print(f"  🔷 Mermaid Diagrams: {len(results['recommendations']['mermaid_diagram'])} blocks")
    print(f"     → Convert to visual flowcharts, architectures, sequences")
    print(f"  🖼️  Code Images: {len(results['recommendations']['code_image'])} blocks")
    print(f"     → Convert to syntax-highlighted SVG images")
    print(f"  ✅ Existing Mermaid: {len(results['recommendations']['existing_mermaid'])} blocks")
    print(f"     → Already visualized, keep as-is")
    print(f"  📝 Keep as Code: {len(results['recommendations']['keep_code'])} blocks")
    print(f"     → Small or simple blocks, keep as markdown")
    print()
    
    print(f"🎯 NEXT STEPS:")
    print(f"  1. Review Mermaid candidates and create diagram specifications")
    print(f"  2. Run generate_code_images.py to convert code blocks to images")
    print(f"  3. Update Mermaid.js version to v11 (currently v10.9.5)")
    print(f"  4. Test rendering performance with visualizations")
    print()
    
    # Show sample Mermaid candidates
    if results['recommendations']['mermaid_diagram']:
        print(f"📋 SAMPLE MERMAID CANDIDATES (First 5):")
        for i, rec in enumerate(results['recommendations']['mermaid_diagram'][:5], 1):
            print(f"  {i}. {rec['file']}:{rec['line']}")
            print(f"     Language: {rec['language'] or '(none)'}, Length: {rec['length']} lines")
            print(f"     Preview: {rec['preview']}...")
            print()


def main():
    parser = argparse.ArgumentParser(description='Analyze code blocks for visualization strategy')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--posts-dir', default='_posts', help='Posts directory (default: _posts)')
    args = parser.parse_args()
    
    posts_dir = Path(args.posts_dir)
    if not posts_dir.exists():
        print(f"Error: Posts directory '{posts_dir}' not found")
        return 1
    
    print(f"Analyzing code blocks in {posts_dir}...")
    results = analyze_all_posts(posts_dir)
    
    # Print human-readable report
    print_report(results)
    
    # Save JSON output if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ Detailed results saved to {output_path}")
    
    return 0


if __name__ == '__main__':
    exit(main())
