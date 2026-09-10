# dashboard

데이터에 닿는 경로와 BI 도구 조작.

## 에이전트가 실패하는 지점

Claude Code에서는 차트를 **그리는** 능력을 내장 `dataviz` 스킬이 이미
갖고 있다. Codex에는 같은 이름의 시스템 스킬이 항상 있다고 가정하지 않고
현재 세션의 스킬 목록을 확인한다. **그러니 차트 그리기용 스킬은 하네스의
현재 기본기를 확인한 뒤에만 만든다.**

실제로 비는 건 두 가지다. **데이터에 닿는 경로**(파일·웨어하우스·API를 실제로 질의), 그리고 **BI 도구 조작**(대시보드를 만들고 고치기).

## 붙일 도구

아래는 역할 카탈로그다. Claude Code 공식 플러그인 이름과 Codex 공식
카탈로그는 일대일로 대응하지 않는다. 2026-09-10 현재 Codex에서는
`posthog`, `amplitude`, `data-analytics`를 확인했고 나머지는 별도 설치 경로를
검증해야 한다.

| 도구 | 역할 |
|---|---|
| `duckdb-skills` | 아무 데이터 파일이나 읽고 SQL 질의. 셋업 비용 0, 가장 범용적. 여기부터 |
| `grafana-mcp` | 대시보드·데이터소스·알림을 직접 만들고 수정 |
| `clickhouse` + `clickhouse-best-practices` | 후자는 스키마·쿼리 28개 규칙. 세트로 |
| `posthog` / `amplitude` | 제품 분석·피처 플래그·실험 |
| `data-engineering` / `data` | 웨어하우스 탐색, Airflow DAG |
| [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design) | 38종 에디토리얼 다이어그램, 자체 완결 HTML+SVG |

## 현재 상태

이 도메인의 `skills/`는 아직 비어 있다. 현재 플러그인을 설치해도 대시보드
스킬이나 위 도구가 함께 설치되지는 않는다.

## 여기 넣을 스킬 후보

- `metric-definition`: 지표를 정의할 때 합의해야 할 것 (분모·기간·중복 제거)
- `query-cost`: 웨어하우스 쿼리 날리기 전 비용 가늠

## 설정 프리셋

이 도메인의 도구는 [`data-analytics`](../presets/project/data-analytics) 프리셋에 들어간다. 적용법은 [`presets/README.md`](../presets)를 본다.

## 설치

```bash
# Claude Code
claude plugin install dashboard@kyle-skills

# Codex: 사용자 캐시는 한 번 준비하고 프로젝트 설정을 복사한다
bash presets/codex/bootstrap.sh
cp -r presets/project/data-analytics/.codex <대상 레포>/
```

스킬은 `dashboard/skills/` 아래에 둔다.
