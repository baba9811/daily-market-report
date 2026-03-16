---
name: sdd-tdd
description: Schema-Driven + Test-Driven Development workflow. Define schemas first, write tests, then implement.
---

## SDD + TDD Development Workflow

When developing new features, follow this strict order:

### Phase 1: Schema-Driven Design (SDD)
1. **Define domain entities** in `backend/src/daily_scheduler/domain/entities/`
2. **Define port interfaces** in `backend/src/daily_scheduler/domain/ports/`
3. **Define DTOs** in `backend/src/daily_scheduler/application/dto/`
4. **Define API schemas** in `backend/src/daily_scheduler/entrypoints/api/schemas/`
5. **Define TypeScript types** in `frontend/src/types/`

### Phase 2: Test-Driven Development (TDD)
6. **Write backend unit tests** in `backend/tests/` — tests MUST fail initially
7. **Write E2E test scenarios** — use Playwright MCP to verify expected UI behavior
8. **Implement backend** — adapters, use cases, routes until tests pass
9. **Implement frontend** — components, pages until E2E tests pass

### Phase 3: Verification
10. Run `make test` — all tests must pass
11. Run `make lint` — no lint/type errors (ruff, pyrefly, oxlint, eslint, tsc)
12. Use Playwright MCP to visually verify the feature end-to-end
13. Run architecture-validator subagent to check boundary compliance

### Rules
- NEVER skip schema definition — it's the contract between layers
- NEVER implement before tests exist
- NEVER mark a feature complete without passing all verification steps
