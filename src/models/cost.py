"""Cost models for ESRS environmental cost assessment results.

Models representing calculated financial costs across ESRS environmental topics
with confidence intervals and audit trails.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json


@dataclass
class CostCategory:
    """Individual cost category result (e.g., E1 carbon pricing cost).

    Represents a single cost calculation result for a specific category
    within an ESRS topic (e.g., E1 carbon pricing, E1 transition costs).

    Attributes:
        category_name: Cost category name (carbon_pricing, transition_costs, etc.)
        esrs_topic: ESRS topic code (E1, E2, E3, E4, E5)
        amount_eur: Cost amount in EUR - median/mean estimate (>= 0)
        amount_eur_lower: Lower bound of 95% confidence interval (5th percentile)
        amount_eur_upper: Upper bound of 95% confidence interval (95th percentile)
        confidence_level: Confidence in cost estimate (0.0-1.0)
        cost_horizon_years: Time horizon for this cost (years from baseline)
        calculation_method: Description of how cost was calculated
        influence_factors_applied: JSON string of factor IDs that influenced this cost
        suspicious_values: JSON string of any suspicious/flagged values
        notes: Optional calculation notes

    Validation:
        - amount_eur >= 0
        - amount_eur_lower <= amount_eur <= amount_eur_upper
        - confidence_level between 0.0 and 1.0
        - cost_horizon_years >= 0
        - esrs_topic in E1-E5
    """

    category_name: str
    esrs_topic: str
    amount_eur: float
    amount_eur_lower: float
    amount_eur_upper: float
    confidence_level: float
    cost_horizon_years: int
    calculation_method: str
    influence_factors_applied: Optional[str] = None
    suspicious_values: Optional[str] = None
    notes: Optional[str] = None

    # Allowed values
    ALLOWED_ESRS_TOPICS = ["E1", "E2", "E3", "E4", "E5"]
    ALLOWED_CATEGORY_NAMES = [
        "carbon_pricing",
        "transition_costs",
        "physical_risk_costs",
        "compliance_costs",
        "abatement_costs",
        "water_efficiency_capex",
        "habitat_restoration",
        "waste_reduction_systems",
        "other"
    ]

    def __post_init__(self):
        """Validate cost category data."""
        # Validate amount
        if self.amount_eur < 0:
            raise ValueError(f"amount_eur must be >= 0, got {self.amount_eur}")
        if self.amount_eur_lower < 0:
            raise ValueError(f"amount_eur_lower must be >= 0, got {self.amount_eur_lower}")
        if self.amount_eur_upper < 0:
            raise ValueError(f"amount_eur_upper must be >= 0, got {self.amount_eur_upper}")

        # Validate confidence interval bounds
        if not (self.amount_eur_lower <= self.amount_eur <= self.amount_eur_upper):
            raise ValueError(
                f"Confidence interval must satisfy: lower <= median <= upper. "
                f"Got lower={self.amount_eur_lower}, median={self.amount_eur}, upper={self.amount_eur_upper}"
            )

        # Validate confidence level
        if not (0.0 <= self.confidence_level <= 1.0):
            raise ValueError(f"confidence_level must be 0.0-1.0, got {self.confidence_level}")

        # Validate cost horizon (>= 0 allows baseline year calculations)
        if self.cost_horizon_years < 0:
            raise ValueError(f"cost_horizon_years must be >= 0, got {self.cost_horizon_years}")

        # Validate ESRS topic
        if self.esrs_topic not in self.ALLOWED_ESRS_TOPICS:
            raise ValueError(f"esrs_topic must be one of {self.ALLOWED_ESRS_TOPICS}, got '{self.esrs_topic}'")

    def get_influence_factors_list(self) -> list[str]:
        """Parse influence_factors_applied JSON string to list.

        Returns:
            List of factor IDs that influenced this cost, or empty list
        """
        if self.influence_factors_applied is None:
            return []
        try:
            return json.loads(self.influence_factors_applied)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in influence_factors_applied: {self.influence_factors_applied}")

    def get_suspicious_values_dict(self) -> Optional[dict]:
        """Parse suspicious_values JSON string to dictionary.

        Returns:
            Dictionary with suspicious values and reasons, or None
        """
        if self.suspicious_values is None:
            return None
        try:
            return json.loads(self.suspicious_values)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in suspicious_values: {self.suspicious_values}")

    def has_suspicious_values(self) -> bool:
        """Check if this cost category has any suspicious values flagged.

        Returns:
            True if suspicious_values is not None and not empty
        """
        return self.suspicious_values is not None and self.suspicious_values.strip() != ""

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if confidence level is high (>= threshold).

        Args:
            threshold: Confidence threshold (default 0.8)

        Returns:
            True if confidence_level >= threshold
        """
        return self.confidence_level >= threshold

    def get_confidence_interval_width(self) -> float:
        """Get width of 95% confidence interval.

        Returns:
            Width of CI in EUR (upper - lower)
        """
        return self.amount_eur_upper - self.amount_eur_lower

    def get_confidence_interval_pct(self) -> float:
        """Get confidence interval width as percentage of median.

        Returns:
            CI width as percentage of median (0-100+)
            Returns 0.0 if median is 0
        """
        if self.amount_eur == 0:
            return 0.0
        return (self.get_confidence_interval_width() / self.amount_eur) * 100


