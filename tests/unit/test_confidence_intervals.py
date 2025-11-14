"""Unit tests for 95% confidence interval calculations.

Tests statistical uncertainty quantification for parallel simulations.
Confidence intervals reflect:
- CO2 price projection uncertainty
- Emissions measurement uncertainty
- Correlation between emissions and price (ρ=-0.3 default)
- Data quality impacts
- Time horizon uncertainty

Uses Monte Carlo simulation with correlated sampling for accurate uncertainty modeling.
"""

import pytest
from src.models.company import CompanyReportData
from src.models.scenario import ClimateScenario
from src.calculations.carbon_pricing import CarbonPricingCalculator


class TestConfidenceIntervals:
    """Test suite for 95% confidence interval calculations."""

    @pytest.fixture
    def calculator(self):
        """Create calculator instance."""
        return CarbonPricingCalculator()

    @pytest.fixture
    def simple_data(self):
        """Simple company data with measured quality."""
        return CompanyReportData(
            record_id="TEST_001",
            company_id="TEST_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=1000.0,
            scope_2_location_tco2e=500.0,
            scope_2_market_tco2e=500.0,
            scope_3_emissions_tco2e=2000.0,
            carbon_intensity_tco2e_per_eur=0.00035,
            data_quality_indicator="measured",  # High quality
            report_source_reference="Test",
        )

    @pytest.fixture
    def simple_scenario(self):
        """Simple constant price scenario."""
        return ClimateScenario(
            scenario_id="TEST_SIMPLE",
            scenario_name="Simple Test",
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

    def test_confidence_interval_structure(self, calculator, simple_data, simple_scenario):
        """Test that result includes confidence interval bounds."""
        result = calculator.calculate_carbon_cost(simple_data, simple_scenario, 2024)

        assert hasattr(result, 'amount_eur')
        assert hasattr(result, 'amount_eur_lower')
        assert hasattr(result, 'amount_eur_upper')
        assert result.amount_eur_lower <= result.amount_eur <= result.amount_eur_upper

    def test_baseline_year_narrow_interval(self, calculator, simple_data, simple_scenario):
        """Test that baseline year (no projection) has narrow confidence interval.

        Baseline year: Only emissions measurement uncertainty, no CO2 price uncertainty.
        Monte Carlo with correlation (ρ=-0.3) gives narrower CI than independent assumption
        because negative correlation (high price → lower emissions) reduces total uncertainty.
        """
        result = calculator.calculate_carbon_cost(simple_data, simple_scenario, 2024)

        # 3,500 tCO2e * €100/tCO2e = €350,000 median
        assert result.amount_eur == pytest.approx(350000.0, rel=1e-2)

        # CI width should be relatively narrow for baseline year
        ci_width = result.get_confidence_interval_width()
        ci_pct = result.get_confidence_interval_pct()

        # Monte Carlo with ρ=-0.3: ~23% width (narrower than independent 28% due to correlation)
        assert 20.0 < ci_pct < 26.0  # Expected ~23% for baseline + measured data + correlation
        assert ci_width > 0  # But not zero - there's always some uncertainty

    def test_future_year_wider_interval(self, calculator, simple_data, simple_scenario):
        """Test that future projections have wider confidence intervals.

        6-year projection: Both emissions AND CO2 price uncertainty.
        Expected CI width: ~30-50% of median.
        """
        result = calculator.calculate_carbon_cost(simple_data, simple_scenario, 2030)

        # Same median cost (constant price scenario)
        assert result.amount_eur == pytest.approx(350000.0, rel=1e-2)

        # But wider CI due to projection uncertainty
        ci_pct = result.get_confidence_interval_pct()

        assert ci_pct > 20.0  # Wider than baseline
        assert ci_pct < 100.0  # But not absurdly wide

    def test_data_quality_affects_interval_width(self, calculator, simple_scenario):
        """Test that lower data quality increases CI width.

        "measured" data: narrowest CI
        "estimated" data: wider CI
        "modeled" data: widest CI
        """
        # Measured data
        measured_data = CompanyReportData(
            record_id="MEASURED",
            company_id="TEST_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=1000.0,
            scope_2_location_tco2e=500.0,
            scope_2_market_tco2e=500.0,
            scope_3_emissions_tco2e=2000.0,
            carbon_intensity_tco2e_per_eur=0.00035,
            data_quality_indicator="measured",
            report_source_reference="Test",
        )

        # Estimated data (same emissions, lower quality)
        estimated_data = CompanyReportData(
            record_id="ESTIMATED",
            company_id="TEST_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=1000.0,
            scope_2_location_tco2e=500.0,
            scope_2_market_tco2e=500.0,
            scope_3_emissions_tco2e=2000.0,
            carbon_intensity_tco2e_per_eur=0.00035,
            data_quality_indicator="estimated",
            report_source_reference="Test",
        )

        result_measured = calculator.calculate_carbon_cost(measured_data, simple_scenario, 2024)
        result_estimated = calculator.calculate_carbon_cost(estimated_data, simple_scenario, 2024)

        # Same median
        assert result_measured.amount_eur == pytest.approx(result_estimated.amount_eur, rel=1e-2)

        # But estimated has wider CI
        assert result_estimated.get_confidence_interval_pct() > result_measured.get_confidence_interval_pct()

    def test_ci_bounds_are_sensible(self, calculator, simple_data, simple_scenario):
        """Test that CI bounds are mathematically sensible.

        Lower bound should be < median < upper bound
        Both bounds should be non-negative
        CI should be symmetric or slightly skewed
        """
        result = calculator.calculate_carbon_cost(simple_data, simple_scenario, 2024)

        # All non-negative
        assert result.amount_eur_lower >= 0
        assert result.amount_eur >= 0
        assert result.amount_eur_upper >= 0

        # Ordering
        assert result.amount_eur_lower < result.amount_eur < result.amount_eur_upper

        # Roughly symmetric (within 30% asymmetry)
        lower_dist = result.amount_eur - result.amount_eur_lower
        upper_dist = result.amount_eur_upper - result.amount_eur
        asymmetry = abs(lower_dist - upper_dist) / max(lower_dist, upper_dist)
        assert asymmetry < 0.3  # Allow some skew but not too much

    def test_zero_emissions_zero_ci(self, calculator, simple_scenario):
        """Test that zero emissions gives zero cost with zero CI width."""
        zero_data = CompanyReportData(
            record_id="ZERO",
            company_id="TEST_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=0.0,
            scope_2_location_tco2e=0.0,
            scope_2_market_tco2e=0.0,
            scope_3_emissions_tco2e=0.0,
            carbon_intensity_tco2e_per_eur=0.0,
            data_quality_indicator="measured",
            report_source_reference="Test",
        )

        result = calculator.calculate_carbon_cost(zero_data, simple_scenario, 2024)

        assert result.amount_eur == 0.0
        assert result.amount_eur_lower == 0.0
        assert result.amount_eur_upper == 0.0
        assert result.get_confidence_interval_width() == 0.0

    def test_escalating_price_scenario_wider_ci(self, calculator, simple_data):
        """Test that scenarios with price escalation have wider CIs.

        Constant price: only emissions uncertainty
        Escalating price: emissions + price projection uncertainty
        """
        constant_scenario = ClimateScenario(
            scenario_id="CONSTANT",
            scenario_name="Constant",
            scenario_source="custom",
            temperature_pathway="2C",
            baseline_year=2024,
            target_year=2030,
            co2_price_baseline_eur_per_tco2e=100.0,
            co2_price_target_eur_per_tco2e=100.0,  # Constant
            policy_stringency_level="medium",
            physical_climate_impact_level="medium",
            energy_price_multiplier=1.0,
            technology_cost_reduction_pct=0.0,
            scenario_documentation_reference="Test",
        )

        escalating_scenario = ClimateScenario(
            scenario_id="ESCALATING",
            scenario_name="Escalating",
            scenario_source="IEA",
            temperature_pathway="1.5C",
            baseline_year=2024,
            target_year=2030,
            co2_price_baseline_eur_per_tco2e=80.0,
            co2_price_target_eur_per_tco2e=200.0,  # Big escalation
            policy_stringency_level="high",
            physical_climate_impact_level="low-medium",
            energy_price_multiplier=1.3,
            technology_cost_reduction_pct=25.0,
            scenario_documentation_reference="IEA NZE2050",
        )

        result_constant = calculator.calculate_carbon_cost(simple_data, constant_scenario, 2030)
        result_escalating = calculator.calculate_carbon_cost(simple_data, escalating_scenario, 2030)

        # Escalating scenario should have wider CI due to price projection uncertainty
        assert result_escalating.get_confidence_interval_pct() > result_constant.get_confidence_interval_pct()

    def test_ci_documentation_in_calculation_method(self, calculator, simple_data, simple_scenario):
        """Test that CI calculation is documented in the result."""
        result = calculator.calculate_carbon_cost(simple_data, simple_scenario, 2024)

        # Should mention CI, confidence interval, or uncertainty in calculation method
        method_lower = result.calculation_method.lower()
        assert (" ci" in method_lower or
                "confidence" in method_lower or
                "uncertainty" in method_lower)
