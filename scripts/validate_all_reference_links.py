#!/usr/bin/env python3
"""
모든 포스트 파일의 참고자료 링크를 검증하고 수정하는 스크립트
"""
import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

# SSL 경고 비활성화 (로컬 환경에서 인증서 문제 해결)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 요청 세션 설정 (재시도 및 타임아웃)
def create_session():
    """HTTP 세션 생성 (재시도 및 타임아웃 설정)"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (compatible; LinkValidator/1.0)'
    })
    return session

# 링크 검증 결과 저장
LINK_RESULTS: Dict[str, Dict] = {}

def extract_links(content: str) -> List[Tuple[str, str, int]]:
    """
    마크다운 파일에서 모든 링크 추출
    
    Returns:
        List of (link_text, url, line_number) tuples
    """
    links = []
    
    # 마크다운 링크 패턴: [text](url)
    md_link_pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
    for match in re.finditer(md_link_pattern, content):
        link_text = match.group(1)
        url = match.group(2)
        # 줄 번호 계산
        line_number = content[:match.start()].count('\n') + 1
        links.append((link_text, url, line_number))
    
    # HTML 링크 패턴: <a href="url">text</a>
    html_link_pattern = r'<a\s+[^>]*href=["\'](https?://[^"\']+)["\'][^>]*>([^<]+)</a>'
    for match in re.finditer(html_link_pattern, content):
        url = match.group(1)
        link_text = match.group(2)
        line_number = content[:match.start()].count('\n') + 1
        links.append((link_text, url, line_number))
    
    # 일반 URL 패턴 (마크다운/HTML 링크가 아닌 경우)
    url_pattern = r'(?<!\]\()(https?://[^\s\)]+)'
    for match in re.finditer(url_pattern, content):
        url = match.group(1)
        # 이미 추출된 링크인지 확인
        if not any(url in link[1] for link in links):
            line_number = content[:match.start()].count('\n') + 1
            links.append(('', url, line_number))
    
    return links

def check_link_exists(session: requests.Session, url: str, timeout: int = 10) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    링크가 존재하는지 확인
    
    Returns:
        (exists, status_code, error_message)
    """
    # 이미 확인한 링크는 재사용
    if url in LINK_RESULTS:
        result = LINK_RESULTS[url]
        return result['exists'], result.get('status_code'), result.get('error')
    
    try:
        parsed = urlparse(url)
        
        # 특수 URL 처리
        if 'twodragon.tistory.com' in parsed.netloc:
            # 티스토리 링크는 존재한다고 가정 (인증 필요할 수 있음)
            result = {'exists': True, 'status_code': 200, 'error': None}
            LINK_RESULTS[url] = result
            return True, 200, None
        
        # HEAD 요청 시도 (SSL 검증 경고 무시)
        try:
            response = session.head(url, timeout=timeout, allow_redirects=True, verify=False)
            status_code = response.status_code
            exists = status_code < 400
            result = {
                'exists': exists,
                'status_code': status_code,
                'error': None if exists else f'HTTP {status_code}'
            }
            LINK_RESULTS[url] = result
            return exists, status_code, result['error']
        except requests.exceptions.SSLError:
            # SSL 오류는 실제로는 존재할 수 있으므로 GET으로 재시도
            try:
                response = session.get(url, timeout=timeout, allow_redirects=True, stream=True, verify=False)
                status_code = response.status_code
                exists = status_code < 400
                result = {
                    'exists': exists,
                    'status_code': status_code,
                    'error': None if exists else f'HTTP {status_code}'
                }
                LINK_RESULTS[url] = result
                return exists, status_code, result['error']
            except requests.exceptions.RequestException:
                # SSL 오류지만 실제로는 존재할 수 있음 (인증서 문제일 수 있음)
                result = {
                    'exists': True,  # SSL 오류는 존재한다고 가정
                    'status_code': None,
                    'error': 'SSL verification failed (may still exist)'
                }
                LINK_RESULTS[url] = result
                return True, None, 'SSL verification failed'
        except requests.exceptions.RequestException as e:
            # HEAD 실패 시 GET 시도
            try:
                response = session.get(url, timeout=timeout, allow_redirects=True, stream=True, verify=False)
                status_code = response.status_code
                exists = status_code < 400
                result = {
                    'exists': exists,
                    'status_code': status_code,
                    'error': None if exists else f'HTTP {status_code}'
                }
                LINK_RESULTS[url] = result
                return exists, status_code, result['error']
            except requests.exceptions.RequestException as e2:
                # 연결 실패는 실제로 존재하지 않을 가능성이 높음
                result = {
                    'exists': False,
                    'status_code': None,
                    'error': str(e2)
                }
                LINK_RESULTS[url] = result
                return False, None, str(e2)
    
    except Exception as e:
        result = {
            'exists': False,
            'status_code': None,
            'error': str(e)
        }
        LINK_RESULTS[url] = result
        return False, None, str(e)

