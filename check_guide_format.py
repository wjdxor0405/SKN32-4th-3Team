#!/usr/bin/env python3
"""data/guide 파일의 형식을 검사한다.

    python check_guide_format.py                 # 기본 경로(data/guide) 검사
    python check_guide_format.py path/to/guide   # 경로 지정

여기서 잡는 것은 "조용히 실패하는" 문제들이다.
seed_docs 는 형식이 어긋나도 에러를 내지 않고 그냥 적재하기 때문에,
제목이 파일명으로 떨어지거나 지역 필터가 빗나가도 눈치채기 어렵다.

검사 항목
  1. 첫 줄이 "[지역명] …" 형태인가        → 아니면 제목이 파일명으로 떨어진다
  2. 제목 길이가 80자 이하인가            → 넘으면 _extract_title 이 파일명을 쓴다
  3. '출처:' / '지역:' 헤더가 있는가
  4. 제목에서 뽑은 region 과 '지역:' 값이 같은가
  5. 파일명(stem)에서 뽑은 region 도 같은가  → RAG_SOURCE=files 모드는 파일명을 본다
  6. === 섹션 === 과 [블록] 이 하나 이상 있는가  → 청킹 단위
  7. 〔확인: …〕 같은 초안 표시가 남아 있지 않은가
  8. '작성 기준일' 이 출처 줄에 있는가 (경고)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# 지역 매핑은 members/regions.py 한 곳에서만 가져온다.
# (이 스크립트가 자체 사본을 들고 있으면, 지역을 추가할 때마다
#  여기까지 고쳐야 하고 잊으면 멀쩡한 파일이 FAIL 로 잡힌다.)
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

try:
    from members.regions import COMMON_CODE, resolve_region
except ImportError:  # pragma: no cover
    print("members/regions.py 를 찾을 수 없습니다. 프로젝트 루트에서 실행하십시오.")
    raise SystemExit(2)


SECTION = re.compile(r"^\s*=+\s*(.+?)\s*=+\s*$", re.M)
ITEM = re.compile(r"^\s*\[(.+)\]\s*$", re.M)
PLACEHOLDER = re.compile(r"〔확인|여기부터 복사|※ 초안")


def region_of(text: str) -> str | None:
    return resolve_region(text)


def first_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def check(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ([f"UTF-8 로 읽히지 않습니다 (cp949 저장 의심)"], [])

    title = first_line(text)

    # 1·2. 제목
    if not title.startswith("["):
        errors.append(f'첫 줄이 "[" 로 시작하지 않습니다 → 제목이 파일명으로 대체됩니다: {title[:40]!r}')
    elif len(title) > 80:
        errors.append(f"제목이 {len(title)}자입니다 (80자 초과) → 제목이 파일명으로 대체됩니다")

    # 3. 헤더
    source_line = next((l for l in text.splitlines() if l.startswith("출처:")), None)
    region_line = next((l for l in text.splitlines() if l.startswith("지역:")), None)
    if source_line is None:
        errors.append("'출처:' 줄이 없습니다")
    if region_line is None:
        errors.append("'지역:' 줄이 없습니다")

    # 4·5. 지역 코드 3중 일치
    declared = region_line.split(":", 1)[1].strip() if region_line else None
    from_title = region_of(title) or COMMON_CODE
    from_stem = region_of(path.stem) or COMMON_CODE

    if declared and declared != from_title:
        errors.append(
            f"제목이 가리키는 지역과 '지역:' 값이 다릅니다 "
            f"(제목→{from_title} / 지역:{declared}) → 지역 필터가 빗나갑니다"
        )
    if declared and declared != from_stem:
        errors.append(
            f"파일명이 가리키는 지역과 '지역:' 값이 다릅니다 "
            f"(파일명→{from_stem} / 지역:{declared}) → files 모드에서 필터가 빗나갑니다"
        )

    # 6. 청킹 단위
    sections = SECTION.findall(text)
    items = ITEM.findall(text)
    if not sections:
        errors.append("'=== 섹션 ===' 이 하나도 없습니다 → 문자 단위로 잘립니다")
    if not items:
        warnings.append("'[블록]' 이 하나도 없습니다 → 청크가 커질 수 있습니다")

    # 7. 초안 표시
    if PLACEHOLDER.search(text):
        errors.append("초안 표시(〔확인: …〕 등)가 남아 있습니다 → 그대로 색인됩니다")

    # 8. 기준일
    if source_line and "기준일" not in source_line:
        warnings.append("출처 줄에 '작성 기준일' 이 없습니다 (요일·수수료는 자주 바뀝니다)")

    return errors, warnings


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/guide")
    if not target.is_dir():
        print(f"폴더를 찾을 수 없습니다: {target}")
        return 2

    files = sorted(p for p in target.iterdir() if p.suffix.lower() in {".txt", ".md"})
    if not files:
        print(f"검사할 파일이 없습니다: {target}")
        return 2

    total_err = total_warn = 0
    for path in files:
        errors, warnings = check(path)
        total_err += len(errors)
        total_warn += len(warnings)

        if not errors and not warnings:
            print(f"  OK   {path.name}")
            continue

        print(f"  {'FAIL' if errors else 'WARN'} {path.name}")
        for e in errors:
            print(f"         [오류] {e}")
        for w in warnings:
            print(f"         [경고] {w}")

    print(f"\n파일 {len(files)}개 · 오류 {total_err}건 · 경고 {total_warn}건")
    return 1 if total_err else 0


if __name__ == "__main__":
    raise SystemExit(main())
