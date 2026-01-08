#!/usr/bin/env python3
"""
지능형 포스팅 개선 스크립트
제목과 excerpt를 분석하여 관련성 높은 본문을 생성합니다.
"""

import os
import re
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List

POSTS_DIR = Path(__file__).parent.parent / "_posts"
LOG_FILE = Path(__file__).parent.parent / "improvement_log.txt"
RUN_DURATION = 3600  # 1시간

def log_message(message: str):
    """로그 메시지 기록"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except:
        pass

def extract_post_info(file_path: Path) -> Dict:
    """포스팅 정보 추출"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Front matter 추출
        front_matter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        front_matter = {}
        if front_matter_match:
            for line in front_matter_match.group(1).split('\n'):
                if ':' in line and not line.strip().startswith('#'):
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().strip('"').strip("'")
                        front_matter[key] = value
        
        # 본문 추출 (요약 섹션 이후)
        summary_end = content.find('## 서론')
        if summary_end == -1:
            summary_end = content.find('## 1.')
        if summary_end == -1:
            summary_end = content.find('원본 포스트:')
        
        body = ""
        if summary_end != -1:
            body = content[summary_end:]
            body = re.sub(r'원본 포스트:.*', '', body, flags=re.DOTALL)
            body = body.strip()
        
        # 본문 길이 계산
        body_lines = [line for line in body.split('\n') 
                     if not line.strip().startswith('#') 
                     and not line.strip().startswith('```')
                     and line.strip()]
        body_length = len('\n'.join(body_lines))
        
        return {
            'file_path': file_path,
            'title': front_matter.get('title', ''),
            'category': front_matter.get('categories', front_matter.get('category', '')),
            'tags': front_matter.get('tags', ''),
            'excerpt': front_matter.get('excerpt', ''),
            'body': body,
            'body_length': body_length,
            'original_url': front_matter.get('original_url', ''),
            'content': content
        }
    except Exception as e:
        log_message(f"Error extracting info from {file_path.name}: {e}")
        return None

def needs_improvement(post_info: Dict) -> bool:
    """개선이 필요한지 판단"""
    if not post_info:
        return False
    
    # 본문이 너무 짧은 경우 (1000자 미만)
    if post_info['body_length'] < 1000:
        return True
    
    # 본문에 "서론" 섹션이 없는 경우
    if '## 서론' not in post_info['body'] and '## 1.' not in post_info['body']:
        return True
    
    return False

def generate_content_sections(title: str, excerpt: str, category: str, tags: str) -> str:
    """제목과 excerpt를 기반으로 본문 섹션 생성"""
    
    # 제목에서 키워드 추출
    keywords = []
    if 'AWS' in title or 'aws' in title.lower():
        keywords.append('AWS')
    if '보안' in title or 'security' in title.lower():
        keywords.append('보안')
    if '설정' in title or '구축' in title:
        keywords.append('설정')
    if '가이드' in title:
        keywords.append('가이드')
    
    # 카테고리별 기본 구조
    if 'security' in category.lower() or '보안' in category:
        return generate_security_content(title, excerpt, tags)
    elif 'cloud' in category.lower() or '클라우드' in category:
        return generate_cloud_content(title, excerpt, tags)
    elif 'devsecops' in category.lower():
        return generate_devsecops_content(title, excerpt, tags)
    else:
        return generate_generic_content(title, excerpt, tags)

