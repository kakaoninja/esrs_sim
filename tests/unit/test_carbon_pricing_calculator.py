"""Unit tests for carbon pricing cost calculator.

Tests the core carbon pricing calculation logic using known test data.
This follows TDD - tests written first, then implementation.

Test Data Reference:
- SimpleCo: 3,500 tCO2e total emissions, €100/tCO2e price → €350,000 cost
- ComplexCorp: 200,000 tCO2e total emissions, €130/tCO2e price → €26,000,000 cost
"""

import pytest
from src.models.company import CompanyReportData
from src.models.scenario import ClimateScenario
from src.calculations.carbon_pricing import CarbonPricingCalculator


class TestCarbonPricingCalculator:
    """Test suite for CarbonPricingCalculator."""

    @pytest.fixture
    def simple_company_data(self):
        """SimpleCo test data: 3,500 tCO2e total emissions."""
        return CompanyReportData(
            record_id="TEST_SIMPLE_001_2024",
            company_id="TEST_SIMPLE_001",
            reporting_year=2024,
            scope_1_emissions_tco2e=1000.0,
            scope_2_location_tco2e=500.0,
            scope_2_market_tco2e=500.0,
            scope_3_emissions_tco2e=2000.0,
            carbon_intensity_tco2e_per_eur=0.00035,
            data_quality_indicator="measured",
            report_source_reference="Test Fixture",
        )

    @pytest.fixture
    def simple_scenario(self):
        """Simple scenario: constant €100/tCO2e carbon price."""
        return ClimateScenario(
            scenario_id="TEST_SIMPLE_CARBON_PRICE",
            scenario_name="Simple Carbon Price Test Scenario",
            scenario_source="custom",
            temperature_pathway="2C",
            baseline_year=2024,
            target_year=2030,
            co2_price_baseline_eur_per_tco2e=100.0,
            co2_price_target_eur_per_tco2e=100.0,
            policy_stringency_level="medium",
            physical_climate_impact_level="medium",
            energy_price_multiplier=1.0,
            technology_cost_reduction_pct=0.0,
            scenario_documentation_reference="Test Fixture",
        )

    @pytest.fixture
    def complex_company_data(self):
        """ComplexCorp test data: 200,000 tCO2e total emissions."""
        return CompanyReportData(
            record_id="TEST_COMPLEX_001_2024",
            company_id="TEST_COMPLEX_001",
            reporting_year=2024,
            scope_1_emissions_tco2e=50000.0,
            scope_2_location_tco2e=30000.0,
            scope_2_market_tco2e=30000.0,
            scope_3_emissions_tco2e=120000.0,
            carbon_intensity_tco2e_per_eur=0.0004,
            data_quality_indicator="measured",
            report_source_reference="Test Fixture",
        )

    @pytest.fixture
    def iea_nz2050_scenario(self):
        """IEA Net Zero 2050 scenario: €80 baseline → €130 target."""
        return ClimateScenario(
            scenario_id="IEA_NZ2050_TEST",
            scenario_name="IEA Net Zero by 2050 Test Scenario",
            scenario_source="IEA",
            temperature_pathway="1.5C",
            baseline_year=2024,
            target_year=2030,
            co2_price_baseline_eur_per_tco2e=80.0,
            co2_price_target_eur_per_tco2e=130.0,
            policy_stringency_level="high",
            physical_climate_impact_level="low-medium",
            energy_price_multiplier=1.3,
            technology_cost_reduction_pct=25.0,
            scenario_documentation_reference="IEA NZE2050",
        )

    def test_calculator_initialization(self):
        """Test CarbonPricingCalculator can be instantiated."""
        calculator = CarbonPricingCalculator()
        assert calculator is not None

    def test_simple_carbon_cost_baseline_year(self, simple_company_data, simple_scenario):
        """Test carbon cost at baseline year (2024).

        Expected: 3,500 tCO2e * €100/tCO2e = €350,000
        Confidence: 0.95 (from scenario)
        """
        calculator = CarbonPricingCalculator()
        result = calculator.calculate_carbon_cost(
            company_data=simple_company_data,
            scenario=simple_scenario,
            target_year=2024  # Use baseline year
        )

        assert result is not None
        assert result.amount_eur == pytest.approx(350000.0, rel=1e-2)
        assert result.confidence_level == pytest.approx(0.95, abs=0.01)
        assert result.esrs_topic == "E1"
        assert result.category_name == "carbon_pricing"

    def test_simple_carbon_cost_target_year(self, simple_company_data, simple_scenario):
        """Test carbon cost at target year (2030) with constant price.

        Expected: 3,500 tCO2e * €100/tCO2e = €350,000 (same as baseline)
        """
        calculator = CarbonPricingCalculator()
        result = calculator.calculate_carbon_cost(
            company_data=simple_company_data,
            scenario=simple_scenario,
            target_year=2030
        )

        assert result.amount_eur == pytest.approx(350000.0, rel=1e-2)

    def test_complex_carbon_cost_with_price_escalation(self, complex_company_data, iea_nz2050_scenario):
        """Test carbon cost with price escalation (IEA NZ2050 scenario).

        Expected at 2030 target year: 200,000 tCO2e * €130/tCO2e = €26,000,000
        Confidence: 0.80 (lower due to projection uncertainty)
        """
        calculator = CarbonPricingCalculator()
        result = calculator.calculate_carbon_cost(
            company_data=complex_company_data,
            scenario=iea_nz2050_scenario,
            target_year=2030
        )

        assert result.amount_eur == pytest.approx(26000000.0, rel=1e-2)
        assert result.confidence_level == pytest.approx(0.80, abs=0.05)
        assert result.cost_horizon_years == 6  # 2030 - 2024

    def test_carbon_cost_interpolated_year(self, complex_company_data, iea_nz2050_scenario):
        """Test carbon cost at intermediate year (2027) with linear interpolation.

        Price interpolation: €80 + (€130 - €80) * (2027 - 2024) / (2030 - 2024)
                           = €80 + €50 * 3/6 = €80 + €25 = €105/tCO2e
        Expected: 200,000 tCO2e * €105/tCO2e = €21,000,000
        """
        calculator = CarbonPricingCalculator()
        result = calculator.calculate_carbon_cost(
            company_data=complex_company_data,
            scenario=iea_nz2050_scenario,
            target_year=2027
        )

        assert result.amount_eur == pytest.approx(21000000.0, rel=1e-2)
        assert result.cost_horizon_years == 3  # 2027 - 2024

    def test_total_emissions_calculation(self, simple_company_data):
        """Test that calculator uses Scope 1 + 2 (market) + 3 for total emissions.

        Expected: 1,000 + 500 + 2,000 = 3,500 tCO2e
        """
        calculator = CarbonPricingCalculator()
        total = calculator._calculate_total_emissions(simple_company_data)

        assert total == pytest.approx(3500.0, rel=1e-6)

    def test_total_emissions_without_scope3(self):
        """Test emissions calculation when Scope 3 is None."""
        company_data = CompanyReportData(
            record_id="TEST_NO_SCOPE3",
            company_id="TEST_001",
            reporting_year=2024,
            scope_1_emissions_tco2e=1000.0,
            scope_2_location_tco2e=500.0,
            scope_2_market_tco2e=400.0,
            scope_3_emissions_tco2e=None,  # No Scope 3 data
            carbon_intensity_tco2e_per_eur=0.0001,
            data_quality_indicator="estimated",
            report_source_reference="Test",
        )

        calculator = CarbonPricingCalculator()
        total = calculator._calculate_total_emissions(company_data)

        assert total == pytest.approx(1400.0, rel=1e-6)  # 1,000 + 400

    def test_zero_emissions(self):
        """Test handling of zero emissions (edge case)."""
        company_data = CompanyReportData(
            record_id="TEST_ZERO",
            company_id="TEST_001",
            reporting_year=2024,
            scope_1_emissions_tco2e=0.0,
            scope_2_location_tco2e=0.0,
            scope_2_market_tco2e=0.0,
            scope_3_emissions_tco2e=0.0,
            carbon_intensity_tco2e_per_eur=0.0,
            data_quality_indicator="measured",
            report_source_reference="Test",
        )

        scenario = ClimateScenario(
            scenario_id="TEST",
            scenario_name="Test",
            scenario_source="custom",
            temperature_pathway="2C",
            baseline_year=2024,
            target_year=2030,
            co2_price_baseline_eur_per_tco2e=100.0,
            co2_price_target_eur_per_tco2e=100.0,
            policy_stringency_level="medium",
            physical_climate_impact_level="medium",
            energy_price_multiplier=1.0,
            technology_cost_reduction_pct=0.0,
            scenario_documentation_reference="Test",
        )

        calculator = CarbonPricingCalculator()
        result = calculator.calculate_carbon_cost(company_data, scenario, 2024)

        assert result.amount_eur == 0.0

    def test_confidence_level_adjustment_for_projections(self, simple_company_data, simple_scenario):
        """Test that confidence decreases for longer time horizons.

        Baseline year (2024): high confidence
        Target year (2030): lower confidence due to projection uncertainty
        """
        calculator = CarbonPricingCalculator()

        result_2024 = calculator.calculate_carbon_cost(simple_company_data, simple_scenario, 2024)
        result_2030 = calculator.calculate_carbon_cost(simple_company_data, simple_scenario, 2030)

        # Confidence should decrease with longer horizon
        assert result_2030.confidence_level <= result_2024.confidence_level
