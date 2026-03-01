<!--
📋 SYNC IMPACT REPORT — Constitution Update to v1.0.0
═══════════════════════════════════════════════════════════════════════════

VERSION CHANGE:
  [UNVERSIONED] → v1.0.0 (MAJOR: Initial constitution establishment)

MODIFIED PRINCIPLES:
  - All principles newly defined based on existing architectural patterns

ADDED SECTIONS:
  ✓ Core Principles (5 principles)
  ✓ Development Standards (technology stack, code quality)
  ✓ Quality Assurance (validation, testing, documentation)
  ✓ Governance (versioning, amendments, compliance)

REMOVED SECTIONS:
  - None (initial version)

TEMPLATES STATUS:
  ✅ .github/copilot-instructions.md — Aligned with constitution
  ✅ .specify/templates/plan-template.md — Updated with constitution checklist
  ✅ .specify/templates/spec-template.md — Updated with constitutional requirements note
  ✅ .specify/templates/tasks-template.md — Updated with validation checklist

FOLLOW-UP TODOS:
  - Add constitution compliance checks to CI/CD pipeline (future)
  - Create constitution training materials for new contributors (future)
  - Review quarterly for constitutional compliance

═══════════════════════════════════════════════════════════════════════════
-->

# Portfolio Manager v2 Constitution

## Core Principles

### I. Immutability of Financial Events (NON-NEGOTIABLE)

**Every financial action (buy or sell) MUST be represented as a new, immutable operation.**

Rules:
- Operations are events, not mutable state
- NEVER mutate an existing operation to represent a sale
- A sale MUST always be a new record with `movement_type = "VENDA"`
- Deletion of operations MUST be explicit and auditable
- Historical operations MUST NEVER be modified to correct errors—create compensating operations instead

**Rationale:** Financial systems demand complete auditability. Every transaction must be traceable for reconciliation, tax reporting, and regulatory compliance. Mutating historical data destroys the audit trail and makes reconciliation with external sources (broker statements, tax authorities) impossible.

---

### II. Idempotency and Data Integrity

**Import operations MUST be idempotent—importing the same source file multiple times MUST NOT create duplicates.**

Rules:
- Deduplication based on logical business key: `trade_date`, `movement_type`, `market`, `institution`, `ticker`, `quantity`, `price`
- Database MUST enforce uniqueness via constraints
- Code MUST handle conflicts gracefully with clear user feedback
- External data sources (B3 Excel reports) MUST be parseable multiple times safely
- Retry operations MUST produce identical results

**Rationale:** Users will inevitably re-upload files. Duplicates corrupt positions, inflate P&L calculations, and create reconciliation nightmares. Idempotency is not optional in financial systems.

---

### III. Clarity Over Premature Abstraction

**Favor explicit, readable code over clever abstractions or premature optimization.**

Rules:
- Code MUST be self-documenting with descriptive names
- Functions MUST be small, single-purpose, and easily testable
- Avoid ORMs—prefer explicit SQL for database operations
- No "God classes" or multi-thousand-line files
- Extract complexity into well-named helper functions
- Configuration MUST be separate from business logic
- YAGNI: Implement only what is needed now

**Rationale:** This project intentionally chooses clarity and maintainability over sophistication. Future senior developers must understand the code quickly. Financial logic is complex enough without adding architectural complexity.

---

### IV. Event-Based Thinking

**Derived values (positions, balances, P&L) MUST be calculated from operations, not stored as authoritative state.**

Rules:
- Operations are the source of truth
- Positions, balances, and P&L are computed views
- Do NOT store derived financial metrics as persistent state (at least initially)
- Aggregations MUST be deterministic and reproducible
- State reconciliation MUST always be possible from operation history

**Rationale:** Storing derived state creates synchronization problems and data integrity risks. When bugs occur in calculation logic, stored state becomes permanently incorrect. Event sourcing ensures correctness can always be restored by recalculating from source events.

---

### V. Simplicity as a Feature

**Complexity MUST be justified. Default to the simplest solution that solves the problem.**

Rules:
- Start simple, add complexity only when necessary
- Remove code that isn't being used
- Avoid speculative generality—solve today's problems, not tomorrow's hypothetical ones
- Technology choices MUST favor simplicity: SQLite over PostgreSQL until scale demands it
- No heavy frameworks, complex state management, or over-engineered abstractions
- Every abstraction MUST earn its place by solving multiple concrete problems

**Rationale:** Complexity is a liability. It increases bugs, slows development, and makes onboarding harder. The project explicitly values "clarity, auditability, and correctness over premature abstraction."

---

## Development Standards

### Technology Stack

The following stack is standardized for consistency and simplicity:

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Backend | Python + FastAPI | 3.11+ | Explicit typing, async support, simple deployment |
| Database | SQLite (WAL mode) | 3.x | Zero-configuration, embedded, sufficient for MVP scale |
| Frontend | React + TypeScript | 18.x | Industry standard, strong typing, component architecture |
| Build | Vite | 5.x+ | Fast, modern, simple configuration |
| Containers | Docker Compose | 2.x | Reproducible development environment |
| Market Data | yfinance | 0.2.x+ | Reliable, free, sufficient for Brazilian market |
| Parsing | Pandas + OpenPyXL | Latest | Standard tools for Excel processing |