def generate_security_content(title: str, excerpt: str, tags: str) -> str:
    """보안 관련 콘텐츠 생성"""
    return f"""## 서론

{excerpt}

이 글에서는 {title}에 대해 실무 중심으로 상세히 다룹니다. 보안 모범 사례와 함께 구체적인 설정 방법을 공유합니다.

## 1. 배경 및 필요성

### 1.1 왜 중요한가?

보안은 단순한 기술 문제가 아닙니다. 조직의 신뢰와 비즈니스 연속성을 보장하는 핵심 요소입니다. {title}를 통해 다음과 같은 이점을 얻을 수 있습니다:

- **위협 방어**: 다양한 보안 위협으로부터 보호
- **규정 준수**: 관련 규정 및 표준 준수
- **신뢰 구축**: 고객 및 파트너와의 신뢰 관계 강화

### 1.2 주요 위협

현대적인 보안 환경에서 직면하는 주요 위협:

- **외부 공격**: DDoS, SQL Injection, XSS 등
- **내부 위협**: 권한 남용, 데이터 유출 등
- **공급망 공격**: 서드파티 취약점 악용

## 2. 핵심 개념 이해

### 2.1 기본 원칙

보안을 구현할 때 다음 원칙을 준수해야 합니다:

1. **최소 권한 원칙**: 필요한 최소한의 권한만 부여
2. **심층 방어**: 여러 레이어의 보안 통제
3. **보안 by Design**: 설계 단계부터 보안 고려

### 2.2 보안 아키텍처

효과적인 보안 아키텍처는 다음 요소로 구성됩니다:

- **네트워크 보안**: 방화벽, 네트워크 분할
- **애플리케이션 보안**: 코드 보안, 입력 검증
- **데이터 보안**: 암호화, 접근 제어

## 3. 실전 설정 가이드

### 3.1 준비 사항

설정을 시작하기 전에 다음을 확인합니다:

- **요구사항 분석**: 보안 요구사항 및 규정 확인
- **환경 준비**: 필요한 도구 및 리소스 준비
- **정책 수립**: 보안 정책 및 절차 문서화

### 3.2 단계별 구현

#### 3.2.1 초기 설정

```bash
# 기본 보안 설정 예시
# 실제 환경에 맞게 수정 필요
```

#### 3.2.2 보안 정책 적용

보안 정책을 적용합니다:

- 접근 제어 정책 설정
- 암호화 정책 구성
- 모니터링 정책 활성화

#### 3.2.3 테스트 및 검증

설정 완료 후 다음 테스트를 수행합니다:

- 기능 테스트
- 보안 테스트
- 성능 테스트

## 4. 모니터링 및 대응

### 4.1 로깅 및 모니터링

보안 이벤트를 모니터링하기 위한 설정:

- **로그 수집**: 모든 보안 이벤트 로깅
- **실시간 모니터링**: 이상 행위 탐지
- **알림 설정**: 중요한 이벤트 즉시 알림

### 4.2 사고 대응

보안 사고 발생 시 대응 절차:

1. **인지**: 사고 신호 감지
2. **격리**: 영향 범위 제한
3. **조사**: 원인 분석
4. **복구**: 정상 상태 복구
5. **개선**: 재발 방지 조치

## 5. 모범 사례

### 5.1 보안 모범 사례

- **정기적인 보안 점검**: 취약점 스캔 및 보안 감사
- **자동화된 보안 스캔**: CI/CD 파이프라인에 보안 스캔 통합
- **보안 교육**: 직원 보안 인식 교육

### 5.2 운영 모범 사례

- **변경 관리**: 모든 변경사항 문서화 및 승인
- **백업 및 복구**: 정기적인 백업 및 복구 테스트
- **문서화**: 보안 정책 및 절차 문서화

## 6. 문제 해결

### 6.1 일반적인 문제

자주 발생하는 문제와 해결 방법:

**문제**: 설정 오류로 인한 접근 차단
- **원인**: 잘못된 보안 정책 설정
- **해결**: 정책 재검토 및 수정

**문제**: 성능 저하
- **원인**: 과도한 보안 검사
- **해결**: 보안 정책 최적화

### 6.2 트러블슈팅 가이드

문제 발생 시 확인 순서:

1. 로그 확인
2. 보안 정책 검증
3. 네트워크 연결 확인
4. 리소스 상태 확인

## 결론

{title}에 대해 다루었습니다. 올바른 보안 설정과 지속적인 모니터링을 통해 안전한 환경을 구축할 수 있습니다.

보안은 한 번 설정하고 끝나는 것이 아니라 지속적인 관리와 개선이 필요합니다. 정기적인 보안 점검과 업데이트를 통해 최신 위협에 대응할 수 있습니다.

---

원본 포스트: [원본 URL은 파일에서 추출]
"""

