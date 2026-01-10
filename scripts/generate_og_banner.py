#!/usr/bin/env python3
"""
Open Graph 배너 이미지 생성 스크립트
카카오톡, SNS 공유용 OG 이미지를 자동으로 생성합니다.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import re

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ 필요한 패키지가 설치되지 않았습니다.")
    print("다음 명령어로 설치해주세요:")
    print("  pip install Pillow")
    sys.exit(1)

def parse_frontmatter(file_path):
    """Front matter 파싱"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Front matter가 있는지 확인
    if not content.startswith('---'):
        return {}
    
    # Front matter 추출
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    
    frontmatter_text = parts[1].strip()
    metadata = {}
    
    # 간단한 YAML 파싱
    for line in frontmatter_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # 따옴표 제거
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            # 리스트 처리
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
            
            metadata[key] = value
    
    return metadata

# 색상 테마 (DevSecOps 테마)
COLORS = {
    'background': '#0a0e27',  # 어두운 네이비
    'primary': '#00d4ff',    # 시안 블루
    'secondary': '#00ff88',  # 그린
    'accent': '#ff6b6b',     # 레드
    'text': '#ffffff',       # 화이트
    'text_secondary': '#b0b0b0',  # 회색
}

# 카테고리별 색상
CATEGORY_COLORS = {
    'security': '#ff6b6b',
    'devsecops': '#00d4ff',
    'devops': '#00ff88',
    'cloud': '#4dabf7',
    'kubernetes': '#339af0',
    'finops': '#ffd43b',
    'incident': '#ff8787',
    'default': '#00d4ff'
}

def get_font_path():
    """시스템 폰트 경로 찾기"""
    # macOS
    if sys.platform == 'darwin':
        font_paths = [
            '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/AppleGothic.ttf',
        ]
    # Linux
    elif sys.platform.startswith('linux'):
        font_paths = [
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        ]
    # Windows
    else:
        font_paths = [
            'C:/Windows/Fonts/malgun.ttf',
            'C:/Windows/Fonts/gulim.ttc',
        ]
    
    for path in font_paths:
        if os.path.exists(path):
            return path
    
    # 기본 폰트 사용
    return None

def load_font(size, bold=False):
    """폰트 로드"""
    font_path = get_font_path()
    try:
        if font_path:
            if bold:
                # Bold 폰트 시도
                bold_path = font_path.replace('.ttf', 'Bold.ttf').replace('.ttc', 'Bold.ttc')
                if os.path.exists(bold_path):
                    return ImageFont.truetype(bold_path, size)
                return ImageFont.truetype(font_path, size)
            return ImageFont.truetype(font_path, size)
    except Exception as e:
        print(f"⚠️  폰트 로드 실패: {e}")
    
    # 기본 폰트
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

