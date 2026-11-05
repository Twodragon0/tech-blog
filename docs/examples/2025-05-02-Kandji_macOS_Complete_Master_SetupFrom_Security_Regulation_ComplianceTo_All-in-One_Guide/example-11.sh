# 1. VPP 토큰 유효성 확인 (Kandji Console → Integrations → Apple Business Manager)
curl -X GET "https://api.kandji.io/api/v1/integrations/vpp" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  | jq '.token_expiry'

# 2. 앱 라이선스 잔여 확인
curl -X GET "https://api.kandji.io/api/v1/apps" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  | jq '.[] | {name: .name, available_licenses: .available_licenses}'

# 3. 디바이스 ABM 연결 확인
sudo /usr/libexec/mdmclient QueryDeviceInformation | grep -i "EnrolledViaDEP"

# 4. Kandji 에이전트 로그 확인
log show --predicate 'subsystem == "com.kandji.agent"' --last 1h | grep -i "app install"
