#!/usr/bin/env python3
"""
오디오 생성 상태 확인 스크립트
"""

from pathlib import Path

OUTPUT_DIR = Path("output")

improved_scripts = sorted(OUTPUT_DIR.glob("*_improved.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
generated_audios = list(OUTPUT_DIR.glob("*_audio_improved.mp3"))

completed = []
missing = []

for script in improved_scripts:
    base = script.stem.replace("_improved", "").replace("_script", "")
    audio = OUTPUT_DIR / f"{base}_audio_improved.mp3"
    
    if audio.exists():
        size = audio.stat().st_size
        completed.append({
            "script": script.name,
            "audio": audio.name,
            "size": size
        })
    else:
        missing.append(script.name)

print("=" * 60)
print("📊 오디오 생성 상태")
print("=" * 60)
print(f"\n총 개선된 대본: {len(improved_scripts)}개")
print(f"✅ 생성 완료: {len(completed)}개")
print(f"⏳ 생성 필요: {len(missing)}개")

if completed:
    print(f"\n✅ 생성된 오디오:")
    for item in completed[:10]:
        print(f"   - {item['audio']} ({item['size'] / 1024:.1f} KB)")

if missing:
    print(f"\n⏳ 생성 필요한 대본:")
    for name in missing[:10]:
        print(f"   - {name}")
    if len(missing) > 10:
        print(f"   ... 외 {len(missing) - 10}개")

print(f"\n💡 생성 명령:")
if missing:
    print(f"   python scripts/generate_audio_batch.py")
    print(f"   또는")
    print(f"   python scripts/generate_audio_from_improved_split.py output/{missing[0]}")
