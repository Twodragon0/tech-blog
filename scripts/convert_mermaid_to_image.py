#!/usr/bin/env python3
"""
머메이드 차트를 이미지로 변환하는 스크립트

복잡한 머메이드 차트를 PNG 이미지로 변환하여 포스팅에 사용합니다.
mermaid-cli (mmdc) 또는 Playwright를 사용하여 변환합니다.

필요 패키지:
    # 방법 1: mermaid-cli 사용 (권장)
    npm install -g @mermaid-js/mermaid-cli
    
    # 방법 2: Playwright 사용
    pip install playwright
    playwright install chromium

사용법:
    python3 scripts/convert_mermaid_to_image.py _posts/2026-01-15-Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_Security_Practical_Guide.md
"""

import os
import re
import sys
import base64
import urllib.parse
import requests
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
DIAGRAMS_DIR = IMAGES_DIR / "diagrams"

# mermaid.ink API 엔드포인트
MERMAID_INK_API = "https://mermaid.ink/img"


def log_message(message: str, level: str = "INFO"):
    """로그 메시지 출력"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "DIAGRAM": "📊"}
    icon = icons.get(level, "ℹ️")
    print(f"[{timestamp}] {icon} {message}")


def extract_mermaid_charts(content: str) -> List[Tuple[int, str, str]]:
    """
    마크다운 내용에서 머메이드 차트 추출
    
    Returns:
        List of (line_number, chart_id, chart_content) tuples
    """
    charts = []
    pattern = r'```mermaid\n(.*?)```'
    
    matches = list(re.finditer(pattern, content, re.DOTALL))
    for idx, match in enumerate(matches):
        chart_content = match.group(1).strip()
        line_number = content[:match.start()].count('\n') + 1
        chart_id = f"mermaid_chart_{idx + 1}"
        charts.append((line_number, chart_id, chart_content))
    
    return charts


def is_complex_chart(chart_content: str) -> bool:
    """
    차트가 복잡한지 판단 (이미지로 변환할 가치가 있는지)
    
    복잡도 기준:
    - 노드가 10개 이상
    - 서브그래프가 3개 이상
    - 연결선이 15개 이상
    """
    # 노드 개수 (대괄호로 감싸진 텍스트)
    nodes = len(re.findall(r'\["[^"]+"\]', chart_content))
    
    # 서브그래프 개수
    subgraphs = len(re.findall(r'subgraph\s+', chart_content, re.IGNORECASE))
    
    # 연결선 개수
    edges = len(re.findall(r'->|--', chart_content))
    
    # 복잡도 점수
    complexity_score = nodes * 1 + subgraphs * 3 + edges * 0.5
    
    # 복잡한 차트 판단 기준
    is_complex = (
        nodes >= 10 or
        subgraphs >= 3 or
        edges >= 15 or
        complexity_score >= 30
    )
    
    return is_complex


def convert_mermaid_to_image(chart_content: str, output_path: Path) -> bool:
    """
    머메이드 차트를 이미지로 변환
    
    mermaid-cli (mmdc) 또는 Playwright를 사용하여 변환합니다.
    """
    import subprocess
    import tempfile
    
    try:
        log_message(f"🔄 이미지 변환 중: {output_path.name}")
        
        # 임시 파일에 차트 내용 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(chart_content)
            tmp_mmd_path = tmp_file.name
        
        try:
            # mermaid-cli (mmdc) 사용 시도
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # mmdc 명령어 실행 (경로 확인)
            mmdc_path = 'mmdc'
            # npx를 통해 실행 시도 (로컬 설치된 경우)
            import shutil
            if not shutil.which('mmdc'):
                mmdc_path = 'npx'
                cmd = [
                    mmdc_path,
                    '-y',  # npx 자동 설치
                    '@mermaid-js/mermaid-cli',
                    '-i', tmp_mmd_path,
                    '-o', str(output_path),
                    '-t', 'default',
                    '-b', 'white',
                    '-w', '2400',  # 넓은 이미지
                    '-H', '1800'   # 높은 이미지
                ]
            else:
                cmd = [
                    mmdc_path,
                    '-i', tmp_mmd_path,
                    '-o', str(output_path),
                    '-t', 'default',
                    '-b', 'white',
                    '-w', '2400',  # 넓은 이미지
                    '-H', '1800'   # 높은 이미지
                ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and output_path.exists():
                file_size = output_path.stat().st_size
                log_message(f"✅ 이미지 생성 완료: {output_path.name} ({file_size} bytes)", "SUCCESS")
                return True
            else:
                # mmdc 오류 메시지 출력
                if result.stderr:
                    error_msg = result.stderr[:200]  # 처음 200자만
                    log_message(f"⚠️ mmdc 오류: {error_msg}", "WARNING")
                # mmdc가 없거나 실패한 경우, Playwright 사용 시도
                log_message(f"⚠️ mmdc 실패, Playwright로 시도 중...", "WARNING")
                return convert_with_playwright(chart_content, output_path)
                
        finally:
            # 임시 파일 삭제
            try:
                os.unlink(tmp_mmd_path)
            except:
                pass
                
    except FileNotFoundError:
        # mmdc가 설치되지 않은 경우
        log_message(f"⚠️ mermaid-cli (mmdc)가 설치되지 않았습니다. Playwright로 시도 중...", "WARNING")
        return convert_with_playwright(chart_content, output_path)
    except subprocess.TimeoutExpired:
        log_message(f"❌ 변환 타임아웃", "ERROR")
        return False
    except Exception as e:
        log_message(f"❌ 변환 실패: {str(e)}", "ERROR")
        # Playwright로 재시도
        return convert_with_playwright(chart_content, output_path)


def convert_with_playwright(chart_content: str, output_path: Path) -> bool:
    """
    Playwright를 사용하여 머메이드 차트를 이미지로 변환
    """
    try:
        from playwright.sync_api import sync_playwright
        import tempfile
        
        log_message(f"🎭 Playwright로 이미지 생성 중...")
        
        # HTML 템플릿 생성 (mermaid 10.9.5 호환)
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.5/dist/mermaid.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: white;
        }}
    </style>
</head>
<body>
    <div class="mermaid">
{chart_content}
    </div>
    <script>
        mermaid.initialize({{ 
            startOnLoad: true, 
            theme: 'default',
            securityLevel: 'loose',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true
            }}
        }});
    </script>
</body>
</html>"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_template, wait_until='networkidle')
            
            # SVG 요소가 렌더링될 때까지 대기
            page.wait_for_selector('.mermaid svg', timeout=10000)
            
            # SVG 요소 찾기
            svg_element = page.query_selector('.mermaid svg')
            if svg_element:
                # PNG로 스크린샷
                page.screenshot(path=str(output_path), full_page=True)
                browser.close()
                
                file_size = output_path.stat().st_size
                log_message(f"✅ 이미지 생성 완료 (Playwright): {output_path.name} ({file_size} bytes)", "SUCCESS")
                return True
            else:
                browser.close()
                log_message(f"❌ SVG 요소를 찾을 수 없습니다", "ERROR")
                return False
                
    except ImportError:
        log_message(f"❌ Playwright가 설치되지 않았습니다.", "ERROR")
        log_message(f"💡 설치 방법: pip install playwright && playwright install chromium", "INFO")
        return False
    except Exception as e:
        log_message(f"❌ Playwright 변환 실패: {str(e)}", "ERROR")
        return False


def process_post(post_file: Path, force: bool = False) -> bool:
    """포스팅 파일 처리"""
    log_message(f"📄 포스팅 처리 시작: {post_file.name}")
    
    # 파일 읽기
    try:
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        log_message(f"❌ 파일 읽기 실패: {str(e)}", "ERROR")
        return False
    
    # 머메이드 차트 추출
    charts = extract_mermaid_charts(content)
    log_message(f"📊 {len(charts)}개의 머메이드 차트 발견")
    
    if not charts:
        log_message("💡 변환할 차트가 없습니다.", "INFO")
        return True
    
    # 모든 차트를 이미지로 변환 (모든 차트를 변환하도록 수정)
    charts_to_convert = []
    for line_num, chart_id, chart_content in charts:
        charts_to_convert.append((line_num, chart_id, chart_content))
        log_message(f"  ✓ 차트 발견 (라인 {line_num}): {chart_id}", "DIAGRAM")
    
    if not charts_to_convert:
        log_message("💡 변환할 차트가 없습니다.", "INFO")
        return True
    
    log_message(f"📊 {len(charts_to_convert)}개의 차트를 이미지로 변환합니다.")
    
    # 포스팅 파일명 기반으로 이미지 디렉토리 생성
    post_stem = post_file.stem
    post_diagrams_dir = DIAGRAMS_DIR / post_stem
    post_diagrams_dir.mkdir(parents=True, exist_ok=True)
    
    # 각 차트 변환
    success_count = 0
    image_replacements = []
    
    for line_num, chart_id, chart_content in charts_to_convert:
        # 이미지 파일명 생성
        image_filename = f"{post_stem}_{chart_id}.png"
        image_path = post_diagrams_dir / image_filename
        
        # 이미지가 이미 존재하는지 확인
        if image_path.exists() and not force:
            log_message(f"⏭️  이미지가 이미 존재합니다: {image_filename}", "INFO")
            success_count += 1
            # 마크다운에서 이미지로 교체할 정보 저장
            relative_image_path = f"/assets/images/diagrams/{post_stem}/{image_filename}"
            image_replacements.append((line_num, chart_id, relative_image_path, chart_content))
            continue
        
        # 이미지 변환
        if convert_mermaid_to_image(chart_content, image_path):
            success_count += 1
            # 마크다운에서 이미지로 교체할 정보 저장
            relative_image_path = f"/assets/images/diagrams/{post_stem}/{image_filename}"
            image_replacements.append((line_num, chart_id, relative_image_path, chart_content))
        else:
            log_message(f"⚠️  차트 변환 실패: {chart_id}", "WARNING")
    
        # 마크다운 파일 업데이트 (이미지로 교체)
        if image_replacements:
            log_message(f"📝 마크다운 파일 업데이트 중...")
            
            # 각 차트를 찾아서 이미지로 교체
            # 정규식으로 머메이드 블록을 찾아서 교체하는 방식으로 변경
            pattern = r'```mermaid\n(.*?)```'
            
            # 교체할 차트를 딕셔너리로 변환 (빠른 검색을 위해)
            chart_replacements = {}
            for line_num, chart_id, img_path, original_content in image_replacements:
                chart_replacements[original_content.strip()] = (chart_id, img_path)
            
            def replace_mermaid(match):
                chart_content = match.group(1).strip()
                # 차트 내용이 교체 대상인지 확인
                if chart_content in chart_replacements:
                    chart_id, img_path = chart_replacements[chart_content]
                    # 이미지로 교체 (Jekyll relative_url 필터 사용)
                    log_message(f"  ✓ 차트 교체: {chart_id} -> {img_path}", "SUCCESS")
                    return f'<img src="{{{{ \'{img_path}\' | relative_url }}}}" alt="{chart_id}" loading="lazy" class="post-image">'
                # 교체 대상이 아니면 원본 유지
                return match.group(0)
            
            new_content = re.sub(pattern, replace_mermaid, content, flags=re.DOTALL)
            
            # 파일 저장
            with open(post_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            log_message(f"✅ 마크다운 파일 업데이트 완료: {len(image_replacements)}개 차트를 이미지로 교체", "SUCCESS")
    
    log_message(f"📊 처리 완료: {success_count}/{len(charts_to_convert)}개 차트 변환 성공", "SUCCESS")
    return success_count == len(charts_to_convert)


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="머메이드 차트를 이미지로 변환",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 특정 포스팅 처리
  python3 scripts/convert_mermaid_to_image.py _posts/2026-01-15-Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_Security_Practical_Guide.md
  
  # 모든 포스팅 처리
  python3 scripts/convert_mermaid_to_image.py --all
  
  # 강제 재생성
  python3 scripts/convert_mermaid_to_image.py _posts/2026-01-15-...md --force
        """
    )
    
    parser.add_argument(
        "post_file",
        nargs="?",
        help="처리할 포스팅 파일 (선택사항)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="모든 포스팅 처리"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="이미지가 있어도 강제로 재생성"
    )
    
    args = parser.parse_args()
    
    # 모든 포스팅 처리
    if args.all:
        log_message("📊 모든 포스팅의 머메이드 차트를 이미지로 변환합니다.", "INFO")
        post_files = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        log_message(f"📄 {len(post_files)}개 포스팅 파일 발견", "INFO")
        
        success_count = 0
        for post_file in post_files:
            try:
                if process_post(post_file, force=args.force):
                    success_count += 1
                print()  # 빈 줄 추가
            except Exception as e:
                log_message(f"❌ 포스팅 처리 실패: {post_file.name} - {str(e)}", "ERROR")
        
        log_message("=" * 80)
        log_message(f"📊 처리 완료: {success_count}/{len(post_files)}개 성공", "SUCCESS")
        log_message("=" * 80)
        sys.exit(0 if success_count == len(post_files) else 1)
    
    # 특정 파일 처리
    if not args.post_file:
        parser.print_help()
        sys.exit(1)
    
    post_path = Path(args.post_file)
    if not post_path.is_absolute():
        post_path = PROJECT_ROOT / post_path
    
    if not post_path.exists():
        log_message(f"❌ 파일을 찾을 수 없습니다: {post_path}", "ERROR")
        sys.exit(1)
    
    # 처리
    success = process_post(post_path, force=args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
