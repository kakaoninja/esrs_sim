# Data Model: ESRS Environmental Topics Financial Impact Assessment

**Feature**: 001-esrs-e1-simulation
**Date**: 2025-11-14

## Overview

This data model supports ESRS E1-E5 financial cost assessment using scenario-based modeling with influence factors and double materiality framework.

## Core Entities

### CompanyProfile

Represents the organization being assessed.

**Fields**:
- `company_id` (str, PK): Unique company identifier
- `company_name` (str): Legal company name
- `industry_code` (str): NACE or ISIC classification code
- `annual_revenue_eur` (float): Annual revenue in euros
- `reporting_year` (int): Fiscal year for data (YYYY)
- `esrs_topics_applicable` (dict): Flags for E1, E2, E3, E4, E5 applicability

**Validation**:
- `company_id`: Non-empty, unique
- `annual_revenue_eur`: > 0
- `reporting_year`: 2020-2100 range
- `esrs_topics_applicable`: At least one topic must be True

**Relationships**:
- One CompanyProfile → Many CompanyReportData
- One CompanyProfile → Many CostCalculationConfiguration

---

### CompanyReportData

Environmental metrics extracted from annual/sustainability reports.

**Fields**:
- `record_id` (str, PK): Unique record identifier
- `company_id` (str, FK): References CompanyProfile
- `reporting_year` (int): Year of data
- `scope_1_emissions_tco2e` (float, nullable): Direct emissions
- `scope_2_location_tco2e` (float, nullable): Indirect emissions (location-based)
- `scope_2_market_tco2e` (float, nullable): Indirect emissions (market-based)
- `scope_3_emissions_tco2e` (float, nullable): Value chain emissions
- `carbon_intensity_tco2e_per_eur` (float, computed): Total emissions / revenue
- `pollution_metrics` (JSON, nullable): E2 pollutant types, quantities, units
- `water_consumption_m3` (float, nullable): E3 water use
- `water_discharge_m3` (float, nullable): E3 water discharge
- `biodiversity_land_use_ha` (float, nullable): E4 land use in hectares
- `biodiversity_habitat_impact_score` (float, nullable): E4 impact rating
- `waste_generation_tonnes` (float, nullable): E5 waste produced
- `recycling_rate_pct` (float, nullable): E5 recycling percentage (0-100)
- `material_recovery_pct` (float, nullable): E5 material recovery (0-100)
- `data_quality_indicator` (enum): "measured", "estimated", "calculated"
- `report_source_reference` (str): Citation to source document

**Validation**:
- Emissions values: >= 0 if provided
- `carbon_intensity_tco2e_per_eur`: Auto-calculated from (scope1 + scope2 + scope3) / revenue
- Percentages: 0-100 range
- At least one ESRS-relevant field must be populated

**Relationships**:
- Many CompanyReportData → One CompanyProfile

---

### ClimateScenario

Predefined climate/environmental scenario definition.

**Fields**:
- `scenario_id` (str, PK): Unique scenario identifier
- `scenario_name` (str): Human-readable name (e.g., "IEA Net Zero 2050")
- `scenario_source` (enum): "IEA", "NGFS", "IPCC", "custom"
- `temperature_pathway` (enum): "1.5C", "2C", "3C_plus"
- `co2_price_trajectory_description` (str): Textual description of price evolution
- `co2_price_baseline_year` (int): Reference year for CO2 price
- `co2_price_baseline_eur_per_tco2e` (float): CO2 price in baseline year
- `co2_price_projections` (JSON): Array of {year, price_eur_per_tco2e}
- `policy_stringency_level` (enum): "low", "medium", "high"
- `physical_climate_impact_level` (enum): "low", "medium", "high"
- `scenario_documentation_reference` (str): URL or citation to source

**Validation**:
- `co2_price_baseline_eur_per_tco2e`: >= 0
- `co2_price_projections`: Monotonically increasing or stable (no price decreases over time)
- `scenario_documentation_reference`: Must be provided for non-custom scenarios

