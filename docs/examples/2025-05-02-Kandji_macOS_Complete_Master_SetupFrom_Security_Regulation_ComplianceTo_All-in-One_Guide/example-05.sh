# Okta Device Trust 연동 확인 스크립트
# Kandji 관리 디바이스에서 Okta Device Trust 인증서 상태 점검

# 1. Okta Device Trust 인증서 확인
security find-certificate -a -Z /Library/Keychains/System.keychain \
  | grep -A 5 "Okta Device Trust"

# 2. MDM 등록 상태 확인
profiles status -type enrollment

# 3. Okta Verify 앱 설치 확인
ls /Applications/ | grep -i "Okta Verify"
