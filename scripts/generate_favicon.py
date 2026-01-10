#!/usr/bin/env python3
"""
Favicon 및 Apple Touch Icon 생성 스크립트
보안 아이콘(🔒)을 기반으로 PNG 아이콘을 생성합니다.
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("PIL/Pillow가 설치되어 있지 않습니다.")
    print("설치: pip install Pillow")

def create_favicon(output_path, size=32):
    """Favicon 생성 (32x32 또는 16x16)"""
    if not HAS_PIL:
        return False
    
    try:
        # 보안 아이콘을 나타내는 간단한 디자인
        # 배경: 어두운 파란색 (#1a237e)
        # 전경: 밝은 파란색 (#3f51b5)으로 보안 아이콘 스타일
        img = Image.new('RGB', (size, size), color='#1a237e')
        draw = ImageDraw.Draw(img)
        
        # 간단한 보안 아이콘 (자물쇠 모양)
        # 자물쇠 본체
        lock_body_y = size * 0.4
        lock_width = size * 0.4
        lock_height = size * 0.35
        
        # 자물쇠 본체 (둥근 사각형)
        x1 = (size - lock_width) / 2
        y1 = lock_body_y
        x2 = x1 + lock_width
        y2 = y1 + lock_height
        
        # 자물쇠 본체 그리기
        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=size * 0.05,
            fill='#3f51b5',
            outline='#ffffff',
            width=1
        )
        
        # 자물쇠 고리 (위쪽 반원)
        arc_radius = lock_width * 0.3
        arc_center_x = size / 2
        arc_center_y = lock_body_y
        
        # 반원 그리기
        draw.arc(
            [arc_center_x - arc_radius, arc_center_y - arc_radius * 2,
             arc_center_x + arc_radius, arc_center_y],
            start=180,
            end=0,
            fill='#3f51b5',
            width=int(size * 0.15)
        )
        
        # 작은 크기에서는 단순화
        if size <= 32:
            # 작은 원으로 단순화
            draw.ellipse(
                [arc_center_x - arc_radius * 0.8, arc_center_y - arc_radius * 1.5,
                 arc_center_x + arc_radius * 0.8, arc_center_y - arc_radius * 0.3],
                fill='#3f51b5',
                outline='#ffffff',
                width=1
            )
        
        img.save(output_path, 'PNG', optimize=True)
        print(f"✓ 생성 완료: {output_path} ({size}x{size})")
        return True
        
    except Exception as e:
        print(f"✗ 생성 실패: {e}")
        return False

def create_apple_touch_icon(output_path, size=180):
    """Apple Touch Icon 생성 (180x180)"""
    if not HAS_PIL:
        return False
    
    try:
        # Apple Touch Icon은 더 큰 크기이므로 더 자세한 디자인 가능
        img = Image.new('RGB', (size, size), color='#1a237e')
        draw = ImageDraw.Draw(img)
        
        # 배경에 그라데이션 효과 (선택사항)
        # 간단한 원형 배경
        margin = size * 0.1
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill='#283593',
            outline='#3f51b5',
            width=int(size * 0.02)
        )
        
        # 자물쇠 아이콘 (중앙에 배치)
        lock_size = size * 0.5
        lock_x = (size - lock_size) / 2
        lock_y = (size - lock_size) / 2
        
        # 자물쇠 본체
        lock_body_y = lock_y + lock_size * 0.2
        lock_width = lock_size * 0.5
        lock_height = lock_size * 0.4
        
        x1 = lock_x + (lock_size - lock_width) / 2
        y1 = lock_body_y
        x2 = x1 + lock_width
        y2 = y1 + lock_height
        
        # 자물쇠 본체
        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=size * 0.02,
            fill='#3f51b5',
            outline='#ffffff',
            width=int(size * 0.02)
        )
        
        # 자물쇠 고리
        arc_radius = lock_width * 0.4
        arc_center_x = size / 2
        arc_center_y = lock_body_y
        
        # 반원
        draw.arc(
            [arc_center_x - arc_radius, arc_center_y - arc_radius * 2.2,
             arc_center_x + arc_radius, arc_center_y - arc_radius * 0.2],
            start=180,
            end=0,
            fill='#3f51b5',
            width=int(size * 0.08)
        )
        
        # 고리 연결
        draw.ellipse(
            [arc_center_x - arc_radius * 0.9, arc_center_y - arc_radius * 2.0,
             arc_center_x + arc_radius * 0.9, arc_center_y - arc_radius * 0.4],
            fill='#3f51b5',
            outline='#ffffff',
            width=int(size * 0.02)
        )
        
        img.save(output_path, 'PNG', optimize=True)
        print(f"✓ 생성 완료: {output_path} ({size}x{size})")
        return True
        
    except Exception as e:
        print(f"✗ 생성 실패: {e}")
        return False

def main():
    """메인 함수"""
    # 프로젝트 루트 디렉토리 찾기
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    images_dir = project_root / 'assets' / 'images'
    
    # 디렉토리 확인
    if not images_dir.exists():
        print(f"✗ 디렉토리가 없습니다: {images_dir}")
        sys.exit(1)
    
    # Favicon 생성 (32x32)
    favicon_path = images_dir / 'favicon.png'
    success1 = create_favicon(favicon_path, size=32)
    
    # Apple Touch Icon 생성 (180x180)
    apple_icon_path = images_dir / 'apple-touch-icon.png'
    success2 = create_apple_touch_icon(apple_icon_path, size=180)
    
    if success1 and success2:
        print("\n✓ 모든 아이콘이 성공적으로 생성되었습니다!")
        return 0
    else:
        print("\n✗ 일부 아이콘 생성에 실패했습니다.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
