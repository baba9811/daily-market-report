---
name: architecture-validator
description: Validates hexagonal architecture boundaries - domain must not import infrastructure or entrypoints
model: sonnet
---

## Task
Validate that the hexagonal architecture boundaries are respected in the current changes.

## Architecture Rules
The backend follows Hexagonal Architecture (Ports & Adapters):

```
domain/          → NO imports from application/, infrastructure/, entrypoints/
application/     → May import domain/ only
infrastructure/  → May import domain/, application/
entrypoints/     → May import domain/, application/, infrastructure/
```

## Steps
1. Run `git diff --name-only` to find changed Python files
2. For each changed file in `backend/src/daily_scheduler/`:
   - Determine which layer it belongs to (domain, application, infrastructure, entrypoints)
   - Check all import statements
   - Flag any imports that violate the layer boundaries above
3. Also check for:
   - Domain entities importing SQLAlchemy, FastAPI, or any framework
   - Application use cases importing concrete adapters instead of ports
   - Circular dependencies between modules
4. Report violations with file path, line number, and the offending import
