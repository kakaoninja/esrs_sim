"""Correlation models for influence factors in ESRS cost assessment.

Correlations between influence factors (e.g., carbon price and policy stringency)
affect how costs compound or offset each other in scenario-based modeling.

The user specified: "the relation between those factors may also be described
with a 0-1 float, including confidence"
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class InfluenceFactorCorrelation:
    """Correlation between two influence factors.

    Represents the relationship strength between two influence factors
    (e.g., carbon pricing and policy stringency are highly correlated).
    Correlations are used to adjust cost calculations when multiple
    factors affect the same cost category.

    Attributes:
        correlation_id: Unique correlation identifier
        factor_1_id: Foreign key to first InfluenceFactor
        factor_2_id: Foreign key to second InfluenceFactor
        correlation_strength: Correlation coefficient (0.0-1.0, where 1.0 = perfect correlation)
        correlation_confidence: Confidence in correlation estimate (0.0-1.0)
        scenario_id: Foreign key to ClimateScenario (correlations may vary by scenario)
        rationale: Optional explanation of why these factors are correlated

    Validation:
        - correlation_strength between 0.0 and 1.0
        - correlation_confidence between 0.0 and 1.0
        - factor_1_id != factor_2_id (no self-correlation)

    Note:
        We use 0-1 scale (not -1 to 1) as per user specification. All correlations
        are positive relationships - negative correlations are handled through
        inverse cost adjustments in calculation logic.
    """

    correlation_id: str
    factor_1_id: str
    factor_2_id: str
    correlation_strength: float
    correlation_confidence: float
    scenario_id: str
    rationale: Optional[str] = None

    def __post_init__(self):
        """Validate correlation data."""
        # Validate correlation strength (0-1 as per user spec)
        if not (0.0 <= self.correlation_strength <= 1.0):
            raise ValueError(f"correlation_strength must be 0.0-1.0, got {self.correlation_strength}")

        # Validate correlation confidence
        if not (0.0 <= self.correlation_confidence <= 1.0):
            raise ValueError(f"correlation_confidence must be 0.0-1.0, got {self.correlation_confidence}")

        # Validate no self-correlation
        if self.factor_1_id == self.factor_2_id:
            raise ValueError(f"factor_1_id and factor_2_id cannot be the same (no self-correlation): {self.factor_1_id}")

    def is_strong_correlation(self, threshold: float = 0.7) -> bool:
        """Check if correlation is strong (above threshold).

        Args:
            threshold: Correlation strength threshold (default 0.7)

        Returns:
            True if correlation_strength >= threshold
        """
        return self.correlation_strength >= threshold

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if correlation confidence is high (above threshold).

        Args:
            threshold: Confidence threshold (default 0.8)

        Returns:
            True if correlation_confidence >= threshold
        """
        return self.correlation_confidence >= threshold

    def involves_factor(self, factor_id: str) -> bool:
        """Check if this correlation involves a specific factor.

        Args:
            factor_id: Factor ID to check

        Returns:
            True if factor_id is either factor_1_id or factor_2_id
        """
        return factor_id in (self.factor_1_id, self.factor_2_id)

    def get_other_factor(self, factor_id: str) -> Optional[str]:
        """Get the other factor ID in this correlation.

        Args:
            factor_id: One of the factor IDs in this correlation

        Returns:
            The other factor ID, or None if factor_id not in correlation
        """
        if factor_id == self.factor_1_id:
            return self.factor_2_id
        elif factor_id == self.factor_2_id:
            return self.factor_1_id
        else:
            return None


@dataclass
class CorrelationModel:
    """Collection of correlations for a scenario.

    Represents the full correlation matrix for influence factors in a scenario.
    This is a convenience model for working with multiple correlations together.

    Attributes:
        scenario_id: Climate scenario these correlations apply to
        correlations: List of InfluenceFactorCorrelation objects
        model_notes: Optional notes about the correlation model approach
    """

    scenario_id: str
    correlations: list[InfluenceFactorCorrelation]
    model_notes: Optional[str] = None

    def __post_init__(self):
        """Validate correlation model."""
        # Validate all correlations belong to this scenario
        for corr in self.correlations:
            if corr.scenario_id != self.scenario_id:
                raise ValueError(f"Correlation {corr.correlation_id} has scenario_id '{corr.scenario_id}' "
                               f"but CorrelationModel has scenario_id '{self.scenario_id}'")

    def get_correlations_for_factor(self, factor_id: str) -> list[InfluenceFactorCorrelation]:
        """Get all correlations involving a specific factor.

        Args:
            factor_id: Factor ID to search for

        Returns:
            List of InfluenceFactorCorrelation objects involving this factor
        """
        return [corr for corr in self.correlations if corr.involves_factor(factor_id)]

    def get_correlation_between(self, factor_1_id: str, factor_2_id: str) -> Optional[InfluenceFactorCorrelation]:
        """Get correlation between two specific factors.

        Args:
            factor_1_id: First factor ID
            factor_2_id: Second factor ID

        Returns:
            InfluenceFactorCorrelation if found, None otherwise
        """
        for corr in self.correlations:
            if (corr.factor_1_id == factor_1_id and corr.factor_2_id == factor_2_id) or \
               (corr.factor_1_id == factor_2_id and corr.factor_2_id == factor_1_id):
                return corr
        return None

    def get_strong_correlations(self, threshold: float = 0.7) -> list[InfluenceFactorCorrelation]:
        """Get all strong correlations (strength >= threshold).

        Args:
            threshold: Correlation strength threshold (default 0.7)

        Returns:
            List of strong InfluenceFactorCorrelation objects
        """
        return [corr for corr in self.correlations if corr.is_strong_correlation(threshold)]

    def count_correlations(self) -> int:
        """Get total number of correlations in model.

        Returns:
            Number of correlations
        """
        return len(self.correlations)
