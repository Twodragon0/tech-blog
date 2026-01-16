#!/usr/bin/env python3
"""
Post-Mortem Next.js SSR Error Incident SVG 이미지 생성
nano banana 스타일의 간단한 SVG 이미지를 생성합니다.
"""

from pathlib import Path
import textwrap

# 프로젝트 루트 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ASSETS_IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# 출력 디렉토리 생성
ASSETS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

def generate_postmortem_svg():
    """Post-Mortem Next.js SSR Error Incident SVG 이미지 생성"""
    print("🎨 Post-Mortem SVG 이미지 생성 중...")
    
    output_path = ASSETS_IMAGES_DIR / "2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis.svg"
    
    # 제목 텍스트
    title = "Post-Mortem: Next.js SSR Error & Cloudflare Blocking ALB 5XX Incident Analysis"
    
    # 제목을 여러 줄로 나누기
    wrapper = textwrap.TextWrapper(width=40)
    title_lines = wrapper.wrap(title)
    
    text_elements = ""
    y_offset = 180
    for i, line in enumerate(title_lines):
        text_elements += f'  <text x="400" y="{y_offset}" text-anchor="middle" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="#FFFFFF">{line}</text>\n'
        y_offset += 35
    
    # SVG 내용 생성
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" viewBox="0 0 800 400">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1e3a8a;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#3b82f6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#1e40af;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- 배경 -->
  <rect width="800" height="400" fill="url(#grad1)" />
  
  <!-- 아이콘 영역 -->
  <g transform="translate(400, 80) scale(2)">
    <!-- Next.js 로고 (간단한 원형) -->
    <circle cx="0" cy="0" r="25" fill="#FFFFFF" opacity="0.9"/>
    <text x="0" y="8" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#1e3a8a">N</text>
    
    <!-- 에러 표시 -->
    <circle cx="30" cy="-20" r="8" fill="#ef4444"/>
    <text x="30" y="-15" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#FFFFFF">!</text>
    
    <!-- Cloudflare 아이콘 (간단한 구름 모양) -->
    <path d="M -50 -10 Q -60 -20 -50 -30 Q -40 -20 -50 -10" fill="#f97316" opacity="0.8"/>
    <path d="M -40 -10 Q -50 -20 -40 -30 Q -30 -20 -40 -10" fill="#f97316" opacity="0.8"/>
    <path d="M -30 -10 Q -40 -20 -30 -30 Q -20 -20 -30 -10" fill="#f97316" opacity="0.8"/>
  </g>
  
  <!-- 제목 텍스트 -->
{text_elements}
  
  <!-- 부제목 -->
  <text x="400" y="280" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#e0e7ff" opacity="0.9">Incident Response &amp; Analysis</text>
  
  <!-- 태그 -->
  <g transform="translate(400, 320)">
    <rect x="-80" y="-12" width="50" height="24" rx="12" fill="#3b82f6" opacity="0.8"/>
    <text x="-55" y="5" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#FFFFFF">Next.js</text>
    
    <rect x="-20" y="-12" width="50" height="24" rx="12" fill="#f97316" opacity="0.8"/>
    <text x="5" y="5" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#FFFFFF">Cloudflare</text>
    
    <rect x="40" y="-12" width="50" height="24" rx="12" fill="#ef4444" opacity="0.8"/>
    <text x="65" y="5" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#FFFFFF">Incident</text>
  </g>
  
  <!-- 하단 텍스트 -->
  <text x="780" y="380" text-anchor="end" font-family="monospace" font-size="12" fill="rgba(255,255,255,0.5)">2026-01-16</text>
</svg>'''
    
    # 파일 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    if output_path.exists():
        print(f"✅ 생성 완료: {output_path}")
        return True
    else:
        print(f"❌ 생성 실패: {output_path}")
        return False

def main():
    """메인 함수"""
    print("🚀 Post-Mortem SVG 이미지 생성 시작\n")
    
    success = generate_postmortem_svg()
    
    print("\n" + "="*60)
    if success:
        print("✅ SVG 이미지 생성 완료!")
        return 0
    else:
        print("❌ SVG 이미지 생성 실패")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
