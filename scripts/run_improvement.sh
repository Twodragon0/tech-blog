#!/bin/bash
# 포스팅 개선 스크립트 실행

cd "$(dirname "$0")/.."
python3 scripts/continuous_improve_posts.py
