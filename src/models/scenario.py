"""Climate scenario models for ESRS environmental cost assessment.

References:
- IEA Net Zero by 2050: https://www.iea.org/reports/net-zero-by-2050
- NGFS Climate Scenarios: https://www.ngfs.net/ngfs-scenarios-portal/
- IPCC AR6: Temperature pathways and climate projections
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClimateScenario:
    """Climate scenario for forward-looking cost modeling.

    Represents a climate transition scenario (e.g., IEA NZ2050, NGFS) with
    key parameters for modeling future costs under different policy, technology,
    and physical climate pathways.

    Attributes:
        scenario_id: Unique scenario identifier
        scenario_name: Human-readable scenario name
        scenario_source: Source organization (IEA, NGFS, IPCC, custom, etc.)
        temperature_pathway: Temperature target (1.5C, 2C, 3C, 4C+)
        baseline_year: Starting year for scenario (typically current year)
        target_year: Target year for projections (e.g., 2030, 2050)
        co2_price_baseline_eur_per_tco2e: CO2 price at baseline year (EUR/tCO2e, >= 0)
        co2_price_target_eur_per_tco2e: CO2 price at target year (EUR/tCO2e, >= 0)
        policy_stringency_level: Policy stringency (low/medium/high/very_high)
        physical_climate_impact_level: Physical climate impacts (low/low-medium/medium/medium-high/high)
        energy_price_multiplier: Energy price change multiplier (>= 0, 1.0 = no change)
        technology_cost_reduction_pct: Technology cost reduction percentage (0-100)
        scenario_documentation_reference: Reference to source documentation

    Validation:
        - baseline_year and target_year between 2020 and 2100
        - target_year > baseline_year
        - CO2 prices >= 0
        - energy_price_multiplier >= 0
        - technology_cost_reduction_pct between 0 and 100
        - policy_stringency_level in allowed values
        - physical_climate_impact_level in allowed values
        - temperature_pathway in allowed values
    """

    scenario_id: str
    scenario_name: str
    scenario_source: str
    temperature_pathway: str
    baseline_year: int
    target_year: int
    co2_price_baseline_eur_per_tco2e: float
    co2_price_target_eur_per_tco2e: float
    policy_stringency_level: str
    physical_climate_impact_level: str
    energy_price_multiplier: float
    technology_cost_reduction_pct: float
    scenario_documentation_reference: str

    # Allowed values for categorical fields
    ALLOWED_TEMPERATURE_PATHWAYS = ["1.5C", "2C", "3C", "4C+"]
    ALLOWED_POLICY_STRINGENCY = ["low", "medium", "high", "very_high"]
    ALLOWED_PHYSICAL_IMPACT = ["low", "low-medium", "medium", "medium-high", "high"]

    def __post_init__(self):
        """Validate climate scenario data."""
        # Validate years
        if not (2020 <= self.baseline_year <= 2100):
            raise ValueError(f"baseline_year must be between 2020 and 2100, got {self.baseline_year}")
        if not (2020 <= self.target_year <= 2100):
            raise ValueError(f"target_year must be between 2020 and 2100, got {self.target_year}")
        if self.target_year <= self.baseline_year:
            raise ValueError(f"target_year ({self.target_year}) must be > baseline_year ({self.baseline_year})")

        # Validate CO2 prices
        if self.co2_price_baseline_eur_per_tco2e < 0:
            raise ValueError(f"co2_price_baseline_eur_per_tco2e must be >= 0, got {self.co2_price_baseline_eur_per_tco2e}")
        if self.co2_price_target_eur_per_tco2e < 0:
            raise ValueError(f"co2_price_target_eur_per_tco2e must be >= 0, got {self.co2_price_target_eur_per_tco2e}")

        # Validate energy price multiplier
        if self.energy_price_multiplier < 0:
            raise ValueError(f"energy_price_multiplier must be >= 0, got {self.energy_price_multiplier}")

        # Validate technology cost reduction percentage
        if not (0 <= self.technology_cost_reduction_pct <= 100):
            raise ValueError(f"technology_cost_reduction_pct must be 0-100, got {self.technology_cost_reduction_pct}")

        # Validate categorical fields
        if self.temperature_pathway not in self.ALLOWED_TEMPERATURE_PATHWAYS:
            raise ValueError(f"temperature_pathway must be one of {self.ALLOWED_TEMPERATURE_PATHWAYS}, got '{self.temperature_pathway}'")
        if self.policy_stringency_level not in self.ALLOWED_POLICY_STRINGENCY:
            raise ValueError(f"policy_stringency_level must be one of {self.ALLOWED_POLICY_STRINGENCY}, got '{self.policy_stringency_level}'")
        if self.physical_climate_impact_level not in self.ALLOWED_PHYSICAL_IMPACT:
            raise ValueError(f"physical_climate_impact_level must be one of {self.ALLOWED_PHYSICAL_IMPACT}, got '{self.physical_climate_impact_level}'")

    def get_co2_price_for_year(self, year: int) -> float:
        """Calculate interpolated CO2 price for a given year.

        Linear interpolation between baseline and target year CO2 prices.
        If year is before baseline, returns baseline price.
        If year is after target, returns target price.

        Args:
            year: Year to calculate CO2 price for

        Returns:
            CO2 price in EUR/tCO2e for the given year
        """
        if year <= self.baseline_year:
            return self.co2_price_baseline_eur_per_tco2e
        if year >= self.target_year:
            return self.co2_price_target_eur_per_tco2e

        # Linear interpolation
        years_elapsed = year - self.baseline_year
        total_years = self.target_year - self.baseline_year
        price_change = self.co2_price_target_eur_per_tco2e - self.co2_price_baseline_eur_per_tco2e

        return self.co2_price_baseline_eur_per_tco2e + (price_change * years_elapsed / total_years)

    def get_policy_stringency_index(self) -> float:
        """Convert policy stringency level to numeric index (0-10 scale).

        Returns:
            Policy stringency index: low=2.5, medium=5.0, high=7.5, very_high=9.5
        """
        stringency_map = {
            "low": 2.5,
            "medium": 5.0,
            "high": 7.5,
            "very_high": 9.5,
        }
        return stringency_map[self.policy_stringency_level]

    def get_physical_impact_index(self) -> float:
        """Convert physical climate impact level to numeric index (0-10 scale).

        Returns:
            Physical impact index: low=1.0, low-medium=2.5, medium=5.0, medium-high=7.5, high=9.0
        """
        impact_map = {
            "low": 1.0,
            "low-medium": 2.5,
            "medium": 5.0,
            "medium-high": 7.5,
            "high": 9.0,
        }
        return impact_map[self.physical_climate_impact_level]

    def is_high_ambition(self) -> bool:
        """Check if scenario represents high climate ambition (1.5C or 2C pathway with high policy stringency).

        Returns:
            True if scenario is 1.5C or 2C pathway with high/very_high policy stringency
        """
        high_ambition_pathways = ["1.5C", "2C"]
        high_policy = ["high", "very_high"]
        return (self.temperature_pathway in high_ambition_pathways and
                self.policy_stringency_level in high_policy)
