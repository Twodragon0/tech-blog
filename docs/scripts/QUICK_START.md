# 🚀 빠른 시작 가이드

## AI 기반 포스팅 개선 (권장)

### 0단계: 의존성 설치

```bash
cd ~/Desktop/tech-blog
./scripts/install_dependencies.sh
```

또는:

```bash
pip3 install requests certifi
```

### 1단계: API 키 설정

```bash
cd ~/Desktop/tech-blog
./scripts/setup_ai_keys.sh
```

Claude API 키와 Gemini API 키를 입력하세요. (없어도 작동하지만 품질이 낮아집니다)

### 2단계: 즉시 실행 (1시간)

```bash
./scripts/run_ai_improvement.sh
```

### 3단계: 백그라운드 실행 (선택)

```bash
./scripts/start_ai_background.sh
```

### 4단계: 로그 확인

```bash
tail -f ai_improvement_log.txt
```

## 기본 템플릿 기반 개선

API 키 없이도 작동하는 기본 개선:

```bash
./scripts/run_1hour_improvement.sh
```

## 전체 가이드

- **AI 기반 개선**: [README_AI_IMPROVEMENT.md](README_AI_IMPROVEMENT.md)
- **기본 개선**: [README_IMPROVEMENT.md](README_IMPROVEMENT.md)
