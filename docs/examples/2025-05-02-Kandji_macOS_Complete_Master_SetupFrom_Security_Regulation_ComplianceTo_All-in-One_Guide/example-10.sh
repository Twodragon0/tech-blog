# 1. MDM 등록 상태 확인
profiles status -type enrollment

# 2. UAMDM(사용자 승인 MDM) 활성화 여부 확인
sudo /usr/libexec/mdmclient QuerySecurityInfo | grep -i "user approved"

# 3. 사용자 승인 유도 (시스템 설정 → 개인 정보 보호 및 보안 → 프로파일)
open "x-apple.systempreferences:com.apple.preferences.security"

# 4. DEP 재등록 (Recovery Mode에서 실행)
# csrutil disable  ← Apple Silicon: Startup Security Utility에서 변경
sudo /usr/libexec/mdmclient dep nag
