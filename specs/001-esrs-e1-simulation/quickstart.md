# Quickstart: ESRS Environmental Financial Impact Assessment

**Feature**: 001-esrs-e1-simulation
**Date**: 2025-11-14

## Overview

Calculate financial costs for ESRS environmental topics (E1-E5) using scenario-based modeling with influence factors.

## Prerequisites

- Python 3.11+
- SQLite database with company report data populated
- Predefined climate scenario configuration files

## Installation

```bash
# Clone repository
git clone <repository-url>
cd master_climate_sim

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
# Expected: numpy>=1.24, pandas>=2.0, scipy>=1.10, pytest>=7.4
```

## Database Setup

```bash
# Initialize database with schema
sqlite3 data/master_climate_sim.db < specs/001-esrs-e1-simulation/contracts/database-schemas.sql

# Populate with your company data
# (See data-model.md for schema details)
```

## Basic Usage

### 1. Single Company, Single Scenario Cost Calculation

```bash
python -m src.cli calculate \
  --company-id "ACME_CORP" \
  --scenario-id "IEA_NZ2050" \
  --topics E1,E2,E3,E4,E5 \
  --output results/acme_iea_nz2050.csv
```

**Output**: CSV file with cost estimates for each ESRS topic and cost category.

### 2. Multi-Scenario Comparison

```bash
python -m src.cli compare \
  --company-id "ACME_CORP" \
  --scenarios "IEA_NZ2050,NGFS_CurrentPolicies,NGFS_NetZero" \
  --topics E1,E3 \
  --output results/acme_scenario_comparison.csv
```

**Output**: CSV with costs across all scenarios for comparison.

### 3. Custom Correlation Model

```bash
python -m src.cli calculate \
  --company-id "ACME_CORP" \
  --scenario-id "IEA_NZ2050" \
  --correlation-model "CustomModel_v2" \
  --topics E1 \
  --output results/acme_custom_correlations.csv
```

## Configuration Files

### Climate Scenario Definition (JSON)

Location: `config/scenarios/iea_nz2050.json`

```json
{
  "scenario_id": "IEA_NZ2050",
  "scenario_name": "IEA Net Zero 2050",
  "scenario_source": "IEA",
  "temperature_pathway": "1.5C",
  "co2_price_baseline_year": 2025,
  "co2_price_baseline_eur_per_tco2e": 80.0,
  "co2_price_projections": [
    {"year": 2025, "price_eur_per_tco2e": 80},
    {"year": 2030, "price_eur_per_tco2e": 130},
    {"year": 2040, "price_eur_per_tco2e": 200},
    {"year": 2050, "price_eur_per_tco2e": 250}
  ],
  "policy_stringency_level": "high",
  "physical_climate_impact_level": "low",
  "scenario_documentation_reference": "https://www.iea.org/reports/net-zero-by-2050"
}
```

### Influence Factor Definition (JSON)

Location: `config/influence_factors/eu_ets_carbon_price.json`

```json
{
  "factor_id": "EU_ETS_Carbon_Price",
  "factor_name": "EU ETS Carbon Price",
  "factor_type": "economic",
  "measurement_unit": "EUR/tCO2e",
  "applicable_esrs_topics": {
    "E1": true,
    "E2": false,
    "E3": false,
    "E4": false,
    "E5": false
  },
  "baseline_value": 85.0,
  "is_global_factor": false
}
```

## Data Requirements

### Minimum Required Company Data

For basic E1 (Climate) cost calculation:

```sql
-- Insert company profile
INSERT INTO company_profiles VALUES (
    'ACME_CORP',
    'ACME Corporation',
    'C24.10',  -- NACE code for basic iron and steel
    50000000.0,  -- €50M revenue
    2024,
    1, 0, 0, 0, 0  -- E1 applicable only
);

-- Insert emissions data
INSERT INTO company_report_data VALUES (
    'ACME_2024_001',
    'ACME_CORP',
    2024,
    5000.0,    -- Scope 1: 5,000 tCO2e
    3000.0,    -- Scope 2 (location): 3,000 tCO2e
    2500.0,    -- Scope 2 (market): 2,500 tCO2e
    12000.0,   -- Scope 3: 12,000 tCO2e
    0.0004,    -- Carbon intensity: 0.4 tCO2e/€1000
    NULL,      -- Pollution metrics (not needed for E1)
    NULL,      -- Water consumption (not needed for E1)
    NULL,      -- Water discharge (not needed for E1)
    NULL,      -- Biodiversity land use (not needed for E1)
    NULL,      -- Biodiversity impact score (not needed for E1)
    NULL,      -- Waste generation (not needed for E1)
    NULL,      -- Recycling rate (not needed for E1)
    NULL,      -- Material recovery (not needed for E1)
    'measured',
    'Annual Report 2024, Page 45'
);
```

