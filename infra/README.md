# infra

IaC, 배포, 관측, 인시던트.

## 에이전트가 실패하는 지점

**런타임에서 무슨 일이 벌어지는지 못 읽는다.** 그래서 디버깅이 로그 조회가 아니라 추측이 된다. 관측 도구를 붙이는 순간 이 성격이 바뀐다. 에러를 상상하는 대신 조회한다.

IaC 쪽은 반대 문제다. state·잠금·drift 같은 개념이 코드에 안 드러나 있어서, 문법은 맞는데 운영상 위험한 변경을 낸다.

## 붙일 도구

| 도구 | 역할 |
|---|---|
| `sentry` | 에러·스택 트레이스·이슈 검색. 도입 비용 최저, 효과 즉각 |
| `github` | 공식 MCP. 이슈·PR·리뷰·코드 검색·CI 상태 |
| `terraform` | IaC 쓴다면 무조건 |
| `aws-core` / `azure` / `cloudflare` / `railway` | 쓰는 클라우드 **하나만** |
| `vercel` | 배포·로그·환경변수·도메인. 스킬 36개이므로 프로젝트 스코프에서만 켠다 |
| `datadog` / `honeycomb` / `grafana-cloud-mcp` | 로그·메트릭·트레이스 질의 |
| `semgrep` | 작성 시점에 보안 취약점 차단 |

## 여기 넣을 스킬 후보

- `deploy-checklist`: 배포 전 확인할 것 (마이그레이션 순서·롤백·피처 플래그)
- `incident-triage`: 장애 신고를 받았을 때 좁혀가는 순서
- `tf-review`: Terraform plan을 읽을 때 봐야 할 위험 신호

## 설정 프리셋

이 도메인의 도구는 [`infra-terraform`](../presets/project/infra-terraform) · [`nextjs-vercel`](../presets/project/nextjs-vercel) 프리셋에 들어간다. 적용법은 [`presets/README.md`](../presets)를 본다.
