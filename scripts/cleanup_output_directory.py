#!/usr/bin/env python3
"""
output 디렉토리 정리 스크립트
- 중복 파일 제거 (_improved_improved.txt 등)
- 오래된 임시 파일 정리
- 파일 크기 분석
"""

from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path("output")
DRY_RUN = True  # 실제 삭제 전에 미리보기


def analyze_output_directory():
    """output 디렉토리 분석"""
    files_by_type = defaultdict(list)
    total_size = 0

    if not OUTPUT_DIR.exists():
        print(f"❌ {OUTPUT_DIR} 디렉토리가 존재하지 않습니다.")
        return

    for file_path in OUTPUT_DIR.rglob("*"):
        if file_path.is_file():
            size = file_path.stat().st_size
            total_size += size
            ext = file_path.suffix.lower()

            files_by_type[ext].append(
                {
                    "path": file_path,
                    "size": size,
                    "mtime": datetime.fromtimestamp(file_path.stat().st_mtime),
                }
            )

    print("=" * 70)
    print("📊 output 디렉토리 분석 결과")
    print("=" * 70)
    print(f"\n총 파일 수: {sum(len(files) for files in files_by_type.values())}개")
    print(f"총 크기: {total_size / 1024 / 1024:.2f} MB")

    print("\n📁 파일 타입별 통계:")
    for ext, files in sorted(
        files_by_type.items(), key=lambda x: len(x[1]), reverse=True
    ):
        total_type_size = sum(f["size"] for f in files)
        print(
            f"  {ext or '(확장자 없음)':15} {len(files):4}개  {total_type_size / 1024 / 1024:7.2f} MB"
        )

    return files_by_type, total_size


def find_duplicate_files(files_by_type):
    """중복 파일 찾기"""
    duplicates = []

    # _improved_improved.txt 파일 찾기
    improved_improved = [
        f
        for f in files_by_type.get(".txt", [])
        if "_improved_improved" in f["path"].name
    ]

    if improved_improved:
        print("\n🔄 중복 파일 발견:")
        print(f"  _improved_improved.txt: {len(improved_improved)}개")
        duplicates.extend(improved_improved)

    # 같은 베이스명의 여러 버전 파일 찾기
    base_files = defaultdict(list)
    for ext, files in files_by_type.items():
        for file_info in files:
            name = file_info["path"].stem
            # 베이스명 추출 (버전 제거)
            base = (
                name.replace("_improved_improved", "")
                .replace("_improved", "")
                .replace("_script", "")
            )
            base_files[base].append((ext, file_info))

    # 여러 버전이 있는 파일 찾기
    multi_version = {
        base: files for base, files in base_files.items() if len(files) > 1
    }

    if multi_version:
        print("\n📦 여러 버전 파일:")
        for base, versions in list(multi_version.items())[:10]:
            print(f"  {base}:")
            for ext, file_info in versions:
                print(
                    f"    - {file_info['path'].name} ({file_info['size'] / 1024:.1f} KB)"
                )

    return duplicates, multi_version


def find_old_files(files_by_type, days=90):
    """오래된 파일 찾기"""
    cutoff_date = datetime.now() - timedelta(days=days)
    old_files = []

    for files in files_by_type.values():
        for file_info in files:
            if file_info["mtime"] < cutoff_date:
                old_files.append(file_info)

    if old_files:
        print(f"\n⏰ {days}일 이상 된 파일: {len(old_files)}개")
        for file_info in sorted(old_files, key=lambda x: x["mtime"])[:10]:
            age_days = (datetime.now() - file_info["mtime"]).days
            print(
                f"  - {file_info['path'].name} ({age_days}일 전, {file_info['size'] / 1024:.1f} KB)"
            )

    return old_files


def cleanup_files(duplicates, old_files, dry_run=True):
    """파일 정리"""
    to_delete = []

    # 중복 파일 삭제 대상
    for file_info in duplicates:
        to_delete.append(file_info["path"])

    # 오래된 임시 파일 삭제 대상 (90일 이상)
    for file_info in old_files:
        # 중요한 파일은 제외
        if file_info["path"].name.endswith("_audio_improved.mp3"):
            continue  # 오디오 파일은 보존
        if ".audio_generation_progress.json" in file_info["path"].name:
            continue  # 진행 상태 파일은 보존
        to_delete.append(file_info["path"])

    if not to_delete:
        print("\n✅ 삭제할 파일이 없습니다.")
        return

    total_size = sum(f.stat().st_size for f in to_delete)
    print(
        f"\n🗑️  삭제 대상: {len(to_delete)}개 파일 ({total_size / 1024 / 1024:.2f} MB)"
    )

    if dry_run:
        print("\n⚠️  DRY RUN 모드 - 실제로 삭제하지 않습니다.")
        print("\n삭제될 파일 목록:")
        for file_path in to_delete[:20]:
            print(f"  - {file_path.name}")
        if len(to_delete) > 20:
            print(f"  ... 외 {len(to_delete) - 20}개")
        print("\n💡 실제 삭제하려면 DRY_RUN = False로 설정하세요.")
    else:
        print("\n⚠️  실제 삭제를 진행합니다...")
        deleted = 0
        for file_path in to_delete:
            try:
                file_path.unlink()
                deleted += 1
            except Exception as e:
                print(f"  ❌ {file_path.name} 삭제 실패: {e}")
        print(f"✅ {deleted}개 파일 삭제 완료")


def main():
    """메인 함수"""
    print("🧹 output 디렉토리 정리 시작\n")

    # 디렉토리 분석
    files_by_type, total_size = analyze_output_directory()

    if not files_by_type:
        return

    # 중복 파일 찾기
    duplicates, multi_version = find_duplicate_files(files_by_type)

    # 오래된 파일 찾기
    old_files = find_old_files(files_by_type, days=90)

    # 파일 정리
    cleanup_files(duplicates, old_files, dry_run=DRY_RUN)

    print("\n" + "=" * 70)
    print("✅ 정리 완료")
    print("=" * 70)


if __name__ == "__main__":
    main()
