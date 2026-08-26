"""지역 코드 단일 정의.

여기가 지역에 관한 유일한 원본입니다. 지역을 추가·수정할 때 고칠 곳은
아래 REGIONS 하나이며, 나머지는 전부 여기서 파생됩니다.

  - members.models.REGION_CHOICES      (드롭다운 · 모델 choices)
  - rag.management.commands.seed_docs  (문서 제목 → region)
  - rag.service._extract_region        (파일명 → region)
  - members.guides.GUIDE_DATA          (가이드 페이지 슬러그)
  - templates/home.html                (지역 카드)

── 통합 전에 있던 문제 ──────────────────────────────────────
매핑이 세 벌로 흩어져 있었고 내용이 서로 달랐습니다. 특히
rag/service.py 에만 있던 "부산" → busan_namgu 별칭 때문에,
부산의 다른 구를 추가하면 그 문서가 남구 문서로 조용히 오태깅됩니다.
(에러도 경고도 나지 않습니다.)

원인은 부분 문자열 매칭입니다. 짧은 키가 먼저 걸리면 상위 지역명이
하위 지역을 먹습니다. 그래서 이 모듈은 **긴 별칭부터** 매칭합니다.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────
# 지역 정의 — 지역을 추가할 때 고치는 곳은 여기뿐입니다.
#
#   code    : DB 에 저장되는 값. REGION_CHOICES 의 첫 항목.
#   label   : 드롭다운·화면에 보이는 이름.
#   slug    : 가이드 페이지 URL 조각 ("region-" 뒤에 붙는 부분).
#   aliases : 문서 제목·파일명에서 이 지역을 찾아낼 키워드.
#             제목 표기와 파일명 표기가 다르면 둘 다 넣어야 합니다.
#             예) 제목 "[부산 남구]" / 파일명 "..._부산남구_..."
#
# ⚠️ aliases 에 상위 지역명(“부산”, “인천”, “서울”)만 단독으로 넣지 마십시오.
#    같은 광역 안에 다른 기초단체를 추가하는 순간 오태깅이 발생합니다.
# ─────────────────────────────────────────────────────────────
REGIONS: list[dict] = [
    {
        "code": "seoul",
        "label": "서울",
        "slug": "seoul",
        "aliases": ["서울특별시", "서울시", "서울"],
    },
    {
        "code": "cheonan",
        "label": "천안",
        "slug": "cheonan",
        "aliases": ["천안시", "천안"],
    },
    {
        "code": "busan_namgu",
        "label": "부산 남구",
        "slug": "busan",
        "aliases": ["부산광역시 남구", "부산 남구", "부산남구"],
    },
    {
        "code": "incheon_michuhol",
        "label": "인천 미추홀구",
        "slug": "incheon",
        "aliases": ["인천광역시 미추홀구", "인천 미추홀구", "인천미추홀구", "미추홀"],
    },
    {
        "code": "sejong",
        "label": "세종",
        "slug": "sejong",
        "aliases": ["세종특별자치시", "세종시", "세종"],
    },
    {
        "code": "jeju",
        "label": "제주",
        "slug": "jeju",
        "aliases": ["제주특별자치도", "제주도", "제주"],
    },
]

COMMON_CODE = "common"
COMMON_LABEL = "전국 공통"


# ── 파생물 ───────────────────────────────────────────────────

REGION_CHOICES: list[tuple[str, str]] = [(COMMON_CODE, COMMON_LABEL)] + [
    (r["code"], r["label"]) for r in REGIONS
]

REGION_CODES: tuple[str, ...] = tuple(r["code"] for r in REGIONS)

GUIDE_SLUGS: dict[str, str] = {r["code"]: f"region-{r['slug']}" for r in REGIONS}

# 긴 별칭 우선. 같은 길이면 정의 순서를 유지한다.
_ALIAS_TABLE: tuple[tuple[str, str], ...] = tuple(
    sorted(
        ((alias, r["code"]) for r in REGIONS for alias in r["aliases"]),
        key=lambda pair: -len(pair[0]),
    )
)


def resolve_region(text: str) -> str | None:
    """문서 제목이나 파일명에서 지역 코드를 찾는다.

    찾지 못하면 None 을 돌려준다. 호출하는 쪽이 상황에 맞게
    None 또는 "common" 으로 해석한다.

        >>> resolve_region("[부산 남구] 분리배출 가이드")
        'busan_namgu'
        >>> resolve_region("[가이드]_인천미추홀구_분리배출_요령")
        'incheon_michuhol'
        >>> resolve_region("[공통] 음식물쓰레기 구분 기준")

    """
    if not text:
        return None
    for alias, code in _ALIAS_TABLE:
        if alias in text:
            return code
    return None


def region_label(code: str | None) -> str:
    """지역 코드를 화면용 이름으로 바꾼다."""
    if not code or code == COMMON_CODE:
        return COMMON_LABEL
    for r in REGIONS:
        if r["code"] == code:
            return r["label"]
    return code
