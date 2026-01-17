#!/usr/bin/env python3
"""
포스팅에 toc 필드 추가 스크립트
"""

import re
from pathlib import Path

POSTS_DIR = Path("_posts")

# toc 필드가 누락된 파일 목록
MISSING_TOC_FILES = [
    "2025-04-29-SKT_Security_Issue_Complete_Response_Guide_IMEI_Check_USIMeSIM_Replace_And_MFA_Importance.md",
    "2025-04-30-Public_PCEven_in_Safely_Passkey_OTP_Strong_Password_Management_Usage.md",
    "2025-05-02-Kandji_macOS_Complete_Master_SetupFrom_Security_Regulation_ComplianceTo_All-in-One_Guide.md",
    "2025-05-09-Cloud_Security_Course_7Batch_-_4Week_AWS_Vulnerability_Inspection_And_ISMS_Response_Guide.md",
    "2025-05-16-Cloud_Security_Course_7Batch_-_5Week_AWS_Control_Tower_And_ZTNA.md",
    "2025-05-24-Amazon_Q_DeveloperAnd_GitHub_Advanced_Security_Security_And_AWS.md",
    "2025-05-30-Kubernetes_Minikube_ampamp_K9s_Practice_Guide_Problem_From_Resolution_Practical_TestTo.md",
    "2025-06-05-Email_Delivery_Trust_Improve_SendGrid_SPF_DKIM_DMARC_Setup_Complete_Guide.md",
    "2025-09-16-AWS_reInforce_2025_Cloud_Security_Current_and_Future.md",
    "2025-09-17-NPM_ampquotShai-Huludampquot_Self_Replication_Worm_Attack_180_Above_Package_Breach_Large_scale_Supply_Chain_Attack_Complete_Analysis.md",
    "2025-10-31-AI_amplsquoSecretaryamprsquo_amplsquoSecurity_Holeamprsquo_For_Enterprise_AI_Service_Security_Guide.md",
    "2025-11-19-Post-Mortem_2025_11_18_Cloudflare_Global_Incident_Response_Log_What_Learned.md",
    "2025-12-17-12_Conference_Review_AWSKRUG_OWASP_Datadog_Preview_See_2025_AIAnd_Security_Coexistence.md",
]

def add_toc_field(file_path: Path):
    """포스팅에 toc 필드 추가"""
    content = file_path.read_text(encoding="utf-8")
    
    if not content.startswith("---"):
        print(f"⚠️  {file_path.name}: No front matter found")
        return False
    
    # front matter 끝 찾기
    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"⚠️  {file_path.name}: Invalid front matter format")
        return False
    
    front_matter = parts[1]
    body = parts[2]
    
    # 이미 toc 필드가 있는지 확인
    if "toc:" in front_matter:
        print(f"✓  {file_path.name}: toc field already exists")
        return False
    
    # image_alt 다음에 toc 추가 (또는 마지막에)
    if "image_alt:" in front_matter:
        # image_alt 다음에 toc 추가
        front_matter = re.sub(
            r'(image_alt:.*?)\n',
            r'\1\ntoc: true\n',
            front_matter,
            flags=re.DOTALL
        )
    else:
        # front matter 끝에 toc 추가
        front_matter = front_matter.rstrip() + "\ntoc: true\n"
    
    # 파일 저장
    new_content = f"---{front_matter}---{body}"
    file_path.write_text(new_content, encoding="utf-8")
    print(f"✓  {file_path.name}: toc field added")
    return True

def main():
    """메인 함수"""
    updated = 0
    for filename in MISSING_TOC_FILES:
        file_path = POSTS_DIR / filename
        if file_path.exists():
            if add_toc_field(file_path):
                updated += 1
        else:
            print(f"⚠️  {filename}: File not found")
    
    print(f"\n✓  Updated {updated} files")

if __name__ == "__main__":
    main()
