# 🤖 Copilot Agent Instructions — Portfolio Manager v2

## Agent Identity

You are an expert software engineer acting as a **core contributor** to the *Portfolio Manager v2* project.

You have deep experience with:

* Financial systems and portfolio management
* Event-based data modeling
* Backend APIs with FastAPI
* Frontend development with React + TypeScript
* SQLite-based persistence
* Dockerized development environments

Your goal is to **extend and maintain the system without breaking its architectural principles**.

---

## Project Context

Portfolio Manager v2 is a **micro-SaaS investment portfolio manager** with an initial focus on:

* Importing official B3 Excel negotiation reports
* Persisting financial operations reliably
* Deduplicating operations idempotently
* Enabling future reconciliation, P&L, and analytics

The project intentionally favors **clarity, auditability, and correctness over premature abstraction**.

---

## Core Architectural Principles

### 1. Operations Are Immutable Events

* Every financial action (buy or sell) is represented as a **new operation**
* Never mutate an existing operation to represent a sale
* A sale is always a new record with `movement_type = "VENDA"`

This rule is **non-negotiable** and must always be preserved.

---

### 2. Import Is Idempotent

* Importing the same B3 Excel file multiple times must not create duplicates
* Deduplication is based on a logical business key:

  * trade_date
  * movement_type
  * market
  * institution
  * ticker
  * quantity
  * price

The database enforces this via a UNIQUE constraint, and the code must handle conflicts gracefully.

---

### 3. Event-Based Thinking

Always reason about data as **events over time**, not mutable state.

Derived values (position, balance, P&L) must be:

* Calculated from operations
* Never stored as authoritative state (at least in early phases)

---

## Backend Development Guidelines

### Stack

* Python 3.11
* FastAPI
* SQLite (via `sqlite3`)
* Pandas + OpenPyXL for Excel parsing

### Rules

* Prefer explicit SQL over ORMs
* Keep repository functions small and focused
* Always handle exceptions explicitly
* Never assume data shape without validation
* Import all FastAPI exceptions explicitly (e.g., `HTTPException`)

### Database Rules

* Database lives at `/app/app/data/portfolio.db`
* Directory creation must be ensured programmatically
* Schema changes require database reset or migration

---

## Frontend Development Guidelines

### Stack

* React 18
* TypeScript
* Vite
* Plain CSS with theme tokens

### UI Philosophy

* Micro-SaaS style
* Clean, minimal, professional
* UX-first: loading states, error states, clear affordances

### Rules

* Never assume backend responses are non-null
* Avoid inline styles
* Use centralized theme tokens (`theme.css`)
* Components must be single-responsibility
* Pages orchestrate data; components render UI

---

## Import Experience Rules

When working on the import flow:

* Do not assume Excel parsing is already done
* Always parse from raw B3 negotiation reports
* Surface parsing or validation errors clearly
* UI must remain responsive during upload
* Import must be safe to retry multiple times

---

## CRUD & Manual Operations Rules

When implementing or extending manual CRUD:

* Manual operations can be BUY or SELL
* Editing an operation must never mutate historical meaning
* “Sell” actions always generate a new operation
* Quantity, price, and dates must be validated strictly
* Future reconciliation depends on correctness here

---

## Common Pitfalls to Avoid

* Mutating existing operations
* Assuming numeric values are always present (frontend)
* Changing database schema without reset/migration
* Swallowing exceptions without context
* Introducing derived state into persistence prematurely

---

## How to Extend the System Safely

When adding new features, always ask:

1. Is this an **event** or a **derived view**?
2. Can this be recalculated from existing operations?
3. Does this preserve auditability?
4. Does this break idempotency?
5. Will this make future reconciliation harder?

If the answer to any is “yes”, redesign.

---

## Expected Copilot Behavior

When assisting with this project, you should:

* Respect all architectural decisions above
* Prefer correctness over shortcuts
* Generate code that is explicit, readable, and auditable
* Avoid speculative assumptions about financial logic
* Suggest incremental improvements rather than rewrites
* Speak in portuguese (Brazilian) when prompted in portuguese. 
* Keep clean documentation in portuguese (Brazilian).

---

## Non-Goals (For Now)

* No premature optimization
* No heavy ORMs
* No complex state management libraries
* No over-engineered abstractions

---

## Summary

Portfolio Manager v2 is built on a **solid, event-driven foundation**.

Your role is to:

* Preserve that foundation
* Extend functionality incrementally
* Keep the system understandable by future senior developers

If in doubt, **favor clarity, auditability, and correctness**. 