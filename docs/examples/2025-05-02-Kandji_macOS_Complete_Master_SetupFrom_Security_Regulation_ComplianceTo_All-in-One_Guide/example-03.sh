#!/bin/bash
# CIS Benchmark 핵심 항목 자동 감사
echo "=== CIS macOS Benchmark 감사 ==="

# CIS 1.1: 자동 업데이트
auto_update=$(defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled 2>/dev/null)
[ "$auto_update" = "1" ] && echo "PASS [1.1] 자동 업데이트 활성화" || echo "FAIL [1.1] 자동 업데이트 비활성화"

# CIS 2.3.1: 방화벽
fw_state=$(defaults read /Library/Preferences/com.apple.alf globalstate 2>/dev/null)
[ "$fw_state" != "0" ] && echo "PASS [2.3.1] 방화벽 활성화" || echo "FAIL [2.3.1] 방화벽 비활성화"

# CIS 2.5.1: FileVault
fv=$(fdesetup status)
echo "$fv" | grep -q "On" && echo "PASS [2.5.1] FileVault 활성화" || echo "FAIL [2.5.1] FileVault 비활성화"

# CIS 2.10.1: SIP
csrutil status | grep -q "enabled" && echo "PASS [2.10.1] SIP 활성화" || echo "FAIL [2.10.1] SIP 비활성화"
