# Research: ESRS Environmental Topics (E1-E5) Financial Impact Assessment

**Feature**: 001-esrs-e1-simulation
**Date**: 2025-11-14
**Status**: Complete

## Research Questions

Based on Technical Context NEEDS CLARIFICATION items and Constitution Check actions:

1. CuPy vs NumPy for cost calculation workload - Is GPU acceleration justified?
2. Primary dependencies selection and rationale
3. Authoritative sources for ESRS cost calculation methodologies
4. Test dataset requirements with known cost outcomes

## 1. CuPy vs NumPy Decision

### Decision: **NumPy-first with optional CuPy acceleration**

### Rationale

**Workload Analysis**:
- Cost calculations involve: matrix operations (correlation applications), statistical sampling (confidence intervals via Monte Carlo or bootstrap), array transformations (influence factor applications)
- Dataset size: Company report data is **modest** (dozens to hundreds of metrics per company, single-year snapshots)
- Computation patterns: Primarily vectorized operations, not inherently parallel beyond NumPy's built-in BLAS/LAPACK optimizations

**CuPy GPU Acceleration Assessment**:
- **Benefits**: 10-100x speedup for large matrix operations (>10k x 10k), massive parallel Monte Carlo sampling (millions of iterations)
- **Costs**: Additional dependency complexity, CUDA/ROCm runtime requirement, GPU availability assumption, increased debugging difficulty
- **Current scope**: Corporate datasets are small (hundreds of data points, not millions); confidence intervals likely use analytical methods or modest sampling (1000-10000 iterations)

**Performance Projection**:
- NumPy alone: Estimated <1 second for single ESRS topic cost calculation with 1000 Monte Carlo samples
- Full E1-E5 assessment with 5 scenarios: <10 seconds (well under 60-second target)
- CuPy acceleration: Would reduce to <1 second total, but marginal benefit given already-fast execution

**Constitution Alignment**:
- Principle V (Simplicity): NumPy-only is simpler, fewer dependencies, easier maintenance
- Principle III (Performance): NumPy meets performance targets; CuPy is premature optimization

### Implementation Strategy

1. **Phase 1 (MVP)**: Implement all calculations using NumPy
   - Vectorized operations for cost calculations
   - NumPy random sampling for confidence intervals (or analytical confidence bounds where applicable)
   - Profile actual performance with realistic datasets

2. **Phase 2 (Optional optimization)**: Add CuPy support if profiling reveals bottlenecks
   - Conditional import: `try: import cupy as cp; except: cp = np`
   - Runtime detection: Use CuPy only if available and beneficial
   - Benchmark: Measure actual speedup on real workloads before committing to CuPy dependency

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| CuPy-only | Maximum performance | CUDA dependency, GPU requirement, deployment complexity | Violates simplicity principle; not all users have GPUs |
| NumPy-only | Simple, portable, sufficient | Potentially slower for future large-scale extensions | **SELECTED for MVP** - sufficient performance, can add CuPy later if needed |
| JAX | GPU/TPU support, autodiff for optimization | Heavier dependency, less mature ecosystem | Overkill for current requirements |
| Numba JIT | Speed up NumPy with JIT compilation | Additional complexity, debugging challenges | NumPy vectorization should suffice |

## 2. Primary Dependencies

### Decision: **NumPy, Pandas, SciPy, sqlite3 (built-in), pytest**

### Rationale

#### NumPy 1.24+
- **Purpose**: Numerical array operations, vectorized cost calculations, statistical sampling
- **Why needed**: Core mathematical engine for all cost calculations
- **License**: BSD (corporate-compatible)
- **Maturity**: Extremely mature (20+ years), stable API
- **Alternatives**: None viable for scientific Python

#### Pandas 2.0+
- **Purpose**: Data manipulation (company report data, CSV I/O, dataframe operations)
- **Why needed**: Simplifies working with tabular data (company profiles, emissions data, cost results)
- **License**: BSD (corporate-compatible)
- **Maturity**: Industry standard for data analysis
- **Alternatives**: Plain NumPy arrays (too low-level, error-prone); Polars (newer, less mature)

#### SciPy 1.10+
- **Purpose**: Statistical methods (interpolation for missing data, confidence interval calculations, hypothesis testing)
- **Why needed**: FR-012 requires statistical interpolation; confidence intervals require statistical functions
- **License**: BSD (corporate-compatible)
- **Maturity**: Mature scientific computing library
- **Alternatives**: Implement interpolation manually (reinventing wheel); statsmodels (heavier, unnecessary)

