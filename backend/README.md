# backend

API 경계, 스키마, 마이그레이션. 서버 쪽 판단을 굳히는 스킬.

## 에이전트가 실패하는 지점

**스키마를 모르는 채 쿼리를 쓴다.** 컬럼명·인덱스·제약을 추측으로 채우고, 그럴듯하지만 안 도는 SQL을 낸다. 마이그레이션은 롤백 경로를 안 그리고 앞으로만 간다.

DB 플러그인을 붙이면 스키마를 직접 읽고 마이그레이션을 실행하므로 이 실패 모드 자체가 사라진다. **쓰는 DB 하나만** 고르는 게 핵심이다. 여러 개 켜면 컨텍스트만 먹는다.

## 붙일 도구

| 도구 | 역할 |
|---|---|
| `prisma` / `supabase` / `neon` / `mongodb` / `convex` | **하나만.** 스키마 조회·마이그레이션·쿼리 실행 |
| `postman` | 컬렉션 동기화, 클라이언트 코드 생성, 테스트 실행 |
| `mcp-server-dev` · `agent-sdk-dev` | 에이전트/MCP 서버를 직접 만들 때 |
| `auth0` / `workos` | 로그인·SSO·MFA·RBAC |
| `redis-development` | 자료구조 선택·캐싱 전략·벡터 검색 |
| `42crunch-api-security-testing` | OpenAPI 스펙 자동 감사. 공개 API를 낼 때 |
| [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) | `api-and-interface-design`만 발췌해 참고 |

## 여기 넣을 스킬 후보

- `api-design`: 엔드포인트 설계 시 물어야 할 것 (버저닝·에러 형태·페이지네이션)
- `schema-review`: 마이그레이션 전 확인 목록 (인덱스·NOT NULL·롤백 경로)
- `idempotency`: 재시도 안전성을 어디에 넣을지

## 설정 프리셋

이 도메인의 도구는 [`backend-postgres`](../presets/project/backend-postgres) 프리셋에 들어간다. 적용법은 [`presets/README.md`](../presets)를 본다.

## 설치

```bash
# Claude Code
claude plugin install backend@kyle-skills

# Codex
codex plugin add backend@kyle-skills
```

스킬은 `backend/skills/` 아래에 둔다.
