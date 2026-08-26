# APPLY — 적용 안내

2026-08-26 · 1단계 데이터 심화 + REGION_MAP 통합 + 신규 지역 3곳

이 압축을 **리포지토리 루트에 그대로 풀면** 경로가 맞습니다.

---

## 0. 한눈에

| | 내용 |
|---|---|
| 지역 | 6개 → **9개** (대전·울산·수원 추가) |
| 지역 청크 | 119 → **165** (39% 증가) |
| 지역 코드 매핑 | 세 벌 → **한 벌** (`members/regions.py`) |
| 지역 추가 시 손댈 곳 | 5곳 → **2곳** |
| 검증 | 회귀 0건 · 별칭 충돌 0건 · 형식 오류 0건 |

**마이그레이션이 필요합니다.** `REGION_CHOICES` 에 지역 3개가 늘었습니다.

---

## 1. 파일

### 새로 생기는 파일

| 경로 | 용도 |
|---|---|
| `members/regions.py` | **지역 정의 단일 원본.** 지역 추가는 여기만 고칩니다 |
| `verify_regions.py` | 지역 매핑 회귀 + 별칭 충돌 검증 |
| `check_guide_format.py` | 가이드 파일 형식 검사 |
| `data/guide/[가이드]_대전시_…` | 신규 |
| `data/guide/[가이드]_울산시_…` | 신규 |
| `data/guide/[가이드]_수원시_…` | 신규 |
| `docs/` 5개 문서 | 완료 보고 · 수집 체크리스트 · 2단계 계획 · RUN.md 수정안 · 행정구역 확인 기록 |

### 덮어쓰는 파일

| 경로 | 무엇이 바뀌나 |
|---|---|
| `members/models.py` | `REGION_CHOICES` 하드코딩 → `regions.py` 재수출 |
| `members/views.py` | `HomeView` 가 지역 카드를 동적으로 전달 |
| `templates/home.html` | 지역 카드 6개 하드코딩 → 반복문 |
| `rag/service.py` | `_extract_region()` 자체 표 제거 (**`"부산"` 별칭 삭제**) |
| `rag/management/commands/seed_docs.py` | 자체 `REGION_MAP` 제거 |
| `data/guide/` 지역 6개 | 1단계 데이터 심화 결과 |

공통 가이드 9개는 수정하지 않아 넣지 않았습니다.

---

## 2. 적용

```bat
:: 압축을 리포 루트에 풀고
python verify_regions.py
python check_guide_format.py data\guide
```

기대 결과

```
✓ 기존 15개 전부 통합 전과 동일합니다. (신규 지역 3개는 정상)
✓ 서로 겹치는 별칭이 없습니다.
파일 18개 · 오류 0건 · 경고 1건
```

경고 1건은 환경부 공통 파일의 작성 기준일 누락입니다 (원 작성자만 채울 수 있음).

```bat
python manage.py makemigrations members chat boards rag
python manage.py migrate
```

`REGION_CHOICES` 를 공유하는 필드가 **4개 앱 5개**입니다.

| 앱 | 모델 · 필드 | 생기는 파일 |
|---|---|---|
| members | `Member.region` | `members/migrations/0002_….py` |
| chat | `ChatSession.region`, `ChatLog.region` | `chat/migrations/0003_….py` |
| boards | `Board.region` | `boards/migrations/0003_….py` |
| rag | `Document.region` | `rag/migrations/0002_….py` |

파일명 뒷부분은 Django 가 작업 내용으로 자동 생성합니다
(예: `0002_alter_member_region.py`). chat 은 필드가 둘이라 이름이 길어집니다.
`dashboard` 는 `REGION_CHOICES` 를 쓰지만 모델 필드가 없어 마이그레이션이 없습니다.

내용은 전부 `AlterField` 하나이며, `choices` 목록에 세 줄이 추가되는 것뿐입니다.
**`migrate` 는 실제 스키마를 바꾸지 않습니다** — `choices` 는 Django 레벨의
검증 규칙이라 컬럼 정의(`varchar(50)`)가 그대로입니다. 기존 회원·게시글·대화
기록의 `region` 값도 손실 없이 유지됩니다.

**마이그레이션 파일 4개는 반드시 커밋에 포함하십시오.** 올리지 않으면 팀원이
각자 `makemigrations` 를 돌리게 되고, 같은 내용이 사람마다 다른 이름으로 생겨
충돌합니다. **한 사람이 만들어 푸시하고 나머지는 pull 후 `migrate` 만** 돌리는
것이 안전합니다.

앱을 빠뜨리면 팀원마다 마이그레이션 상태가 갈립니다.

```bat
:: RAG_SOURCE 에 맞는 것 하나만
python manage.py rag_reindex              :: RAG_SOURCE=files
python manage.py seed_docs --reindex      :: RAG_SOURCE=db
```

적재 로그에서 `(지역: daejeon)`, `(지역: ulsan)`, `(지역: suwon)` 이 찍히는지 확인합니다.

---

## 3. 되돌리기

```bat
git checkout members/ rag/ templates/ data/guide/
del members\regions.py verify_regions.py check_guide_format.py
del data\guide\[가이드]_대전시_분리배출_요령.txt
del data\guide\[가이드]_울산시_분리배출_요령.txt
del data\guide\[가이드]_수원시_분리배출_요령.txt
rmdir /s /q docs
python manage.py makemigrations members chat boards rag
python manage.py migrate
```