def generate_cloud_content(title: str, excerpt: str, tags: str) -> str:
    """클라우드 관련 콘텐츠 생성"""
    return f"""## 서론

{excerpt}

이 글에서는 {title}에 대해 클라우드 환경에서의 실무 경험을 바탕으로 상세히 다룹니다.

## 1. 클라우드 아키텍처 개요

### 1.1 클라우드의 장점

클라우드 환경을 활용하면 다음과 같은 이점을 얻을 수 있습니다:

- **확장성**: 필요에 따라 리소스 확장/축소
- **비용 효율성**: 사용한 만큼만 비용 지불
- **가용성**: 고가용성 인프라 제공
- **보안**: 클라우드 제공업체의 보안 인프라 활용

### 1.2 주요 클라우드 서비스

클라우드 환경에서 활용할 수 있는 주요 서비스:

- **컴퓨팅**: 가상 서버, 컨테이너, 서버리스
- **스토리지**: 객체 스토리지, 블록 스토리지
- **네트워킹**: VPC, 로드 밸런서, CDN
- **데이터베이스**: 관리형 데이터베이스 서비스

## 2. 아키텍처 설계

### 2.1 설계 원칙

효과적인 클라우드 아키텍처 설계 원칙:

1. **확장 가능한 설계**: 수평 확장 가능한 구조
2. **고가용성**: 다중 AZ 및 리전 활용
3. **보안**: 네트워크 분할 및 접근 제어
4. **비용 최적화**: 적절한 리소스 크기 선택

### 2.2 네트워크 아키텍처

클라우드 네트워크 아키텍처 구성:

- **VPC**: 논리적 네트워크 격리
- **서브넷**: 퍼블릭/프라이빗 서브넷 분리
- **라우팅**: 라우팅 테이블 구성
- **보안 그룹**: 인스턴스 레벨 방화벽

## 3. 실전 구현

### 3.1 인프라 구성

```hcl
# Terraform 예시
# 실제 환경에 맞게 수정 필요
```

### 3.2 보안 설정

보안 설정 구성:

- IAM 역할 및 정책 설정
- 보안 그룹 규칙 구성
- 네트워크 ACL 설정

### 3.3 모니터링 구성

모니터링 설정:

- CloudWatch 메트릭 수집
- 로그 수집 및 분석
- 알림 설정

## 4. 비용 최적화

### 4.1 비용 관리 전략

- **리소스 태깅**: 비용 추적을 위한 태그 설정
- **리저브드 인스턴스**: 장기 사용 시 할인 활용
- **스팟 인스턴스**: 유연한 워크로드에 활용

### 4.2 FinOps 실천

- **비용 모니터링**: 정기적인 비용 분석
- **최적화 권장사항**: 클라우드 제공업체 권장사항 활용
- **예산 관리**: 예산 설정 및 알림

## 결론

{title}에 대해 클라우드 환경에서의 구현 방법을 다루었습니다. 올바른 아키텍처 설계와 지속적인 최적화를 통해 효율적인 클라우드 환경을 구축할 수 있습니다.

---

원본 포스트: [원본 URL은 파일에서 추출]
"""

def generate_devsecops_content(title: str, excerpt: str, tags: str) -> str:
    """DevSecOps 관련 콘텐츠 생성"""
    return f"""## 서론

{excerpt}

이 글에서는 {title}에 대해 DevSecOps 관점에서 실무 경험을 공유합니다.

## 1. DevSecOps 개요

### 1.1 DevSecOps란?

DevSecOps는 개발(Dev), 보안(Sec), 운영(Ops)을 통합하여 소프트웨어 개발 생명주기 전반에 보안을 통합하는 방법론입니다.

### 1.2 주요 원칙

- **보안 by Design**: 설계 단계부터 보안 고려
- **자동화**: 보안 검사를 자동화
- **지속적인 모니터링**: 런타임 보안 모니터링

## 2. 보안 통합

### 2.1 CI/CD 파이프라인에 보안 통합

- **정적 코드 분석**: SAST 도구 활용
- **의존성 스캔**: 취약한 라이브러리 탐지
- **컨테이너 스캔**: 컨테이너 이미지 보안 검사

### 2.2 인프라 보안

- **IaC 보안**: Terraform, CloudFormation 보안 검사
- **컴플라이언스**: 정책 기반 컴플라이언스 검사
- **시크릿 관리**: 안전한 시크릿 저장 및 관리

## 결론

{title}에 대해 DevSecOps 관점에서 다루었습니다. 보안을 개발 프로세스에 통합하여 안전한 소프트웨어를 효율적으로 제공할 수 있습니다.

---

원본 포스트: [원본 URL은 파일에서 추출]
"""

def generate_generic_content(title: str, excerpt: str, tags: str) -> str:
    """일반적인 콘텐츠 생성"""
    return f"""## 서론

{excerpt}

이 글에서는 {title}에 대해 상세히 다룹니다.

## 1. 개요

### 1.1 배경

{excerpt[:200]}...

### 1.2 목적

이 가이드의 목적은 다음과 같습니다:

- 실무 중심의 가이드 제공
- 구체적인 설정 방법 공유
- 모범 사례 제시

## 2. 핵심 내용

### 2.1 기본 개념

주요 개념을 이해하는 것이 중요합니다.

### 2.2 실전 적용

실제 환경에 적용하는 방법을 다룹니다.

## 결론

{title}에 대해 다루었습니다. 실무에 바로 적용할 수 있는 내용을 공유했습니다.

---

원본 포스트: [원본 URL은 파일에서 추출]
"""

