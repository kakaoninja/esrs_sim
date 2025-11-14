-- ESRS Environmental Topics Financial Impact Assessment
-- SQLite Database Schema
-- Feature: 001-esrs-e1-simulation
-- Date: 2025-11-14

-- ============================================================================
-- Company Data
-- ============================================================================

CREATE TABLE company_profiles (
    company_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    industry_code TEXT NOT NULL,
    annual_revenue_eur REAL NOT NULL CHECK (annual_revenue_eur > 0),
    reporting_year INTEGER NOT NULL CHECK (reporting_year BETWEEN 2020 AND 2100),
    esrs_e1_applicable INTEGER NOT NULL DEFAULT 1 CHECK (esrs_e1_applicable IN (0,1)),
    esrs_e2_applicable INTEGER NOT NULL DEFAULT 0 CHECK (esrs_e2_applicable IN (0,1)),
    esrs_e3_applicable INTEGER NOT NULL DEFAULT 0 CHECK (esrs_e3_applicable IN (0,1)),
    esrs_e4_applicable INTEGER NOT NULL DEFAULT 0 CHECK (esrs_e4_applicable IN (0,1)),
    esrs_e5_applicable INTEGER NOT NULL DEFAULT 0 CHECK (esrs_e5_applicable IN (0,1)),
    CHECK (
        esrs_e1_applicable = 1 OR
        esrs_e2_applicable = 1 OR
        esrs_e3_applicable = 1 OR
        esrs_e4_applicable = 1 OR
        esrs_e5_applicable = 1
    )
);

CREATE TABLE company_report_data (
    record_id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    reporting_year INTEGER NOT NULL,
    scope_1_emissions_tco2e REAL CHECK (scope_1_emissions_tco2e >= 0),
    scope_2_location_tco2e REAL CHECK (scope_2_location_tco2e >= 0),
    scope_2_market_tco2e REAL CHECK (scope_2_market_tco2e >= 0),
    scope_3_emissions_tco2e REAL CHECK (scope_3_emissions_tco2e >= 0),
    carbon_intensity_tco2e_per_eur REAL,
    pollution_metrics TEXT,  -- JSON
    water_consumption_m3 REAL CHECK (water_consumption_m3 >= 0),
    water_discharge_m3 REAL CHECK (water_discharge_m3 >= 0),
    biodiversity_land_use_ha REAL CHECK (biodiversity_land_use_ha >= 0),
    biodiversity_habitat_impact_score REAL,
    waste_generation_tonnes REAL CHECK (waste_generation_tonnes >= 0),
    recycling_rate_pct REAL CHECK (recycling_rate_pct BETWEEN 0 AND 100),
    material_recovery_pct REAL CHECK (material_recovery_pct BETWEEN 0 AND 100),
    data_quality_indicator TEXT CHECK (data_quality_indicator IN ('measured', 'estimated', 'calculated')),
    report_source_reference TEXT,
    FOREIGN KEY (company_id) REFERENCES company_profiles(company_id)
);

-- ============================================================================
-- Scenarios & Influence Factors
-- ============================================================================

CREATE TABLE climate_scenarios (
    scenario_id TEXT PRIMARY KEY,
    scenario_name TEXT NOT NULL UNIQUE,
    scenario_source TEXT NOT NULL CHECK (scenario_source IN ('IEA', 'NGFS', 'IPCC', 'custom')),
    temperature_pathway TEXT NOT NULL CHECK (temperature_pathway IN ('1.5C', '2C', '3C_plus')),
    co2_price_trajectory_description TEXT,
    co2_price_baseline_year INTEGER NOT NULL,
    co2_price_baseline_eur_per_tco2e REAL NOT NULL CHECK (co2_price_baseline_eur_per_tco2e >= 0),
    co2_price_projections TEXT,  -- JSON array
    policy_stringency_level TEXT CHECK (policy_stringency_level IN ('low', 'medium', 'high')),
    physical_climate_impact_level TEXT CHECK (physical_climate_impact_level IN ('low', 'medium', 'high')),
    scenario_documentation_reference TEXT
);

CREATE TABLE influence_factors (
    factor_id TEXT PRIMARY KEY,
    factor_name TEXT NOT NULL,
    factor_type TEXT NOT NULL CHECK (factor_type IN ('economic', 'regulatory', 'physical', 'technological')),
    measurement_unit TEXT NOT NULL,
    e1_applicable INTEGER NOT NULL DEFAULT 0 CHECK (e1_applicable IN (0,1)),
    e2_applicable INTEGER NOT NULL DEFAULT 0 CHECK (e2_applicable IN (0,1)),
    e3_applicable INTEGER NOT NULL DEFAULT 0 CHECK (e3_applicable IN (0,1)),
    e4_applicable INTEGER NOT NULL DEFAULT 0 CHECK (e4_applicable IN (0,1)),
    e5_applicable INTEGER NOT NULL DEFAULT 0 CHECK (e5_applicable IN (0,1)),
    baseline_value REAL NOT NULL,
    is_global_factor INTEGER NOT NULL CHECK (is_global_factor IN (0,1)),
    CHECK (
        e1_applicable = 1 OR
        e2_applicable = 1 OR
        e3_applicable = 1 OR
        e4_applicable = 1 OR
        e5_applicable = 1
    )
);

CREATE TABLE influence_factor_values (
    value_id TEXT PRIMARY KEY,
    factor_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    projection_year INTEGER NOT NULL,
    factor_value REAL NOT NULL,
    data_source_reference TEXT,
    FOREIGN KEY (factor_id) REFERENCES influence_factors(factor_id),
    FOREIGN KEY (scenario_id) REFERENCES climate_scenarios(scenario_id)
);

