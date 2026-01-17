#!/usr/bin/env python3
"""
템플릿 섹션 제거 스크립트
- 1.2 주요 개념
- 2. 핵심 내용 (템플릿)
- 3. 모범 사례 (템플릿)
- 4. 문제 해결 (템플릿)
"""

import re
from pathlib import Path

TEMPLATE_SECTIONS = [
    (r'### 1\.2 주요 개념\s*\n\s*이 가이드에서 다루는 주요 개념:\s*\n\s*- \*\*보안\*\*: 안전한 구성 및 접근 제어\s*\n\s*- \*\*효율성\*\*: 최적화된 설정 및 운영\s*\n\s*- \*\*모범 사례\*\*: 검증된 방법론 적용\s*\n', ''),
    (r'## 2\. 핵심 내용\s*\n\s*### 2\.1 기본 설정\s*\n\s*기본 설정을 시작하기 전에 다음 사항을 확인해야 합니다:\s*\n\s*1\. \*\*요구사항 분석\*\*: 필요한 기능 및 성능 요구사항 파악\s*\n\s*2\. \*\*환경 준비\*\*: 필요한 도구 및 리소스 준비\s*\n\s*3\. \*\*보안 정책\*\*: 보안 정책 및 규정 준수 사항 확인\s*\n\s*### 2\.2 단계별 구현\s*\n\s*#### 단계 1: 초기 설정\s*\n\s*초기 설정 단계에서는 기본 구성을 수행합니다\.\s*\n\s*```bash\s*\n# 예시 명령어\s*\n# 실제 설정에 맞게 수정 필요\s*```\s*\n\s*#### 단계 2: 보안 구성\s*\n\s*보안 설정을 구성합니다:\s*\n\s*- 접근 제어 설정\s*\n- 암호화 구성\s*\n- 모니터링 활성화\s*\n', ''),
    (r'## 3\. 모범 사례\s*\n\s*### 3\.1 보안 모범 사례\s*\n\s*- \*\*최소 권한 원칙\*\*: 필요한 최소한의 권한만 부여\s*\n- \*\*정기적인 보안 점검\*\*: 취약점 스캔 및 보안 감사\s*\n- \*\*자동화된 보안 스캔\*\*: CI/CD 파이프라인에 보안 스캔 통합\s*\n\s*### 3\.2 운영 모범 사례\s*\n\s*- \*\*자동화된 배포 파이프라인\*\*: 일관성 있는 배포\s*\n- \*\*정기적인 백업\*\*: 데이터 보호\s*\n- \*\*모니터링\*\*: 지속적인 상태 모니터링\s*\n', ''),
    (r'## 4\. 문제 해결\s*\n\s*### 4\.1 일반적인 문제\s*\n\s*자주 발생하는 문제와 해결 방법:\s*\n\s*\*\*문제 1\*\*: 설정 오류\s*\n- \*\*원인\*\*: 잘못된 구성\s*\n- \*\*해결\*\*: 설정 파일 재확인 및 수정\s*\n\s*\*\*문제 2\*\*: 성능 저하\s*\n- \*\*원인\*\*: 리소스 부족\s*\n- \*\*해결\*\*: 리소스 확장 또는 최적화\s*\n', ''),
]

def remove_template_sections(content):
    """템플릿 섹션 제거"""
    for pattern, replacement in TEMPLATE_SECTIONS:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # 섹션 번호 재조정 (5번 -> 2번으로 변경된 경우)
    content = re.sub(r'## 5\.', '## 2.', content)
    content = re.sub(r'### 5\.', '### 2.', content)
    
    return content

def process_file(file_path):
    """파일 처리"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixed_content = remove_template_sections(content)
        
        if original_content != fixed_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """메인 함수"""
    posts_dir = Path(__file__).parent.parent / '_posts'
    
    target_files = [
        '2025-05-24-Amazon_Q_DeveloperAnd_GitHub_Advanced_Security_Security_And_AWS.md',
        '2025-05-09-Cloud_Security_Course_7Batch_-_4Week_AWS_Vulnerability_Inspection_And_ISMS_Response_Guide.md',
        '2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_And_ZTNA.md',
        '2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide.md',
        '2025-04-30-Public_PCEven_in_Safely_Passkey_OTP_Strong_Password_Management_Usage.md',
        '2025-04-29-SKT_Security_Issue_Complete_Response_Guide_IMEI_Check_USIMeSIM_Replace_And_MFA_Importance.md',
    ]
    
    modified_files = []
    
    for filename in target_files:
        file_path = posts_dir / filename
        if file_path.exists():
            if process_file(file_path):
                modified_files.append(filename)
                print(f"Fixed: {filename}")
        else:
            print(f"Not found: {filename}")
    
    print(f"\nTotal files modified: {len(modified_files)}")
    return modified_files

if __name__ == '__main__':
    main()