def improve_post(post_info: Dict) -> bool:
    """포스팅 개선"""
    try:
        content = post_info['content']
        title = post_info['title']
        excerpt = post_info['excerpt']
        category = post_info['category']
        tags = post_info['tags']
        original_url = post_info['original_url']
        
        # 요약 섹션 찾기
        summary_match = re.search(r'(## 📋 포스팅 요약\n\n.*?\n\n)', content, re.DOTALL)
        if not summary_match:
            return False
        
        summary_end = summary_match.end()
        
        # 기존 본문 확인
        existing_body_start = content.find('## 서론', summary_end)
        if existing_body_start == -1:
            existing_body_start = content.find('## 1.', summary_end)
        
        # 본문이 이미 충분히 긴 경우 스킵
        if existing_body_start != -1:
            existing_body = content[existing_body_start:]
            body_length = len([line for line in existing_body.split('\n') 
                             if not line.strip().startswith('#') 
                             and not line.strip().startswith('```')
                             and line.strip()])
            if body_length > 1000:
                return False
        
        # 개선된 본문 생성
        improved_body = generate_content_sections(title, excerpt, category, tags)
        
        # 원본 URL 추가
        if original_url:
            improved_body = improved_body.replace('[원본 URL은 파일에서 추출]', 
                                                 f'[{original_url}]({original_url})')
        
        # 기존 본문이 있으면 교체, 없으면 추가
        if existing_body_start != -1:
            # 원본 포스트 링크까지 제거
            original_link_start = content.find('원본 포스트:', existing_body_start)
            if original_link_start != -1:
                new_content = content[:summary_end] + '\n' + improved_body
            else:
                new_content = content[:existing_body_start] + improved_body
        else:
            # 본문이 없으면 추가
            original_link_start = content.find('원본 포스트:', summary_end)
            if original_link_start != -1:
                new_content = content[:summary_end] + '\n' + improved_body
            else:
                new_content = content.rstrip() + '\n\n' + improved_body
        
        # 파일 저장
        post_info['file_path'].write_text(new_content, encoding='utf-8')
        return True
        
    except Exception as e:
        log_message(f"Error improving {post_info['file_path'].name}: {e}")
        import traceback
        log_message(traceback.format_exc())
        return False

def main():
    """메인 함수"""
    start_time = time.time()
    improved_count = 0
    checked_count = 0
    
    log_message("=" * 60)
    log_message("지능형 포스팅 개선 프로세스 시작")
    log_message(f"실행 시간: {RUN_DURATION}초 (1시간)")
    log_message("=" * 60)
    
    # 모든 포스팅 파일 목록
    all_posts = list(POSTS_DIR.glob("*.md"))
    posts_to_improve = []
    
    # 개선이 필요한 포스팅 식별
    log_message("\n포스팅 분석 중...")
    for post_file in sorted(all_posts):
        try:
            post_info = extract_post_info(post_file)
            if not post_info:
                continue
                
            checked_count += 1
            
            if needs_improvement(post_info):
                posts_to_improve.append(post_info)
                log_message(f"  개선 필요: {post_file.name} (본문: {post_info['body_length']}자)")
        except Exception as e:
            log_message(f"  오류: {post_file.name} - {e}")
    
    log_message(f"\n총 {len(all_posts)}개 포스팅 중 {len(posts_to_improve)}개 개선 필요")
    log_message(f"개선 프로세스 시작...\n")
    
    # 개선 프로세스 실행
    for i, post_info in enumerate(posts_to_improve, 1):
        # 시간 체크
        elapsed_time = time.time() - start_time
        if elapsed_time >= RUN_DURATION:
            log_message(f"\n실행 시간 ({RUN_DURATION}초) 도달. 프로세스 종료.")
            break
        
        log_message(f"[{i}/{len(posts_to_improve)}] {post_info['file_path'].name}")
        
        if improve_post(post_info):
            improved_count += 1
            log_message(f"  ✓ 개선 완료")
        else:
            log_message(f"  ✗ 개선 실패 또는 스킵")
        
        # 다음 포스팅 처리 전 잠시 대기
        time.sleep(0.5)
    
    elapsed_time = time.time() - start_time
    
    # 최종 리포트
    log_message("\n" + "=" * 60)
    log_message("포스팅 개선 프로세스 완료")
    log_message(f"실행 시간: {elapsed_time:.2f}초")
    log_message(f"확인한 포스팅: {checked_count}개")
    log_message(f"개선한 포스팅: {improved_count}개")
    log_message(f"남은 포스팅: {len(posts_to_improve) - improved_count}개")
    log_message("=" * 60)

if __name__ == "__main__":
    main()
