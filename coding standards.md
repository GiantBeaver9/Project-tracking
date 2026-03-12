# Coding Standards & Technical Conventions

**Project:** Project Tracker  
**Version:** 1.0  
**Date:** March 2026  
**Status:** Adopted  

> These standards apply to all code written for the Project Tracker system across every layer: Python API, Svelte frontend, React Native mobile app, SQL schema, and infrastructure. No exceptions without a documented ADR (Architecture Decision Record).

---

## Table of Contents

1. [Core Engineering Principles](#1-core-engineering-principles)
2. [SOLID Principles — Applied](#2-solid-principles--applied)
3. [Composition Over Inheritance](#3-composition-over-inheritance)
4. [No Hard-Coded Strings — Constants Everywhere](#4-no-hard-coded-strings--constants-everywhere)
5. [Python — API & Backend](#5-python--api--backend)
6. [Svelte — Frontend](#6-svelte--frontend)
7. [React Native — Mobile](#7-react-native--mobile)
8. [SQL & Database Conventions](#8-sql--database-conventions)
9. [API Design Conventions](#9-api-design-conventions)
10. [Testing Standards](#10-testing-standards)
11. [Git & Version Control](#11-git--version-control)
12. [Security Conventions](#12-security-conventions)
13. [Error Handling](#13-error-handling)
14. [Tooling & Enforcement](#14-tooling--enforcement)
15. [Architecture Decision Records](#15-architecture-decision-records)

---

## 1. Core Engineering Principles

These are the non-negotiables. Every PR reviewer should be asking these questions.

### 1.1 Single Responsibility

Every module, class, function, and component does **one thing**. If you find yourself writing "and" in a docstring — `"validates input and saves to the database"` — that is two responsibilities and should be two functions.

```python
# BAD — two responsibilities in one function
def submit_timecard(timecard_id: int, user_id: int) -> TimeCard:
    timecard = db.get(TimeCard, timecard_id)
    if timecard.total_hours > 24:
        raise ValueError("Hours exceed daily limit")
    timecard.status = TimecardStatus.SUBMITTED
    db.save(timecard)
    email_service.send(timecard.approver, "New submission")
    return timecard

# GOOD — each function has one job
def validate_timecard_hours(timecard: TimeCard) -> None:
    if timecard.total_hours > MAX_DAILY_HOURS:
        raise TimecardValidationError(ErrorCodes.HOURS_EXCEED_DAILY_LIMIT)

def submit_timecard(timecard: TimeCard) -> TimeCard:
    validate_timecard_hours(timecard)
    timecard.status = TimecardStatus.SUBMITTED
    return timecard

def notify_approver_of_submission(timecard: TimeCard) -> None:
    email_service.send(timecard.approver_id, EmailTemplates.TIMECARD_SUBMITTED)
```

### 1.2 Open/Closed

Code should be **open for extension, closed for modification**. Adding a new expense category, a new OT rule scope, or a new approval stage should not require editing existing validated logic — it should mean adding a new implementation of an existing interface.

### 1.3 Liskov Substitution

Any subtype must be fully substitutable for its base type without breaking callers. In practice for this codebase: if you pass a `ContractorEstimate` where an `Estimate` is expected, everything should still work correctly. If it doesn't, your abstraction is wrong.

### 1.4 Interface Segregation

Don't force a module to depend on interfaces it doesn't use. Prefer many small, focused interfaces/protocols over one large one. An expense approver should not need to import anything from the overtime engine.

### 1.5 Dependency Inversion

High-level modules must not depend on low-level modules. Both depend on abstractions. Concretely: the approval workflow engine does not import SQLAlchemy directly — it depends on a repository abstraction. The email sender is injected, not instantiated inside business logic.

```python
# BAD — business logic depends on infrastructure directly
class TimecardService:
    def submit(self, timecard_id: int) -> None:
        db = SessionLocal()           # direct infrastructure dependency
        sendgrid = SendGridClient()   # direct infrastructure dependency
        ...

# GOOD — dependencies injected, business logic isolated
class TimecardService:
    def __init__(
        self,
        repo: TimecardRepository,
        notifier: NotificationService,
    ) -> None:
        self._repo = repo
        self._notifier = notifier

    def submit(self, timecard_id: int) -> None:
        timecard = self._repo.get_by_id(timecard_id)
        ...
```

---

## 2. SOLID Principles — Applied

The SOLID principles above are abstract. Here is how they map to concrete decisions in this codebase.

| Principle | Concrete Rule |
|-----------|--------------|
| **S** — Single Responsibility | One file per service class. Routes, services, and repositories are always in separate files. A FastAPI router file contains **only** route handlers — no business logic. |
| **O** — Open/Closed | New approval stages, OT rule scopes, and expense categories are added by creating new constants/handlers — not by editing `if/elif` chains in existing code. Use handler registries and dispatch tables. |
| **L** — Liskov Substitution | All repository implementations must satisfy the full interface contract. Tests run against the interface, not the concrete class. |
| **I** — Interface Segregation | `ApprovalService` and `OvertimeService` have no shared imports. Each layer (route → service → repository) imports only what it needs from the layer directly below it. |
| **D** — Dependency Inversion | All services receive their dependencies via constructor injection. FastAPI dependency injection (`Depends()`) is used for routes. No `import` of a concrete infrastructure class inside a service module. |

---

## 3. Composition Over Inheritance

**There is no inheritance in this codebase except for:**
- Pydantic `BaseModel` (framework requirement)
- SQLAlchemy `Base` (framework requirement)
- Standard library exceptions (e.g., `class TimecardError(ValueError)`)

Everything else uses **composition**. If you are writing `class X(Y)` and Y is your own code — stop and reconsider.

### 3.1 Why

Inheritance couples the child to all current and future changes in the parent. In a system this complex, that coupling becomes a maintenance liability quickly. Composition lets you swap pieces independently and test them in isolation.

### 3.2 How — Python

```python
# BAD — inheritance to share behavior
class BaseApprover:
    def notify(self): ...
    def log_action(self): ...

class TimecardApprover(BaseApprover):
    def approve(self): ...

class ExpenseApprover(BaseApprover):  # now coupled to BaseApprover forever
    def approve(self): ...

# GOOD — compose from small, focused collaborators
class ApprovalNotifier:
    def notify(self, approver_id: int, template: str) -> None: ...

class ApprovalAuditLogger:
    def log(self, action: ApprovalAction) -> None: ...

class TimecardApprovalService:
    def __init__(self, notifier: ApprovalNotifier, logger: ApprovalAuditLogger) -> None:
        self._notifier = notifier
        self._logger = logger

    def approve(self, timecard: TimeCard, approver: User) -> TimeCard: ...

class ExpenseApprovalService:
    def __init__(self, notifier: ApprovalNotifier, logger: ApprovalAuditLogger) -> None:
        self._notifier = notifier
        self._logger = logger

    def approve(self, report: ExpenseReport, approver: User) -> ExpenseReport: ...
```

### 3.3 How — Svelte Components

```svelte
<!-- BAD — a monolith component that "extends" by growing -->
<!-- TimecardView.svelte — 800 lines doing everything -->

<!-- GOOD — compose small focused components -->
<!-- TimecardGrid.svelte     — just the AG Grid wrapper -->
<!-- TimecardFooter.svelte   — totals, OT breakdown -->
<!-- TimecardRowActions.svelte — add/remove row controls -->
<!-- TimecardSubmitBar.svelte — submit button + status -->

<!-- Parent assembles them -->
<TimecardGrid {entries} on:change={handleChange} />
<TimecardFooter {totals} />
<TimecardSubmitBar status={card.status} on:submit={handleSubmit} />
```

### 3.4 How — React Native

```tsx
// BAD — one screen component with all logic
export function ClockInScreen() {
  // GPS logic, worker type display, project picker, submit — all inline
}

// GOOD — compose focused components and hooks
function useGpsCapture() { ... }          // hook owns GPS logic
function useActiveProjects() { ... }      // hook owns project fetch

export function ClockInScreen() {
  const gps = useGpsCapture()
  const projects = useActiveProjects()
  return (
    <ScreenShell>
      <GpsStatusIndicator accuracy={gps.accuracy} />
      <ProjectSelector projects={projects.data} />
      <WorkerTypeBadge type={user.workerType} />  {/* read-only display */}
      <ClockInButton onPress={handleClockIn} />
    </ScreenShell>
  )
}
```

---

## 4. No Hard-Coded Strings — Constants Everywhere

**No string literal that carries meaning may appear outside a constants file.** This applies to: status values, category codes, role names, event names, error messages, API paths, table names in audit logs, email template keys, and environment variable names.

### 4.1 Python Constants

All constants live in `app/constants/`. One file per domain.

```
app/
  constants/
    __init__.py
    approval.py
    expense.py
    overtime.py
    roles.py
    timecard.py
    notifications.py
    errors.py
```

```python
# app/constants/timecard.py
from enum import StrEnum

class TimecardStatus(StrEnum):
    DRAFT       = "DRAFT"
    SUBMITTED   = "SUBMITTED"
    IN_REVIEW   = "IN_REVIEW"
    APPROVED    = "APPROVED"
    REJECTED    = "REJECTED"
    LOCKED      = "LOCKED"

class WorkerType(StrEnum):
    EMPLOYEE    = "EMPLOYEE"
    CONTRACTOR  = "CONTRACTOR"

MAX_DAILY_HOURS: float = 24.0
MAX_WEEKLY_HOURS_WARNING: float = 60.0

# app/constants/expense.py
class ExpenseCategory(StrEnum):
    LABOR           = "LABOR"
    MATERIALS       = "MATERIALS"
    EQUIPMENT       = "EQUIPMENT"
    TRAVEL          = "TRAVEL"
    SUBCONTRACTOR   = "SUBCONTRACTOR"
    PERMITS         = "PERMITS"
    OTHER           = "OTHER"

class TaxType(StrEnum):
    SALES   = "SALES"
    USE     = "USE"
    EXCISE  = "EXCISE"
    VAT     = "VAT"
    OTHER   = "OTHER"

# app/constants/approval.py
class WorkflowType(StrEnum):
    TIME_CARD = "TIME_CARD"
    EXPENSE   = "EXPENSE"

class RejectionReturnPolicy(StrEnum):
    STAGE_1        = "STAGE_1"
    SUBMITTER_ONLY = "SUBMITTER_ONLY"

class ApprovalAction(StrEnum):
    APPROVE  = "APPROVE"
    REJECT   = "REJECT"
    ESCALATE = "ESCALATE"
    AUTO_APPROVE = "AUTO_APPROVE"

# app/constants/errors.py
class ErrorCodes(StrEnum):
    HOURS_EXCEED_DAILY_LIMIT    = "HOURS_EXCEED_DAILY_LIMIT"
    INVALID_PROJECT_CODE        = "INVALID_PROJECT_CODE"
    TIMECARD_ALREADY_SUBMITTED  = "TIMECARD_ALREADY_SUBMITTED"
    EXPENSE_RECEIPT_REQUIRED    = "EXPENSE_RECEIPT_REQUIRED"
    UNAUTHORIZED_ENTITY_ACCESS  = "UNAUTHORIZED_ENTITY_ACCESS"
    OT_RULE_CONFLICT            = "OT_RULE_CONFLICT"
```

```python
# BANNED anywhere outside constants files:
timecard.status = "SUBMITTED"       # ❌ hard-coded string
if category == "LABOR":             # ❌ hard-coded string
raise ValueError("Hours too high")  # ❌ magic message string

# REQUIRED:
timecard.status = TimecardStatus.SUBMITTED          # ✅
if category == ExpenseCategory.LABOR:               # ✅
raise TimecardValidationError(ErrorCodes.HOURS_EXCEED_DAILY_LIMIT)  # ✅
```

### 4.2 Svelte / TypeScript Constants

```typescript
// src/constants/timecard.ts
export const TimecardStatus = {
  DRAFT:      "DRAFT",
  SUBMITTED:  "SUBMITTED",
  IN_REVIEW:  "IN_REVIEW",
  APPROVED:   "APPROVED",
  REJECTED:   "REJECTED",
  LOCKED:     "LOCKED",
} as const
export type TimecardStatus = typeof TimecardStatus[keyof typeof TimecardStatus]

// src/constants/routes.ts
export const Routes = {
  DASHBOARD:          "/dashboard",
  PROJECTS:           "/projects",
  TIMECARD:           "/timecard",
  TIMECARD_PERIOD:    (periodId: string) => `/timecard/${periodId}`,
  APPROVALS:          "/approvals",
  REPORTS:            "/reports",
} as const

// src/constants/api.ts
export const ApiEndpoints = {
  PROJECTS_ACTIVE:    "/api/v1/projects/active",
  TIMECARD:           (periodId: string) => `/api/v1/timecards/${periodId}`,
  TIMECARD_SUBMIT:    (periodId: string) => `/api/v1/timecards/${periodId}/submit`,
  EXPENSES:           "/api/v1/expenses",
  EXPENSE_REPORT:     (reportId: string) => `/api/v1/expenses/reports/${reportId}`,
} as const
```

### 4.3 React Native Constants

```typescript
// src/constants/storage.ts  — MMKV keys
export const StorageKeys = {
  AUTH_TOKEN:       "auth_token",
  REFRESH_TOKEN:    "refresh_token",
  ACTIVE_CLOCKIN:   "active_clockin",
  DRAFT_EXPENSE:    "draft_expense",
} as const

// src/constants/navigation.ts
export const Screens = {
  HOME:             "Home",
  CLOCK_IN:         "ClockIn",
  TIME_CARD:        "TimeCard",
  PROGRESS_REPORT:  "ProgressReport",
  EXPENSE_ENTRY:    "ExpenseEntry",
  PROFILE:          "Profile",
} as const
```

---

## 5. Python — API & Backend

### 5.1 Tooling

| Tool | Purpose | Configuration |
|------|---------|--------------|
| `ruff` | Linting + formatting (replaces flake8, isort, black) | `pyproject.toml` |
| `mypy` | Static type checking (strict mode) | `pyproject.toml` |
| `pytest` | Testing | `pyproject.toml` |
| `pytest-cov` | Coverage reporting | Min 80% enforced in CI |
| `alembic` | DB migrations | `alembic/` directory |
| `pydantic v2` | Request/response validation | All FastAPI models |

### 5.2 Project Structure

```
app/
  api/
    v1/
      routes/         # FastAPI routers — route handlers only, no logic
        timecards.py
        projects.py
        expenses.py
        overtime.py
  constants/          # All enums and constant values (see Section 4)
  models/             # SQLAlchemy ORM models
  schemas/            # Pydantic request/response schemas
  services/           # Business logic — one file per domain
    timecard_service.py
    expense_service.py
    overtime_service.py
    approval_service.py
  repositories/       # DB access layer — one file per model/domain
    timecard_repo.py
    expense_repo.py
  core/
    config.py         # Settings from environment variables only
    security.py       # JWT, password hashing
    dependencies.py   # FastAPI Depends() functions
  workers/            # Celery tasks
  tests/
    unit/
    integration/
```

### 5.3 Type Annotations

Every function must be fully annotated. No `Any` without a comment explaining why. Mypy runs in strict mode in CI — a type error is a build failure.

```python
# BAD
def get_timecard(id, user):
    ...

# GOOD
def get_timecard(timecard_id: int, user: AuthenticatedUser) -> TimeCard:
    ...
```

### 5.4 Pydantic Schemas

Request and response schemas are **always separate** from ORM models. Never return a SQLAlchemy model directly from a route.

```python
# schemas/timecard.py
class TimecardEntryCreate(BaseModel):
    project_id: int
    task_id: int | None = None
    entry_date: date
    hours: Annotated[Decimal, Field(ge=0, le=MAX_DAILY_HOURS)]
    is_billable: bool
    notes: Annotated[str, Field(max_length=500)] | None = None

class TimecardEntryResponse(BaseModel):
    entry_id: int
    project_code: str
    entry_date: date
    hours_regular: Decimal
    hours_overtime: Decimal
    hours_doubletime: Decimal
    is_billable: bool

    model_config = ConfigDict(from_attributes=True)
```

### 5.5 Repository Pattern

All database access goes through a repository class. No raw SQL or ORM queries in service files or route handlers.

```python
# repositories/timecard_repo.py
class TimecardRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, timecard_id: int) -> TimeCard | None:
        return self._session.get(TimeCard, timecard_id)

    def get_draft_for_user_period(
        self, user_id: int, period_id: int
    ) -> TimeCard | None:
        return (
            self._session.query(TimeCard)
            .filter(
                TimeCard.user_id == user_id,
                TimeCard.period_id == period_id,
                TimeCard.status == TimecardStatus.DRAFT,
            )
            .one_or_none()
        )
```

### 5.6 Settings — No Hard-Coded Configuration

All configuration comes from environment variables via a Pydantic `Settings` class. No `.env` values in code.

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    redis_url: str
    blob_storage_url: str
    sendgrid_api_key: str
    geocoding_api_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
```

---

## 6. Svelte — Frontend

### 6.1 Tooling

| Tool | Purpose |
|------|---------|
| TypeScript | Required on all `.svelte` and `.ts` files — no plain JS |
| `eslint` + `svelte/eslint-plugin` | Linting |
| `prettier` | Formatting |
| `vitest` | Unit tests |
| `playwright` | E2E tests |

### 6.2 File & Component Naming

| Thing | Convention | Example |
|-------|-----------|---------|
| Components | PascalCase | `TimecardGrid.svelte` |
| Stores | camelCase + `.store.ts` | `timecard.store.ts` |
| Utilities | camelCase + `.utils.ts` | `hours.utils.ts` |
| Constants | camelCase + `.constants.ts` | `timecard.constants.ts` |
| API calls | camelCase + `.api.ts` | `timecard.api.ts` |
| Types | PascalCase in `.types.ts` | `TimecardEntry` in `timecard.types.ts` |

### 6.3 Component Rules

- One component per file
- Props are always typed with a TypeScript interface
- No business logic in `.svelte` files — extract to a `.utils.ts` or store
- No API calls directly in components — go through an `.api.ts` module
- No inline styles — use Tailwind utility classes only

```svelte
<!-- BAD -->
<script>
  let entries = []
  onMount(async () => {
    const res = await fetch('/api/v1/timecards/current')  // ❌ inline fetch
    entries = await res.json()
  })
</script>

<!-- GOOD -->
<script lang="ts">
  import { loadCurrentTimecard } from '$lib/api/timecard.api'
  import type { TimecardEntry } from '$lib/types/timecard.types'
  import { TimecardStatus } from '$lib/constants/timecard.constants'

  let entries: TimecardEntry[] = []
  onMount(async () => {
    entries = await loadCurrentTimecard()
  })
</script>
```

### 6.4 Stores

Use Svelte stores for shared state. Stores are thin — they hold state and expose actions. No business logic inside a store beyond what's needed to keep state consistent.

```typescript
// timecard.store.ts
import { writable, derived } from 'svelte/store'
import type { TimecardEntry } from '$lib/types/timecard.types'
import { TimecardStatus } from '$lib/constants/timecard.constants'

const _entries = writable<TimecardEntry[]>([])
const _status = writable<TimecardStatus>(TimecardStatus.DRAFT)

export const timecardStore = {
  entries: { subscribe: _entries.subscribe },
  status:  { subscribe: _status.subscribe },
  setEntries: (entries: TimecardEntry[]) => _entries.set(entries),
  setStatus:  (status: TimecardStatus)   => _status.set(status),
}
```

---

## 7. React Native — Mobile

### 7.1 Tooling

| Tool | Purpose |
|------|---------|
| TypeScript | Required — strict mode |
| `eslint` + `@typescript-eslint` | Linting |
| `prettier` | Formatting |
| `jest` + `@testing-library/react-native` | Unit + component tests |
| `detox` | E2E tests (optional, Phase 2) |

### 7.2 File Structure

```
src/
  screens/          # One file per screen
  components/       # Reusable UI components
  hooks/            # Custom hooks — one concern per hook
  api/              # API client functions
  constants/        # Enums and constant values (see Section 4)
  stores/           # Zustand stores
  types/            # TypeScript interfaces/types
  utils/            # Pure utility functions
  navigation/       # React Navigation config
```

### 7.3 Custom Hooks

Every non-trivial piece of logic that interacts with device APIs, async state, or external data must live in a custom hook. Screens compose hooks.

```typescript
// hooks/useGpsCapture.ts
export function useGpsCapture() {
  const [coords, setCoords] = useState<GpsCoords | null>(null)
  const [accuracy, setAccuracy] = useState<number | null>(null)
  const [error, setError] = useState<GpsError | null>(null)

  const capture = useCallback(async () => {
    // all GPS logic here, not in the screen
  }, [])

  return { coords, accuracy, error, capture }
}

// hooks/useActiveProjects.ts
export function useActiveProjects() {
  return useQuery({
    queryKey: [QueryKeys.ACTIVE_PROJECTS],
    queryFn: fetchActiveProjects,
    staleTime: STALE_TIME.PROJECTS,
  })
}
```

### 7.4 No Inline Styles

All styles use `StyleSheet.create()`. No `style={{ color: 'red' }}` inline objects.

```tsx
// BAD
<Text style={{ fontSize: 16, color: '#1F4E79', fontWeight: 'bold' }}>
  Clock In
</Text>

// GOOD
<Text style={styles.heading}>Clock In</Text>

const styles = StyleSheet.create({
  heading: {
    fontSize: 16,
    color: Colors.PRIMARY_BLUE,   // ← constant, not hex literal
    fontWeight: 'bold',
  },
})
```

---

## 8. SQL & Database Conventions

### 8.1 Naming

| Object | Convention | Example |
|--------|-----------|---------|
| Tables | PascalCase, singular | `TimeCard`, `ExpenseReport` |
| Columns | snake_case | `submitted_at`, `is_billable` |
| Primary keys | `{table_lower}_id` | `timecard_id`, `expense_id` |
| Foreign keys | `{referenced_table_lower}_id` | `project_id`, `user_id` |
| Boolean columns | prefix `is_` or `has_` | `is_active`, `is_tax_exempt` |
| Timestamp columns | suffix `_at` | `created_at`, `submitted_at` |
| Indexes | `ix_{table}_{column(s)}` | `ix_TimeCard_user_id_period_id` |
| Unique constraints | `uq_{table}_{column(s)}` | `uq_Project_entity_id_code` |

### 8.2 All Schema Changes via Alembic

No manual DDL against any non-local database. Ever. Schema changes are:

1. Written as an Alembic migration script
2. Code-reviewed like application code
3. Applied to staging before production
4. Reversible — every migration has a working `downgrade()`

### 8.3 No Raw SQL in Application Code

All queries go through SQLAlchemy ORM via the repository layer. If a query is too complex for the ORM (e.g., a deeply nested reporting query), it must use SQLAlchemy `text()` with **named bind parameters only** — never string concatenation.

```python
# BANNED — SQL injection vector and maintenance hazard
query = f"SELECT * FROM TimeCard WHERE user_id = {user_id}"

# ALLOWED only when ORM is genuinely insufficient
from sqlalchemy import text
result = session.execute(
    text("SELECT * FROM TimeCard WHERE user_id = :uid AND status = :status"),
    {"uid": user_id, "status": TimecardStatus.SUBMITTED},
)
```

### 8.4 Every Table Has

- A surrogate integer primary key (`{table}_id`)
- `created_at DATETIME NOT NULL DEFAULT GETUTCDATE()`
- `updated_at DATETIME NOT NULL DEFAULT GETUTCDATE()` (updated via trigger or ORM event)
- Appropriate indexes on all foreign key columns and frequently filtered columns

---

## 9. API Design Conventions

### 9.1 URL Structure

- Base: `/api/v1/`
- Resources are **plural nouns**: `/projects`, `/timecards`, `/expenses`
- Sub-resources use nesting: `/projects/{id}/tasks`, `/timecards/{period_id}/entries`
- Actions that don't map cleanly to CRUD use a verb suffix: `/timecards/{id}/submit`, `/timecards/{id}/approve`
- No verbs in resource URLs: `/get-projects` is banned

### 9.2 HTTP Methods

| Action | Method | Example |
|--------|--------|---------|
| Fetch list | GET | `GET /projects` |
| Fetch one | GET | `GET /projects/{id}` |
| Create | POST | `POST /projects` |
| Full replace | PUT | `PUT /timecards/{id}/entries` |
| Partial update | PATCH | `PATCH /projects/{id}` |
| Delete (soft) | DELETE | `DELETE /expenses/{id}` |
| State transition | POST to sub-resource | `POST /timecards/{id}/submit` |

### 9.3 Response Envelope

All responses use a consistent envelope:

```json
{
  "data": { ... },        // the resource or list
  "meta": {               // pagination, counts — only on list responses
    "total": 142,
    "page": 1,
    "page_size": 50
  },
  "errors": null          // null on success; array of error objects on failure
}
```

Error response:
```json
{
  "data": null,
  "errors": [
    {
      "code": "HOURS_EXCEED_DAILY_LIMIT",
      "field": "hours",
      "message": "Total hours for a single day cannot exceed 24."
    }
  ]
}
```

Error `code` values come from `ErrorCodes` constants — never free-form strings.

### 9.4 Versioning

- The current API version is `v1`
- Breaking changes require a new version (`v2`) — existing `v1` routes are not modified
- Additive changes (new optional fields, new endpoints) are allowed in the current version
- Deprecation is announced in response headers before removal: `Deprecation: true`, `Sunset: <date>`

---

## 10. Testing Standards

### 10.1 Coverage Requirements

| Layer | Minimum Coverage | Enforced In |
|-------|-----------------|-------------|
| Service layer (Python) | 90% | CI |
| Repository layer (Python) | 80% | CI |
| Route handlers (Python) | 80% | CI |
| Utility functions (Svelte/TS) | 85% | CI |
| Custom hooks (React Native) | 85% | CI |
| Overall project | 80% | CI |

Coverage below threshold = failed build. No exceptions without a documented waiver in the PR.

### 10.2 Test Categories

**Unit tests** — pure logic, no I/O, no DB, no network. Fast. Run on every commit.
- OT rule calculation logic
- Tax calculation (auto-calc, override, exempt)
- Expense subtotal/total derivation
- Estimate cost computation

**Integration tests** — tests that hit a real test database. Run on every PR.
- Repository methods with real queries
- API route tests via `httpx.AsyncClient`
- Workflow state machine transitions

**E2E tests** — full browser/device flow. Run nightly and before release.
- Time card weekly entry and submission
- Expense entry with receipt upload and approval
- Clock-in GPS capture on mobile

### 10.3 Test Naming

```python
# Pattern: test_{unit_under_test}__{scenario}__{expected_outcome}

def test_calculate_ot_hours__california_rule__daily_threshold_applied():
    ...

def test_submit_timecard__already_submitted__raises_conflict_error():
    ...

def test_expense_tax__is_tax_exempt_flag__tax_amount_is_zero():
    ...
```

### 10.4 No Logic in Tests

Tests assert behavior — they do not contain conditional logic (`if`, `for`, `try/except`). If you need a loop to set up test data, use a factory or fixture.

---

## 11. Git & Version Control

### 11.1 Branch Naming

```
feature/{ticket-id}-short-description     → feature/PT-142-expense-tax-calc
fix/{ticket-id}-short-description         → fix/PT-201-ot-rule-null-pointer
chore/{short-description}                 → chore/update-dependencies
docs/{short-description}                  → docs/add-api-auth-guide
```

### 11.2 Commit Messages — Conventional Commits

Format: `{type}({scope}): {description}`

```
feat(expenses): add tax-exempt flag to expense line items
fix(overtime): handle null daily_dt_threshold in CA rule
refactor(approval): extract rejection routing to policy class
test(timecard): add unit tests for 7th-day OT rule
docs(api): document expense report endpoints
chore(deps): upgrade fastapi to 0.115.0
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`

### 11.3 Pull Request Rules

- Minimum **1 approving review** from a team member who did not write the PR
- CI must pass (lint, type check, tests, coverage) before merge
- No `console.log`, `print()`, or debug statements in merged code
- PR description must reference the ticket ID and include a brief "what changed and why"
- Squash merge to `main` — no merge commits

### 11.4 Protected Branches

| Branch | Protection |
|--------|-----------|
| `main` | No direct push. PR + CI + review required |
| `staging` | No direct push. PR from feature branch or `main` |
| `production` | Deploy-only. Merge from `staging` after sign-off |

---

## 12. Security Conventions

### 12.1 Authentication & Authorization

- Never trust the client for authorization decisions — all checks happen server-side in the service layer
- Entity ID is always read from the **JWT token claims**, never from request body or query params
- Contractor tokens carry `is_contractor: true` — any service that returns cost or rate data must check this claim and exclude those fields

### 12.2 Secrets

- No secrets in source code. Ever. Not even in comments.
- No secrets in git history — use `git-secrets` or `trufflehog` in CI to scan
- All secrets via environment variables loaded through the `Settings` class (Section 5.6)
- Rotate secrets on any suspected exposure — do not wait to confirm

### 12.3 Input Validation

- All API input validated by Pydantic schemas before reaching service layer
- All DB queries use parameterized statements (Section 8.3)
- File uploads (receipts, progress photos, Excel imports) must validate:
  - MIME type (server-side, not just file extension)
  - Maximum file size before reading content
  - Virus scan before committing to blob storage (ClamAV or equivalent)

### 12.4 Logging

- Never log: passwords, tokens, full credit card numbers, SSNs, loaded rates, or PII beyond user ID
- Always log: user ID, entity ID, action, resource type, resource ID, timestamp, IP address
- Use structured JSON logging — no free-form `print()` or unstructured string logs in production

---

## 13. Error Handling

### 13.1 Exception Hierarchy

```
ProjectTrackerError (base)
  ├── ValidationError
  │     ├── TimecardValidationError
  │     ├── ExpenseValidationError
  │     └── EstimateValidationError
  ├── AuthorizationError
  │     ├── InsufficientRoleError
  │     └── EntityAccessDeniedError
  ├── NotFoundError
  ├── ConflictError
  │     └── TimecardAlreadySubmittedError
  └── IntegrationError
        ├── PayrollSyncError
        └── GeocodingError
```

All exceptions carry an `error_code: ErrorCodes` from the constants file. HTTP status codes are mapped from exception types in a single error handler — not scattered across route handlers.

### 13.2 Never Swallow Exceptions

```python
# BANNED
try:
    do_something()
except Exception:
    pass  # ← you just hid a bug forever

# REQUIRED — either handle specifically or re-raise
try:
    result = geocode_address(address)
except GeocodingError as e:
    logger.warning("Geocoding failed for address %s: %s", address.address_id, e)
    address.geocode_status = GeocodeStatus.FAILED
    # intentional — geocoding failure is non-fatal, continue
```

### 13.3 Frontend Error Handling

- All API calls go through a central `apiClient` wrapper that handles 401 (token refresh), 403 (show permission denied), 422 (surface validation errors to the form), and 5xx (show global error toast)
- Components never catch fetch errors directly — they receive error state from stores or React Query

---

## 14. Tooling & Enforcement

### 14.1 CI Pipeline (every PR)

```
1. Lint        → ruff check . (Python), eslint (TS/Svelte/RN)
2. Format      → ruff format --check, prettier --check
3. Type check  → mypy app/ (strict), tsc --noEmit
4. Unit tests  → pytest tests/unit/, jest
5. Coverage    → pytest-cov (min 80%), jest --coverage
6. Integration → pytest tests/integration/ (against test DB)
7. Security    → trufflehog (secret scan), bandit (Python SAST)
```

All 7 steps must pass. A single failure blocks merge.

### 14.2 `pyproject.toml` Reference

```toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "UP", "S", "B", "A"]
# A = flake8-builtins (no shadowing builtins)
# S = bandit security rules
# B = flake8-bugbear
# N = pep8-naming

[tool.mypy]
strict = true
ignore_missing_imports = false

[tool.pytest.ini_options]
addopts = "--cov=app --cov-report=term-missing --cov-fail-under=80"
```

### 14.3 Pre-commit Hooks

All developers install pre-commit hooks on clone:

```bash
pip install pre-commit && pre-commit install
```

Hooks run: `ruff`, `mypy`, `prettier`, `eslint`, `trufflehog` before every commit. A failing hook blocks the commit locally before it reaches CI.

---

## 16. Org Hierarchy & Permission Verification Patterns

This section defines the mandatory coding patterns for all code that touches the org hierarchy, node resolution, or data access gating. These patterns are non-negotiable — every repository method, service call, and API route that returns data must follow them.

### 16.1 The VerifiedPermission Object

No repository method may execute a data query without receiving a `VerifiedPermission` object. This object is the proof that the permission check already passed. It is never constructed by a caller — only by the `PermissionService`.

```python
# app/schemas/permission.py
from dataclasses import dataclass

@dataclass(frozen=True)
class VerifiedPermission:
    """
    Proof that a user's permission for a node has been checked and confirmed.
    Constructed only by PermissionService — never instantiated directly by callers.
    All fields are read-only (frozen dataclass).
    """
    user_id: int
    node_id: int
    is_viewer: bool
    is_timecard_submitter: bool
    is_timecard_approver: bool
    is_timecard_viewer: bool
    is_expense_submitter: bool
    is_expense_approver: bool
    is_expense_cost_viewer: bool
    is_project_cost_viewer: bool
    is_report_viewer: bool
    is_report_exporter: bool
    is_node_admin: bool
    is_user_admin: bool
    # ... all is_* flags from the Permissions table
    user_type: str   # WorkerType.EMPLOYEE | WorkerType.CONTRACTOR
```

### 16.2 PermissionService — The Only Way In

```python
# app/services/permission_service.py
from app.constants.errors import ErrorCodes
from app.schemas.permission import VerifiedPermission

class PermissionService:
    def __init__(self, repo: PermissionRepository) -> None:
        self._repo = repo

    def verify(
        self,
        user_id: int,
        node_id: int,
        required_flag: str,         # e.g., "is_timecard_submitter"
    ) -> VerifiedPermission:
        """
        Loads and validates a user's permission for a node.
        Raises AuthorizationError if:
          - No membership exists for the user on this node
          - is_data_verified is False
          - The required_flag is False
          - The permission is expired or inactive
        Never reveals whether the node exists to unauthorized callers.
        """
        perm = self._repo.get(user_id=user_id, node_id=node_id)

        if (
            perm is None
            or not perm.is_active
            or not perm.is_data_verified
            or (perm.expires_at and perm.expires_at < utcnow())
        ):
            # Return identical error regardless of reason — no leaking node existence
            raise AuthorizationError(ErrorCodes.UNAUTHORIZED_NODE_ACCESS)

        if not getattr(perm, required_flag, False):
            raise AuthorizationError(ErrorCodes.INSUFFICIENT_NODE_PERMISSION)

        return VerifiedPermission(**perm.__dict__)
```

### 16.3 Repository Methods Require VerifiedPermission

Every repository method that returns data takes `verified: VerifiedPermission` as a required argument. It does not re-check permissions — that already happened. But it will not compile/run without the object being present.

```python
# app/repositories/timecard_repo.py
class TimecardRepository:

    def get_for_period(
        self,
        period_id: int,
        verified: VerifiedPermission,   # ← required; no default
    ) -> list[TimeCard]:
        """Returns time cards the verified user is entitled to see."""
        query = (
            self._session.query(TimeCard)
            .filter(TimeCard.period_id == period_id)
        )
        # Scope results to what this permission allows
        if not verified.is_timecard_viewer:
            # User can only see their own cards
            query = query.filter(TimeCard.user_id == verified.user_id)
        # Node isolation — always applied regardless of other flags
        query = query.filter(TimeCard.node_id == verified.node_id)
        return query.all()

    # BANNED — no data method without VerifiedPermission
    def get_all(self) -> list[TimeCard]:   # ❌ will not be merged
        ...
```

### 16.4 FastAPI Route Pattern

Routes verify permissions via a `Depends()` factory. The service layer receives the verified object — it never calls `PermissionService` itself.

```python
# app/api/v1/routes/timecards.py
from fastapi import APIRouter, Depends
from app.core.dependencies import get_verified_timecard_submitter

router = APIRouter(prefix="/timecards")

@router.get("/{period_id}/entries")
async def get_timecard_entries(
    period_id: int,
    verified: VerifiedPermission = Depends(get_verified_timecard_submitter),
    service: TimecardService = Depends(get_timecard_service),
) -> TimecardResponse:
    # verified is already checked — just pass it through
    return service.get_entries(period_id=period_id, verified=verified)

# app/core/dependencies.py
def get_verified_timecard_submitter(
    node_id: int = Query(...),
    current_user: AuthenticatedUser = Depends(get_current_user),
    perm_service: PermissionService = Depends(get_permission_service),
) -> VerifiedPermission:
    return perm_service.verify(
        user_id=current_user.user_id,
        node_id=node_id,
        required_flag=PermissionFlags.IS_TIMECARD_SUBMITTER,
    )
```

### 16.5 Node Tree Queries — Always Use the Closure Table

Never walk the `parent_node_id` chain in application code with a loop or recursive CTE in a hot path. Always use `OrgNodeClosure`.

```python
# BANNED — recursive loop in application code
def get_ancestor_nodes(node_id: int) -> list[OrgNode]:
    nodes = []
    current = repo.get(node_id)
    while current.parent_node_id:          # ❌ N+1 queries
        current = repo.get(current.parent_node_id)
        nodes.append(current)
    return nodes

# REQUIRED — single join via closure table
def get_ancestor_nodes(node_id: int) -> list[OrgNode]:
    return (
        self._session.query(OrgNode)
        .join(OrgNodeClosure, OrgNodeClosure.ancestor_node_id == OrgNode.node_id)
        .filter(OrgNodeClosure.descendant_node_id == node_id)
        .filter(OrgNodeClosure.depth > 0)     # exclude self
        .order_by(OrgNodeClosure.depth.desc()) # root first
        .all()
    )
```

### 16.6 OT Rule Resolution — Node Ancestor Walk

The OT rule resolver uses the closure table to walk up the user's node ancestors, checking for the first matching `OvertimeRuleAssignment` at each level.

```python
# app/services/overtime_service.py
class OvertimeRuleResolver:

    def resolve(self, user_id: int, workplace_state: str) -> OvertimeRule:
        """
        Priority: USER → NODE (leaf-to-root) → UNION → PROJECT → STATE
        Uses closure table — no recursive loops.
        """
        # 1. User-level override
        rule = self._find_assignment(OTScopeType.USER, user_id)
        if rule:
            return rule

        # 2. Walk node ancestors from most specific (leaf) to least (root)
        ancestor_node_ids = self._node_repo.get_ancestor_ids_leaf_first(user_id)
        for node_id in ancestor_node_ids:
            rule = self._find_assignment(OTScopeType.NODE, node_id)
            if rule:
                return rule

        # 3. Union
        rule = self._find_union_assignment(user_id)
        if rule:
            return rule

        # 4. State fallback
        rule = self._find_assignment(OTScopeType.STATE, workplace_state)
        if rule:
            return rule

        raise OTRuleNotFoundError(ErrorCodes.NO_OT_RULE_RESOLVED)
```

### 16.7 Constants for Permission Flags

Never reference permission flag names as string literals. Use the constants file.

```python
# app/constants/permissions.py
class PermissionFlags(StrEnum):
    IS_VIEWER                = "is_viewer"
    IS_DATA_VERIFIED         = "is_data_verified"
    IS_USER_ADMIN            = "is_user_admin"
    IS_ROLE_ADMIN            = "is_role_admin"
    IS_PROJECT_CREATOR       = "is_project_creator"
    IS_PROJECT_EDITOR        = "is_project_editor"
    IS_PROJECT_VIEWER        = "is_project_viewer"
    IS_PROJECT_COST_VIEWER   = "is_project_cost_viewer"
    IS_TIMECARD_SUBMITTER    = "is_timecard_submitter"
    IS_TIMECARD_APPROVER     = "is_timecard_approver"
    IS_TIMECARD_EDITOR       = "is_timecard_editor"
    IS_TIMECARD_VIEWER       = "is_timecard_viewer"
    IS_EXPENSE_SUBMITTER     = "is_expense_submitter"
    IS_EXPENSE_APPROVER      = "is_expense_approver"
    IS_EXPENSE_VIEWER        = "is_expense_viewer"
    IS_EXPENSE_COST_VIEWER   = "is_expense_cost_viewer"
    IS_REPORT_VIEWER         = "is_report_viewer"
    IS_REPORT_EXPORTER       = "is_report_exporter"
    IS_PAYROLL_EXPORTER      = "is_payroll_exporter"
    IS_ESTIMATOR             = "is_estimator"
    IS_ESTIMATE_VIEWER       = "is_estimate_viewer"
    IS_ESTIMATE_IMPORTER     = "is_estimate_importer"
    IS_NODE_ADMIN            = "is_node_admin"
    IS_WORKFLOW_ADMIN        = "is_workflow_admin"
    IS_OT_RULE_ADMIN         = "is_ot_rule_admin"
    IS_PAYROLL_ADMIN         = "is_payroll_admin"

class NodeScopeType(StrEnum):
    ENTERPRISE   = "ENTERPRISE"
    COMPANY      = "COMPANY"
    DIVISION     = "DIVISION"
    DEPARTMENT   = "DEPARTMENT"
    TEAM         = "TEAM"
    PERSONA      = "PERSONA"
    CUSTOM       = "CUSTOM"

class OTScopeType(StrEnum):
    USER    = "USER"
    NODE    = "NODE"
    UNION   = "UNION"
    PROJECT = "PROJECT"
    STATE   = "STATE"
```

### 16.8 Frontend Default-Deny Pattern

On the Svelte frontend, every route that displays node-scoped data follows this pattern. Components render a blank/loading state until `is_data_verified` is confirmed from the API. No partial data, no optimistic rendering of unverified content.

```typescript
// src/stores/permission.store.ts
import { PermissionStatus } from '$lib/constants/permissions.constants'

const _status = writable<PermissionStatus>(PermissionStatus.UNVERIFIED)
const _permission = writable<VerifiedPermission | null>(null)

export const permissionStore = {
  status:     { subscribe: _status.subscribe },
  permission: { subscribe: _permission.subscribe },

  async verify(nodeId: string, requiredFlag: PermissionFlag): Promise<void> {
    _status.set(PermissionStatus.LOADING)
    try {
      const perm = await verifyNodePermission(nodeId, requiredFlag)
      _permission.set(perm)
      _status.set(PermissionStatus.VERIFIED)
    } catch {
      _permission.set(null)
      _status.set(PermissionStatus.DENIED)
    }
  }
}
```

```svelte
<!-- Every data page waits for VERIFIED before rendering -->
{#if $permissionStore.status === PermissionStatus.LOADING}
  <LoadingSpinner />
{:else if $permissionStore.status === PermissionStatus.VERIFIED}
  <TimecardGrid {entries} />
{:else if $permissionStore.status === PermissionStatus.DENIED}
  <AccessDenied />   <!-- no detail about why or whether node exists -->
{/if}
```


Significant technical decisions are documented as ADRs in `/docs/adr/`. ADRs are short — they record the context, the decision, and the consequences. They are not changed once accepted; if a decision is reversed, a new ADR supersedes the old one.

### ADR Template

```markdown
# ADR-{NNN}: {Short Title}

**Date:** YYYY-MM-DD  
**Status:** Proposed | Accepted | Superseded by ADR-{NNN}

## Context
What situation or problem prompted this decision?

## Decision
What did we decide to do?

## Consequences
What are the positive and negative results of this decision?
What is now easier? What is now harder?
```

### Required ADRs Before Development Starts

| # | Topic | Why It Must Be Decided First |
|---|-------|------------------------------|
| ADR-001 | Offline mobile strategy (queue or require connectivity) | Changes entire mobile architecture |
| ADR-002 | Geocoding provider (Google Maps vs Azure Maps) | API key procurement and cost model |
| ADR-003 | Blob storage provider (Azure Blob vs S3) | Receipt and photo upload pipeline |
| ADR-004 | Payroll system target + file format | Determines sync output schema |
| ADR-005 | SSO provider (single Azure AD tenant or multi-IdP) | Auth architecture |
| ADR-006 | Composite tax handling (combined rate vs line-item breakdown) | Tax report accuracy |
| ADR-007 | Mobile app distribution (App Store vs enterprise MDM) | Build and signing pipeline |
| ADR-008 | Org hierarchy model: closure table chosen over adjacency list / nested sets | Subtree queries in single join; tradeoff is insert/move cost on closure table maintenance |