@dataclass
class CostCalculationConfiguration:
    """Configuration parameters for cost calculation run.

    Stores the configuration used for a specific cost assessment to enable
    reproducibility and audit trail.

    Attributes:
        config_id: Unique configuration identifier
        scenario_id: Climate scenario used
        cost_horizon_years: Default cost horizon for projections
        interpolation_method: Method for missing data (linear, quadratic, etc.)
        correlation_adjustment_enabled: Whether to adjust for factor correlations
        suspicious_value_threshold: Threshold for flagging suspicious values
        calculation_timestamp: When this calculation was performed
        notes: Optional configuration notes
    """

    config_id: str
    scenario_id: str
    cost_horizon_years: int
    interpolation_method: str
    correlation_adjustment_enabled: bool
    suspicious_value_threshold: float
    calculation_timestamp: str
    notes: Optional[str] = None

    # Allowed values
    ALLOWED_INTERPOLATION_METHODS = ["linear", "quadratic", "cubic", "nearest"]

    def __post_init__(self):
        """Validate configuration data."""
        # Validate cost horizon (>= 0 allows baseline year calculations)
        if self.cost_horizon_years < 0:
            raise ValueError(f"cost_horizon_years must be >= 0, got {self.cost_horizon_years}")

        # Validate interpolation method
        if self.interpolation_method not in self.ALLOWED_INTERPOLATION_METHODS:
            raise ValueError(f"interpolation_method must be one of {self.ALLOWED_INTERPOLATION_METHODS}, got '{self.interpolation_method}'")

        # Validate suspicious value threshold
        if not (0.0 <= self.suspicious_value_threshold <= 1.0):
            raise ValueError(f"suspicious_value_threshold must be 0.0-1.0, got {self.suspicious_value_threshold}")