**브랜치를 따서 작업하시는 편이 낫습니다.** 마이그레이션이 끼면 되돌리기가
번거롭습니다. 브랜치째 버리는 것이 가장 깔끔합니다.

---

## 4. 아직 안 된 것 — 반드시 읽으십시오

### 신규 3개 지역은 랜딩 카드에 안 나옵니다 (의도한 동작)

`members/guides.py` 의 `GUIDE_DATA` 에 `region-daejeon`, `region-ulsan`,
`region-suwon` 콘텐츠가 아직 없습니다.

`HomeView` 가 **가이드 콘텐츠가 있는 지역만** 카드로 내보내도록 해 두었으므로,
지금 상태에서 랜딩에는 기존 6개만 보입니다. 이렇게 하지 않으면 카드를 눌렀을 때
`GuideView` 가 `Http404` 를 냅니다.

**챗봇과 회원가입 드롭다운에서는 9개 지역이 모두 동작합니다.**
`guides.py` 콘텐츠를 채우면 카드가 자동으로 나타납니다.

### 평가 문항이 없습니다

`evals/qa_set.json` 에 대전·울산·수원 문항이 없어, 지금 평가를 돌리면
새 지역의 품질을 측정하지 못합니다. 지역당 2문항 추가를 권합니다.

**데이터를 작성한 사람이 아닌 다른 팀원이 출제해야 합니다.**
자기가 쓴 문서를 보고 문제를 내면 평가가 아니라 자문자답이 됩니다.

### 측정에서 볼 것

기준선(2026-08-26, openai + MySQL, min_score 0.3):

```
통과율 90.0% (27/30) · 평균 4.22 · 환각 0 · 오거부 3
region_specific 10/10 (avg 5.0)
```

지역 청크가 119 → 165 로 **39% 늘었습니다.** 1단계에서 겪은 "청크 밀림"이
총량 효과로 재발할 수 있는 구간입니다. **기존 6개 지역 점수가 떨어졌는지**를
가장 먼저 보십시오. 새 지역은 13~18청크로 눌러 두었고 기존 파일은 건드리지
않았지만, 총량 증가는 피할 수 없습니다.

떨어졌다면 새 지역을 절반씩 빼며 이분탐색합니다.

---

## 5. 지역 추가 방법 (이번 통합 이후)

`members/regions.py` 의 `REGIONS` 에 항목 하나를 넣습니다.

```python
{
    "code": "daegu",
    "color": "#4A7C2D",
    "label": "대구",
    "slug": "daegu",
    "aliases": ["대구광역시", "대구시", "대구"],
},
```

이것만으로 `REGION_CHOICES`(드롭다운 5곳) · 랜딩 카드 · 가이드 슬러그 ·
제목/파일명 매칭이 전부 따라옵니다.

**따로 손댈 곳은 두 군데입니다.**

1. `members/guides.py` 에 `'region-daegu'` 콘텐츠
2. `evals/qa_set.json` 에 문항 2개

그리고 `makemigrations` → `migrate`.

### ⚠️ 추가 전에 행정구역 상태를 확인하십시오

2026년에 광역 행정통합이 실제로 일어났습니다. **광주광역시는 2026-07-01
전라남도와 통합되어 폐지되었습니다.** 이번 작업에서 광주 가이드를 만들려다
발견해 중단했습니다. 자세한 경위와 지역별 판정은
`docs/행정구역_확인_기록.md` 와 `members/regions.py` 상단 주석에 있습니다.

확인할 것 세 가지:

1. 그 행정구역이 지금도 존재하는가
2. 통합·분리 논의가 진행 중인가 (진행 중이면 자료가 곧 바뀜)
3. 통합되었다면 **단일 배출 체계가 성립하는 범위인가**

---

## 6. 팀 확인이 필요한 사항

1. **천안 배출 요일** — `members/guides.py` 가이드 페이지의
   "월·수·금(재활용), 화·목·토(일반)" 출처를 찾지 못했습니다.
   앱 화면과 챗봇 답변이 어긋나면 시연에서 바로 드러납니다.
2. **미추홀 재활용품 요일** — 구청 안내(주 3회)와 조례 시행규칙(화·목)이 다릅니다.
   평가는 구청 기준으로 통과했지만 조례가 근거라면 정답이 바뀝니다.
3. **robots.txt 차단 사이트 교차 확인** — 부산 남구·세종·천안·대전은
   검색 결과 요약으로만 확인한 항목이 있습니다.
4. **대전 재확인** — 충남대전 통합은 보류 상태이나 재점화 가능성이
   거론됩니다. 시연 전에 한 번 더 확인하십시오.
5. **서울 평가 문항 0개** — 기본값 지역인데 `region_specific` 문항이 없습니다.

### 울산·수원에서 확인 못 해 뺀 것

- 울산: 폐의약품, 폐형광등·폐건전지 (공식 출처를 찾지 못함)
- 수원: 폐의약품

확인되지 않은 항목은 추측해서 채우지 않고 통째로 뺐습니다.
빈칸은 공통 가이드가 받아 주지만, 틀린 지역 정보는 챗봇이 확신에 차서
잘못 답하게 만듭니다.