#### sqlite3 (Python built-in)
- **Purpose**: Database access for company data, scenarios, influence factors
- **Why needed**: Spec requires SQLite for data persistence
- **License**: Public domain
- **Maturity**: Bundled with Python standard library
- **Alternatives**: None (SQLite specified in requirements)

#### pytest 7.4+
- **Purpose**: Test framework for TDD (unit, integration, contract tests)
- **Why needed**: Constitution Principle II mandates test-first development
- **License**: MIT (corporate-compatible)
- **Maturity**: Industry standard Python testing framework
- **Alternatives**: unittest (built-in but less powerful); nose (deprecated)

### Additional Utilities (Standard Library)

- **csv**: CSV output generation (built-in)
- **json**: Scenario definition loading (built-in)
- **argparse**: CLI argument parsing (built-in)
- **logging**: Structured logging for audit trails (built-in)
- **dataclasses** or **Pydantic**: Data validation for models (dataclasses built-in; Pydantic if validation complexity increases)

### Dependencies NOT Included

- **CuPy**: Deferred to Phase 2 if profiling shows need
- **Matplotlib/Plotly**: Out of scope (spec specifies CSV output only, no visualizations)
- **Requests/HTTPx**: Out of scope (no external data fetching)
- **FastAPI/Flask**: Out of scope (command-line tool, not web service)

## 3. Authoritative Sources for ESRS Cost Calculation Methodologies

### Decision: Use multi-source methodology references

### Climate Scenario Sources