@dataclass
class CostAssessmentResult:
    """Complete cost assessment result for a company under a scenario.

    Represents the full output of a cost assessment run, including all
    cost categories across ESRS topics, total costs, confidence levels,
    and audit trail information.

    Attributes:
        result_id: Unique result identifier
        company_id: Company assessed
        scenario_id: Scenario used
        reporting_year: Company's reporting year (baseline)
        assessment_timestamp: When assessment was performed
        cost_categories: List of CostCategory objects
        total_environmental_cost_eur: Total cost across all ESRS topics - median (>= 0)
        total_environmental_cost_eur_lower: Lower bound 95% CI for total cost
        total_environmental_cost_eur_upper: Upper bound 95% CI for total cost
        overall_confidence_level: Weighted average confidence (0.0-1.0)
        e1_total_cost_eur: E1 Climate total cost - median (>= 0)
        e1_total_cost_eur_lower: E1 lower bound 95% CI
        e1_total_cost_eur_upper: E1 upper bound 95% CI
        e2_total_cost_eur: E2 Pollution total cost - median (>= 0)
        e3_total_cost_eur: E3 Water total cost - median (>= 0)
        e4_total_cost_eur: E4 Biodiversity total cost - median (>= 0)
        e5_total_cost_eur: E5 Circular Economy total cost - median (>= 0)
        has_suspicious_values: Flag if any suspicious values detected
        calculation_notes: Optional notes about calculation
        config_id: Foreign key to CostCalculationConfiguration

    Validation:
        - All cost amounts >= 0
        - overall_confidence_level between 0.0 and 1.0
        - total_environmental_cost_eur equals sum of topic costs
    """

    result_id: str
    company_id: str
    scenario_id: str
    reporting_year: int
    assessment_timestamp: str
    cost_categories: list[CostCategory]
    total_environmental_cost_eur: float
    total_environmental_cost_eur_lower: float
    total_environmental_cost_eur_upper: float
    overall_confidence_level: float
    e1_total_cost_eur: float = 0.0
    e1_total_cost_eur_lower: float = 0.0
    e1_total_cost_eur_upper: float = 0.0
    e2_total_cost_eur: float = 0.0
    e3_total_cost_eur: float = 0.0
    e4_total_cost_eur: float = 0.0
    e5_total_cost_eur: float = 0.0
    has_suspicious_values: bool = False
    calculation_notes: Optional[str] = None
    config_id: Optional[str] = None

    def __post_init__(self):
        """Validate cost assessment result data."""
        # Validate all cost amounts
        if self.total_environmental_cost_eur < 0:
            raise ValueError(f"total_environmental_cost_eur must be >= 0, got {self.total_environmental_cost_eur}")
        if self.e1_total_cost_eur < 0:
            raise ValueError(f"e1_total_cost_eur must be >= 0, got {self.e1_total_cost_eur}")
        if self.e2_total_cost_eur < 0:
            raise ValueError(f"e2_total_cost_eur must be >= 0, got {self.e2_total_cost_eur}")
        if self.e3_total_cost_eur < 0:
            raise ValueError(f"e3_total_cost_eur must be >= 0, got {self.e3_total_cost_eur}")
        if self.e4_total_cost_eur < 0:
            raise ValueError(f"e4_total_cost_eur must be >= 0, got {self.e4_total_cost_eur}")
        if self.e5_total_cost_eur < 0:
            raise ValueError(f"e5_total_cost_eur must be >= 0, got {self.e5_total_cost_eur}")

        # Validate confidence level
        if not (0.0 <= self.overall_confidence_level <= 1.0):
            raise ValueError(f"overall_confidence_level must be 0.0-1.0, got {self.overall_confidence_level}")

        # Validate reporting year
        if not (2020 <= self.reporting_year <= 2100):
            raise ValueError(f"reporting_year must be between 2020 and 2100, got {self.reporting_year}")

        # Validate total equals sum of topics (within tolerance for floating point)
        calculated_total = (self.e1_total_cost_eur + self.e2_total_cost_eur +
                          self.e3_total_cost_eur + self.e4_total_cost_eur +
                          self.e5_total_cost_eur)
        tolerance = 0.01  # 1 cent tolerance for floating point rounding
        if abs(self.total_environmental_cost_eur - calculated_total) > tolerance:
            raise ValueError(f"total_environmental_cost_eur ({self.total_environmental_cost_eur}) "
                           f"must equal sum of topic costs ({calculated_total})")

    def get_categories_by_topic(self, esrs_topic: str) -> list[CostCategory]:
        """Get all cost categories for a specific ESRS topic.

        Args:
            esrs_topic: ESRS topic code (E1-E5)

        Returns:
            List of CostCategory objects for this topic
        """
        return [cat for cat in self.cost_categories if cat.esrs_topic == esrs_topic]

    def get_cost_as_percentage_of_revenue(self, annual_revenue_eur: float) -> float:
        """Calculate total environmental cost as percentage of revenue.

        Args:
            annual_revenue_eur: Company's annual revenue in EUR

        Returns:
            Cost as percentage of revenue (0-100)
        """
        if annual_revenue_eur <= 0:
            raise ValueError(f"annual_revenue_eur must be > 0, got {annual_revenue_eur}")
        return (self.total_environmental_cost_eur / annual_revenue_eur) * 100

    def get_suspicious_categories(self) -> list[CostCategory]:
        """Get all cost categories with suspicious values flagged.

        Returns:
            List of CostCategory objects with suspicious values
        """
        return [cat for cat in self.cost_categories if cat.has_suspicious_values()]

    def count_categories(self) -> int:
        """Get total number of cost categories calculated.

        Returns:
            Number of cost categories
        """
        return len(self.cost_categories)
