# Cloudflare WAF 커스텀 규칙 생성
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/rulesets" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "Custom WAF Rules",
    "kind": "zone",
    "phase": "http_request_firewall_custom",
    "rules": [
      {
        "action": "block",
        "expression": "(http.request.uri.query contains \"SELECT\" and http.request.uri.query contains \"FROM\") or (http.request.body contains \"UNION SELECT\")",
        "description": "SQL Injection 차단 규칙"
      },
      {
        "action": "challenge",
        "expression": "cf.threat_score gt 30",
        "description": "위협 점수 높은 요청에 챌린지 적용"
      }
    ]
  }'
