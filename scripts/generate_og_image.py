#!/usr/bin/env python3
"""
Open Graph 이미지 생성 스크립트
SVG를 PNG로 변환하여 카카오톡 공유용 이미지를 생성합니다.
"""

import subprocess
import sys
from pathlib import Path

def check_dependencies():
    """필요한 도구가 설치되어 있는지 확인"""
    try:
        subprocess.run(['which', 'inkscape'], check=True, capture_output=True)
        return 'inkscape'
    except subprocess.CalledProcessError:
        pass
    
    try:
        subprocess.run(['which', 'rsvg-convert'], check=True, capture_output=True)
        return 'rsvg'
    except subprocess.CalledProcessError:
        pass
    
    try:
        import cairosvg
        return 'cairosvg'
    except ImportError:
        pass
    
    return None

def convert_svg_to_png_svg(svg_path, png_path, width=1200, height=630):
    """cairosvg를 사용하여 SVG를 PNG로 변환"""
    try:
        import cairosvg
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=width,
            output_height=height
        )
        return True
    except Exception as e:
        print(f"cairosvg 변환 실패: {e}")
        return False

def convert_svg_to_png_inkscape(svg_path, png_path, width=1200, height=630):
    """Inkscape를 사용하여 SVG를 PNG로 변환"""
    try:
        subprocess.run([
            'inkscape',
            '--export-type=png',
            f'--export-width={width}',
            f'--export-height={height}',
            f'--export-filename={png_path}',
            str(svg_path)
        ], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Inkscape 변환 실패: {e}")
        return False

def convert_svg_to_png_rsvg(svg_path, png_path, width=1200, height=630):
    """rsvg-convert를 사용하여 SVG를 PNG로 변환"""
    try:
        subprocess.run([
            'rsvg-convert',
            '--width', str(width),
            '--height', str(height),
            '--format', 'png',
            '--output', str(png_path),
            str(svg_path)
        ], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"rsvg-convert 변환 실패: {e}")
        return False

def main():
    """메인 함수"""
    base_dir = Path(__file__).parent.parent
    svg_path = base_dir / 'assets' / 'images' / 'og-default.svg'
    png_path = base_dir / 'assets' / 'images' / 'og-default.png'
    
    if not svg_path.exists():
        print(f"❌ SVG 파일을 찾을 수 없습니다: {svg_path}")
        sys.exit(1)
    
    tool = check_dependencies()
    
    if not tool:
        print("❌ SVG를 PNG로 변환할 수 있는 도구가 없습니다.")
        print("\n다음 중 하나를 설치해주세요:")
        print("1. cairosvg: pip install cairosvg")
        print("2. Inkscape: brew install inkscape (macOS) 또는 apt-get install inkscape (Linux)")
        print("3. librsvg: brew install librsvg (macOS) 또는 apt-get install librsvg2-bin (Linux)")
        sys.exit(1)
    
    print(f"✅ {tool}를 사용하여 변환합니다...")
    
    success = False
    if tool == 'cairosvg':
        success = convert_svg_to_png_svg(svg_path, png_path)
    elif tool == 'inkscape':
        success = convert_svg_to_png_inkscape(svg_path, png_path)
    elif tool == 'rsvg':
        success = convert_svg_to_png_rsvg(svg_path, png_path)
    
    if success:
        print(f"✅ PNG 이미지가 생성되었습니다: {png_path}")
        print(f"   크기: 1200x630 (Open Graph 표준)")
    else:
        print("❌ PNG 변환에 실패했습니다.")
        sys.exit(1)

if __name__ == '__main__':
    main()
