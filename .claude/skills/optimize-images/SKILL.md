---
name: optimize-images
description: 이미지 최적화 및 정리
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash, Read, Glob, Grep
---

블로그 이미지를 최적화합니다.

1. 한국어 파일명 탐지 및 변환: `python3 scripts/rename_images_to_english.py --yes`
2. 누락된 포스트 이미지 생성: `python3 scripts/generate_post_images.py --all`
3. SVG 파일 검증:
   - 한국어 텍스트 포함 여부 확인
   - UTF-8 인코딩 확인
   - 특수문자 확인 (허용 안됨)
4. 미사용 이미지 탐지:
   - assets/images/ 파일 중 _posts/에서 참조되지 않는 것 리스트
5. 이미지 크기 확인: 과도하게 큰 파일 경고