**Relationships**:
- One ClimateScenario → Many InfluenceFactorValues
- One ClimateScenario → Many CostCalculationConfiguration

---

### InfluenceFactor

Variable that affects cost calculations.

**Fields**:
- `factor_id` (str, PK): Unique factor identifier
- `factor_name` (str): Human-readable name (e.g., "EU ETS Carbon Price")
- `factor_type` (enum): "economic", "regulatory", "physical", "technological"
- `measurement_unit` (str): Unit of measurement (e.g., "EUR/tCO2e", "EUR/MWh", "index 0-100")
- `applicable_esrs_topics` (dict): Flags for E1, E2, E3, E4, E5 applicability
- `baseline_value` (float): Value in reference year
- `is_global_factor` (bool): True if applies to all companies, False if company-specific

**Validation**:
- At least one ESRS topic must be applicable
- `baseline_value`: Must be provided

**Relationships**:
- One InfluenceFactor → Many InfluenceFactorValues
- One InfluenceFactor → Many InfluenceFactorCorrelations

---

### InfluenceFactorValues

Scenario-specific projected values for influence factors.

**Fields**:
- `value_id` (str, PK): Unique value identifier
- `factor_id` (str, FK): References InfluenceFactor
- `scenario_id` (str, FK): References ClimateScenario
- `projection_year` (int): Year of projection
- `factor_value` (float): Projected value
- `data_source_reference` (str): Source for this projection

**Validation**:
- `projection_year`: >= baseline year
- `factor_value`: Appropriate range for factor type (validated per factor)

**Relationships**:
- Many InfluenceFactorValues → One InfluenceFactor
- Many InfluenceFactorValues → One ClimateScenario

---

### CorrelationModel

Named collection of correlation configurations.

**Fields**:
- `model_id` (str, PK): Unique model identifier
- `model_name` (str): Human-readable name (e.g., "Default Linear Correlations")
- `model_description` (str): Methodology explanation
- `creation_date` (date): When model was created

**Validation**:
- `model_name`: Non-empty, unique

**Relationships**:
- One CorrelationModel → Many InfluenceFactorCorrelations

---

### InfluenceFactorCorrelation

Relationship strength between influence factor and cost outcome.

**Fields**:
- `correlation_id` (str, PK): Unique correlation identifier
- `model_id` (str, FK): References CorrelationModel
- `factor_id` (str, FK): References InfluenceFactor
- `target_esrs_topic` (enum): "E1", "E2", "E3", "E4", "E5"
- `target_cost_category` (enum): "carbon_pricing", "transition", "physical_risk", "compliance"
- `correlation_strength` (float): 0.0-1.0 (0 = no correlation, 1 = perfect correlation)
- `confidence_level` (float): 0.0-1.0 (uncertainty in correlation estimate)
- `correlation_methodology_description` (str): How correlation was derived

**Validation**:
- `correlation_strength`: 0.0-1.0 range
- `confidence_level`: 0.0-1.0 range
- Factor's applicable topics must include target_esrs_topic

**Relationships**:
- Many InfluenceFactorCorrelations → One CorrelationModel
- Many InfluenceFactorCorrelations → One InfluenceFactor

---

### CostCategory

Type of financial cost associated with ESRS compliance.

**Fields**:
- `category_id` (str, PK): Unique category identifier
- `category_name` (enum): "carbon_pricing", "transition", "physical_risk", "compliance"
- `calculation_methodology_description` (str): Formula and approach
- `applicable_esrs_topics` (dict): Flags for E1, E2, E3, E4, E5 applicability

**Validation**:
- `category_name`: Must be one of the four predefined categories
- At least one ESRS topic must be applicable

**Relationships**:
- One CostCategory → Many CostAssessmentResults

---

### CostCalculationConfiguration

