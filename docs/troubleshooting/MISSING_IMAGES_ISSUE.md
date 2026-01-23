# 누락된 이미지 및 에러 해결 가이드

## 문제 요약

현재 포스트 `2026-01-15-Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_Security_Practical_Guide.md`에서 다음 문제가 발생하고 있습니다:

### 1. 누락된 다이어그램 이미지 (12개)

다음 이미지 파일들이 `/assets/images/diagrams/` 디렉토리에 없습니다:

1. `docker_core_components.png` - Docker 핵심 구성 요소
2. `vm_vs_container_comparison.png` - VM vs Container 비교
3. `container_isolation_mechanism.png` - 컨테이너 격리 메커니즘
4. `kubernetes_core_resources.png` - Kubernetes 핵심 리소스
5. `kubernetes_cluster_architecture.png` - Kubernetes 클러스터 아키텍처
6. `container_security_least_privilege.png` - 컨테이너 보안 최소 권한 원칙
7. `container_image_scanning_tools.png` - 컨테이너 이미지 스캔 도구
8. `kubernetes_security_context_concept.png` - Security Context 개념도
9. `pod_security_standards_levels.png` - Pod Security Standards 레벨
10. `network_policy_concept.png` - Network Policy 동작 원리
11. `rbac_structure.png` - RBAC 구조
12. `container_image_comparison.png` - 컨테이너 이미지 비교

### 2. WebP 이미지 404 에러 (정상 동작)

`image-optimizer.js`가 자동으로 WebP 형식을 시도하지만, 파일이 없어 404가 발생합니다.
이는 **정상 동작**이며, 자동으로 원본 PNG 형식으로 폴백됩니다.

**해결 방법**: 
- 이미지 생성 시 WebP 형식도 함께 생성하거나
- 현재처럼 원본 PNG만 사용해도 됩니다 (성능 최적화는 선택사항)

### 3. Favicon 누락

`/assets/images/favicon.png` 파일이 없습니다.

**해결 방법**:
```bash
python3 scripts/generate_favicon.py
```

### 4. Giscus API 404 에러

Giscus API가 404를 반환하는 경우:
- GitHub Discussions가 아직 생성되지 않았거나
- `term` 매핑이 올바르지 않을 수 있습니다

**해결 방법**:
- 첫 댓글 작성 시 자동으로 Discussion이 생성됩니다
- 또는 Giscus 설정에서 `strict: "0"`으로 설정되어 있어 정상 동작입니다

### 5. Mermaid.js 에러

Mermaid 다이어그램 렌더링 중 Promise rejection이 발생할 수 있습니다.

**해결 방법**:
- 이미 에러 핸들링이 개선되었습니다
- 다이어그램이 없는 경우 에러가 발생하지 않습니다

## 해결 단계

### 즉시 해결 가능한 항목

1. **Favicon 생성**:
   ```bash
   cd /Users/twodragon/Library/CloudStorage/GoogleDrive-twodragon114@gmail.com/내\ 드라이브/tech-blog
   python3 scripts/generate_favicon.py
   ```

2. **에러 필터링 개선** (완료):
   - WebP 404 에러 필터링 강화
   - Mermaid 에러 필터링 추가
   - 다이어그램 이미지 404 필터링 추가

### 다이어그램 이미지 생성 필요

다이어그램 이미지는 다음 방법 중 하나로 생성할 수 있습니다:

1. **수동 생성**: 
   - Draw.io, Excalidraw, Figma 등으로 다이어그램 생성
   - PNG 형식으로 저장하여 `/assets/images/diagrams/`에 배치

2. **자동 생성 스크립트 작성** (권장):
   - Python + PIL/Pillow로 다이어그램 생성
   - 또는 Gemini API를 사용한 이미지 생성 워크플로우 활용

3. **임시 해결**:
   - 이미지 참조를 주석 처리하거나
   - 대체 텍스트로 설명 추가

## 권장 작업 순서

1. ✅ 에러 필터링 개선 (완료)
2. ⏳ Favicon 생성
3. ⏳ 다이어그램 이미지 생성 (12개)
4. ⏳ WebP 변환 (선택사항, 성능 최적화)

## 참고

- WebP 404 에러는 정상 동작이며, 원본 이미지로 자동 폴백됩니다
- Giscus 404는 첫 댓글 작성 시 자동으로 해결됩니다
- Mermaid 에러는 이미 핸들링이 개선되었습니다
