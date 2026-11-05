# 특정 국가 차단을 위한 AWS WAF Geo Match 규칙 생성
aws wafv2 create-rule-group \
  --name "GeoBlockRuleGroup" \
  --scope REGIONAL \
  --capacity 50 \
  --rules '[
    {
      "Name": "BlockHighRiskCountries",
      "Priority": 1,
      "Action": { "Block": {} },
      "Statement": {
        "GeoMatchStatement": {
          "CountryCodes": ["CN", "RU", "KP"]
        }
      },
      "VisibilityConfig": {
        "SampledRequestsEnabled": true,
        "CloudWatchMetricsEnabled": true,
        "MetricName": "GeoBlockRule"
      }
    }
  ]' \
  --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=GeoBlockRuleGroup
