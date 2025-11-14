# Implementation Plan: ESRS Environmental Topics (E1-E5) Financial Impact Assessment

**Branch**: `001-esrs-e1-simulation` | **Date**: 2025-11-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-esrs-e1-simulation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Calculate financial costs for ESRS environmental topics (E1: Climate, E2: Pollution, E3: Water, E4: Biodiversity, E5: Circular Economy) using scenario-based cost modeling with double materiality framework. Extract company environmental data from annual/sustainability reports (Scope 1/2/3 emissions, revenue, environmental metrics), apply climate scenarios (IEA, NGFS) with influence factors (CO2 prices, energy prices, regulatory stringency, technology costs, physical impacts), and calculate costs across categories (carbon pricing, transition, physical risk, compliance) with confidence intervals. Output results in CSV format with complete audit trails for ESRS assurance.

## Technical Context

**Language/Version**: Python 3.11+ (chosen for scientific computing ecosystem, NumPy/CuPy GPU acceleration capability, strong statistical libraries)
**Primary Dependencies**: NEEDS CLARIFICATION (CuPy for GPU-accelerated numerical computation, NumPy for array operations, Pandas for data manipulation, SciPy for statistical methods, SQLite driver for database access)
**Storage**: SQLite (single-user local database, schema-defined, user-populated with company report data)
**Testing**: pytest (unit tests, integration tests, contract tests for cost calculation validation)
**Target Platform**: Windows/Linux/macOS desktop (single-user local execution environment)
**Project Type**: Single project (command-line tool with library structure)
**Performance Goals**: <60 seconds for complete ESRS E1-E5 cost assessment (typical SME dataset: Scope 1/2/3 emissions + revenue); <5 seconds for single-topic calculation
**Constraints**: Single-user execution, no network dependency, CSV output only, file system security only, must handle sparse/incomplete data gracefully
**Scale/Scope**: Designed for individual corporate datasets (1 company at a time), support for 5 ESRS topics (E1-E5), multiple scenarios (5-10 predefined + custom), hundreds of influence factor combinations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Scientific Accuracy (NON-NEGOTIABLE)

- ✅ **PASS**: Feature requires ESRS-compliant cost calculations based on recognized climate standards (IEA, NGFS scenarios, GHG Protocol carbon accounting)
- ✅ **PASS**: All cost methodologies must reference authoritative sources (ESRS technical standards, climate economics literature)
- ✅ **PASS**: Calculations must be reproducible with documented assumptions (scenario parameters, influence factor correlations, imputation methods)
- **Action Required**: Identify authoritative sources for cost calculation methodologies in Phase 0 research

### II. Test-First Development (NON-NEGOTIABLE)

- ✅ **PASS**: Feature requires contract tests for cost calculation outputs (stable CSV format, expected columns, confidence interval validation)
- ✅ **PASS**: Unit tests required for financial quantification models (known cost inputs → expected cost outputs)
- ✅ **PASS**: Integration tests required for ESRS compliance logic (double materiality classification, scenario application, influence factor correlation)
- ✅ **PASS**: Data transformation validation tests (report data extraction, interpolation for missing values, suspicious value flagging)
- **Action Required**: Define test datasets with known cost outcomes for TDD validation

### III. Performance & Scalability

- ✅ **PASS**: Performance target (<60 seconds for E1-E5 assessment) aligns with constitution target (<60 seconds for large enterprise dataset)
- ⚠️ **REVIEW NEEDED**: Constitution mentions "millions of data points" and "parallel computation for complex simulations"
  - **This feature**: Company report data is single-year snapshots (not time-series), modest data volumes (dozens to hundreds of metrics per company)
  - **Assessment**: Performance targets are appropriate; CuPy GPU acceleration may be overkill for current scope but supports future extensions
- **Action Required**: Profile actual computational bottlenecks in Phase 1; determine if CuPy GPU acceleration is justified vs NumPy CPU-only

### IV. Data Integrity & Traceability

- ✅ **PASS**: Feature requires complete audit trails (FR-015: methodology, data sources, scenario assumptions, influence factors, imputations)
- ✅ **PASS**: Input validation with clear error messages (FR-011: schema validation, sparse data warnings)
- ✅ **PASS**: Data lineage tracking (company report data → cost calculations → CSV output with traceability)
- ✅ **PASS**: Suspicious value flagging with reasons (FR-013: negative costs, extreme outliers, threshold violations)
- **Action Required**: Define audit trail CSV schema and structured logging format in Phase 1

### V. Simplicity & Maintainability