**Stack changes require explicit justification and constitution amendment.**

---

### Code Quality Requirements

#### Backend (Python/FastAPI)

- Explicit SQL over ORMs
- Type hints on all function signatures
- Explicit exception handling (NO swallowing exceptions)
- Repository pattern for data access
- Services for business logic
- FastAPI dependency injection where appropriate
- Context managers for database connections
- NO SQL injection vulnerabilities—parameterized queries only

#### Frontend (React/TypeScript)

- Strict TypeScript mode (`strict: true`)
- Components MUST be single-responsibility
- Pages orchestrate data; components render UI
- NO inline styles—use centralized theme tokens (`theme.css`)
- Explicit null/undefined handling (NO `!` assertions without justification)
- Loading states, error states, empty states always visible
- NO assumptions about API response shapes

#### Database

- Schema at `/backend/app/data/portfolio.db`
- Migrations OR explicit reset procedures for schema changes
- UNIQUE constraints for business keys
- Foreign keys for referential integrity
- Indexes for performance-critical queries
- NO premature denormalization

---

## Quality Assurance

### Validation Protocol

**Every code change MUST pass validation before being considered complete:**

#### 1. Critical Error Check
- Syntax errors, type mismatches, undefined variables
- Import errors and missing dependencies
- Linter warnings (backend: flake8/black, frontend: ESLint)
- Type checker errors (mypy for Python, tsc for TypeScript)

#### 2. Anti-Pattern Detection
- Mutating operations (violates Principle I)
- Hardcoded values that should be configurable
- Swallowed exceptions without logging
- Database connections without context managers
- Missing error handling in API endpoints
- SQL injection vulnerabilities
- Frontend components without error states

#### 3. Immediate Correction
- If critical errors or anti-patterns found: **FIX IMMEDIATELY**
- Do NOT proceed until code is clean
- Document what was fixed and why

---

### Testing Requirements

**All implementations MUST be tested before commit:**

#### Backend Testing
- Test endpoints with curl or HTTP client (Postman, Thunder Client)
- Verify database operations with sample data
- Test error handling with invalid inputs
- Confirm logging output is correct and meaningful

#### Frontend Testing
- Verify UI renders correctly in browser
- Test user interactions (clicks, form submissions, navigation)
- Validate error states and loading states display correctly
- Check API integration via browser network tab

#### Integration Testing
- Test full workflows (e.g., file upload → import → display → calculation)
- Verify Docker containers restart correctly
- Confirm environment variables load properly
- Test CORS and API communication

---

### Documentation Requirements

**Documentation MUST be updated AFTER every significant implementation:**

#### Documentation Structure

All documentation lives in `docs/` with the following structure:
- `docs/architecture/` — System design decisions and principles
- `docs/api/` — API endpoint documentation
- `docs/guides/` — How-to guides and tutorials
- `docs/development/` — Development workflows and setup
- `docs/deployment/` — Deployment and operations instructions

#### Documentation Standards

- Write in **Portuguese (Brazilian)** for all user-facing docs
- Use clear, simple language (avoid jargon unless necessary)
- Include code examples for complex features
- Add Mermaid diagrams for complex workflows
- Keep examples up-to-date with actual code
- Document WHY decisions were made, not just WHAT was implemented

#### What to Document

- New features: purpose, usage, examples
- API changes: endpoints, request/response formats, error codes
- Configuration changes: environment variables, settings files
- Architecture decisions: reasoning behind technical choices
- Known limitations: what doesn't work yet and why

---

### Validation Checklist

Before marking any task as complete, verify:

- [ ] Code runs without errors
- [ ] No anti-patterns introduced
- [ ] Tests executed successfully (manual or automated)
- [ ] Documentation updated in `docs/`
- [ ] Code is simple enough to document clearly
- [ ] Changes follow all five core principles
- [ ] Git commit message is descriptive and follows conventions

**If ANY item is unchecked, continue working until ALL are complete.**

---

## Governance

### Authority and Compliance

- This constitution supersedes all other practices and guidelines
- All pull requests MUST verify compliance with constitutional principles
- Code reviews MUST explicitly check for principle violations
- Complexity additions MUST be justified in writing

### Amendment Procedure

Constitution changes require:
1. Written proposal with rationale
2. Impact analysis on existing codebase
3. Template synchronization plan
4. Version bump according to semantic rules (see below)
5. Update to this document with change log

### Versioning

Constitution follows semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR:** Backward-incompatible changes (principle removals or redefinitions)
- **MINOR:** New principles added or existing principles materially expanded
- **PATCH:** Clarifications, wording improvements, typo fixes

### Runtime Development Guidance

For operational development instructions and agent-specific guidance, refer to:
- `.github/copilot-instructions.md` — AI assistant operational rules
- `docs/architecture/principios-core.md` — Extended architectural documentation
- `docs/development/setup.md` — Development environment setup

### Compliance Review

Quarterly review of codebase for constitutional compliance recommended.

---

**Version**: 1.0.0 | **Ratified**: 2026-02-22 | **Last Amended**: 2026-02-22