-- ============================================================================
-- Correlation Models
-- ============================================================================

CREATE TABLE correlation_models (
    model_id TEXT PRIMARY KEY,
    model_name TEXT NOT NULL UNIQUE,
    model_description TEXT,
    creation_date TEXT NOT NULL  -- ISO 8601 date
);

CREATE TABLE influence_factor_correlations (
    correlation_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    factor_id TEXT NOT NULL,
    target_esrs_topic TEXT NOT NULL CHECK (target_esrs_topic IN ('E1', 'E2', 'E3', 'E4', 'E5')),
    target_cost_category TEXT NOT NULL CHECK (target_cost_category IN ('carbon_pricing', 'transition', 'physical_risk', 'compliance')),
    correlation_strength REAL NOT NULL CHECK (correlation_strength BETWEEN 0.0 AND 1.0),
    confidence_level REAL NOT NULL CHECK (confidence_level BETWEEN 0.0 AND 1.0),
    correlation_methodology_description TEXT,
    FOREIGN KEY (model_id) REFERENCES correlation_models(model_id),
    FOREIGN KEY (factor_id) REFERENCES influence_factors(factor_id)
);

-- ============================================================================
-- Cost Categories
-- ============================================================================

CREATE TABLE cost_categories (
    category_id TEXT PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE CHECK (category_name IN ('carbon_pricing', 'transition', 'physical_risk', 'compliance')),
    calculation_methodology_description TEXT,
    e1_applicable INTEGER NOT NULL DEFAULT 0 CHECK (e1_applicable IN (0,1)),
    e2_applicable INTEGER NOT NULL DEFAULT 0 CHECK (e2_applicable IN (0,1)),
    e3_applicable INTEGER NOT NULL DEFAULT 0 CHECK (e3_applicable IN (0,1)),
    e4_applicable INTEGER NOT NULL DEFAULT 0 CHECK (e4_applicable IN (0,1)),
    e5_applicable INTEGER NOT NULL DEFAULT 0 CHECK (e5_applicable IN (0,1))
);

-- ============================================================================
-- Calculations & Results
-- ============================================================================

CREATE TABLE cost_calculation_configurations (
    calculation_id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    model_id TEXT NOT NULL,
    assess_e1 INTEGER NOT NULL DEFAULT 0 CHECK (assess_e1 IN (0,1)),
    assess_e2 INTEGER NOT NULL DEFAULT 0 CHECK (assess_e2 IN (0,1)),
    assess_e3 INTEGER NOT NULL DEFAULT 0 CHECK (assess_e3 IN (0,1)),
    assess_e4 INTEGER NOT NULL DEFAULT 0 CHECK (assess_e4 IN (0,1)),
    assess_e5 INTEGER NOT NULL DEFAULT 0 CHECK (assess_e5 IN (0,1)),
    materiality_approach TEXT NOT NULL CHECK (materiality_approach IN ('financial', 'impact', 'both')),
    target_confidence_level_pct INTEGER NOT NULL CHECK (target_confidence_level_pct IN (90, 95, 99)),
    creation_timestamp TEXT NOT NULL,  -- ISO 8601 datetime
    FOREIGN KEY (company_id) REFERENCES company_profiles(company_id),
    FOREIGN KEY (scenario_id) REFERENCES climate_scenarios(scenario_id),
    FOREIGN KEY (model_id) REFERENCES correlation_models(model_id),
    CHECK (
        assess_e1 = 1 OR
        assess_e2 = 1 OR
        assess_e3 = 1 OR
        assess_e4 = 1 OR
        assess_e5 = 1
    )
);

CREATE TABLE cost_assessment_results (
    result_id TEXT PRIMARY KEY,
    calculation_id TEXT NOT NULL,
    esrs_topic TEXT NOT NULL CHECK (esrs_topic IN ('E1', 'E2', 'E3', 'E4', 'E5')),
    cost_category TEXT NOT NULL CHECK (cost_category IN ('carbon_pricing', 'transition', 'physical_risk', 'compliance')),
    calculated_cost_amount_eur REAL NOT NULL,
    confidence_interval_lower_eur REAL NOT NULL,
    confidence_interval_upper_eur REAL NOT NULL,
    influence_factor_contributions TEXT,  -- JSON
    suspicious_value_flag INTEGER NOT NULL DEFAULT 0 CHECK (suspicious_value_flag IN (0,1)),
    suspicious_value_reason TEXT,
    calculation_timestamp TEXT NOT NULL,  -- ISO 8601 datetime
    methodology_documentation_reference TEXT,
    FOREIGN KEY (calculation_id) REFERENCES cost_calculation_configurations(calculation_id),
    CHECK (confidence_interval_lower_eur <= calculated_cost_amount_eur),
    CHECK (calculated_cost_amount_eur <= confidence_interval_upper_eur)
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

CREATE INDEX idx_report_data_company ON company_report_data(company_id);
CREATE INDEX idx_report_data_year ON company_report_data(reporting_year);
CREATE INDEX idx_factor_values_factor ON influence_factor_values(factor_id);
CREATE INDEX idx_factor_values_scenario ON influence_factor_values(scenario_id);
CREATE INDEX idx_correlations_model ON influence_factor_correlations(model_id);
CREATE INDEX idx_correlations_factor ON influence_factor_correlations(factor_id);
CREATE INDEX idx_results_calculation ON cost_assessment_results(calculation_id);
CREATE INDEX idx_results_topic ON cost_assessment_results(esrs_topic);