## Example Output

Running the basic calculation produces:

`results/acme_iea_nz2050.csv`:
```csv
calculation_id,company_id,company_name,scenario_id,scenario_name,esrs_topic,cost_category,calculated_cost_eur,ci_lower_eur,ci_upper_eur,confidence_level_pct,top_influence_factor_1,top_influence_factor_1_contribution_pct,suspicious_value_flag,data_quality_warning,calculation_timestamp,methodology_reference
CALC_20251114_001,ACME_CORP,ACME Corporation,IEA_NZ2050,IEA Net Zero 2050,E1,carbon_pricing,2600000.00,2340000.00,2860000.00,95,EU_ETS_Carbon_Price,65.3,FALSE,,2025-11-14T10:30:45Z,ESRS_E1_Carbon_Pricing_v1.0
CALC_20251114_001,ACME_CORP,ACME Corporation,IEA_NZ2050,IEA Net Zero 2050,E1,transition,12500000.00,10000000.00,15000000.00,95,Technology_Cost_Decline,48.2,FALSE,,2025-11-14T10:30:45Z,ESRS_E1_Transition_Cost_v1.0
CALC_20251114_001,ACME_CORP,ACME Corporation,IEA_NZ2050,IEA Net Zero 2050,E1,physical_risk,3200000.00,2500000.00,4100000.00,95,Physical_Climate_Impact_Level,72.1,FALSE,,2025-11-14T10:30:45Z,ESRS_E1_Physical_Risk_v1.0
CALC_20251114_001,ACME_CORP,ACME Corporation,IEA_NZ2050,IEA Net Zero 2050,E1,compliance,450000.00,380000.00,520000.00,95,Reporting_Complexity,55.0,FALSE,,2025-11-14T10:30:45Z,ESRS_E1_Compliance_Cost_v1.0
```

## Interpreting Results

- **calculated_cost_eur**: Best estimate of financial cost
- **ci_lower_eur / ci_upper_eur**: Confidence interval bounds (default 95%)
- **top_influence_factor_N**: Key drivers of cost (ranked by contribution)
- **suspicious_value_flag**: Review flagged items manually
- **data_quality_warning**: Indicates if data imputation was applied

## Next Steps

1. **Add more companies**: Populate database with additional company profiles and report data
2. **Define custom scenarios**: Create JSON files for company-specific climate pathways
3. **Configure correlations**: Adjust influence factor correlation strengths for your industry
4. **Compare scenarios**: Run multi-scenario analysis to understand cost ranges
5. **Review flagged values**: Investigate any suspicious cost estimates
6. **Generate reports**: Import CSV into Excel/BI tools for stakeholder reporting

## Troubleshooting

### "Company not found" error
- Check `company_id` matches database entry exactly (case-sensitive)
- Verify company has applicable ESRS topics flagged

### "Insufficient data" warning
- System will interpolate missing values (e.g., Scope 3 if unavailable)
- Review `data_quality_warning` column in output
- Populate more complete report data for better accuracy

### Unrealistic cost estimates
- Check scenario parameters (CO2 prices, influence factors)
- Verify company report data accuracy (emissions, revenue)
- Review correlation model configuration
- Flagged values appear in `suspicious_value_flag` column

### Performance issues
- Ensure database indexes are created (see database-schemas.sql)
- Reduce number of ESRS topics in single calculation
- Profile with smaller dataset first

## Development Workflow (TDD)

See `tests/fixtures/` for test datasets with known outcomes. Run tests before implementation:

```bash
# Run all tests
pytest tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Run with coverage
pytest --cov=src tests/
```

## References

- Spec: [spec.md](./spec.md)
- Data Model: [data-model.md](./data-model.md)
- Database Schema: [contracts/database-schemas.sql](./contracts/database-schemas.sql)
- CSV Output Schema: [contracts/cost-output.csv.schema](./contracts/cost-output.csv.schema)
- Research: [research.md](./research.md) (dependencies, methodologies, authoritative sources)
