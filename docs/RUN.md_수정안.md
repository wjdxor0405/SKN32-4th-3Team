# RUN.md 수정 요청 — C절 표가 실제 코드와 어긋납니다

작성일 2026-08-25 · 문서 담당자에게

1단계 데이터 작업 중 적용 절차를 쓰다가 발견했습니다. RUN.md C절의 마지막 두 줄이
낡았습니다. HANDOFF.md 와 실제 코드가 일치하고, **RUN.md 만 갱신되지 않았습니다.**

이 표를 보고 "평가 도구는 아직 못 쓴다"고 판단하면 게이트 측정을 건너뛰게 됩니다.

---

## 고쳐야 할 두 줄

### 현재

```markdown
| 게시판(boards) | ⬜ 모델만 — 강사 자료 CBV 붙여넣기 대기 |
| evals(RAGAS) · measure_threshold | ⬜ import 경로 수정 대기 |
```

### 수정안

```markdown
| 게시판(boards) | ✅ CRUD · 검색 · 지역필터 · 조회수 · 첨부 · 권한 동작 (`verify_boards.py` 20건으로 재검증 가능) |
| evals(LLM 혼합 평가) · measure_threshold | ✅ 이식 · 배선 검증 완료 — **지표 재측정만 남음 (openai 백엔드 필요)** |
```

---

## 근거

| 항목 | RUN.md C절 | 실제 |
|---|---|---|
| boards | "모델만" | `boards/views.py` 120줄, CBV 5개(List·Detail·Create·Update·Delete) 구현. HANDOFF.md 는 "전부 동작" |
| run_eval_hybrid | "import 경로 수정 대기" | `django.setup()` 부트스트랩 있음. import 도 `rag.service` 로 교체 완료 |
| measure_threshold | "import 경로 수정 대기" | 정상 Django management command. `from django.conf import settings` 로 교체 완료 |

HANDOFF.md 2-1·2-2 절에 이식 완료 경위가 기록돼 있습니다.

---

## 명칭도 함께 고칠 것

**"evals(RAGAS)" → "evals(LLM 혼합 평가)"**

HANDOFF.md 가 이미 지적한 사항입니다. 3차 evals 는 RAGAS 가 아니라
LLM 채점 + 규칙 검사를 섞은 방식입니다. RUN.md 에만 옛 명칭이 남아 있습니다.

---

## 함께 보강하면 좋을 것 — 재색인 명령이 모드마다 다르다는 안내

RUN.md 는 A절(퀵스타트)에서 `rag_reindex`, B절(실사용)에서 `seed_docs --reindex` 를
각각 쓰고 있는데, **두 명령의 차이를 한 곳에서 대조해 주는 문장이 없습니다.**

실제로 이번에 `files` 모드 사용자에게 `seed_docs` 를 안내할 뻔했습니다.
`files` 모드는 `data/` 폴더를 직접 읽으므로 `seed_docs` 를 돌려도 색인에 반영되지 않습니다.

C절 표 아래에 한 줄 추가를 제안합니다.

```markdown
> **재색인 명령은 `RAG_SOURCE` 에 따라 다릅니다.**
> `files` → `python manage.py rag_reindex` (data/ 폴더를 직접 읽음)
> `db` → `python manage.py seed_docs --reindex` (documents 테이블로 적재 후 색인)
> 모드를 확인하지 않고 반대쪽 명령을 실행하면 아무 일도 일어나지 않습니다.
```

---

## 참고 — 실행 검증 이력의 숫자가 바뀝니다

RUN.md A절 끝의 "최종 상태: 26문서 / 881청크" 는 1단계 데이터 작업 이후 달라집니다.
**문서 수는 그대로 24개(법령 9 + 가이드 15)** 이고 파일을 추가하지 않았으므로,
바뀌는 것은 청크 수뿐입니다. 지역 파일 6개가 총 9,916자 → 16,859자로 늘었습니다.

재색인 후 실제 숫자를 확인해 이 줄을 갱신해 주십시오.
