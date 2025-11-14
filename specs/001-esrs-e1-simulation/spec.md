# Feature Specification: ESRS Environmental Topics (E1-E5) Financial Impact Assessment

**Feature Branch**: `001-esrs-e1-simulation`
**Created**: 2025-11-14
**Status**: Draft - Scope Corrected
**Input**: User description (corrected scope): "Calculate financial costs for ESRS environmental compliance (E1-E5) using double materiality approach. Extract company carbon/environmental data from reports (Scope 1,2,3 and revenue for carbon intensity). Simulate financial impact under different climate scenarios with influence factors. Focus on impact materiality requiring simulation; financial materiality uses actual company numbers. All cost categories (carbon pricing, transition, physical risks, compliance) with confidence intervals."

## Clarifications

### Session 2025-11-14

**Scope Correction Applied**: Original spec incorrectly focused on simulating future emissions. Corrected to focus on financial cost assessment for ESRS environmental topics using scenario-based modeling.

- Q: How should simulation results be presented to users? → A: CSV output only
- Q: When report data has gaps (missing periods or metrics), how should the system handle this? → A: Use interpolation (statistical imputation to fill gaps)
- Q: When cost calculations produce suspicious results (negative costs, extreme outliers), what should happen? → A: Complete calculation but include traceable suspicious values
- Q: How should data access be controlled for sensitive corporate financial/environmental data? → A: Single-user local execution (no authentication, file system permissions only)
- Q: What minimum data completeness is required from company reports? → A: Any data accepted (no minimum threshold, warn if sparse)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - ESRS Topic Financial Cost Calculation (Priority: P1)

A sustainability finance analyst needs to calculate the financial costs associated with ESRS environmental compliance for each topic (E1: Climate, E2: Pollution, E3: Water, E4: Biodiversity, E5: Circular Economy). They have company environmental data from annual reports and need cost estimates under specific climate/environmental scenarios to support financial planning and materiality assessment.

**Why this priority**: This is the core MVP functionality. Without basic cost calculation capability per ESRS topic, the system provides no value. ESRS double materiality assessment requires quantified financial impacts for decision-making.

**Independent Test**: Can be fully tested by loading company report data (Scope 1,2,3 emissions, revenue, other environmental metrics), selecting a climate scenario, and receiving cost estimates with confidence intervals for each ESRS E topic in CSV format.

**Acceptance Scenarios**:

1. **Given** company environmental data from annual reports (Scope 1,2,3 emissions, revenue), **When** the analyst runs cost calculation for a climate scenario, **Then** the system calculates financial costs for each ESRS E topic with confidence intervals in CSV format
2. **Given** valid company data and selected scenario parameters, **When** the calculation executes, **Then** results include all cost categories (carbon pricing, transition costs, physical risk costs, compliance costs) broken down by ESRS topic
3. **Given** calculation parameters are set, **When** the calculation completes, **Then** the CSV output includes cost methodology, scenario assumptions, and influence factors used for audit trail purposes

---

### User Story 2 - Multi-Scenario Comparison Analysis (Priority: P2)

A climate risk analyst wants to compare financial costs across different climate scenarios (e.g., IEA Net Zero 2050, NGFS Current Policies, 1.5°C vs 2°C warming pathways). They need to see how scenario assumptions (CO2 price trajectories, temperature pathways, policy stringency) affect cost outcomes for each ESRS topic.

**Why this priority**: After basic cost calculation works, scenario comparison enables strategic planning and risk assessment. Organizations need to understand cost implications across plausible futures to make informed climate transition decisions.

**Independent Test**: Can be tested by running cost calculations under multiple scenarios and receiving comparative analysis showing cost differences, key scenario drivers, and sensitivity to scenario parameters.

**Acceptance Scenarios**:

1. **Given** multiple climate scenarios are defined in the system, **When** the analyst runs cost calculation across scenarios, **Then** the output includes cost comparison showing differences by ESRS topic and scenario
2. **Given** scenario definitions with different CO2 price trajectories and temperature pathways, **When** generating cost estimates, **Then** the system applies scenario-specific parameters to calculate differentiated costs
3. **Given** multi-scenario results, **When** the analyst reviews output, **Then** scenarios are compared with key cost drivers identified for each ESRS topic

