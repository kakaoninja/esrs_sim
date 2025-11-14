"""E1 Climate Change cost assessment service.

Orchestrates the complete E1 cost assessment workflow:
1. Data validation
2. Carbon pricing calculation
3. Result aggregation

This is the main service for User Story 1 (E1 Climate MVP).

References:
- ESRS E1: Climate change financial materiality assessment
- Constitution Principle II: Test-driven development
"""

from datetime import datetime
from typing import Optional

from ..models.company import CompanyProfile, CompanyReportData
from ..models.scenario import ClimateScenario
from ..models.cost import CostAssessmentResult, CostCategory
from ..validation.data_validator import DataValidator
from ..calculations.carbon_pricing import CarbonPricingCalculator


class E1CostAssessmentService:
    """Service for E1 Climate Change cost assessment.

    Coordinates validation, calculation, and result generation for
    E1 climate-related financial costs.

    MVP scope: Carbon pricing costs only
    Future: Transition costs, physical risks, compliance costs
    """

    def __init__(self):
        """Initialize E1 cost assessment service with required components."""
        self.validator = DataValidator()
        self.carbon_calculator = CarbonPricingCalculator()

    def assess_e1_costs(
        self,
        company_profile: CompanyProfile,
        company_data: CompanyReportData,
        scenario: ClimateScenario,
        target_year: int
    ) -> CostAssessmentResult:
        """Perform complete E1 cost assessment for a company under a scenario.

        Args:
            company_profile: Company master data
            company_data: Company environmental report data
            scenario: Climate scenario for cost projections
            target_year: Target year for cost calculation

        Returns:
            CostAssessmentResult with E1 costs, confidence levels, and validation info

        Workflow:
            1. Validate company data (warnings don't block, errors do)
            2. Calculate carbon pricing costs
            3. Aggregate costs into result
            4. Return complete assessment
        """
        # Step 1: Validate company data
        validation_result = self.validator.validate(
            company_data,
            annual_revenue_eur=company_profile.annual_revenue_eur
        )

        # Check for blocking errors
        if not validation_result.is_valid:
            raise ValueError(
                f"Data validation failed with errors: {'; '.join(validation_result.errors)}"
            )

        # Step 2: Calculate carbon pricing costs (MVP: only carbon pricing)
        carbon_cost = self.carbon_calculator.calculate_carbon_cost(
            company_data=company_data,
            scenario=scenario,
            target_year=target_year
        )

        # Step 3: Aggregate cost categories
        cost_categories = [carbon_cost]

        # Calculate total E1 cost with confidence intervals (MVP: just carbon pricing)
        # Future: aggregate multiple cost categories with correlated uncertainties
        e1_total = carbon_cost.amount_eur
        e1_total_lower = carbon_cost.amount_eur_lower
        e1_total_upper = carbon_cost.amount_eur_upper

        # Calculate overall confidence (MVP: same as carbon pricing confidence)
        # Future: weighted average across all E1 cost categories
        overall_confidence = carbon_cost.confidence_level

        # Step 4: Build result with confidence intervals
        result = CostAssessmentResult(
            result_id=self._generate_result_id(company_profile, scenario, target_year),
            company_id=company_profile.company_id,
            scenario_id=scenario.scenario_id,
            reporting_year=company_data.reporting_year,
            assessment_timestamp=datetime.now().isoformat(),
            cost_categories=cost_categories,
            total_environmental_cost_eur=e1_total,  # MVP: E1 only
            total_environmental_cost_eur_lower=e1_total_lower,
            total_environmental_cost_eur_upper=e1_total_upper,
            overall_confidence_level=overall_confidence,
            e1_total_cost_eur=e1_total,
            e1_total_cost_eur_lower=e1_total_lower,
            e1_total_cost_eur_upper=e1_total_upper,
            e2_total_cost_eur=0.0,  # Not assessed in MVP
            e3_total_cost_eur=0.0,
            e4_total_cost_eur=0.0,
            e5_total_cost_eur=0.0,
            has_suspicious_values=len(validation_result.suspicious_values) > 0,
            calculation_notes=self._build_calculation_notes(validation_result, scenario, target_year),
            config_id=None,  # No config tracking for MVP
        )

        # Attach validation warnings to result for transparency
        result.validation_warnings = validation_result.warnings
        result.suspicious_value_details = validation_result.suspicious_values

        return result

    def _generate_result_id(self, company_profile: CompanyProfile, scenario: ClimateScenario, target_year: int) -> str:
        """Generate unique result ID.

        Format: COMPANY_ID_SCENARIO_ID_TARGETYEAR_TIMESTAMP
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{company_profile.company_id}_{scenario.scenario_id}_{target_year}_{timestamp}"

    def _build_calculation_notes(
        self,
        validation_result,
        scenario: ClimateScenario,
        target_year: int
    ) -> str:
        """Build calculation notes for audit trail."""
        notes = [
            f"E1 Climate cost assessment using {scenario.scenario_name}.",
            f"Target year: {target_year}. Cost horizon: {target_year - 2024} years.",
            f"MVP scope: Carbon pricing costs only (Scope 1+2+3 emissions).",
        ]

        if validation_result.warnings:
            notes.append(f"Validation warnings: {len(validation_result.warnings)} (see validation_warnings field).")

        if validation_result.suspicious_values:
            notes.append(f"Suspicious values flagged: {len(validation_result.suspicious_values)} (see suspicious_value_details field).")

        return " ".join(notes)
