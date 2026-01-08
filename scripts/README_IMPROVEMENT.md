# 포스팅 자동 개선 스크립트

이 디렉토리에는 블로그 포스팅을 자동으로 개선하는 스크립트들이 포함되어 있습니다.

## 🚀 AI 기반 개선 (권장)

**Claude, Gemini, Cursor를 활용한 지능형 개선**을 원하시면 [README_AI_IMPROVEMENT.md](README_AI_IMPROVEMENT.md)를 참고하세요.

### 빠른 시작
```bash
# 1. API 키 설정
./scripts/setup_ai_keys.sh

# 2. AI 기반 개선 실행 (1시간)
./scripts/run_ai_improvement.sh
```

---

## 기본 개선 스크립트

## 스크립트 목록

### 1. `enhance_all_posts.py`
모든 포스팅의 요약 섹션을 보강합니다.
- 태그, 핵심 내용, 주요 기술/도구, 대상 독자 정보 추가
- 한 번 실행하면 모든 포스팅의 요약 섹션이 표준화됩니다.

**사용법:**
```bash
python3 scripts/enhance_all_posts.py
```

### 2. `smart_improve_posts.py`
지능형 포스팅 개선 스크립트입니다.
- 제목과 excerpt를 분석하여 관련성 높은 본문을 생성합니다.
- 카테고리별로 다른 템플릿을 사용합니다 (보안, 클라우드, DevSecOps 등).
- 본문이 짧은 포스팅(1000자 미만)을 자동으로 개선합니다.
- 1시간 동안 실행되며 지속적으로 포스팅을 개선합니다.

**사용법:**
```bash
# 일반 실행 (테스트용, 빠르게 완료)
python3 scripts/smart_improve_posts.py

# 백그라운드 실행 (1시간 동안 실행)
nohup python3 scripts/smart_improve_posts.py > improvement.log 2>&1 &

# 실행 중인 프로세스 확인
ps aux | grep smart_improve_posts

# 로그 확인
tail -f improvement_log.txt
```

### 3. `continuous_improve_posts.py`
연속적인 포스팅 개선 스크립트입니다.
- 기본 템플릿 기반으로 본문을 생성합니다.
- 1시간 동안 실행됩니다.

## 자동 실행 설정

### macOS/Linux에서 cron으로 자동 실행

```bash
# crontab 편집
crontab -e

# 매일 오전 2시에 실행
0 2 * * * cd /Users/yong/Desktop/tech-blog && /usr/bin/python3 scripts/smart_improve_posts.py >> improvement.log 2>&1
```

### systemd 서비스로 실행 (Linux)

`/etc/systemd/system/blog-improvement.service` 파일 생성:

```ini
[Unit]
Description=Blog Post Improvement Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/Users/yong/Desktop/tech-blog
ExecStart=/usr/bin/python3 scripts/smart_improve_posts.py
Restart=on-failure
StandardOutput=append:/Users/yong/Desktop/tech-blog/improvement.log
StandardError=append:/Users/yong/Desktop/tech-blog/improvement.log

[Install]
WantedBy=multi-user.target
```

서비스 시작:
```bash
sudo systemctl enable blog-improvement.service
sudo systemctl start blog-improvement.service
```

## 개선 기준

스크립트는 다음 조건을 만족하는 포스팅을 개선 대상으로 식별합니다:

1. **본문 길이**: 1000자 미만인 포스팅
2. **구조 부재**: "서론" 또는 "1." 섹션이 없는 포스팅
3. **내용 부족**: 원본 포스트 링크만 있고 본문이 거의 없는 포스팅

## 개선 내용

스크립트는 다음을 수행합니다:

1. **구조화된 본문 생성**:
   - 서론 섹션
   - 개요 및 배경
   - 핵심 내용
   - 실전 가이드
   - 모범 사례
   - 문제 해결
   - 결론

2. **카테고리별 맞춤 콘텐츠**:
   - 보안 관련: 보안 모범 사례, 위협 대응 등
   - 클라우드 관련: 아키텍처 설계, 비용 최적화 등
   - DevSecOps 관련: CI/CD 통합, 자동화 등

3. **원본 링크 보존**: 원본 포스트 링크를 본문 하단에 유지

## 로그 파일

개선 프로세스의 로그는 `improvement_log.txt` 파일에 기록됩니다:

```bash
# 로그 확인
tail -f improvement_log.txt

# 최근 50줄 확인
tail -n 50 improvement_log.txt
```

## 주의사항

1. **백업**: 스크립트 실행 전에 포스팅 파일을 백업하는 것을 권장합니다.
2. **검토**: 자동 생성된 내용은 기본 템플릿 기반이므로, 필요시 수동으로 개선이 필요할 수 있습니다.
3. **원본 보존**: 원본 포스트 링크는 항상 유지되므로 원본 내용을 확인할 수 있습니다.

## 문제 해결

### 스크립트가 실행되지 않는 경우

1. Python 버전 확인:
```bash
python3 --version  # Python 3.6 이상 필요
```

2. 권한 확인:
```bash
chmod +x scripts/smart_improve_posts.py
```

3. 의존성 확인:
```bash
# 필요한 Python 라이브러리가 없으면 설치
pip3 install -r requirements.txt  # 있다면
```

### 개선된 내용이 마음에 들지 않는 경우

1. 원본 포스트 링크를 통해 원본 내용 확인
2. 수동으로 본문 수정
3. 스크립트의 템플릿 함수를 수정하여 원하는 형식으로 변경

## 커스터마이징

스크립트의 템플릿 함수를 수정하여 원하는 형식으로 콘텐츠를 생성할 수 있습니다:

- `generate_security_content()`: 보안 관련 콘텐츠 템플릿
- `generate_cloud_content()`: 클라우드 관련 콘텐츠 템플릿
- `generate_devsecops_content()`: DevSecOps 관련 콘텐츠 템플릿
- `generate_generic_content()`: 일반 콘텐츠 템플릿

각 함수를 수정하여 더 구체적이고 유용한 콘텐츠를 생성할 수 있습니다.
