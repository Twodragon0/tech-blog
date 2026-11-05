# 1. Kandji API로 복구키 조회
curl -X GET "https://api.kandji.io/api/v1/devices/{device_id}/filevault" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  | jq -r '.recovery_key'

# 2. 복구키로 macOS 복구 모드 진입 후 잠금 해제
# - 재시작 후 Command+R 또는 전원 버튼 길게 눌러 복구 모드 진입
# - Disk Utility → 디스크 잠금 해제 시 복구키 입력

# 3. 복구키 회전 (해제 후 즉시 실행)
sudo fdesetup changerecovery -personal