def find_better_link(url: str, context: str = '') -> Optional[str]:
    """
    부적절한 링크에 대한 더 나은 대안 찾기
    
    Returns:
        더 나은 링크 URL 또는 None
    """
    # 부적절한 패턴과 대안 매핑
    replacements = {
        # GitHub 예제 저장소를 코드 타입에 맞게 변경
        r'github\.com/docker-library': {
            'kubernetes': 'https://github.com/kubernetes/examples',
            'terraform': 'https://github.com/terraform-aws-modules',
            'aws': 'https://github.com/aws-samples',
            'default': 'https://github.com/kubernetes/examples'
        },
        # 더미 링크 제거
        r'github\.com/example': None,
    }
    
    # 컨텍스트 기반 대안 찾기
    context_lower = context.lower()
    
    if 'kubernetes' in context_lower or 'k8s' in context_lower:
        if 'github.com/docker-library' in url:
            return 'https://github.com/kubernetes/examples'
    
    if 'terraform' in context_lower:
        if 'github.com/docker-library' in url:
            return 'https://github.com/terraform-aws-modules'
    
    if 'aws' in context_lower:
        if 'github.com/docker-library' in url:
            return 'https://github.com/aws-samples'
    
    return None

def process_post_file(file_path: Path, session: requests.Session, fix_mode: bool = False) -> Dict:
    """
    포스트 파일의 링크 검증 및 수정
    
    Returns:
        검증 결과 딕셔너리
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        links = extract_links(content)
        issues = []
        fixed_content = content
        
        for link_text, url, line_number in links:
            # 링크 검증
            exists, status_code, error = check_link_exists(session, url)
            
            # SSL 오류는 실제 문제가 아닐 수 있으므로 제외
            is_ssl_error = error and 'SSL' in str(error)
            is_404_error = status_code == 404
            
            # 실제 문제가 있는 링크만 리포트
            if not exists and not is_ssl_error:
                # 컨텍스트 추출
                start = max(0, content.rfind('\n', 0, content[:content.find(url)].rfind('\n')) - 200)
                end = min(len(content), content.find(url) + len(url) + 200)
                context = content[start:end]
                
                # 더 나은 링크 찾기
                better_link = find_better_link(url, context)
                
                issue = {
                    'url': url,
                    'link_text': link_text,
                    'line': line_number,
                    'status_code': status_code,
                    'error': error,
                    'better_link': better_link,
                    'context': context[:100] + '...' if len(context) > 100 else context
                }
                issues.append(issue)
                
                # 수정 모드인 경우 링크 교체 또는 제거
                if fix_mode and better_link:
                    # 링크 교체
                    if link_text:
                        old_link = f'[{link_text}]({url})'
                        new_link = f'[{link_text}]({better_link})'
                        fixed_content = fixed_content.replace(old_link, new_link)
                    else:
                        fixed_content = fixed_content.replace(url, better_link)
                elif fix_mode and not better_link:
                    # 링크 제거 (참고 섹션에서)
                    if '> **참고**:' in context or '> **코드 예시**:' in context:
                        # 참고 섹션 전체 제거
                        pattern = rf'> \*\*(?:참고|코드 예시)\*\*:.*?{re.escape(url)}[^\n]*\n'
                        fixed_content = re.sub(pattern, '', fixed_content, flags=re.DOTALL)
            
            # 요청 간 딜레이 (서버 부하 방지)
            time.sleep(0.5)
        
        # 수정된 내용 저장
        if fix_mode and fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
        
        return {
            'file': file_path.name,
            'total_links': len(links),
            'issues': issues,
            'fixed': fix_mode and fixed_content != content
        }
    
    except Exception as e:
        return {
            'file': file_path.name,
            'error': str(e),
            'issues': []
        }

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='포스트 파일의 참고자료 링크 검증')
    parser.add_argument('--fix', action='store_true', help='부적절한 링크 자동 수정')
    parser.add_argument('--file', type=str, help='특정 파일만 검증')
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent
    posts_dir = script_dir.parent / '_posts'
    
    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return 1
    
    # 세션 생성
    session = create_session()
    
    # 파일 목록
    if args.file:
        post_files = [posts_dir / args.file]
    else:
        post_files = sorted(posts_dir.glob('*.md'))
    
    print("=" * 80)
    print("참고자료 링크 검증")
    print("=" * 80)
    print(f"검증 대상 파일: {len(post_files)}개\n")
    
    all_results = []
    total_links = 0
    total_issues = 0
    
    for post_file in post_files:
        if not post_file.exists():
            continue
        
        print(f"검증 중: {post_file.name}...", end=' ', flush=True)
        result = process_post_file(post_file, session, fix_mode=args.fix)
        all_results.append(result)
        
        if 'error' in result:
            print(f"❌ 오류: {result['error']}")
        else:
            total_links += result['total_links']
            issue_count = len(result['issues'])
            total_issues += issue_count
            
            if issue_count > 0:
                print(f"⚠️  {issue_count}개 문제 발견")
            else:
                print("✅ 정상")
    
    # 결과 요약
    print("\n" + "=" * 80)
    print("검증 결과 요약")
    print("=" * 80)
    print(f"총 파일 수: {len(all_results)}")
    print(f"총 링크 수: {total_links}")
    print(f"문제 발견: {total_issues}개\n")
    
    # 문제 상세 보고
    if total_issues > 0:
        print("=" * 80)
        print("문제 상세")
        print("=" * 80)
        
        for result in all_results:
            if result.get('issues'):
                print(f"\n📄 {result['file']}:")
                for issue in result['issues']:
                    print(f"  줄 {issue['line']}: {issue['url']}")
                    print(f"    텍스트: {issue['link_text']}")
                    print(f"    상태: {issue.get('status_code', 'N/A')} - {issue.get('error', 'N/A')}")
                    if issue.get('better_link'):
                        print(f"    제안: {issue['better_link']}")
                    print()
        
        if not args.fix:
            print("\n💡 --fix 옵션을 사용하여 자동으로 수정할 수 있습니다.")
    
    session.close()
    return 0 if total_issues == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
