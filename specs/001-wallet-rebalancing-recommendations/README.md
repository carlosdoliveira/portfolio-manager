# ✅ Planning Complete: Carteiras e Rebalanceamento

**Feature**: 001-wallet-rebalancing-recommendations  
**Branch**: `001-wallet-rebalancing-recommendations`  
**Date**: 2026-02-22  
**Status**: ✅ Phase 0 & 1 Complete - Ready for Implementation

---

## 📋 Artifacts Generated

### Phase 0: Research ✅

- **[research.md](./research.md)** — 7 research decisions covering:
  - Database schema design (3 new tables)
  - Rebalancing algorithm (threshold-based, simple)
  - Frontend UX patterns (cards + drill-down)
  - Integration with existing position_engine
  - Portuguese language coverage strategy
  - Cost estimation formulas
  - Fixed income handling (non-liquid assets)

### Phase 1: Design ✅

- **[data-model.md](./data-model.md)** — Complete data architecture:
  - 3 database tables: `wallets`, `wallet_assets`, `target_allocations`
  - Calculated entities (never persisted): `WalletSummary`, `WalletAllocation`, `RebalancingRecommendation`
  - State transitions and lifecycle diagrams
  - Essential queries and migration scripts

- **[contracts/api.md](./contracts/api.md)** — Full REST API specification:
  - Wallet CRUD endpoints
  - Assets assignment management
  - Target allocations configuration
  - Rebalancing recommendations calculation
  - All request/response schemas in Portuguese

- **[quickstart.md](./quickstart.md)** — Developer and user guides:
  - Local setup instructions
  - Manual testing procedures (curl + browser)
  - End-user step-by-step walkthrough
  - 3 common use cases (Aposentadoria, Crescimento, Dividendos)
  - Troubleshooting guide

- **Agent Context Updated** ✅
  - `.github/agents/copilot-instructions.md` updated with new tech stack

---

## 🎯 Feature Summary

### What It Does

Users can create personalized investment wallets (carteiras) grouped by objective, define target allocations by asset category, and receive intelligent rebalancing recommendations with cost-benefit analysis.

### Key User Stories

1. **P1 - Visualizar Carteiras**: List all wallets with calculated metrics
2. **P2 - Criar Carteiras**: Create custom wallets, assign assets
3. **P3 - Recomendações**: Get rebalancing suggestions with cost analysis
4. **P4 - Execução Guiada**: Step-by-step guided rebalancing (future)

### Constitutional Compliance

✅ **Full Compliance** with all 5 principles:
- **Immutability**: Wallets don't mutate operations; rebalancing creates new immutable operations
- **Idempotency**: Unique constraints prevent duplicates
- **Clarity**: Explicit SQL, small functions, no premature abstraction
- **Event-Based**: All values calculated on-demand from operations
- **Simplicity**: Threshold-based algorithm, no ML or complex optimization

---

## 🏗️ Architecture Decisions

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Database** | 3 SQLite tables | Consistent with existing stack, simple queries |
| **Algorithm** | Threshold-based (5% deviation) | Transparent, easy to understand, democratic |
| **Frontend** | React cards + detail drill-down | Familiar UX pattern, responsive, scalable |
| **Calculations** | On-demand via wallet_calculator.py | Event-based principle, no stored derived state |
| **Language** | 100% Portuguese (BR) | Hard-coded, no i18n overhead for monolingual app |
| **Cost Model** | Configurable constants | Transparent, user-adjustable, sufficient precision |

---

## 📊 Technical Specifications

### Backend Changes

**New Files**:
- `backend/app/repositories/wallets_repository.py` — CRUD operations
- `backend/app/services/wallet_calculator.py` — Allocation calculations
- `backend/app/services/rebalancing_engine.py` — Recommendation algorithm
- `backend/app/tests/test_rebalancing_engine.py` — Unit tests

**Modified Files**:
- `backend/app/main.py` — Add `/api/wallets/*` routes
- `backend/app/db/database.py` — Migration for 3 new tables

### Frontend Changes

**New Files**:
- `frontend/src/pages/Carteiras.tsx` — Main wallets page
- `frontend/src/components/WalletCard.tsx` — Wallet summary card
- `frontend/src/components/WalletForm.tsx` — Create/edit form
- `frontend/src/components/AllocationChart.tsx` — Pie chart (Recharts)
- `frontend/src/components/RebalancingPanel.tsx` — Recommendations panel
- `frontend/src/components/AssetAllocationEditor.tsx` — Target % editor
- `frontend/src/styles/carteiras.css` — Feature-specific styles

**Modified Files**:
- `frontend/src/api/client.ts` — Add wallet API methods
- `frontend/src/App.tsx` — Add `/carteiras` route

### Database Schema