- ✅ **PASS**: Single project structure (no unnecessary abstraction layers)
- ✅ **PASS**: Clear domain naming (ESRS terminology: E1-E5 topics, double materiality, influence factors, scenarios)
- ✅ **PASS**: MVP-first approach (P1: basic cost calculation, P2: scenario comparison, P3: custom correlations)
- ⚠️ **REVIEW NEEDED**: CuPy dependency adds complexity
  - **Rationale**: User explicitly requested CuPy in original description; GPU acceleration may benefit large-scale Monte Carlo uncertainty quantification for confidence intervals
  - **Mitigation**: Make CuPy optional (fall back to NumPy if not available); implement NumPy version first, CuPy optimization second
- **Action Required**: Evaluate CuPy necessity in Phase 0 research; document simpler NumPy-only alternative

**Overall Gate Status (Pre-Design)**: ✅ **CONDITIONAL PASS** - Proceed to Phase 0 research with actions:
1. Research CuPy vs NumPy for cost calculation workload (decide if GPU acceleration justified)
2. Identify authoritative cost methodology sources (ESRS, climate economics, carbon pricing literature)
3. Define test datasets with known cost outcomes for TDD

---

## Constitution Check Re-Evaluation (Post-Design)

*GATE: Re-checked after Phase 1 design completion*

### I. Scientific Accuracy (NON-NEGOTIABLE)

- ✅ **PASS**: Research identified authoritative sources (IEA, NGFS, IPCC for scenarios; ESRS, GHG Protocol for methodologies)
- ✅ **PASS**: Data model includes `methodology_documentation_reference` for all cost calculations
- ✅ **PASS**: Database schema enforces data validation constraints
- ✅ **PASS**: Test fixtures defined with known cost outcomes for validation

### II. Test-First Development (NON-NEGOTIABLE)

- ✅ **PASS**: Test structure defined (unit, integration, contract tests in separate directories)
- ✅ **PASS**: Contract tests will validate CSV output schema stability
- ✅ **PASS**: Test fixtures with known outcomes enable TDD workflow (research.md section 4)
- ✅ **PASS**: Quickstart includes TDD workflow instructions

### III. Performance & Scalability

- ✅ **PASS**: NumPy-first approach selected (simpler, meets performance targets)
- ✅ **PASS**: CuPy deferred to Phase 2 optimization if profiling shows need
- ✅ **PASS**: Database indexes defined for query performance
- ✅ **PASS**: Single project structure supports efficient development

### IV. Data Integrity & Traceability

- ✅ **PASS**: Audit trail CSV schema defined (separate from main results)
- ✅ **PASS**: Data model includes suspicious value flagging with reasons
- ✅ **PASS**: Database schema enforces referential integrity (foreign keys)
- ✅ **PASS**: CSV output includes methodology references and calculation timestamps

### V. Simplicity & Maintainability

- ✅ **PASS**: Dependencies minimized to essential libraries (NumPy, Pandas, SciPy, pytest)
- ✅ **PASS**: Clear domain structure (models, services, calculations, data, validation, output)
- ✅ **PASS**: CuPy complexity avoided in MVP
- ✅ **PASS**: Standard library used where possible (csv, json, argparse, logging)

**Overall Gate Status (Post-Design)**: ✅ **FULL PASS** - All constitution principles satisfied. Ready for `/speckit.tasks` and implementation.

## Project Structure

### Documentation (this feature)

```text
specs/001-esrs-e1-simulation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── cost-calculation-input.schema.json
│   ├── cost-calculation-output.csv.schema
│   └── database-schemas.sql
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/              # Data models for entities (Company, Scenario, InfluenceFactor, CostResult)
├── services/            # Business logic (CostCalculator, ScenarioEngine, CorrelationModel)
├── calculations/        # Cost calculation implementations (CarbonPricing, TransitionCost, PhysicalRisk, Compliance)
├── data/                # Data access layer (SQLite database interactions, schema definitions)
├── interpolation/       # Missing data handling (statistical interpolation methods)
├── validation/          # Input validation and suspicious value detection
├── output/              # CSV output generation with audit trails
└── cli/                 # Command-line interface (main entry point)

tests/
├── contract/            # CSV output format validation, cost calculation stability tests
├── integration/         # End-to-end cost calculation flows, scenario application tests
├── unit/                # Individual calculation components, correlation models, interpolation methods
└── fixtures/            # Test data (known company data, expected cost outcomes, reference scenarios)

data/
└── master_climate_sim.db  # SQLite database (schema defined, user-populated)

config/
└── scenarios/           # Predefined scenario definitions (IEA, NGFS JSON files)
```

**Structure Decision**: Selected **single project structure** because:
- Command-line tool with library components (no web frontend, no mobile app)
- Single-user local execution (no client-server architecture needed)
- Calculation logic can be cleanly organized into services and models
- Tests structured by type (contract, integration, unit) per constitution requirements