---

### User Story 3 - Influence Factor Correlation Modeling (Priority: P3)

A data scientist needs to configure and refine the correlation relationships between influence factors (CO2 price, energy prices, regulatory stringency, technology costs, physical climate impacts) and cost outcomes. They want to define correlation strengths (0-1 float), test different correlation assumptions, and assess model confidence.

**Why this priority**: This enables customization and improvement of the cost model. While important for accuracy, the system can function with default correlation models, making this lower priority than core cost calculation capability.

**Independent Test**: Can be tested by defining custom influence factor correlations, running cost calculations with different correlation configurations, and comparing model outputs with confidence metrics.

**Acceptance Scenarios**:

1. **Given** multiple influence factors with configurable correlations, **When** the data scientist sets correlation strengths (0-1 float), **Then** subsequent cost calculations use the configured correlation model
2. **Given** correlation model configuration and company data, **When** the system calculates costs, **Then** it provides confidence metrics reflecting correlation uncertainty
3. **Given** different correlation configurations, **When** running comparison calculations, **Then** the system shows how correlation assumptions affect cost outcomes and confidence levels

---

### User Story 4 - Double Materiality Assessment (Priority: P2)

A sustainability reporting manager needs to perform double materiality assessment for ESRS environmental topics. They need to separate financial materiality (costs to the company from environmental issues) from impact materiality (company's environmental impact on climate/ecosystems), with financial costs calculated for topics requiring impact materiality simulation.

**Why this priority**: Double materiality is a core ESRS requirement. The system must support proper materiality assessment methodology, distinguishing between topics requiring simulation (impact materiality) versus direct calculation (financial materiality).

**Independent Test**: Can be tested by identifying which ESRS topics require impact materiality simulation, running cost calculations only for those topics, and receiving materiality classification with rationale.

**Acceptance Scenarios**:

1. **Given** ESRS environmental topics (E1-E5), **When** the system performs materiality classification, **Then** it identifies which topics require impact materiality simulation versus financial materiality direct calculation
2. **Given** topics requiring impact materiality simulation, **When** the analyst runs cost assessment, **Then** the system simulates costs using influence factors and scenario parameters
3. **Given** topics with financial materiality only, **When** the analyst reviews results, **Then** the system uses actual company financial data without scenario-based simulation

---

### Edge Cases

- **Incomplete report data**: When company reports have gaps (missing Scope 3, incomplete water data, no biodiversity metrics), the system uses statistical interpolation to fill missing values and documents which metrics were imputed. Any level of data completeness is accepted, with warnings issued when data is sparse
- **Missing influence factor data**: When influence factor data is unavailable for specific scenarios (e.g., sector-specific CO2 price projections not defined), how does the system handle calculations?
- **Suspicious cost calculations**: When cost calculations produce unrealistic results (negative costs, extreme cost outliers, implausible confidence intervals), the calculation completes and outputs all values with suspicious values clearly flagged and traceable (including reason and threshold violated)
- **Zero or near-zero baseline emissions**: How does the system calculate climate transition costs when company has minimal current emissions (new company, low-carbon operations)?
- **Cross-topic influence factor sharing**: When multiple ESRS topics share influence factors (e.g., energy price affects E1 climate and E2 pollution), how are correlations and cost impacts allocated across topics?
- **Scenario parameter conflicts**: When scenario definitions contain conflicting assumptions (e.g., high CO2 price with low policy stringency), how does the system resolve or flag inconsistencies?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST calculate financial costs for all ESRS environmental topics (E1: Climate, E2: Pollution, E3: Water, E4: Biodiversity, E5: Circular Economy) based on company report data and scenario parameters
- **FR-002**: System MUST extract and process company environmental data from reports, including Scope 1/2/3 emissions, revenue, carbon intensity (tCO2e/€), and other environmental metrics (pollution, water, biodiversity, circularity indicators)
- **FR-003**: System MUST support multiple climate scenario definitions (e.g., IEA Net Zero, NGFS scenarios, 1.5°C/2°C warming pathways) with configurable parameters (CO2 price trajectories, temperature pathways, policy stringency)
- **FR-004**: System MUST calculate costs across all relevant categories for each ESRS topic: carbon pricing costs, climate transition costs, physical risk costs, and compliance/reporting costs
- **FR-005**: System MUST apply influence factors to cost calculations, including CO2 prices, energy prices, regulatory stringency, technology costs, physical climate impacts, and sector-specific factors
- **FR-006**: System MUST support configurable correlation relationships between influence factors and cost outcomes, represented as 0-1 float values with associated confidence levels
- **FR-007**: System MUST identify shared influence factors across ESRS topics and properly allocate their impacts to each topic's cost calculation
- **FR-008**: System MUST implement double materiality framework, distinguishing between financial materiality (direct calculation from company data) and impact materiality (scenario-based simulation with influence factors)
- **FR-009**: System MUST produce confidence intervals for all cost estimates, reflecting uncertainty in scenario parameters, influence factor correlations, and data quality
- **FR-010**: System MUST provide detailed database schema definitions for all required data entities (company report data, scenarios, cost categories, influence factors, correlation parameters)
- **FR-011**: System MUST validate input data against expected schemas, provide actionable error messages for data quality issues, and issue warnings when company report data is sparse (without blocking cost calculation execution)
- **FR-012**: System MUST handle missing or incomplete company report data using statistical interpolation methods to fill gaps, with all imputed values clearly documented in audit trail outputs
- **FR-013**: System MUST detect unrealistic cost calculation outcomes (negative costs, extreme outliers), complete the calculation, and flag suspicious values in the output with traceability information (reason for flag, threshold violated)
- **FR-014**: System MUST output all cost assessment results in CSV file format with clearly labeled columns for ESRS topics, cost categories, scenario parameters, confidence intervals, and a flag column indicating suspicious values with traceability details
- **FR-015**: System MUST generate audit trail outputs documenting cost calculation methodology, input data sources (report extracts), scenario assumptions, influence factors applied, correlation models used, and any data imputation performed
- **FR-016**: System MUST operate as single-user local execution, relying on file system permissions for data access control without requiring application-level authentication or authorization
- **FR-017**: System MUST support scenario comparison functionality, allowing users to calculate costs under multiple scenarios and output comparative analysis showing cost differences and key drivers

### Key Entities

- **Company Environmental Profile**: Represents the organization being assessed; includes company identifier, industry classification (NACE/ISIC), revenue, reporting year, ESRS topics applicable to the company

- **Company Report Data**: Environmental metrics extracted from annual/sustainability reports; includes Scope 1/2/3 GHG emissions (tCO2e), revenue (€), carbon intensity (tCO2e/€), pollution metrics, water consumption/discharge, biodiversity impact indicators, circularity metrics, data quality indicators, report reference

- **Climate Scenario**: Predefined climate/environmental scenario definition; includes scenario identifier, scenario name (e.g., IEA Net Zero 2050, NGFS Current Policies), temperature pathway (1.5°C, 2°C, 3°C+), CO2 price trajectory parameters, policy stringency level, physical climate impact assumptions, scenario source reference

- **Influence Factor**: Variable that affects cost calculations; includes factor identifier, factor name, factor type (economic/regulatory/physical/technological), measurement unit, applicability to ESRS topics (which topics it influences), historical/baseline value, scenario-specific projected values

- **Influence Factor Correlation**: Relationship strength between influence factor and cost outcome; includes correlation identifier, influence factor identifier, target ESRS topic, target cost category, correlation strength (0-1 float), confidence level (0-1 float), correlation methodology description

- **Cost Category**: Type of financial cost associated with ESRS compliance; includes cost category identifier, category name (carbon pricing/transition/physical risk/compliance), calculation methodology, applicable ESRS topics

- **Cost Calculation Configuration**: Parameters for a specific cost assessment run; includes calculation identifier, company identifier, scenario identifier(s), ESRS topics to assess, materiality approach (financial/impact/both), influence factors enabled, correlation model selected, confidence level target

- **Cost Assessment Result**: Output of cost calculation; includes result identifier, calculation configuration identifier, ESRS topic, cost category, calculated cost amount (€), confidence interval lower bound (€), confidence interval upper bound (€), influence factor contributions, suspicious value flags, calculation timestamp

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Analysts can calculate complete ESRS E1-E5 financial cost assessment for a single climate scenario in under 60 seconds for typical corporate dataset (Scope 1,2,3 emissions and revenue)
- **SC-002**: Cost calculations produce estimates with documented confidence levels (e.g., 90-95% confidence intervals) for all ESRS topics and cost categories
- **SC-003**: The system correctly processes and validates company report data against provided database schemas with 100% error detection for schema violations
- **SC-004**: Influence factor sensitivity analysis identifies and ranks the top 3 most significant factors affecting cost outcomes for each ESRS topic
- **SC-005**: Scenario comparison analysis shows cost differences between scenarios with clearly identified drivers (e.g., "CO2 price difference accounts for 60% of E1 cost variation between scenarios")
- **SC-006**: Double materiality classification correctly identifies which ESRS topics require impact materiality simulation versus financial materiality direct calculation for a given company
- **SC-007**: Generated cost assessment outputs include complete audit trail documentation sufficient for ESRS assurance review (methodology, data sources, assumptions, calculations)
- **SC-008**: The MVP cost calculation runs successfully with at least one default climate scenario (e.g., IEA Net Zero 2050) and default influence factor correlations without requiring custom configuration
- **SC-009**: Cross-topic analysis correctly attributes shared influence factor impacts to multiple ESRS topics (e.g., energy price affects both E1 climate transition costs and E2 pollution abatement costs)

## Assumptions & Dependencies *(optional)*

### Assumptions

- Companies have annual or sustainability reports containing environmental data (at minimum Scope 1,2 emissions and revenue for carbon intensity calculation; any level of data completeness is accepted, with warnings issued for sparse data)
- Carbon intensity (tCO2e/€ revenue) is a valid metric for scaling emissions to financial impacts across scenarios
- Climate scenarios from recognized sources (IEA, NGFS, IPCC) provide reasonable parameter ranges for cost modeling
- Influence factors are quantifiable and can be assigned correlation strengths (0-1 float) to cost outcomes based on domain expertise or empirical analysis
- Default correlation models based on industry research and climate economics literature provide reasonable accuracy for initial MVP
- Database schema will be populated by users extracting data from reports; system reads existing data rather than performing automated report parsing
- ESRS environmental topics (E1-E5) are the relevant scope; social and governance topics (S, G) are out of scope
- Cost calculation horizons of 1-5 years are the primary use case for corporate financial planning
- System runs in single-user local environment; data access security is managed through operating system file permissions

### Dependencies

- Availability of company environmental data from annual/sustainability reports in structured format
- Database infrastructure for data persistence (schema definitions provided, data not pre-populated)
- Statistical/numerical computation libraries capable of cost modeling, uncertainty quantification, and correlation analysis
- Understanding of ESRS technical requirements, double materiality framework, and climate scenario methodologies (IEA, NGFS)
- Domain expertise to define initial influence factor correlations and validate cost model outputs
- Access to climate scenario parameters (CO2 price trajectories, temperature pathways) from recognized sources

## Scope Boundaries *(optional)*

### In Scope

- Financial cost calculation for all ESRS environmental topics: E1 (Climate), E2 (Pollution), E3 (Water & Marine Resources), E4 (Biodiversity & Ecosystems), E5 (Circular Economy)
- All cost categories: carbon pricing, climate transition costs, physical risk costs, compliance/reporting costs
- Multiple climate scenario support (IEA, NGFS, custom scenarios)
- Double materiality framework implementation (financial vs impact materiality)
- Influence factor modeling with configurable correlations (0-1 float) and confidence levels
- Shared influence factors across ESRS topics with proper cost allocation
- Scenario comparison and sensitivity analysis
- Database schema definitions for all required entities
- Validation and error handling for input data quality
- Audit trail and methodology documentation
- Confidence intervals and uncertainty quantification
- MVP with at least one default scenario and correlation model
- CSV output format with suspicious value flagging

### Out of Scope

- Automated data extraction/parsing from PDF reports or external systems (users provide structured data)
- Pre-populated sample datasets or test data generation
- ESRS social (S1-S4) and governance (G1) topics (environmental topics only)
- Emissions forecasting or future emissions simulation (costs are calculated for scenarios, not emissions projected)
- Scenario planning UI or interactive dashboards
- Integration with specific ESRS reporting platforms or software
- Machine learning model training for influence factor correlations (initial MVP uses expert-defined or statistical correlations)
- Real-time data processing or streaming analytics
- Multi-company comparison or benchmarking analysis
- Regulatory interpretation or compliance advisory
- Multi-user authentication and authorization systems
- Role-based access control or user management features
- Network-based or client-server deployment architectures
- Automated report generation beyond CSV output (no PDF, Word, or formatted reports)

## Data Schema Requirements *(optional)*

The following database schema definitions MUST be provided (data not pre-populated):

### Company Profile Schema
- Company identifier (primary key)
- Company name
- Industry classification code (NACE/ISIC)
- Annual revenue (€)
- Reporting year
- Applicable ESRS topics (E1, E2, E3, E4, E5 flags)

### Company Report Data Schema
- Record identifier (primary key)
- Company identifier (foreign key)
- Reporting year
- Scope 1 emissions (tCO2e)
- Scope 2 emissions - location-based (tCO2e)
- Scope 2 emissions - market-based (tCO2e)
- Scope 3 emissions (tCO2e)
- Carbon intensity (tCO2e/€ revenue)
- Pollution metrics (E2) - pollutant types, quantities, units
- Water consumption (E3) - volume (m³), stress level
- Water discharge (E3) - volume (m³), quality indicators
- Biodiversity impact indicators (E4) - land use (ha), habitat impact scores
- Circularity metrics (E5) - waste generation (tonnes), recycling rate (%), material recovery
- Data quality indicator (measured/estimated/calculated)
- Report source reference

### Climate Scenario Schema
- Scenario identifier (primary key)
- Scenario name
- Scenario source (IEA, NGFS, IPCC, custom)
- Temperature pathway (1.5°C, 2°C, 3°C+)
- CO2 price trajectory description
- CO2 price baseline year (€/tCO2e)
- CO2 price projected year 1 (€/tCO2e)
- CO2 price projected year 2-5 (€/tCO2e)
- Policy stringency level (low/medium/high)
- Physical climate impact level (low/medium/high)
- Scenario documentation reference

### Influence Factor Schema
- Factor identifier (primary key)
- Factor name
- Factor type (economic/regulatory/physical/technological)
- Measurement unit
- Applicable ESRS topics (E1, E2, E3, E4, E5 flags)
- Baseline value (for reference year)
- Is global factor (boolean) - vs company-specific

### Influence Factor Values Schema
- Value identifier (primary key)
- Factor identifier (foreign key)
- Scenario identifier (foreign key)
- Projection year
- Factor value
- Data source reference

### Correlation Model Schema
- Model identifier (primary key)
- Model name
- Model description
- Creation date

### Influence Factor Correlation Schema
- Correlation identifier (primary key)
- Model identifier (foreign key)
- Influence factor identifier (foreign key)
- Target ESRS topic (E1, E2, E3, E4, E5)
- Target cost category (carbon pricing/transition/physical risk/compliance)
- Correlation strength (0-1 float)
- Confidence level (0-1 float)
- Correlation methodology description

### Cost Category Schema
- Category identifier (primary key)
- Category name (carbon pricing/transition/physical risk/compliance)
- Calculation methodology description
- Applicable ESRS topics (E1, E2, E3, E4, E5 flags)

### Cost Calculation Configuration Schema
- Calculation identifier (primary key)
- Company identifier (foreign key)
- Scenario identifier (foreign key)
- Model identifier (foreign key) - correlation model
- ESRS topics to assess (E1, E2, E3, E4, E5 flags)
- Materiality approach (financial/impact/both)
- Target confidence level (percentage)
- Creation timestamp

### Cost Assessment Result Schema
- Result identifier (primary key)
- Calculation configuration identifier (foreign key)
- ESRS topic (E1, E2, E3, E4, E5)
- Cost category (carbon pricing/transition/physical risk/compliance)
- Calculated cost amount (€)
- Confidence interval lower bound (€)
- Confidence interval upper bound (€)
- Influence factor contributions (JSON or separate table)
- Suspicious value flag (boolean)
- Suspicious value reason (text)
- Calculation timestamp
- Methodology documentation reference
