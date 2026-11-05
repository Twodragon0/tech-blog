# 1. mdmclient 프로세스 CPU/메모리 사용량 확인
top -l 1 -s 0 | grep -i mdmclient

# 2. Kandji 에이전트 리소스 사용량 확인
ps aux | grep -E "kandji|mdmclient" | awk '{print $1, $2, $3, $4, $11}'

# 3. 최근 1시간 에이전트 로그 오류 확인
log show --predicate 'subsystem == "com.kandji.agent"' --last 1h --level error

# 4. 과도한 스크립트 실행 여부 확인
log show --predicate 'process == "bash" OR process == "python3"' --last 30m | wc -l