#### IEA (International Energy Agency)
- **Source**: IEA Net Zero by 2050 Roadmap, World Energy Outlook
- **Use**: CO2 price trajectories, energy price projections, technology cost curves
- **Access**: Public reports (https://www.iea.org/)
- **Citation**: IEA (2021). Net Zero by 2050: A Roadmap for the Global Energy Sector.

#### NGFS (Network for Greening the Financial System)
- **Source**: NGFS Climate Scenarios for central banks and supervisors
- **Use**: Standardized climate pathways (Orderly, Disorderly, Hot house world), CO2 pricing, GDP impacts
- **Access**: Public data portal (https://www.ngfs.net/ngfs-scenarios-portal/)
- **Citation**: NGFS (2023). NGFS Climate Scenarios for central banks and supervisors.

#### IPCC (Intergovernmental Panel on Climate Change)
- **Source**: AR6 Working Group III (Mitigation), Shared Socioeconomic Pathways (SSPs)
- **Use**: Temperature pathways (1.5°C, 2°C, 3°C+), physical climate impact projections
- **Access**: Public reports (https://www.ipcc.ch/)
- **Citation**: IPCC (2022). Climate Change 2022: Mitigation of Climate Change.

### Cost Calculation Methodologies

#### ESRS Technical Standards
- **Source**: ESRS E1 Climate Change (EFRAG final standards)
- **Use**: Disclosure requirements, double materiality framework, financial impact quantification guidance
- **Access**: EU Official Journal, EFRAG website
- **Citation**: European Commission (2023). Commission Delegated Regulation on European Sustainability Reporting Standards.

#### GHG Protocol
- **Source**: Corporate Standard, Scope 3 Standard, Mitigation Goal Standard
- **Use**: Carbon accounting methodologies, emission intensity metrics, target-setting frameworks
- **Access**: Public standards (https://ghgprotocol.org/)
- **Citation**: GHG Protocol (2004/2011/2014). Corporate Accounting and Reporting Standards.

#### Carbon Pricing Literature
- **Source**: World Bank State and Trends of Carbon Pricing, IMF Working Papers on carbon taxation
- **Use**: Carbon pricing mechanisms (ETS, carbon tax), price volatility, compliance costs
- **Access**: World Bank reports, IMF publications
- **Citation**: World Bank (2023). State and Trends of Carbon Pricing.

#### Climate Economics Research
- **Source**: Stern Review, DICE model (Nordhaus), academic literature on climate transition costs
- **Use**: Physical risk cost methodologies, adaptation cost estimates, stranded asset valuation
- **Access**: Academic journals, policy reports
- **Citation**: Stern, N. (2006). The Economics of Climate Change: The Stern Review.

### Implementation Strategy

1. **Scenario Parameters**: Encode IEA/NGFS/IPCC scenarios as JSON configuration files with source citations
2. **Cost Formulas**: Document all cost calculation formulas in code comments with specific source references (e.g., "ESRS E1 para 34: transition cost = baseline capex * (low-carbon tech premium) * carbon intensity reduction target")
3. **Methodology Documentation**: Generate `methodology.md` in Phase 1 documenting each cost category calculation with authoritative source mappings

## 4. Test Dataset Requirements

### Decision: Create synthetic test datasets with known cost outcomes

### Test Dataset Structure

#### Minimal Test Case (for unit tests)
```python
# Company: SimpleCo (fictional SME)
{
  "company_id": "TEST_SIMPLE_001",
  "revenue_eur": 10_000_000,  # €10M revenue
  "scope_1_tco2e": 1_000,      # 1,000 tCO2e
  "scope_2_tco2e": 500,        # 500 tCO2e
  "scope_3_tco2e": 2_000,      # 2,000 tCO2e
  "carbon_intensity": 0.00035  # 3,500 tCO2e / €10M = 0.35 tCO2e/€k
}

# Scenario: Simple CO2 Price
{
  "scenario_id": "TEST_SIMPLE_CARBON_PRICE",
  "co2_price_eur_per_tco2e": 100  # €100/tCO2e
}

# Expected Cost (Scope 1 carbon pricing only):
# 1,000 tCO2e * €100/tCO2e = €100,000
```

#### Comprehensive Test Case (for integration tests)
```python
# Company: ComplexCorp (fictional large enterprise)
{
  "company_id": "TEST_COMPLEX_001",
  "revenue_eur": 500_000_000,  # €500M revenue
  "scope_1_tco2e": 50_000,
  "scope_2_tco2e": 30_000,
  "scope_3_tco2e": 120_000,
  "carbon_intensity": 0.0004,  # 200,000 tCO2e / €500M
  "pollution_metrics": {"NOx_tonnes": 100, "SOx_tonnes": 50},
  "water_consumption_m3": 1_000_000,
  "biodiversity_land_use_ha": 50,
  "waste_generation_tonnes": 5_000,
  "recycling_rate_pct": 30
}

# Scenario: IEA Net Zero 2050 (simplified)
{
  "scenario_id": "TEST_IEA_NZ2050",
  "co2_price_2025": 80,
  "co2_price_2030": 130,
  "co2_price_2050": 250,
  "energy_price_multiplier": 1.2,  # 20% increase vs baseline
  "technology_cost_decline_pct": 30,  # Green tech 30% cheaper by 2030
  "policy_stringency": "high"
}

# Expected Costs (E1 Climate example):
# - Carbon Pricing: (50k + 30k + 120k) * €130/tCO2e = €26M (2030)
# - Transition: Estimated capex for decarbonization = €50M over 5 years
# - Physical Risk: Climate adaptation costs = €5M
# - Compliance: ESRS reporting infrastructure = €0.5M
# - Total E1: €81.5M (with confidence interval ±20%)
```

#### Edge Case Test Cases
1. **Sparse Data**: Company with only Scope 1 emissions, missing Scope 2/3
2. **Zero Emissions**: New low-carbon company (near-zero baseline)
3. **Extreme Outlier**: Heavy industry with very high carbon intensity
4. **Incomplete Metrics**: E1-E3 data available, E4-E5 missing

### Validation Approach

1. **Known Outcome Tests**: For each test case, manually calculate expected costs using documented formulas
2. **Tolerance**: Accept ±1% variation for floating-point precision
3. **Contract Stability**: CSV output format must remain stable across code changes
4. **TDD Workflow**:
   - Write test with known input → expected output
   - Run test (should fail - no implementation yet)
   - Implement calculation
   - Run test (should pass)
   - Refactor

### Test Data Storage

- **Location**: `tests/fixtures/`
- **Format**: JSON files for easy readability and modification
- **Files**:
  - `company_simple.json` (minimal test company)
  - `company_complex.json` (comprehensive test company)
  - `scenario_simple_carbon_price.json`
  - `scenario_iea_nz2050.json`
  - `scenario_ngfs_current_policies.json`
  - `expected_costs_simple.json` (known outcomes)
  - `expected_costs_complex.json` (known outcomes)

## Research Conclusions

### Resolved NEEDS CLARIFICATION

1. **Primary Dependencies**: NumPy, Pandas, SciPy, sqlite3, pytest (all mature, well-maintained, license-compatible)
2. **CuPy Decision**: NumPy-first for MVP; CuPy optional in Phase 2 if profiling shows need
3. **Authoritative Sources**: IEA, NGFS, IPCC for scenarios; ESRS, GHG Protocol, climate economics literature for methodologies
4. **Test Datasets**: Synthetic datasets with known cost outcomes in `tests/fixtures/`

### Constitution Check Updated Status

- ✅ All research actions completed
- ✅ No unjustified complexity violations
- ✅ Scientific accuracy ensured through authoritative source references
- ✅ TDD enabled with known-outcome test datasets

### Ready for Phase 1

Proceed to:
1. Data model design (`data-model.md`)
2. Contract definitions (`contracts/`)
3. Quickstart guide (`quickstart.md`)
