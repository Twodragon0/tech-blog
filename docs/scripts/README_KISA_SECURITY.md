# KISA 보안공지 수집 및 블로그 초안 생성

KISA 보호나라(https://www.boho.or.kr) 보안공지를 자동으로 수집하고, 블로그 포스트 초안을 생성하는 스크립트입니다.

## 기능

- KISA 보안공지 자동 수집
- CVE 번호 자동 추출 및 NVD 링크 생성
- 벤더별 보안 페이지 자동 매핑
- 카테고리 자동 분류 (랜섬웨어, 피싱, 취약점 등)
- 블로그 초안 자동 생성

## 사용법

### 기본 사용

```bash
# 최근 30일 보안공지 수집
python3 scripts/collect_kisa_security.py

# 최근 7일 보안공지 수집
python3 scripts/collect_kisa_security.py --days 7

# 블로그 초안 생성 포함
python3 scripts/collect_kisa_security.py --generate-draft
```

### 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--days` | 30 | 수집 기간 (일) |
| `--pages` | 3 | 수집할 페이지 수 |
| `--generate-draft` | False | 블로그 초안 생성 |
| `--max-drafts` | 5 | 생성할 최대 초안 수 |
| `--use-cache` | False | 캐시된 데이터 사용 |

### 예시

```bash
# 최근 90일 보안공지 수집, 최대 5개 초안 생성
python3 scripts/collect_kisa_security.py --days 90 --pages 5 --generate-draft --max-drafts 5

# 캐시된 데이터로 초안 생성
python3 scripts/collect_kisa_security.py --use-cache --generate-draft
```

## 출력 파일

### 수집 데이터
- `_data/kisa_security_notices.json` - 수집된 보안공지 JSON

### 생성된 초안
- `_drafts/YYYY-MM-DD-KISA_*.md` - 블로그 초안 파일

## 지원 벤더

다음 벤더에 대해 자동으로 보안 페이지 링크를 생성합니다:

| 벤더 | 보안 페이지 |
|------|------------|
| Microsoft | MSRC |
| Adobe | Adobe Security |
| Apple | Apple Security |
| Google/Chrome | Chrome Releases |
| Oracle | Oracle Security Alerts |
| Cisco | Cisco Security |
| VMware | VMware Security |
| Fortinet | FortiGuard PSIRT |
| Palo Alto | Security Advisories |
| TP-Link | Security Advisory |
| Trend Micro | Vulnerability Response |
| MongoDB | MongoDB Alerts |
| ... | 30+ 벤더 지원 |

## CVE 레퍼런스

CVE 번호가 발견되면 자동으로 다음 레퍼런스를 생성합니다:

- NVD (National Vulnerability Database)
- MITRE CVE
- CVE Details

## 카테고리 자동 분류

| 카테고리 | 키워드 |
|----------|--------|
| ransomware | 랜섬웨어, 암호화, 복호화 |
| phishing | 피싱, 스미싱, 큐싱 |
| vulnerability | 취약점, CVE, 보안 업데이트 |
| malware | 악성코드, 트로이목마, 백도어 |
| apt | APT, 지능형 지속 위협 |
| ddos | DDoS, 서비스 거부 |
| data_breach | 정보유출, 개인정보 |

## 워크플로우

```
KISA 보안공지 → collect_kisa_security.py → _data/kisa_security_notices.json
                          ↓
                 --generate-draft
                          ↓
                   _drafts/*.md → 수동 검토 → _posts/*.md (게시)
```

## 보안 고려사항

- API 키나 민감 정보는 사용하지 않음
- SSL 인증서 검증 경고가 발생할 수 있음 (KISA 사이트 인증서 문제)
- 수집된 데이터는 로컬에만 저장

## 문제 해결

### SSL 인증서 오류
KISA 사이트의 SSL 인증서 문제로 경고가 발생할 수 있습니다. 스크립트는 이를 자동으로 처리합니다.

### 빈 결과
날짜 범위를 확인하세요. `--days` 옵션으로 더 긴 기간을 지정해보세요.

### 파싱 오류
KISA 사이트 구조가 변경되면 파싱 로직 업데이트가 필요할 수 있습니다.

## 관련 파일

- `scripts/collect_kisa_security.py` - 메인 스크립트
- `scripts/collect_tech_news.py` - 기술 뉴스 수집 (유사 기능)
- `scripts/generate_news_draft.py` - 뉴스 초안 생성
