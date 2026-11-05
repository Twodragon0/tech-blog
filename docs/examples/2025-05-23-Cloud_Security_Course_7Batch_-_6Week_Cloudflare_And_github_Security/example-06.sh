# Cloudflare 보안 이벤트 조회
curl -s "https://api.cloudflare.com/client/v4/zones/{zone_id}/security/events?per_page=50" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" | \
  jq '.result[] | {action, clientIP: .clientIP, uri: .clientRequestHTTPHost, ruleId: .ruleId}'

# Cloudflare Firewall 이벤트 분석 (GraphQL)
curl -s "https://api.cloudflare.com/client/v4/graphql" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{
    "query": "{ viewer { zones(filter: {zoneTag: \"{zone_id}\"}) { firewallEventsAdaptive(filter: {datetime_gt: \"2025-05-22T00:00:00Z\"}, limit: 100, orderBy: [datetime_DESC]) { action clientIP clientRequestHTTPHost ruleId } } } }"
  }'
