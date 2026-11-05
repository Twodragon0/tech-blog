# 1. 802.1X 인증서 키체인 확인
security find-certificate -a -Z /Library/Keychains/System.keychain \
  | grep -B 5 "802.1X\|RADIUS\|WPA"

# 2. Wi-Fi 프로파일 설치 상태 확인
profiles list -verbose | grep -i "Wi-Fi\|802.1X"

# 3. 인증서 유효기간 확인
security find-certificate -c "Your-Corp-CA" -p | openssl x509 -noout -dates

# 4. 네트워크 연결 진단 로그
log show --predicate 'subsystem == "com.apple.eap"' --last 30m | tail -50
