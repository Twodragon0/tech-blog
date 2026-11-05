# 1. APNs 연결 확인
nc -zv gateway.push.apple.com 2195
nc -zv feedback.push.apple.com 2196

# 2. MDM 등록 상태 확인
sudo /usr/libexec/mdmclient dep nag

# 3. ABM 서버 접근 확인
curl -sv https://deviceenrollment.apple.com/ping

# 4. Kandji 에이전트 재시작
sudo launchctl kickstart -k system/com.kandji.agent
