"""Data validation service for company environmental data.

Validates data quality and flags suspicious values per user specification:
"complete simulation but include traceable suspicious values"

Validation focuses on:
- Missing data detection
- Unrealistic/suspicious value flagging
- Data quality assessment
- Consistency checks
"""

from dataclasses import dataclass, field
from typing import Optional
import json

from ..models.company import CompanyReportData


@dataclass
class ValidationResult:
    """Result of data validation with errors, warnings, and suspicious values.

    Attributes:
        is_valid: Whether data passes validation (no blocking errors)
        errors: List of error messages (block calculation)
        warnings: List of warning messages (calculation proceeds with caution)
        suspicious_values: List of suspicious value descriptions (flagged but not blocked)
    """

    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suspicious_values: list[str] = field(default_factory=list)


class DataValidator:
    """Validator for company environmental report data.

    Performs business logic validation beyond model-level constraints.
    Flags suspicious values without blocking calculations (per user spec).
    """

    # Thresholds for suspicious value detection
    CARBON_INTENSITY_MAX_NORMAL = 0.01  # tCO2e/EUR (very high threshold)
    CARBON_INTENSITY_MIN_NORMAL = 0.00001  # tCO2e/EUR (very low threshold)
    CARBON_INTENSITY_TOLERANCE = 0.20  # 20% tolerance for consistency check

    def validate(
        self,
        company_data: CompanyReportData,
        annual_revenue_eur: Optional[float] = None
    ) -> ValidationResult:
        """Validate company environmental data.

        Args:
            company_data: Company report data to validate
            annual_revenue_eur: Optional revenue for consistency checks

        Returns:
            ValidationResult with errors, warnings, and suspicious values
        """
        result = ValidationResult()

        # Check data quality indicator
        self._check_data_quality(company_data, result)

        # Check for missing data
        self._check_missing_data(company_data, result)

        # Check for unrealistic values
        self._check_unrealistic_values(company_data, result)

        # Check carbon intensity consistency (if revenue provided)
        if annual_revenue_eur is not None:
            self._check_carbon_intensity_consistency(company_data, annual_revenue_eur, result)

        # Check pollution metrics JSON validity
        self._check_pollution_metrics(company_data, result)

        # Set overall validity (errors block calculation, warnings/suspicious don't)
        result.is_valid = len(result.errors) == 0

        return result

    def _check_data_quality(self, data: CompanyReportData, result: ValidationResult):
        """Check data quality indicator and flag if low quality."""
        if data.data_quality_indicator in ["incomplete", "modeled"]:
            result.warnings.append(
                f"Data quality is '{data.data_quality_indicator}'. "
                f"Results may have higher uncertainty."
            )

    def _check_missing_data(self, data: CompanyReportData, result: ValidationResult):
        """Check for missing data fields and flag warnings."""
        # Scope 3 missing is common and acceptable (warning only)
        if data.scope_3_emissions_tco2e is None:
            result.warnings.append(
                "Scope 3 emissions data is missing. "
                "Carbon cost calculation will use Scope 1+2 only."
            )

        # Missing E2-E5 environmental data is acceptable for E1-only assessment
        # (these would only matter for full ESRS E1-E5 assessment)

    def _check_unrealistic_values(self, data: CompanyReportData, result: ValidationResult):
        """Check for unrealistic or suspicious values."""
        # Check carbon intensity range
        if data.carbon_intensity_tco2e_per_eur > self.CARBON_INTENSITY_MAX_NORMAL:
            result.suspicious_values.append(
                f"Carbon intensity ({data.carbon_intensity_tco2e_per_eur:.6f} tCO2e/EUR) "
                f"is extremely high (> {self.CARBON_INTENSITY_MAX_NORMAL}). "
                f"This may indicate data quality issues."
            )

        if data.carbon_intensity_tco2e_per_eur < self.CARBON_INTENSITY_MIN_NORMAL:
            result.suspicious_values.append(
                f"Carbon intensity ({data.carbon_intensity_tco2e_per_eur:.8f} tCO2e/EUR) "
                f"is extremely low (< {self.CARBON_INTENSITY_MIN_NORMAL}). "
                f"This may indicate incomplete emissions data or data quality issues."
            )

    def _check_carbon_intensity_consistency(
        self,
        data: CompanyReportData,
        annual_revenue_eur: float,
        result: ValidationResult
    ):
        """Check if reported carbon intensity matches calculated intensity.

        Args:
            data: Company report data
            annual_revenue_eur: Annual revenue for calculation
            result: ValidationResult to update
        """
        # Calculate expected intensity from emissions and revenue
        total_emissions = data.scope_1_emissions_tco2e + data.scope_2_market_tco2e
        if data.scope_3_emissions_tco2e is not None:
            total_emissions += data.scope_3_emissions_tco2e

        if annual_revenue_eur > 0:
            calculated_intensity = total_emissions / annual_revenue_eur

            # Check if reported matches calculated (within tolerance)
            reported_intensity = data.carbon_intensity_tco2e_per_eur
            diff = abs(calculated_intensity - reported_intensity)
            max_diff = calculated_intensity * self.CARBON_INTENSITY_TOLERANCE

            if diff > max_diff:
                result.suspicious_values.append(
                    f"Reported carbon intensity ({reported_intensity:.6f} tCO2e/EUR) "
                    f"differs from calculated intensity ({calculated_intensity:.6f} tCO2e/EUR) "
                    f"by more than {self.CARBON_INTENSITY_TOLERANCE*100:.0f}%. "
                    f"Emissions: {total_emissions:,.0f} tCO2e, Revenue: €{annual_revenue_eur:,.0f}."
                )

    def _check_pollution_metrics(self, data: CompanyReportData, result: ValidationResult):
        """Check validity of pollution metrics JSON."""
        if data.pollution_metrics is not None:
            try:
                json.loads(data.pollution_metrics)
            except json.JSONDecodeError as e:
                result.errors.append(
                    f"Invalid JSON in pollution_metrics field: {str(e)}"
                )
