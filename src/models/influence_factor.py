"""Influence factor models for ESRS environmental cost assessment.

Influence factors are external variables (carbon prices, energy prices, policy
stringency, etc.) that drive environmental costs under different climate scenarios.

References:
- NGFS Scenarios: Defines key influence factors for climate transition analysis
- IPCC AR6: Physical climate risk factors
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class InfluenceFactor:
    """Definition of an influence factor for scenario-based cost modeling.

    Represents a key variable (e.g., CO2 price, energy price, regulatory stringency)
    that influences environmental costs. Each factor is linked to a specific
    climate scenario and ESRS topic.

    Attributes:
        factor_id: Unique factor identifier
        factor_name: Human-readable factor name
        factor_type: Type of influence factor (carbon_pricing, energy_pricing, regulatory, etc.)
        esrs_topic: ESRS topic code (E1, E2, E3, E4, E5)
        unit: Measurement unit (EUR/tCO2e, multiplier, index_0_10, percentage, etc.)
        scenario_id: Foreign key to ClimateScenario
        baseline_value: Factor value at baseline year
        target_value: Factor value at target year
        confidence_level: Confidence in factor projection (0.0-1.0)
        data_source_reference: Reference to source for factor values

    Validation:
        - confidence_level between 0.0 and 1.0
        - esrs_topic in E1-E5
        - factor_type in allowed values
    """

    factor_id: str
    factor_name: str
    factor_type: str
    esrs_topic: str
    unit: str
    scenario_id: str
    baseline_value: float
    target_value: float
    confidence_level: float
    data_source_reference: str

    # Allowed values
    ALLOWED_ESRS_TOPICS = ["E1", "E2", "E3", "E4", "E5"]
    ALLOWED_FACTOR_TYPES = [
        "carbon_pricing",
        "energy_pricing",
        "regulatory",
        "technology",
        "physical_risk",
        "resource_scarcity",
        "market",
        "other"
    ]

    def __post_init__(self):
        """Validate influence factor data."""
        # Validate confidence level
        if not (0.0 <= self.confidence_level <= 1.0):
            raise ValueError(f"confidence_level must be 0.0-1.0, got {self.confidence_level}")

        # Validate ESRS topic
        if self.esrs_topic not in self.ALLOWED_ESRS_TOPICS:
            raise ValueError(f"esrs_topic must be one of {self.ALLOWED_ESRS_TOPICS}, got '{self.esrs_topic}'")

        # Validate factor type
        if self.factor_type not in self.ALLOWED_FACTOR_TYPES:
            raise ValueError(f"factor_type must be one of {self.ALLOWED_FACTOR_TYPES}, got '{self.factor_type}'")

    def get_value_for_year(self, year: int, baseline_year: int, target_year: int) -> float:
        """Calculate interpolated factor value for a given year.

        Linear interpolation between baseline and target year values.

        Args:
            year: Year to calculate factor value for
            baseline_year: Baseline year from scenario
            target_year: Target year from scenario

        Returns:
            Factor value for the given year
        """
        if year <= baseline_year:
            return self.baseline_value
        if year >= target_year:
            return self.target_value

        # Linear interpolation
        years_elapsed = year - baseline_year
        total_years = target_year - baseline_year
        value_change = self.target_value - self.baseline_value

        return self.baseline_value + (value_change * years_elapsed / total_years)

    def is_regulatory_factor(self) -> bool:
        """Check if factor is regulatory/policy-driven.

        Returns:
            True if factor_type is 'regulatory'
        """
        return self.factor_type == "regulatory"

    def is_carbon_pricing(self) -> bool:
        """Check if factor is carbon pricing.

        Returns:
            True if factor_type is 'carbon_pricing'
        """
        return self.factor_type == "carbon_pricing"


@dataclass
class InfluenceFactorValue:
    """Time-series value for an influence factor.

    Represents the value of an influence factor at a specific year within
    a scenario. Used for non-linear factor projections where linear
    interpolation is insufficient.

    Attributes:
        value_id: Unique value identifier
        factor_id: Foreign key to InfluenceFactor
        year: Year for this value (2020-2100)
        value: Factor value for this year
        notes: Optional notes about this specific value

    Validation:
        - year between 2020 and 2100
    """

    value_id: str
    factor_id: str
    year: int
    value: float
    notes: Optional[str] = None

    def __post_init__(self):
        """Validate influence factor value data."""
        # Validate year
        if not (2020 <= self.year <= 2100):
            raise ValueError(f"year must be between 2020 and 2100, got {self.year}")
