# skills

에이전트 스킬 모음. 도메인별로 나눠, 내가 반복하는 판단을 스킬로 굳혀둔 곳.

레포 자체가 **플러그인 마켓플레이스**다. 도메인 하나가 플러그인 하나이므로, 어느 레포에서 어떤 도메인을 켤지 골라서 설치한다.

---

## 쓰는 법

Claude Code 와 Codex 양쪽을 지원한다. 스킬 본문은 하나이고, 하네스별로 다른 건 매니페스트뿐이다.

### 최초 1회

```bash
# Claude Code
claude plugin marketplace add kyle-park-io/skills

# Codex 및 크로스 런타임 하네스는 .agents/plugins/marketplace.json 을 읽는다
```

플러그인을 쓰지 않고 스킬만 가져가려면 `~/.agents/skills/` 에 링크한다. Codex, Copilot CLI, Gemini CLI 가 공통으로 인식하는 경로다. 다만 전 도메인이 상주하므로 아래 컨텍스트 예산 원칙과 상충한다.

### 어디서나 쓸 도메인은 유저 스코프로

`architecture`와 `process`는 스택을 안 가리므로 전역으로 켠다.

```bash
claude plugin install architecture@kyle-skills
claude plugin install process@kyle-skills
```

### 새 레포를 만들면

그 레포의 스택에 해당하는 도메인만 켠다.

```bash
cd <새 레포>
claude plugin install backend@kyle-skills    # scope: project
```

`<repo>/.claude/settings.json`에 기록되므로 **커밋한다.** 그 레포를 여는 사람은 누구나 같은 도메인이 켜진 상태로 시작한다.

프리셋을 통째로 복사해도 된다. 스택별로 공식 플러그인까지 묶어뒀다.

```bash
cp -r presets/project/backend-postgres/.claude <새 레포>/
```

### 갱신

```bash
claude plugin marketplace update kyle-skills
```

### 왜 심볼릭 링크가 아닌가

`~/.claude/skills/`에 도메인 폴더를 링크하면 **7개 도메인이 전부 항상 상주한다.** 그건 아래 컨텍스트 예산 원칙과 정면으로 충돌한다. 마켓플레이스 방식은 유저 스코프와 프로젝트 스코프를 구분하는 하네스 기본 메커니즘을 그대로 쓰므로, 켤 곳에서만 켜진다. 복사와 달리 원본이 갈라지지도 않는다.

---

## 구조

```
skills/
├── domains.json           단일 진실 원본. 매니페스트는 여기서 생성된다
├── scripts/
│   └── gen-manifests.py   하네스별 매니페스트 생성기
├── AGENTS.md              이 레포에서 작업하는 에이전트용 지침
├── .claude-plugin/
│   └── marketplace.json   Claude Code 마켓플레이스 (생성물)
├── .agents/plugins/
│   └── marketplace.json   크로스 런타임 마켓플레이스 (생성물)
├── architecture/          코드베이스 구조 파악, 다이어그램, ADR
├── backend/               API 경계 설계, 스키마, 마이그레이션
├── frontend/              UI 구현, 성능 진단, 브라우저 검증
├── dashboard/             데이터 접근, 차트, BI 도구
├── infra/                 IaC, 배포, 관측, 인시던트
├── process/               작업 절차 (superpowers 보강)
├── skill-authoring/       스킬 자체를 만들고 검증하는 법
├── _template/             새 스킬 시작점
├── presets/               복사해서 쓰는 설정 원본 (스택별)
└── docs/                  운영 기준
```

각 도메인 폴더의 `README.md`는 **카탈로그**다. 그 도메인에서 에이전트가 실패하는 지점, 쓸 만한 공식 플러그인과 OSS 스킬, 그리고 여기 직접 넣을 스킬 후보를 적어둔다.

설정 파일은 도메인 폴더에 두지 않는다. 레포 하나에는 `.claude/settings.json`이 하나뿐이라 도메인으로 쪼개지지 않기 때문이다. 복사해서 쓸 설정은 [`presets/`](presets)에 스택 단위로 모아뒀다.

## 도메인 하나 = 플러그인 하나

```
backend/
├── .claude-plugin/plugin.json   Claude Code 매니페스트 (생성물)
├── .codex-plugin/plugin.json    Codex 매니페스트 (생성물)
├── README.md                    카탈로그
└── skills/
    └── api-design/
        ├── SKILL.md             필수. 하네스 공용
        ├── references/          선택. 길어지는 참고자료
        └── scripts/             선택. 실행 스크립트
```

**매니페스트는 손으로 고치지 않는다.** `domains.json` 을 고치고 `python3 scripts/gen-manifests.py` 를 돌린다. 도메인 7개에 하네스 2개라 매니페스트가 16개다. 손으로 맞추면 갈라진다.

**스킬 본문에는 하네스의 툴 이름을 쓰지 않는다.** "파일을 읽는다"라고 쓰지 "Read 툴로 읽는다"라고 쓰지 않는다. 이것이 같은 파일이 양쪽에서 그대로 도는 유일한 이유다. 자세한 건 [`AGENTS.md`](AGENTS.md).

스킬은 반드시 `<도메인>/skills/` 아래에 둔다. 도메인 폴더 바로 밑이 아니다.

`SKILL.md`의 프론트매터 `name`은 **폴더명과 일치**시킨다. `description`은 "언제 써야 하는지"를 구체적으로 쓴다. 이 한 줄이 발동 정확도를 결정한다.

새로 만들 땐 `_template/SKILL.md`를 복사해서 시작한다.

---

## 원칙: 컨텍스트 예산

**스킬 설명문은 전부 컨텍스트에 상주한다.** 모델은 매 턴 등록된 모든 스킬의 `description`을 훑어 "지금 쓸 게 있나"를 판단한다. 그래서 스킬을 20개 만들면 20배 똑똑해지는 게 아니라, **20개 중에 헷갈리기 시작한다.**

여기에 스킬을 추가할 때 지키는 규칙:

1. **내장·기존 스킬과 겹치는지 먼저 확인한다.** 하네스 내장 16개와 superpowers 14개가 이미 상당 부분을 덮는다. 겹치면 만들지 않는다.
2. **어느 도메인에 넣을지가 곧 스코프 결정이다.** 그 도메인이 유저 스코프면 이 스킬은 어디서나 상주한다.
3. **`description`이 겹치면 둘 다 안 뽑힌다.** 트리거 상황이 다른 스킬과 구별되게 쓴다.

유저 스코프는 **스킬 30개를 넘기지 않는다.** 플러그인 개수가 아니라 스킬 개수로 센다. MCP 전용 플러그인(스킬 0개)은 이 예산에 안 들어가고, 대신 MCP 툴 정의라는 별도 비용을 낸다. 자세한 배경과 도메인별 배치안: [`docs/SETUP-GUIDE.md`](docs/SETUP-GUIDE.md)

## 외부 스킬을 가져올 때

마켓플레이스 밖 OSS 스킬은 검증 없이 넣지 않는다. 스킬은 프롬프트 주입 표면이고, 컨텍스트에 상주하며, 도구 호출을 유도할 수 있다.

1. [`NVIDIA/SkillSpector`](https://github.com/NVIDIA/SkillSpector)로 스캔
2. `SKILL.md`를 직접 읽어 `description`과 본문이 같은 말을 하는지 확인
3. 프로젝트 스코프로만 먼저 켜기
4. 며칠 써본 뒤 유저 스코프 승격 판단

## License

[MIT](./LICENSE)
