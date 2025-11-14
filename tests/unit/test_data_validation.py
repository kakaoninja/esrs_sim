"""Unit tests for data validation service.

Tests validation logic for company data quality assessment and suspicious value detection.
Per user specification: "complete simulation but include traceable suspicious values"

Test cases cover:
- Missing data detection
- Unrealistic value flagging
- Data quality assessment
- Consistency validation
"""

import pytest
from src.models.company import CompanyReportData
from src.validation.data_validator import DataValidator, ValidationResult


class TestDataValidator:
    """Test suite for DataValidator service."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return DataValidator()

    @pytest.fixture
    def valid_company_data(self):
        """Valid company data with no issues."""
        return CompanyReportData(
            record_id="VALID_001",
            company_id="VALID_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=1000.0,
            scope_2_location_tco2e=500.0,
            scope_2_market_tco2e=500.0,
            scope_3_emissions_tco2e=2000.0,
            carbon_intensity_tco2e_per_eur=0.00035,  # 3,500 tCO2e / 10M EUR
            data_quality_indicator="measured",
            report_source_reference="Annual Report 2024",
        )

    def test_validator_initialization(self, validator):
        """Test DataValidator can be instantiated."""
        assert validator is not None

    def test_validate_complete_data(self, validator, valid_company_data):
        """Test validation of complete, high-quality data."""
        result = validator.validate(valid_company_data)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert len(result.suspicious_values) == 0

    def test_detect_missing_scope3(self, validator):
        """Test detection of missing Scope 3 data (warning, not error)."""
        data = CompanyReportData(
            record_id="MISSING_SCOPE3",
            company_id="TEST_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=1000.0,
            scope_2_location_tco2e=500.0,
            scope_2_market_tco2e=500.0,
            scope_3_emissions_tco2e=None,  # Missing
            carbon_intensity_tco2e_per_eur=0.00015,
            data_quality_indicator="measured",
            report_source_reference="Test",
        )

        result = validator.validate(data)

        assert result.is_valid is True  # Still valid, but has warning
        assert len(result.warnings) >= 1
        assert any("Scope 3" in w for w in result.warnings)

    def test_detect_unrealistic_carbon_intensity(self, validator):
        """Test detection of unrealistic carbon intensity (too high).

        Carbon intensity > 0.01 tCO2e/EUR is extremely high (industry average ~0.0003).
        """
        data = CompanyReportData(
            record_id="HIGH_INTENSITY",
            company_id="TEST_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=1000000.0,  # 1M tCO2e
            scope_2_location_tco2e=0.0,
            scope_2_market_tco2e=0.0,
            scope_3_emissions_tco2e=0.0,
            carbon_intensity_tco2e_per_eur=0.1,  # 0.1 tCO2e/EUR = unrealistically high
            data_quality_indicator="measured",
            report_source_reference="Test",
        )

        result = validator.validate(data)

        assert len(result.suspicious_values) >= 1
        assert any("carbon" in str(s).lower() and "intensity" in str(s).lower()
                  for s in result.suspicious_values)

    def test_detect_unrealistic_low_emissions(self, validator):
        """Test detection of suspiciously low emissions for large revenue.

        Very low or zero emissions for a manufacturing company may be suspicious.
        """
        data = CompanyReportData(
            record_id="LOW_EMISSIONS",
            company_id="TEST_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=0.1,  # Near-zero emissions is suspicious
            scope_2_location_tco2e=0.0,
            scope_2_market_tco2e=0.0,
            scope_3_emissions_tco2e=0.0,
            carbon_intensity_tco2e_per_eur=0.000001,  # Unrealistically low
            data_quality_indicator="estimated",
            report_source_reference="Test",
        )

        result = validator.validate(data)

        assert len(result.suspicious_values) >= 1
        assert any("low" in str(s).lower() or "intensity" in str(s).lower()
                  for s in result.suspicious_values)

    def test_detect_inconsistent_carbon_intensity(self, validator):
        """Test detection of carbon intensity inconsistent with emissions.

        If calculated intensity doesn't match reported intensity, flag it.
        Requires revenue to be passed in validation context.
        """
        data = CompanyReportData(
            record_id="INCONSISTENT",
            company_id="TEST_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=3500.0,
            scope_2_location_tco2e=0.0,
            scope_2_market_tco2e=0.0,
            scope_3_emissions_tco2e=0.0,
            carbon_intensity_tco2e_per_eur=0.0001,  # Says 0.0001
            # But 3,500 tCO2e / 10M EUR = 0.00035, not 0.0001
            data_quality_indicator="measured",
            report_source_reference="Test",
        )

        # Validator needs revenue context to check consistency
        result = validator.validate(data, annual_revenue_eur=10000000.0)

        assert len(result.suspicious_values) >= 1
        assert any("intensity" in str(s).lower() for s in result.suspicious_values)

    def test_data_quality_indicator_assessment(self, validator):
        """Test that data quality indicator affects validation severity."""
        # "incomplete" data quality should generate warnings
        data = CompanyReportData(
            record_id="INCOMPLETE_QUALITY",
            company_id="TEST_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=1000.0,
            scope_2_location_tco2e=500.0,
            scope_2_market_tco2e=500.0,
            scope_3_emissions_tco2e=None,
            carbon_intensity_tco2e_per_eur=0.00035,
            data_quality_indicator="incomplete",  # Low quality
            report_source_reference="Test",
        )

        result = validator.validate(data)

        assert len(result.warnings) >= 1
        assert any("quality" in w.lower() or "incomplete" in w.lower()
                  for w in result.warnings)

    def test_detect_negative_recycling_rate_edge_case(self, validator):
        """Test edge case handling (should not occur due to model validation)."""
        # This test documents that model-level validation prevents invalid data
        # DataValidator focuses on business logic validation
        pass  # Model validation prevents this from reaching validator

    def test_pollution_metrics_validation(self, validator):
        """Test validation of pollution metrics JSON data."""
        data = CompanyReportData(
            record_id="POLLUTION_DATA",
            company_id="TEST_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=1000.0,
            scope_2_location_tco2e=500.0,
            scope_2_market_tco2e=500.0,
            scope_3_emissions_tco2e=2000.0,
            carbon_intensity_tco2e_per_eur=0.00035,
            pollution_metrics='{"NOx_tonnes": 100, "SOx_tonnes": 50}',
            data_quality_indicator="measured",
            report_source_reference="Test",
        )

        result = validator.validate(data)

        assert result.is_valid is True
        # Valid JSON pollution data should not generate errors

    def test_invalid_pollution_metrics_json(self, validator):
        """Test detection of invalid JSON in pollution_metrics."""
        data = CompanyReportData(
            record_id="BAD_JSON",
            company_id="TEST_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=1000.0,
            scope_2_location_tco2e=500.0,
            scope_2_market_tco2e=500.0,
            scope_3_emissions_tco2e=2000.0,
            carbon_intensity_tco2e_per_eur=0.00035,
            pollution_metrics='{"NOx_tonnes": invalid}',  # Invalid JSON
            data_quality_indicator="measured",
            report_source_reference="Test",
        )

        result = validator.validate(data)

        assert len(result.errors) >= 1
        assert any("JSON" in e or "pollution" in e.lower() for e in result.errors)

    def test_validation_result_structure(self, validator, valid_company_data):
        """Test ValidationResult has expected structure."""
        result = validator.validate(valid_company_data)

        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'errors')
        assert hasattr(result, 'warnings')
        assert hasattr(result, 'suspicious_values')
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.suspicious_values, list)

    def test_multiple_issues_detected(self, validator):
        """Test that multiple validation issues are all detected."""
        data = CompanyReportData(
            record_id="MULTIPLE_ISSUES",
            company_id="TEST_CO",
            reporting_year=2024,
            scope_1_emissions_tco2e=1000.0,
            scope_2_location_tco2e=500.0,
            scope_2_market_tco2e=500.0,
            scope_3_emissions_tco2e=None,  # Missing (warning)
            carbon_intensity_tco2e_per_eur=0.05,  # Too high (suspicious)
            data_quality_indicator="incomplete",  # Low quality (warning)
            report_source_reference="Test",
        )

        result = validator.validate(data)

        # Should have both warnings and suspicious values
        assert len(result.warnings) >= 2  # Missing Scope 3 + incomplete quality
        assert len(result.suspicious_values) >= 1  # High carbon intensity
