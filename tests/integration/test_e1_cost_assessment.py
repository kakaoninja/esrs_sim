"""Integration tests for E1 Climate cost assessment end-to-end workflow.

Tests the complete flow from test fixtures through validation, calculation,
and result generation using SimpleCo and ComplexCorp test data.

References:
- tests/fixtures/company_simple.json: SimpleCo with €350k expected carbon cost
- tests/fixtures/company_complex.json: ComplexCorp with €26M expected carbon cost
- tests/fixtures/scenario_simple_carbon_price.json: €100/tCO2e constant price
- tests/fixtures/scenario_iea_nz2050.json: IEA Net Zero 2050 scenario
"""

import pytest
import json
from pathlib import Path

from src.models.company import CompanyProfile, CompanyReportData
from src.models.scenario import ClimateScenario
from src.validation.data_validator import DataValidator
from src.calculations.carbon_pricing import CarbonPricingCalculator
from src.services.e1_cost_assessment import E1CostAssessmentService


class TestE1CostAssessmentIntegration:
    """Integration tests for complete E1 cost assessment workflow."""

    @pytest.fixture
    def fixtures_dir(self):
        """Get path to test fixtures directory."""
        return Path(__file__).parent.parent / "fixtures"

    @pytest.fixture
    def simple_company_fixture(self, fixtures_dir):
        """Load SimpleCo test fixture from JSON."""
        with open(fixtures_dir / "company_simple.json") as f:
            return json.load(f)

    @pytest.fixture
    def complex_company_fixture(self, fixtures_dir):
        """Load ComplexCorp test fixture from JSON."""
        with open(fixtures_dir / "company_complex.json") as f:
            return json.load(f)

    @pytest.fixture
    def simple_scenario_fixture(self, fixtures_dir):
        """Load simple carbon price scenario from JSON."""
        with open(fixtures_dir / "scenario_simple_carbon_price.json") as f:
            return json.load(f)

    @pytest.fixture
    def iea_nz2050_fixture(self, fixtures_dir):
        """Load IEA NZ2050 scenario from JSON."""
        with open(fixtures_dir / "scenario_iea_nz2050.json") as f:
            return json.load(f)

    @pytest.fixture
    def e1_service(self):
        """Create E1 cost assessment service instance."""
        return E1CostAssessmentService()

    def test_simple_company_e1_assessment(self, simple_company_fixture, simple_scenario_fixture, e1_service):
        """Test complete E1 assessment for SimpleCo.

        Expected outcome from fixture:
        3,500 tCO2e * €100/tCO2e = €350,000 carbon cost
        """
        # Create model objects from fixture data
        company_data = CompanyReportData(**simple_company_fixture['company_report_data'])
        company_profile = CompanyProfile(**simple_company_fixture['company_profile'])
        scenario = ClimateScenario(**simple_scenario_fixture['climate_scenario'])

        # Run E1 cost assessment
        result = e1_service.assess_e1_costs(
            company_profile=company_profile,
            company_data=company_data,
            scenario=scenario,
            target_year=2030
        )

        # Verify result structure
        assert result is not None
        assert hasattr(result, 'e1_total_cost_eur')
        assert hasattr(result, 'cost_categories')

        # Verify carbon pricing cost matches expected
        assert result.e1_total_cost_eur == pytest.approx(350000.0, rel=1e-2)

        # Check that result has carbon pricing category
        carbon_pricing_costs = [c for c in result.cost_categories if c.category_name == "carbon_pricing"]
        assert len(carbon_pricing_costs) == 1
        assert carbon_pricing_costs[0].amount_eur == pytest.approx(350000.0, rel=1e-2)

    def test_complex_company_e1_assessment(self, complex_company_fixture, iea_nz2050_fixture, e1_service):
        """Test complete E1 assessment for ComplexCorp with IEA NZ2050 scenario.

        Expected outcome from fixture:
        Carbon pricing: €26M (200,000 tCO2e * €130/tCO2e for 2030)
        """
        # Create model objects
        company_data = CompanyReportData(**complex_company_fixture['company_report_data'])
        company_profile = CompanyProfile(**complex_company_fixture['company_profile'])
        scenario = ClimateScenario(**iea_nz2050_fixture['climate_scenario'])

        # Run E1 cost assessment
        result = e1_service.assess_e1_costs(
            company_profile=company_profile,
            company_data=company_data,
            scenario=scenario,
            target_year=2030
        )

        # Verify carbon pricing cost
        carbon_pricing_costs = [c for c in result.cost_categories if c.category_name == "carbon_pricing"]
        assert len(carbon_pricing_costs) == 1
        assert carbon_pricing_costs[0].amount_eur == pytest.approx(26000000.0, rel=1e-2)

        # Verify overall E1 cost (carbon pricing only for MVP)
        assert result.e1_total_cost_eur == pytest.approx(26000000.0, rel=1e-2)

    def test_validation_in_e1_workflow(self, simple_company_fixture, simple_scenario_fixture, e1_service):
        """Test that validation is performed during E1 assessment."""
        company_data = CompanyReportData(**simple_company_fixture['company_report_data'])
        company_profile = CompanyProfile(**simple_company_fixture['company_profile'])
        scenario = ClimateScenario(**simple_scenario_fixture['climate_scenario'])

        result = e1_service.assess_e1_costs(
            company_profile=company_profile,
            company_data=company_data,
            scenario=scenario,
            target_year=2030
        )

        # Result should include validation information
        assert hasattr(result, 'validation_warnings')
        # SimpleCo has missing Scope 3, so should have warning
        assert len(result.validation_warnings) == 0  # Actually SimpleCo has Scope 3 in fixture

    def test_cost_as_percentage_of_revenue(self, simple_company_fixture, simple_scenario_fixture, e1_service):
        """Test calculation of cost as percentage of revenue.

        SimpleCo: €350k cost / €10M revenue = 3.5%
        """
        company_data = CompanyReportData(**simple_company_fixture['company_report_data'])
        company_profile = CompanyProfile(**simple_company_fixture['company_profile'])
        scenario = ClimateScenario(**simple_scenario_fixture['climate_scenario'])

        result = e1_service.assess_e1_costs(
            company_profile=company_profile,
            company_data=company_data,
            scenario=scenario,
            target_year=2030
        )

        cost_pct = result.get_cost_as_percentage_of_revenue(company_profile.annual_revenue_eur)

        assert cost_pct == pytest.approx(3.5, rel=1e-2)  # 350k / 10M * 100 = 3.5%

    def test_confidence_level_in_result(self, simple_company_fixture, simple_scenario_fixture, e1_service):
        """Test that confidence level is properly calculated and included in result."""
        company_data = CompanyReportData(**simple_company_fixture['company_report_data'])
        company_profile = CompanyProfile(**simple_company_fixture['company_profile'])
        scenario = ClimateScenario(**simple_scenario_fixture['climate_scenario'])

        result = e1_service.assess_e1_costs(
            company_profile=company_profile,
            company_data=company_data,
            scenario=scenario,
            target_year=2030
        )

        assert hasattr(result, 'overall_confidence_level')
        # 6-year projection should have reduced confidence
        assert 0.70 <= result.overall_confidence_level <= 0.90

    def test_multiple_scenarios_comparison(self, complex_company_fixture, simple_scenario_fixture, iea_nz2050_fixture, e1_service):
        """Test running same company through different scenarios.

        Verifies that results differ based on scenario carbon prices.
        """
        company_data = CompanyReportData(**complex_company_fixture['company_report_data'])
        company_profile = CompanyProfile(**complex_company_fixture['company_profile'])

        scenario_simple = ClimateScenario(**simple_scenario_fixture['climate_scenario'])
        scenario_iea = ClimateScenario(**iea_nz2050_fixture['climate_scenario'])

        # Assess under both scenarios
        result_simple = e1_service.assess_e1_costs(company_profile, company_data, scenario_simple, 2030)
        result_iea = e1_service.assess_e1_costs(company_profile, company_data, scenario_iea, 2030)

        # Simple scenario (€100/tCO2e): 200k tCO2e * €100 = €20M
        assert result_simple.e1_total_cost_eur == pytest.approx(20000000.0, rel=1e-2)

        # IEA scenario (€130/tCO2e): 200k tCO2e * €130 = €26M
        assert result_iea.e1_total_cost_eur == pytest.approx(26000000.0, rel=1e-2)

        # IEA scenario should cost more due to higher carbon price
        assert result_iea.e1_total_cost_eur > result_simple.e1_total_cost_eur

    def test_baseline_year_vs_target_year(self, simple_company_fixture, simple_scenario_fixture, e1_service):
        """Test assessment at baseline year (2024) vs target year (2030).

        For constant price scenario, cost should be same but confidence differs.
        """
        company_data = CompanyReportData(**simple_company_fixture['company_report_data'])
        company_profile = CompanyProfile(**simple_company_fixture['company_profile'])
        scenario = ClimateScenario(**simple_scenario_fixture['climate_scenario'])

        result_2024 = e1_service.assess_e1_costs(company_profile, company_data, scenario, 2024)
        result_2030 = e1_service.assess_e1_costs(company_profile, company_data, scenario, 2030)

        # Cost should be same (constant €100/tCO2e price)
        assert result_2024.e1_total_cost_eur == pytest.approx(result_2030.e1_total_cost_eur, rel=1e-2)

        # Confidence should be higher for baseline year
        assert result_2024.overall_confidence_level > result_2030.overall_confidence_level

    def test_result_serializable_to_json(self, simple_company_fixture, simple_scenario_fixture, e1_service):
        """Test that result can be serialized to JSON (for CSV export later)."""
        company_data = CompanyReportData(**simple_company_fixture['company_report_data'])
        company_profile = CompanyProfile(**simple_company_fixture['company_profile'])
        scenario = ClimateScenario(**simple_scenario_fixture['climate_scenario'])

        result = e1_service.assess_e1_costs(company_profile, company_data, scenario, 2030)

        # Should be able to extract key fields for JSON/CSV export
        export_data = {
            "company_id": company_profile.company_id,
            "scenario_id": scenario.scenario_id,
            "e1_total_cost_eur": result.e1_total_cost_eur,
            "confidence_level": result.overall_confidence_level,
            "cost_categories_count": len(result.cost_categories),
        }

        # Verify it's JSON-serializable
        json_str = json.dumps(export_data)
        assert json_str is not None
