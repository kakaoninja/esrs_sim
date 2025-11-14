# Implementation Tasks: ESRS Environmental Topics (E1-E5) Financial Impact Assessment

**Feature**: 001-esrs-e1-simulation
**Branch**: `001-esrs-e1-simulation`
**Generated**: 2025-11-14

## Implementation Strategy

**Approach**: Test-Driven Development (TDD) with incremental delivery by user story
**MVP Scope**: User Story 1 only (P1: ESRS Topic Financial Cost Calculation)
**Constitution Compliance**: All tasks follow TDD (Principle II), scientific accuracy (Principle I), and simplicity (Principle V)

### Delivery Phases

1. **Phase 1**: Setup - Project initialization, dependencies, database schema
2. **Phase 2**: Foundational - Core models, data access, test fixtures (blocking prerequisites)
3. **Phase 3**: User Story 1 (P1) - Basic ESRS cost calculation with CSV output [MVP]
4. **Phase 4**: User Story 4 (P2) - Double materiality assessment logic
5. **Phase 5**: User Story 2 (P2) - Multi-scenario comparison analysis
6. **Phase 6**: User Story 3 (P3) - Custom correlation modeling
7. **Phase 7**: Polish - Performance optimization, documentation, edge case handling

### User Story Priorities (from spec.md)

- **P1**: User Story 1 - ESRS Topic Financial Cost Calculation (Core MVP)
- **P2**: User Story 4 - Double Materiality Assessment
- **P2**: User Story 2 - Multi-Scenario Comparison Analysis
- **P3**: User Story 3 - Influence Factor Correlation Modeling

---

## Phase 1: Setup (Project Initialization)

**Goal**: Initialize Python project structure, dependencies, and database schema

**Prerequisites**: None

**Tasks**:

