# Kandji → Splunk HEC 연동 예시
# 1. Kandji Audit Log API로 이벤트 수집
KANDJI_TOKEN="YOUR_KANDJI_API_TOKEN"
SPLUNK_HEC_URL="https://splunk.example.com:8088/services/collector"
SPLUNK_HEC_TOKEN="YOUR_SPLUNK_HEC_TOKEN"

# Kandji audit events 조회 (최근 1시간)
events=$(curl -s -X GET "https://api.kandji.io/api/v1/audit-log?limit=100" \
  -H "Authorization: Bearer ${KANDJI_TOKEN}" | jq -c '.results[]')

# Splunk HEC로 이벤트 전송
echo "$events" | while IFS= read -r event; do
  curl -s -X POST "${SPLUNK_HEC_URL}" \
    -H "Authorization: Splunk ${SPLUNK_HEC_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"sourcetype\": \"kandji:audit\", \"event\": ${event}}"
done
