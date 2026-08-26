#!/usr/bin/env python3
"""REGION_MAP 통합 회귀 검증.

    python verify_regions.py

통합 전 세 벌의 매핑이 내던 결과와, 통합 후 members/regions.py 가 내는
결과를 대조한다. **기존 문서의 태깅은 단 하나도 바뀌면 안 된다.**

추가로, 통합의 목적이었던 "상위 지역명이 하위 지역을 먹는" 문제가
실제로 해소됐는지 확인한다.

Django 없이 단독 실행된다 (regions.py 는 순수 파이썬).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from members.regions import COMMON_CODE, resolve_region  # noqa: E402

# ── 통합 전 매핑 (원본 그대로 박제) ──────────────────────────
LEGACY_TITLE_MAP = {  # seed_docs.REGION_MAP
    "서울": "seoul",
    "천안": "cheonan",
    "부산 남구": "busan_namgu",
    "부산남구": "busan_namgu",
    "세종": "sejong",
    "인천 미추홀구": "incheon_michuhol",
    "인천미추홀구": "incheon_michuhol",
    "미추홀": "incheon_michuhol",
    "제주": "jeju",
}
LEGACY_FILE_MAP = {  # rag.service._extract_region
    "서울": "seoul",
    "천안": "cheonan",
    "부산남구": "busan_namgu",
    "부산": "busan_namgu",
    "세종": "sejong",
    "인천미추홀구": "incheon_michuhol",
    "미추홀": "incheon_michuhol",
    "제주": "jeju",
    "공통": "common",
    "환경부": "common",
}


def legacy(mapping: dict, text: str, fallback):
    for keyword, code in mapping.items():
        if keyword in text:
            return code
    return fallback


def first_line(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            return line.strip()
    return ""


def main() -> int:
    guide_dir = ROOT / "data" / "guide"
    if not guide_dir.is_dir():
        guide_dir = Path("data/guide")
    if not guide_dir.is_dir():
        print(f"data/guide 를 찾을 수 없습니다. 프로젝트 루트에서 실행하십시오.")
        return 2

    files = sorted(guide_dir.glob("*.txt"))
    print(f"■ 회귀 검증 — 기존 가이드 {len(files)}개의 태깅이 그대로인가\n")
    print(f"  {'파일':38s} {'제목기준':>18s} {'파일명기준':>18s}")
    print("  " + "-" * 76)

    failures = 0
    for path in files:
        title = first_line(path)
        stem = path.stem

        # 제목 기준 (seed_docs)
        before_t = legacy(LEGACY_TITLE_MAP, title, None)
        after_t = resolve_region(title)
        ok_t = before_t == after_t

        # 파일명 기준 (rag.service)
        before_f = legacy(LEGACY_FILE_MAP, stem, "common")
        after_f = resolve_region(stem) or COMMON_CODE
        ok_f = before_f == after_f

        if not (ok_t and ok_f):
            failures += 1
        mark_t = "OK" if ok_t else f"✗ {before_t}→{after_t}"
        mark_f = "OK" if ok_f else f"✗ {before_f}→{after_f}"
        print(f"  {path.name[:38]:38s} {mark_t:>18s} {mark_f:>18s}")

    print()
    if failures:
        print(f"  ✗ 태깅이 바뀐 파일 {failures}개 — 통합을 적용하면 안 됩니다.")
    else:
        print(f"  ✓ {len(files)}개 전부 통합 전과 동일합니다.")

    # ── 통합의 목적: 하위 지역 오태깅이 사라졌는가 ──────────
    print("\n■ 확장성 검증 — 같은 광역에 다른 기초단체를 추가하면\n")
    cases = [
        ("[부산 해운대구] 분리배출 가이드", "[가이드]_부산해운대구_분리배출_요령"),
        ("[인천 남동구] 분리배출 가이드", "[가이드]_인천남동구_분리배출_요령"),
        ("[서울 강남구] 분리배출 가이드", "[가이드]_서울강남구_분리배출_요령"),
    ]
    print(f"  {'가상 문서':26s} {'통합 전':>26s} {'통합 후':>18s}")
    print("  " + "-" * 74)
    fixed = 0
    for title, stem in cases:
        b_t = legacy(LEGACY_TITLE_MAP, title, None)
        b_f = legacy(LEGACY_FILE_MAP, stem, "common")
        a_t = resolve_region(title)
        a_f = resolve_region(stem) or COMMON_CODE
        before = f"{b_t} / {b_f}"
        after = f"{a_t} / {a_f}"
        # 통합 전에 잘못된 지역으로 붙었는지
        was_wrong = b_f not in (None, "common") or b_t not in (None, "common")
        now_clean = a_t is None and a_f == "common"
        if was_wrong and now_clean:
            fixed += 1
            note = "  ← 오태깅 해소"
        elif was_wrong:
            note = "  ← 여전히 오태깅"
        else:
            note = ""
        print(f"  {title[:26]:26s} {before:>26s} {after:>18s}{note}")

    print(f"\n  서울 강남구는 통합 후에도 seoul 로 붙습니다 — 별칭에 \"서울\" 이")
    print(f"  남아 있기 때문입니다. 서울을 자치구 단위로 쪼갤 때는")
    print(f"  regions.py 의 seoul aliases 에서 \"서울\" 을 빼고")
    print(f"  \"서울특별시\" 같은 더 긴 표기만 남겨야 합니다.")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