def wrap_text(text, font, max_width):
    """텍스트를 여러 줄로 나누기"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines if lines else [text]

def generate_default_og_image(output_path, site_title="Twodragon's Tech Blog", site_description="DevSecOps, DevOps, FinOps 전문 기술 블로그"):
    """기본 OG 이미지 생성"""
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), color=COLORS['background'])
    draw = ImageDraw.Draw(img)
    
    # 그라데이션 배경 (간단한 원형 그라데이션)
    for i in range(height):
        alpha = int(255 * (1 - i / height) * 0.3)
        color = tuple(min(255, c + alpha) for c in (10, 14, 39))
        draw.rectangle([(0, i), (width, i+1)], fill=color)
    
    # 장식 원형
    draw.ellipse([-200, -200, 400, 400], fill=COLORS['primary'], outline=None)
    draw.ellipse([1000, 300, 1400, 700], fill=COLORS['secondary'], outline=None)
    
    # 타이틀
    title_font = load_font(72, bold=True)
    title_lines = wrap_text(site_title, title_font, width - 200)
    title_y = 150
    
    for i, line in enumerate(title_lines):
        bbox = title_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, title_y + i * 80), line, fill=COLORS['text'], font=title_font)
    
    # 설명
    desc_font = load_font(32)
    desc_lines = wrap_text(site_description, desc_font, width - 200)
    desc_y = title_y + len(title_lines) * 80 + 40
    
    for i, line in enumerate(desc_lines):
        bbox = desc_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, desc_y + i * 40), line, fill=COLORS['text_secondary'], font=desc_font)
    
    # URL
    url_font = load_font(24)
    url_text = "tech.2twodragon.com"
    bbox = url_font.getbbox(url_text)
    url_width = bbox[2] - bbox[0]
    draw.text(((width - url_width) // 2, height - 80), url_text, fill=COLORS['primary'], font=url_font)
    
    # 저장
    img.save(output_path, 'PNG', optimize=True)
    print(f"✅ 기본 OG 이미지 생성: {output_path}")

def generate_post_og_image(post_path, output_path, site_title="Twodragon's Tech Blog"):
    """포스트별 OG 이미지 생성"""
    # Front matter 읽기
    post = parse_frontmatter(post_path)
    
    title = post.get('title', 'Untitled')
    category = post.get('category', '')
    if not category and post.get('categories'):
        categories = post.get('categories')
        if isinstance(categories, list) and categories:
            category = categories[0]
        elif isinstance(categories, str):
            category = categories
    excerpt = post.get('excerpt', post.get('description', ''))
    date = post.get('date', datetime.now())
    
    # 날짜 포맷
    if isinstance(date, str):
        try:
            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        except:
            date = datetime.now()
    
    date_str = date.strftime('%Y. %m. %d')
    
    width, height = 1200, 630
    img = Image.new('RGB', (width, height), color=COLORS['background'])
    draw = ImageDraw.Draw(img)
    
    # 카테고리 색상
    category_color = CATEGORY_COLORS.get(category.lower(), CATEGORY_COLORS['default'])
    
    # 그라데이션 배경
    for i in range(height):
        alpha = int(255 * (1 - i / height) * 0.2)
        color = tuple(min(255, c + alpha) for c in (10, 14, 39))
        draw.rectangle([(0, i), (width, i+1)], fill=color)
    
    # 카테고리 배지
    if category:
        category_font = load_font(28, bold=True)
        category_text = category.upper()
        bbox = category_font.getbbox(category_text)
        badge_width = bbox[2] - bbox[0] + 40
        badge_height = 50
        
        # 배지 배경
        draw.rounded_rectangle(
            [(60, 60), (60 + badge_width, 60 + badge_height)],
            radius=8,
            fill=category_color
        )
        # 배지 텍스트
        draw.text((60 + 20, 60 + 10), category_text, fill=COLORS['text'], font=category_font)
    
    # 제목
    title_font = load_font(64, bold=True)
    title_lines = wrap_text(title, title_font, width - 200)
    title_y = 150
    
    for i, line in enumerate(title_lines[:3]):  # 최대 3줄
        bbox = title_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, title_y + i * 75), line, fill=COLORS['text'], font=title_font)
    
    # 설명 (있는 경우)
    if excerpt:
        desc_font = load_font(28)
        # HTML 태그 제거
        excerpt_clean = re.sub(r'<[^>]+>', '', excerpt)
        excerpt_clean = excerpt_clean[:100] + '...' if len(excerpt_clean) > 100 else excerpt_clean
        desc_lines = wrap_text(excerpt_clean, desc_font, width - 200)
        desc_y = title_y + min(len(title_lines), 3) * 75 + 30
        
        for i, line in enumerate(desc_lines[:2]):  # 최대 2줄
            bbox = desc_font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, desc_y + i * 40), line, fill=COLORS['text_secondary'], font=desc_font)
    
    # 하단 정보
    bottom_y = height - 100
    
    # 날짜
    date_font = load_font(24)
    draw.text((60, bottom_y), date_str, fill=COLORS['text_secondary'], font=date_font)
    
    # URL
    url_font = load_font(24)
    url_text = "tech.2twodragon.com"
    bbox = url_font.getbbox(url_text)
    draw.text((width - bbox[2] + bbox[0] - 60, bottom_y), url_text, fill=COLORS['primary'], font=url_font)
    
    # 장식 요소
    draw.ellipse([-150, -150, 300, 300], fill=category_color, outline=None)
    draw.ellipse([1050, 400, 1350, 700], fill=COLORS['secondary'], outline=None)
    
    # 저장
    img.save(output_path, 'PNG', optimize=True)
    print(f"✅ 포스트 OG 이미지 생성: {output_path}")

def main():
    """메인 함수"""
    base_dir = Path(__file__).parent.parent
    posts_dir = base_dir / '_posts'
    images_dir = base_dir / 'assets' / 'images'
    
    # 디렉토리 생성
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # 기본 OG 이미지 생성
    default_og_path = images_dir / 'og-default.png'
    print("📸 기본 OG 이미지 생성 중...")
    generate_default_og_image(default_og_path)
    
    # 각 포스트별 OG 이미지 생성
    print("\n📸 포스트별 OG 이미지 생성 중...")
    post_files = list(posts_dir.glob('*.md'))
    
    for post_file in post_files:
        # 파일명에서 날짜 제거하고 OG 이미지 이름 생성
        filename = post_file.stem
        # 날짜 부분 제거 (YYYY-MM-DD-)
        filename_clean = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', filename)
        og_filename = f"{filename_clean}_og.png"
        og_path = images_dir / og_filename
        
        # 이미 존재하면 스킵 (선택적)
        if og_path.exists():
            print(f"⏭️  이미 존재: {og_filename}")
            continue
        
        try:
            generate_post_og_image(post_file, og_path)
        except Exception as e:
            print(f"❌ 오류 ({post_file.name}): {e}")
            continue
    
    print(f"\n✅ 완료! 총 {len(post_files)}개 포스트 처리")

if __name__ == '__main__':
    main()