```sql
-- wallets: Main wallet metadata
CREATE TABLE wallets (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    type TEXT CHECK(type IN ('Ações', 'FIIs', 'RF', 'Mista')),
    created_at DATETIME,
    updated_at DATETIME
);

-- wallet_assets: N:M relationship
CREATE TABLE wallet_assets (
    wallet_id INTEGER,
    asset_id INTEGER,
    weight_override REAL CHECK(weight_override BETWEEN 0 AND 100),
    assigned_at DATETIME,
    PRIMARY KEY (wallet_id, asset_id)
);

-- target_allocations: Target percentages per category
CREATE TABLE target_allocations (
    id INTEGER PRIMARY KEY,
    wallet_id INTEGER,
    category TEXT CHECK(category IN ('Ações', 'FIIs', 'RF', 'ETFs', 'Outros')),
    target_percent REAL CHECK(target_percent BETWEEN 0 AND 100),
    UNIQUE(wallet_id, category)
);
```

---

## 🧪 Testing Strategy

### Manual Testing (MVP)

**Backend**:
- curl commands for all endpoints (see quickstart.md)
- Verify database state after CRUD operations
- Test error handling (invalid inputs, missing data)

**Frontend**:
- Browser testing in Chrome/Firefox
- Mobile responsive testing (375px width)
- Loading states, error states, empty states
- Integration with backend via network tab

### Unit Testing (Critical Logic)

**pytest** for:
- `rebalancing_engine.py` — Algorithm correctness
- Edge cases: balanced portfolio, no target allocations, stale quotes
- Cost calculations accuracy

---

## 🚀 Next Steps

### Immediate (Phase 2)

Run `/speckit.tasks` command to generate implementation tasks:

```bash
cd /home/carlosoliveira/Experiments/portfolio-manager-v2
# Command will be available after Phase 1 completion
```

### Implementation Order

1. **Backend Foundation** (1-2 days)
   - Database migration
   - Wallets repository (CRUD)
   - Basic endpoints (GET/POST wallets)

2. **Frontend Foundation** (1-2 days)
   - Carteiras page + routing
   - WalletCard component
   - WalletForm component
   - List view working

3. **Calculations** (2-3 days)
   - wallet_calculator.py
   - Integration with position_engine
   - Allocation endpoints
   - AllocationChart component

4. **Rebalancing** (2-3 days)
   - rebalancing_engine.py
   - Recommendation endpoint
   - RebalancingPanel component
   - Cost-benefit display

5. **Polish** (1 day)
   - Error handling
   - Loading states
   - Documentation
   - Manual testing

**Estimated Total**: 7-10 days development time

---

## 📚 Documentation Location

- **Spec**: `/specs/001-wallet-rebalancing-recommendations/spec.md`
- **Plan**: `/specs/001-wallet-rebalancing-recommendations/plan.md`
- **Research**: `/specs/001-wallet-rebalancing-recommendations/research.md`
- **Data Model**: `/specs/001-wallet-rebalancing-recommendations/data-model.md`
- **API Contracts**: `/specs/001-wallet-rebalancing-recommendations/contracts/api.md`
- **Quickstart**: `/specs/001-wallet-rebalancing-recommendations/quickstart.md`
- **Constitution**: `/.specify/memory/constitution.md`

---

## ⚠️ Known Constraints & Risks

### Constraints

1. **Single-user MVP**: No multi-tenancy, all data belongs to single user
2. **Manual quote updates**: Rebalancing requires updated quotes (user responsibility)
3. **Simplified cost model**: Uses configurable constants, not real-time broker APIs
4. **No automatic execution**: User must manually create operations from suggestions

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Stale quotes | High - wrong recommendations | Validate quote freshness, alert if > 24h |
| Complex portfolios | Medium - slow calculations | Limit 20 assets/wallet initially |
| User misunderstanding | Medium - wrong actions | Clear tooltips, educational content in PT-BR |
| Algorithm too aggressive | Low - impractical suggestions | Show net benefit, allow threshold adjustment |

---

## ✅ Constitutional Re-Check (Post-Design)

All principles verified after Phase 1 design:

- [x] **Principle I: Immutability** — ✅ No mutation of operations
- [x] **Principle II: Idempotency** — ✅ Unique constraints enforced
- [x] **Principle III: Clarity** — ✅ Explicit SQL, small functions
- [x] **Principle IV: Event-Based** — ✅ All values calculated on-demand
- [x] **Principle V: Simplicity** — ✅ Threshold algorithm, no complexity
- [x] **Code Quality** — ✅ TypeScript strict, Python type hints
- [x] **Testing** — ✅ Manual + pytest for critical logic
- [x] **Documentation** — ✅ Comprehensive docs in Portuguese

**Final Compliance**: ✅ **APPROVED** - No violations, no justified exceptions

---

## 🎉 Ready for Implementation

This feature has completed planning phases:
- ✅ Phase 0: Research (all unknowns resolved)
- ✅ Phase 1: Design (data model, contracts, quickstart)
- ✅ Constitution check passed
- ✅ Agent context updated

**Status**: 🟢 **READY FOR PHASE 2** — Task breakdown and implementation

---

**Generated**: 2026-02-22 by `/speckit.plan` command  
**Branch**: `001-wallet-rebalancing-recommendations`  
**Approved**: Constitutional compliance verified