- [ ] T001 Create Python project structure (src/, tests/, data/, config/ directories) per plan.md
- [ ] T002 Create requirements.txt with dependencies: numpy>=1.24, pandas>=2.0, scipy>=1.10, pytest>=7.4
- [ ] T003 Create .gitignore for Python (venv/, __pycache__/, *.pyc, data/*.db, results/)
- [ ] T004 [P] Create README.md with project overview and quickstart instructions
- [ ] T005 [P] Initialize SQLite database schema from contracts/database-schemas.sql at data/master_climate_sim.db
- [ ] T006 [P] Create config/scenarios/ directory for predefined scenario JSON files
- [ ] T007 [P] Create src/__init__.py and module structure (models/, services/, calculations/, data/, interpolation/, validation/, output/, cli/)
- [ ] T008 [P] Create tests/__init__.py and test structure (unit/, integration/, contract/, fixtures/)

**Completion Criteria**: Project structure exists, dependencies installable, database schema loaded

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Implement core models, data access layer, and test fixtures that all user stories depend on

**Prerequisites**: Phase 1 complete

**Foundational Tasks**:

### Test Fixtures (Constitution Principle II: Test-First)

- [ ] T009 Create test fixtures directory tests/fixtures/ with __init__.py
- [ ] T010 Create tests/fixtures/company_simple.json (minimal test company per research.md section 4)
- [ ] T011 [P] Create tests/fixtures/company_complex.json (comprehensive test company)
- [ ] T012 [P] Create tests/fixtures/scenario_simple_carbon_price.json (basic scenario)
- [ ] T013 [P] Create tests/fixtures/scenario_iea_nz2050.json (IEA Net Zero 2050 scenario)
- [ ] T014 [P] Create tests/fixtures/expected_costs_simple.json (known cost outcomes for simple company)
- [ ] T015 [P] Create tests/fixtures/expected_costs_complex.json (known cost outcomes for complex company)

### Core Data Models

- [ ] T016 Create src/models/__init__.py
- [ ] T017 Create src/models/company.py with CompanyProfile and CompanyReportData classes (dataclasses matching data-model.md)
- [ ] T018 [P] Create src/models/scenario.py with ClimateScenario class
- [ ] T019 [P] Create src/models/influence_factor.py with InfluenceFactor and InfluenceFactorValues classes
- [ ] T020 [P] Create src/models/correlation.py with CorrelationModel and InfluenceFactorCorrelation classes
- [ ] T021 [P] Create src/models/cost.py with CostCategory, CostCalculationConfiguration, CostAssessmentResult classes

### Data Access Layer

- [ ] T022 Create src/data/__init__.py
- [ ] T023 Create src/data/database.py with SQLite connection management and schema validation
- [ ] T024 Create src/data/company_repository.py with methods: get_company_profile(), get_company_report_data(), upsert_company()
- [ ] T025 [P] Create src/data/scenario_repository.py with methods: get_scenario(), list_scenarios(), upsert_scenario()
- [ ] T026 [P] Create src/data/influence_factor_repository.py with methods: get_factor(), get_factor_values(), upsert_factor()
- [ ] T027 [P] Create src/data/correlation_repository.py with methods: get_model(), get_correlations(), upsert_model()
- [ ] T028 [P] Create src/data/cost_repository.py with methods: save_calculation_config(), save_results(), get_results()

**Completion Criteria**: All foundational models and data access implemented, test fixtures ready for use

---

## Phase 3: User Story 1 (P1) - ESRS Topic Financial Cost Calculation [MVP]

**Goal**: Implement core cost calculation functionality for ESRS E1-E5 topics with CSV output

**Independent Test**: Load test company data, select scenario, receive CSV with cost estimates and confidence intervals for each ESRS topic

**Prerequisites**: Phase 2 complete

**User Story 1 Tasks**:

### Contract Tests (TDD - Write Tests First)

- [ ] T029 [US1] Create tests/contract/test_csv_output_format.py - validate CSV schema matches contracts/cost-output.csv.schema
- [ ] T030 [US1] Create tests/contract/test_cost_calculation_stability.py - verify same inputs always produce same outputs (±1% tolerance)

### Unit Tests for Calculations (TDD - Write Tests First)

- [ ] T031 [US1] Create tests/unit/test_carbon_pricing_calculator.py using test fixtures with known outcomes
- [ ] T032 [P] [US1] Create tests/unit/test_transition_cost_calculator.py using test fixtures
- [ ] T033 [P] [US1] Create tests/unit/test_physical_risk_calculator.py using test fixtures
- [ ] T034 [P] [US1] Create tests/unit/test_compliance_cost_calculator.py using test fixtures
- [ ] T035 [P] [US1] Create tests/unit/test_confidence_interval_calculator.py - test interval calculation with known distributions

### Validation & Interpolation

- [ ] T036 [US1] Create src/validation/__init__.py
- [ ] T037 [US1] Create src/validation/data_validator.py with validate_company_data(), validate_scenario() methods
- [ ] T038 [US1] Create src/validation/suspicious_value_detector.py with detect_negative_cost(), detect_extreme_outlier() methods
- [ ] T039 [P] [US1] Create src/interpolation/__init__.py
- [ ] T040 [P] [US1] Create src/interpolation/missing_data_handler.py with interpolate_emissions(), document_imputation() methods using SciPy

### Cost Calculation Implementations

- [ ] T041 [US1] Create src/calculations/__init__.py
- [ ] T042 [US1] Implement src/calculations/carbon_pricing.py with CarbonPricingCalculator class (Scope 1+2+3 * CO2 price)
- [ ] T043 [P] [US1] Implement src/calculations/transition_cost.py with TransitionCostCalculator class (technology capex estimates)
- [ ] T044 [P] [US1] Implement src/calculations/physical_risk.py with PhysicalRiskCalculator class (climate adaptation costs)
- [ ] T045 [P] [US1] Implement src/calculations/compliance_cost.py with ComplianceCostCalculator class (reporting infrastructure)
- [ ] T046 [P] [US1] Create src/calculations/confidence_calculator.py with ConfidenceIntervalCalculator class (analytical or Monte Carlo)

### Core Service (Cost Calculator)

- [ ] T047 [US1] Create src/services/__init__.py
- [ ] T048 [US1] Implement src/services/cost_calculator.py with CostCalculatorService class - orchestrates all calculators for all ESRS topics
- [ ] T049 [US1] Add apply_influence_factors() method to CostCalculatorService - applies scenario-specific factor values
- [ ] T050 [US1] Add apply_correlations() method to CostCalculatorService - applies correlation strengths to factor contributions

### CSV Output Generation

- [ ] T051 [US1] Create src/output/__init__.py
- [ ] T052 [US1] Implement src/output/csv_generator.py with CsvOutputGenerator class - generates main results CSV
- [ ] T053 [US1] Add generate_audit_trail_csv() method - generates separate audit trail CSV with imputation/correlation logs
- [ ] T054 [US1] Add format_cost_result() method - formats CostAssessmentResult to CSV row per contracts schema

### CLI Interface

- [ ] T055 [US1] Create src/cli/__init__.py
- [ ] T056 [US1] Implement src/cli/main.py with argparse - subcommand: calculate --company-id --scenario-id --topics --output
- [ ] T057 [US1] Add load_company_data() function - retrieves company from database
- [ ] T058 [US1] Add load_scenario() function - retrieves scenario from database
- [ ] T059 [US1] Add execute_calculation() function - calls CostCalculatorService and saves results

### Integration Tests (TDD - After Implementation)

- [ ] T060 [US1] Create tests/integration/test_e2e_cost_calculation.py - full flow: load test company → calculate → verify CSV output matches expected costs

**User Story 1 Acceptance Criteria**:
1. ✅ Test company (simple) loaded, scenario selected, CSV generated with E1-E5 costs
2. ✅ All cost categories (carbon_pricing, transition, physical_risk, compliance) present for applicable topics
3. ✅ CSV includes methodology references, scenario assumptions, influence factor contributions
4. ✅ Audit trail CSV documents any data imputation performed
5. ✅ Contract tests pass (CSV schema stable)
6. ✅ Unit tests pass (calculations match known outcomes ±1%)

---

## Phase 4: User Story 4 (P2) - Double Materiality Assessment

**Goal**: Implement materiality classification logic (financial vs impact materiality)

**Independent Test**: System classifies ESRS topics correctly, simulates only impact materiality topics

**Prerequisites**: Phase 3 (US1) complete

**User Story 4 Tasks**:

### Unit Tests (TDD - Write Tests First)

- [ ] T061 [US4] Create tests/unit/test_materiality_classifier.py - test classification rules per ESRS double materiality framework

### Materiality Logic

- [ ] T062 [US4] Create src/services/materiality_classifier.py with MaterialityClassifier class
- [ ] T063 [US4] Implement classify_topic() method - returns "financial", "impact", or "both" for each ESRS topic based on company data
- [ ] T064 [US4] Implement get_simulation_topics() method - filters topics requiring scenario-based simulation (impact materiality)
- [ ] T065 [US4] Update CostCalculatorService to call MaterialityClassifier before calculations

### CLI Enhancement

- [ ] T066 [US4] Update src/cli/main.py to add --materiality-approach flag (financial/impact/both)
- [ ] T067 [US4] Add display_materiality_classification() function - shows classification rationale in CLI output

### Integration Tests

- [ ] T068 [US4] Create tests/integration/test_materiality_assessment.py - verify correct topic filtering based on materiality

**User Story 4 Acceptance Criteria**:
1. ✅ System identifies which topics need impact simulation vs direct calculation
2. ✅ Simulations run only for impact materiality topics when specified
3. ✅ Classification rationale included in output

---

## Phase 5: User Story 2 (P2) - Multi-Scenario Comparison Analysis

**Goal**: Enable cost calculation across multiple scenarios with comparison output

**Independent Test**: Run calculation with 3 scenarios, receive comparative CSV showing cost differences and drivers

**Prerequisites**: Phase 3 (US1) complete

**User Story 2 Tasks**:

### Unit Tests (TDD - Write Tests First)

- [ ] T069 [US2] Create tests/unit/test_scenario_comparator.py - test scenario difference calculations and driver identification

### Scenario Comparison Service

- [ ] T070 [US2] Create src/services/scenario_comparator.py with ScenarioComparator class
- [ ] T071 [US2] Implement compare_scenarios() method - calculates cost differences between scenarios for same company
- [ ] T072 [US2] Implement identify_key_drivers() method - determines which scenario parameters cause largest cost variations
- [ ] T073 [US2] Implement calculate_sensitivity() method - shows cost sensitivity to individual scenario parameters

### CSV Output Enhancement

- [ ] T074 [US2] Update src/output/csv_generator.py to add generate_scenario_comparison_csv() method
- [ ] T075 [US2] Add format_scenario_comparison() method - formats multi-scenario results with difference columns

### CLI Enhancement

- [ ] T076 [US2] Update src/cli/main.py to add compare subcommand: compare --company-id --scenarios <list> --topics --output
- [ ] T077 [US2] Add execute_comparison() function - iterates scenarios, calls ScenarioComparator, generates comparison CSV

### Integration Tests

- [ ] T078 [US2] Create tests/integration/test_scenario_comparison.py - run with 3 scenarios, verify comparison CSV correct

**User Story 2 Acceptance Criteria**:
1. ✅ Multiple scenarios processed for same company
2. ✅ Comparison CSV shows cost differences by topic and scenario
3. ✅ Key drivers identified (e.g., "CO2 price difference accounts for 60% of E1 variation")

---

## Phase 6: User Story 3 (P3) - Influence Factor Correlation Modeling

**Goal**: Allow custom correlation configuration and model comparison

**Independent Test**: Define custom correlations (0-1 float), run calculation, verify correlation effects in output

**Prerequisites**: Phase 3 (US1) complete

**User Story 3 Tasks**:

### Unit Tests (TDD - Write Tests First)

- [ ] T079 [US3] Create tests/unit/test_correlation_configurator.py - test correlation validation (0-1 range, confidence levels)
- [ ] T080 [P] [US3] Create tests/unit/test_correlation_model_comparator.py - test model performance comparison logic

### Correlation Configuration

- [ ] T081 [US3] Create src/services/correlation_configurator.py with CorrelationConfigurator class
- [ ] T082 [US3] Implement validate_correlation_strength() method - ensures 0.0-1.0 range
- [ ] T083 [US3] Implement validate_confidence_level() method - ensures 0.0-1.0 range
- [ ] T084 [US3] Implement create_custom_model() method - inserts new CorrelationModel with custom correlations into database

### Model Comparison

- [ ] T085 [US3] Create src/services/correlation_model_comparator.py with ModelComparator class
- [ ] T086 [US3] Implement compare_models() method - runs calculations with different models, compares outcomes
- [ ] T087 [US3] Implement calculate_confidence_metrics() method - shows how correlation uncertainty affects cost confidence intervals

### CLI Enhancement

- [ ] T088 [US3] Update src/cli/main.py to add --correlation-model flag to calculate subcommand
- [ ] T089 [US3] Add configure-correlations subcommand: configure-correlations --model-name --factor-id --topic --category --strength --confidence
- [ ] T090 [US3] Add compare-models subcommand: compare-models --company-id --scenario-id --models <list> --output

### Integration Tests

- [ ] T091 [US3] Create tests/integration/test_custom_correlations.py - create custom model, run calculation, verify correlation effects

**User Story 3 Acceptance Criteria**:
1. ✅ Custom correlation strengths (0-1 float) configurable
2. ✅ Calculations use configured correlations
3. ✅ Confidence metrics reflect correlation uncertainty
4. ✅ Model comparison shows how correlation assumptions affect outcomes

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Performance optimization, comprehensive edge case handling, documentation

**Prerequisites**: Phases 3-6 complete (all user stories implemented)

**Polish Tasks**:

### Edge Case Handling

- [ ] T092 Implement missing influence factor data handling in src/validation/data_validator.py (use baseline values or skip factor)
- [ ] T093 [P] Implement zero/near-zero baseline emissions handling in src/calculations/ (avoid division by zero, use absolute costs)
- [ ] T094 [P] Implement cross-topic factor allocation in CostCalculatorService (distribute shared factor impacts proportionally)
- [ ] T095 [P] Implement scenario parameter conflict detection in src/validation/data_validator.py (flag inconsistent scenarios)

### Performance Optimization

- [ ] T096 Profile cost calculations with realistic datasets using cProfile
- [ ] T097 Optimize bottlenecks if <60 second target not met (vectorize operations, cache scenario loads)
- [ ] T098 Add database query optimization (ensure indexes used, minimize roundtrips)

### Documentation

- [ ] T099 [P] Add docstrings to all public methods (Google style) with references to ESRS, GHG Protocol where applicable
- [ ] T100 [P] Create METHODOLOGY.md documenting all cost calculation formulas with authoritative source citations
- [ ] T101 [P] Update README.md with full usage examples, troubleshooting, references to quickstart.md

### Additional Tests

- [ ] T102 [P] Create tests/integration/test_edge_cases.py - verify sparse data interpolation, suspicious value flagging, zero emissions
- [ ] T103 [P] Add performance benchmark tests in tests/integration/test_performance.py - verify <60 second E1-E5 calculation

**Completion Criteria**: All edge cases handled gracefully, performance targets met, documentation complete

---

## Dependencies & Execution Order

### User Story Dependencies

```
Setup (Phase 1)
    ↓
Foundational (Phase 2)
    ↓
┌───────────────────────────────────────┐
│ User Story 1 (P1) - Core MVP          │ ← MUST complete first
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ User Story 4 (P2) - Materiality       │ ← Independent of US2, US3
│ User Story 2 (P2) - Scenario Compare  │ ← Independent of US4, US3
│ User Story 3 (P3) - Custom Correlations│ ← Independent of US2, US4
└───────────────────────────────────────┘
    ↓
Polish (Phase 7)
```

**Independent Stories**: US2, US3, US4 can be implemented in any order after US1 completes

### Task Parallelization Opportunities

**Within Phase 2 (Foundational)**:
- Test fixtures (T010-T015) - All parallel
- Data models (T017-T021) - All parallel
- Repositories (T024-T028) - All parallel after T023

**Within Phase 3 (User Story 1)**:
- Contract tests (T029-T030) - Parallel
- Unit tests (T031-T035) - All parallel
- Calculators (T042-T045) - All parallel
- Interpolation (T039-T040) - Parallel with validation (T036-T038)

**Within Phases 4-6**:
- Each user story (US2, US3, US4) can be implemented in parallel teams if resources available

**Within Phase 7 (Polish)**:
- Edge cases (T092-T095) - All parallel
- Documentation (T099-T101) - All parallel

---

## Testing Strategy (Constitution Principle II: TDD)

### Test-First Workflow

1. **Write Contract Test** → Define expected CSV output schema
2. **Write Unit Test** → Define expected cost calculation outcome
3. **Run Test** → Should FAIL (red)
4. **Implement Code** → Minimum to pass test
5. **Run Test** → Should PASS (green)
6. **Refactor** → Improve code clarity, no test changes
7. **Run Test** → Still PASS

### Test Coverage Requirements

- **Unit Tests**: All calculation functions (CarbonPricing, Transition, PhysicalRisk, Compliance, ConfidenceInterval)
- **Integration Tests**: End-to-end flows for each user story
- **Contract Tests**: CSV output schema stability

### Test Data (from research.md)

- **Minimal**: tests/fixtures/company_simple.json (5 fields, known outcome: €100k carbon cost)
- **Comprehensive**: tests/fixtures/company_complex.json (all ESRS topics, known outcome: €81.5M total)

---

## MVP Definition

**Minimum Viable Product**: Phase 3 (User Story 1) only

**MVP Scope**:
- ✅ Load company data from SQLite database
- ✅ Select single climate scenario
- ✅ Calculate costs for ESRS E1-E5 topics
- ✅ Output CSV with cost estimates, confidence intervals, audit trail
- ✅ Handle missing data via interpolation
- ✅ Flag suspicious values

**MVP Exclusions** (defer to post-MVP):
- Multi-scenario comparison (US2)
- Custom correlation configuration (US3)
- Double materiality classification (US4)
- Performance optimization beyond basic requirements
- Edge case handling beyond interpolation and flagging

**MVP Success Criteria** (from spec.md User Story 1):
1. Analysts can calculate complete ESRS E1-E5 costs in <60 seconds
2. CSV output matches contract schema
3. All cost categories present for applicable topics
4. Methodology references included in output
5. Test fixtures pass with known outcomes (±1% tolerance)

---

## Task Count Summary

- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 20 tasks (7 fixtures + 5 models + 7 repositories + 1 DB)
- **Phase 3 (US1 - MVP)**: 32 tasks (2 contract tests + 5 unit tests + 4 validation + 2 interpolation + 5 calculations + 1 confidence + 4 service + 4 output + 5 CLI + 1 integration)
- **Phase 4 (US4)**: 8 tasks
- **Phase 5 (US2)**: 10 tasks
- **Phase 6 (US3)**: 13 tasks
- **Phase 7 (Polish)**: 12 tasks

**Total**: 103 tasks

**Parallelizable Tasks**: 45 tasks marked with [P]

**MVP Task Count**: 60 tasks (Phases 1-3)

---

## Next Steps

1. **Start with MVP**: Implement Phases 1-3 (Tasks T001-T060) to deliver User Story 1
2. **Run Tests First**: Follow TDD workflow (write test → fail → implement → pass → refactor)
3. **Validate Against Constitution**: Ensure scientific accuracy (authoritative sources), test coverage, audit trails
4. **Deploy MVP**: User Story 1 provides immediate value for basic ESRS cost assessment
5. **Iterate**: Add US4, US2, US3 based on user feedback and priority

**Estimated MVP Effort**: ~2-3 weeks for solo developer (60 tasks, TDD approach)

**Next Command**: Start implementing with `git checkout 001-esrs-e1-simulation` and begin Phase 1 tasks