Parameters for a specific cost assessment run.

**Fields**:
- `calculation_id` (str, PK): Unique calculation identifier
- `company_id` (str, FK): References CompanyProfile
- `scenario_id` (str, FK): References ClimateScenario
- `model_id` (str, FK): References CorrelationModel
- `esrs_topics_to_assess` (dict): Flags for E1, E2, E3, E4, E5 to include
- `materiality_approach` (enum): "financial", "impact", "both"
- `target_confidence_level_pct` (int): 90, 95, or 99
- `creation_timestamp` (datetime): When calculation was run

**Validation**:
- At least one ESRS topic must be selected for assessment
- `target_confidence_level_pct`: 90, 95, or 99
- Company must have report data for selected topics

**Relationships**:
- Many CostCalculationConfigurations → One CompanyProfile
- Many CostCalculationConfigurations → One ClimateScenario
- Many CostCalculationConfigurations → One CorrelationModel
- One CostCalculationConfiguration → Many CostAssessmentResults

---

### CostAssessmentResult

Output of cost calculation.

**Fields**:
- `result_id` (str, PK): Unique result identifier
- `calculation_id` (str, FK): References CostCalculationConfiguration
- `esrs_topic` (enum): "E1", "E2", "E3", "E4", "E5"
- `cost_category` (enum): "carbon_pricing", "transition", "physical_risk", "compliance"
- `calculated_cost_amount_eur` (float): Estimated cost in euros
- `confidence_interval_lower_eur` (float): Lower bound of confidence interval
- `confidence_interval_upper_eur` (float): Upper bound of confidence interval
- `influence_factor_contributions` (JSON): Array of {factor_id, contribution_pct}
- `suspicious_value_flag` (bool): True if flagged for review
- `suspicious_value_reason` (str, nullable): Explanation if flagged
- `calculation_timestamp` (datetime): When result was generated
- `methodology_documentation_reference` (str): Link to calculation methodology

**Validation**:
- `calculated_cost_amount_eur`: Can be negative (e.g., carbon credit revenue) but flagged if extreme
- `confidence_interval_lower_eur` <= `calculated_cost_amount_eur` <= `confidence_interval_upper_eur`
- Influence factor contributions sum to ~100%

**Relationships**:
- Many CostAssessmentResults → One CostCalculationConfiguration

## Entity Relationship Diagram

```
CompanyProfile (1) ──────< CompanyReportData (M)
CompanyProfile (1) ──────< CostCalculationConfiguration (M)

ClimateScenario (1) ─────< InfluenceFactorValues (M)
ClimateScenario (1) ─────< CostCalculationConfiguration (M)

InfluenceFactor (1) ─────< InfluenceFactorValues (M)
InfluenceFactor (1) ─────< InfluenceFactorCorrelation (M)

CorrelationModel (1) ────< InfluenceFactorCorrelation (M)
CorrelationModel (1) ────< CostCalculationConfiguration (M)

CostCategory (1) ────────< CostAssessmentResult (M)

CostCalculationConfiguration (1) ──< CostAssessmentResult (M)
```

## State Transitions

### CostCalculationConfiguration States

1. **Configured**: User creates calculation with parameters
2. **Validating**: Input data validation in progress
3. **Running**: Cost calculations executing
4. **Completed**: Results available
5. **Failed**: Validation or calculation errors

### Suspicious Value Handling

1. **Calculated**: Cost computed normally
2. **Flagged**: Suspicious pattern detected (negative cost, extreme outlier, implausible confidence interval)
3. **Reviewed**: User acknowledges flag (manual process, not automated)

## Data Constraints Summary

- All monetary values in EUR
- All emissions in tCO2e
- All timestamps in UTC
- All percentages as 0-100 (not 0-1)
- JSON fields validated against schemas (defined in contracts/)
- Nullable fields: Can be NULL if data unavailable (interpolation applied during calculation)
