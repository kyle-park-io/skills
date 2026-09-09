# dashboard

데이터에 닿는 경로와 BI 도구 조작.

## 에이전트가 실패하는 지점

차트를 **그리는** 능력은 이미 충분하다. 하네스 내장 `dataviz` 스킬이 팔레트 공식·축 규칙·접근성 검증기까지 갖고 있다. **그러니 차트 그리기용 스킬은 만들지 않는다.**

실제로 비는 건 두 가지다. **데이터에 닿는 경로**(파일·웨어하우스·API를 실제로 질의), 그리고 **BI 도구 조작**(대시보드를 만들고 고치기).

## 붙일 도구

| 도구 | 역할 |
|---|---|
| `duckdb-skills` | 아무 데이터 파일이나 읽고 SQL 질의. 셋업 비용 0, 가장 범용적. 여기부터 |
| `grafana-mcp` | 대시보드·데이터소스·알림을 직접 만들고 수정 |
| `clickhouse` + `clickhouse-best-practices` | 후자는 스키마·쿼리 28개 규칙. 세트로 |
| `posthog` / `amplitude` | 제품 분석·피처 플래그·실험 |
| `data-engineering` / `data` | 웨어하우스 탐색, Airflow DAG |
| [`cathrynlavery/diagram-design`](https://github.com/cathrynlavery/diagram-design) | 38종 에디토리얼 다이어그램, 자체 완결 HTML+SVG |

## 여기 넣을 스킬 후보

- `metric-definition`: 지표를 정의할 때 합의해야 할 것 (분모·기간·중복 제거)
- `query-cost`: 웨어하우스 쿼리 날리기 전 비용 가늠

## 설정 프리셋

이 도메인의 도구는 [`data-analytics`](../presets/project/data-analytics) 프리셋에 들어간다. 적용법은 [`presets/README.md`](../presets)를 본다.
