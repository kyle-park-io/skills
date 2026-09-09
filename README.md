# skills

에이전트 스킬 모음. 도메인별로 폴더를 나눠, 내가 반복하는 판단을 스킬로 굳혀둔 곳.

Claude Code · Codex · Cursor 등 `SKILL.md` 규약을 따르는 하네스에서 공통으로 쓴다.

---

## 구조

```
skills/
├── architecture/     코드베이스 구조 파악 · 다이어그램 · ADR
├── backend/          API 경계 설계 · 스키마 · 마이그레이션
├── frontend/         UI 구현 · 성능 진단 · 브라우저 검증
├── dashboard/        데이터 접근 · 차트 · BI 도구
├── infra/            IaC · 배포 · 관측 · 인시던트
├── process/          작업 절차 (superpowers 보강)
├── skill-authoring/  스킬 자체를 만들고 검증하는 법
├── _template/        새 스킬 시작점
└── docs/             설정 가이드
```

각 도메인 폴더의 `README.md`는 **카탈로그**다. 그 도메인에서 에이전트가 실패하는 지점, 쓸 만한 공식 플러그인과 OSS 스킬, 그리고 여기 직접 넣을 스킬 후보를 적어둔다.

## 스킬 하나 = 폴더 하나

```
architecture/
└── adr-writing/
    ├── SKILL.md          필수
    ├── references/       선택 · 길어지는 참고자료
    └── scripts/          선택 · 실행 스크립트
```

`SKILL.md`의 프론트매터 `name`은 **폴더명과 일치**시킨다. `description`은 "언제 써야 하는지"를 구체적으로 쓴다. 이 한 줄이 발동 정확도를 결정한다.

새로 만들 땐 `_template/SKILL.md`를 복사해서 시작한다.

## 설치

개인 스킬은 하네스의 스킬 디렉터리에 있으면 플러그인 없이 바로 잡힌다.

```bash
# Claude Code: 도메인 폴더를 통째로 심볼릭 링크
ln -s ~/code/skills/architecture ~/.claude/skills/architecture

# 크로스 런타임 (Codex · Copilot CLI · Gemini CLI)
ln -s ~/code/skills ~/.agents/skills
```

레포별로만 쓸 스킬은 `<repo>/.claude/skills/`에 둔다.

---

## 원칙: 컨텍스트 예산

**스킬 설명문은 전부 컨텍스트에 상주한다.** 모델은 매 턴 등록된 모든 스킬의 `description`을 훑어 "지금 쓸 게 있나"를 판단한다. 그래서 스킬을 20개 만들면 20배 똑똑해지는 게 아니라, **20개 중에 헷갈리기 시작한다.**

여기에 스킬을 추가할 때 지키는 규칙:

1. **내장·기존 스킬과 겹치는지 먼저 확인한다.** 하네스 내장 16개 + superpowers 14개가 이미 상당 부분을 덮는다. 겹치면 안 만든다.
2. **항상 켜둘 것과 레포별로 켤 것을 나눈다.** 유저 스코프는 10개 선에서 끊는다.
3. **`description`이 겹치면 둘 다 안 뽑힌다.** 트리거 상황이 다른 스킬과 구별되게 쓴다.

자세한 배경과 도메인별 배치안: [`docs/SETUP-GUIDE.md`](docs/SETUP-GUIDE.md)

## 외부 스킬을 가져올 때

마켓플레이스 밖 OSS 스킬은 검증 없이 넣지 않는다. 스킬은 프롬프트 주입 표면이고, 컨텍스트에 상주하며, 도구 호출을 유도할 수 있다.

1. [`NVIDIA/SkillSpector`](https://github.com/NVIDIA/SkillSpector)로 스캔
2. `SKILL.md`를 직접 읽어 `description`과 본문이 같은 말을 하는지 확인
3. 프로젝트 스코프로만 먼저 켜기
4. 며칠 써본 뒤 유저 스코프 승격 판단
