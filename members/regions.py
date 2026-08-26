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
# ⚠️ 지역을 추가하기 전에 반드시 현재 행정구역 상태를 확인하십시오.
#
# 2026년에 광역 행정통합이 실제로 일어났습니다. 코드에 지역을 넣기
# 전에 그 행정구역이 아직 존재하는지 검색으로 확인하는 것이 원칙입니다.
# 폐지된 행정구역 기준으로 답하는 챗봇은 틀린 답보다 나쁩니다.
#
#   확인 시점: 2026-08-26
#
#   ✗ 광주광역시 — 폐지됨. 2026-07-01 전라남도와 통합되어
#     "전남광주통합특별시"(약칭 광주특별시) 출범. 광주 5개 구와
#     전남 22개 시군이 단일 광역단체가 되었습니다. 도심과 농어촌이
#     한 코드로 묶여 단일 배출 체계가 성립하지 않고, 출범 두 달째라
#     구청 사이트조차 표기가 엇갈립니다. 그래서 추가하지 않았습니다.
#
#   ○ 대전광역시 — 존속. 충남대전 통합은 2026-02-24 법사위에서
#     보류되었고 이후 멈춘 상태입니다. 다만 재점화 가능성이 거론되므로
#     주기적으로 확인이 필요합니다.
#
#   ○ 대구광역시 — 존속. 대구경북 통합도 같은 날 함께 보류되었습니다.
#     (다만 evals/qa_set.json 의 q027 이 "대구 수성구 = 자료 없음" 을
#      정답으로 쓰므로, 추가하려면 그 문항을 교체해야 합니다.)
#
#   ○ 수원시 — 존속. 경기도 분도는 성사되지 않았고, 추진안대로
#     한강 이남은 '경기도'로 그대로 남으므로 수원은 영향이 없습니다.
#
# ─────────────────────────────────────────────────────────────
# 지역 정의 — 지역을 추가할 때 고치는 곳은 여기뿐입니다.
#
#   code    : DB 에 저장되는 값. REGION_CHOICES 의 첫 항목.
#   label   : 드롭다운·화면에 보이는 이름.
#   color   : 랜딩 화면 지역 카드의 점 색상.
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
        "color": "#2D8B4E",
        "label": "서울",
        "slug": "seoul",
        "aliases": ["서울특별시", "서울시", "서울"],
    },
    {
        "code": "cheonan",
        "color": "#3B7DD8",
        "label": "천안",
        "slug": "cheonan",
        "aliases": ["천안시", "천안"],
    },
    {
        "code": "busan_namgu",
        "color": "#D4890B",
        "label": "부산 남구",
        "slug": "busan",
        "aliases": ["부산광역시 남구", "부산 남구", "부산남구"],
    },
    {
        "code": "incheon_michuhol",
        "color": "#7B2D8B",
        "label": "인천 미추홀구",
        "slug": "incheon",
        "aliases": ["인천광역시 미추홀구", "인천 미추홀구", "인천미추홀구", "미추홀"],
    },
    {
        "code": "sejong",
        "color": "#D44B0B",
        "label": "세종",
        "slug": "sejong",
        "aliases": ["세종특별자치시", "세종시", "세종"],
    },
    {
        "code": "daejeon",
        "color": "#1B9AAA",
        "label": "대전",
        "slug": "daejeon",
        "aliases": ["대전광역시", "대전시", "대전"],
    },
    {
        "code": "ulsan",
        "color": "#8B5A2D",
        "label": "울산",
        "slug": "ulsan",
        "aliases": ["울산광역시", "울산시", "울산"],
    },
    {
        "code": "suwon",
        "color": "#8B2D5A",
        "label": "수원",
        "slug": "suwon",
        "aliases": ["수원특례시", "수원시", "수원"],
    },
    {
        "code": "jeju",
        "color": "#0B8BD4",
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


def region_cards() -> list[dict]:
    """랜딩 화면 지역 카드용 데이터. templates/home.html 이 반복한다.

    display 는 카드에 보이는 이름으로, label 보다 격식 있는 표기를 쓴다.
    """
    formal = {
        "seoul": "서울특별시",
        "cheonan": "천안시",
        "busan_namgu": "부산 남구",
        "incheon_michuhol": "인천 미추홀구",
        "sejong": "세종시",
        "daejeon": "대전광역시",
        "ulsan": "울산광역시",
        "suwon": "수원특례시",
        "jeju": "제주도",
    }
    return [
        {
            "code": r["code"],
            "display": formal.get(r["code"], r["label"]),
            "color": r["color"],
            "slug_url": GUIDE_SLUGS[r["code"]],
        }
        for r in REGIONS
    ]


def check_alias_collisions() -> list[str]:
    """별칭이 다른 지역의 별칭에 포함되는지 검사한다.

    지역을 여러 개 한꺼번에 추가할 때 쓴다. 예를 들어 "부산" 과
    "부산 남구" 처럼 한쪽이 다른 쪽의 부분 문자열이면, 짧은 쪽이 먼저
    걸릴 때 오태깅이 난다. 이 모듈은 긴 별칭부터 매칭하므로 대부분
    안전하지만, 사람이 의도를 확인해 두는 편이 낫다.

    문제가 없으면 빈 리스트를 돌려준다.
    """
    warnings: list[str] = []
    entries = [(alias, r["code"]) for r in REGIONS for alias in r["aliases"]]
    for alias, code in entries:
        for other, other_code in entries:
            if code == other_code or alias == other:
                continue
            if alias in other:
                warnings.append(
                    f'"{alias}"({code}) 가 "{other}"({other_code}) 안에 들어 있습니다 — '
                    f'긴 별칭이 먼저 매칭되므로 현재는 안전하지만 확인하십시오.'
                )
    return warnings
