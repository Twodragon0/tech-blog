#!/bin/bash
# 새 포스트 자동 공유 스크립트
# _posts 디렉토리에서 최근 생성/수정된 포스트를 찾아 LinkedIn에 공유

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# 공유 기록 파일 (중복 공유 방지)
SHARED_LOG="$PROJECT_ROOT/.shared_posts.log"
touch "$SHARED_LOG"

# 최근 24시간 내에 생성/수정된 포스트 찾기
RECENT_POSTS=$(find "$PROJECT_ROOT/_posts" -name "*.md" -type f -mtime -1 2>/dev/null | sort -r)

if [ -z "$RECENT_POSTS" ]; then
    echo "최근 24시간 내 새 포스트가 없습니다."
    exit 0
fi

echo "=========================================="
echo "새 포스트 자동 공유"
echo "=========================================="
echo ""

for post_file in $RECENT_POSTS; do
    # 파일명으로 공유 여부 확인
    post_basename=$(basename "$post_file")
    
    if grep -q "^$post_basename$" "$SHARED_LOG" 2>/dev/null; then
        echo "⏭️  이미 공유됨: $post_basename"
        continue
    fi
    
    echo "📝 공유 중: $post_basename"
    
    # Python 스크립트 실행
    if python3 "$PROJECT_ROOT/scripts/share_sns.py" "$post_file"; then
        # 공유 성공 시 로그에 기록
        echo "$post_basename" >> "$SHARED_LOG"
        echo "✅ 공유 완료: $post_basename"
    else
        echo "❌ 공유 실패: $post_basename"
    fi
    
    echo ""
done

echo "=========================================="
echo "자동 공유 완료"
echo "=========================================="
