# 광고 최적화 가이드 (CLS 방지)

## 개요

Google AdSense 광고가 동적으로 삽입될 때 발생하는 레이아웃 시프트(CLS)를 방지하기 위한 가이드입니다.

## 자동 최적화

`ad-optimizer.js` 스크립트가 자동으로 모든 광고를 `.ad-container`로 감싸서 CLS를 방지합니다.

## 수동 광고 배치 (권장)

광고를 수동으로 배치할 때는 `.ad-container` 클래스를 사용하세요:

### 예시 1: 기본 광고

```html
<div class="ad-container">
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="ca-pub-XXXXXXXXXX"
       data-ad-slot="1234567890"
       data-ad-format="auto"></ins>
  <script>
    (adsbygoogle = window.adsbygoogle || []).push({});
  </script>
</div>
```

### 예시 2: 사이드바 광고 (세로형)

```html
<aside class="sidebar">
  <div class="sidebar-section">
    <div class="ad-container" style="min-height: 600px;">
      <ins class="adsbygoogle"
           style="display:block"
           data-ad-client="ca-pub-XXXXXXXXXX"
           data-ad-slot="1234567890"
           data-ad-format="vertical"></ins>
      <script>
        (adsbygoogle = window.adsbygoogle || []).push({});
      </script>
    </div>
  </div>
</aside>
```

### 예시 3: 본문 중간 광고 (가로형)

```html
<article class="post-content">
  <p>본문 내용...</p>
  
  <div class="ad-container" style="min-height: 90px;">
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-XXXXXXXXXX"
         data-ad-slot="1234567890"
         data-ad-format="horizontal"></ins>
    <script>
      (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
  </div>
  
  <p>계속되는 본문...</p>
</article>
```

## 광고 타입별 권장 높이

| 광고 타입 | 권장 min-height | 설명 |
|---------|----------------|------|
| 가로형 (Banner) | 90px | 728x90, 970x90 |
| 중형 (Rectangle) | 250px | 300x250 |
| 세로형 (Vertical) | 600px | 300x600, 160x600 |
| 자동 (Auto) | 250px | 기본값 |

## CSS 스타일

`.ad-container`는 이미 최적화된 스타일이 적용되어 있습니다:

- 최소 높이 설정으로 공간 확보
- 레이아웃 안정화 (`contain` 속성)
- 광고 로드 전 플레이스홀더

## 성능 모니터링

개발 환경(`localhost`)에서 콘솔을 확인하면 CLS 값과 광고 관련 레이아웃 시프트를 추적할 수 있습니다:

```
[Performance] CLS is high: 0.123456 | 원인: 광고: adsbygoogle
```

## 추가 최적화 팁

1. **광고 위치**: 본문 중간보다는 사이드바나 상단/하단에 배치
2. **광고 개수**: 페이지당 광고 개수를 제한 (3-4개 권장)
3. **로딩 지연**: 중요 콘텐츠 로드 후 광고 로드 (`requestIdleCallback` 사용)

## 문제 해결

### 광고가 여전히 CLS를 유발하는 경우

1. `.ad-container`로 감싸져 있는지 확인
2. `min-height`가 적절히 설정되어 있는지 확인
3. 브라우저 개발자 도구에서 레이아웃 시프트 원인 확인

### 광고가 표시되지 않는 경우

1. AdSense 계정 상태 확인
2. 광고 단위 ID 확인
3. CSP 설정 확인 (`head.html`의 Content-Security-Policy)
