"""Repository for influence factor correlation data persistence.

Provides CRUD operations for InfluenceFactorCorrelation entities with proper
transaction handling and validation.
"""

from typing import Optional
from ..models.correlation import InfluenceFactorCorrelation, CorrelationModel
from .database import get_db


class CorrelationRepository:
    """Data access layer for influence factor correlation entities.

    Handles persistence of InfluenceFactorCorrelation objects,
    mapping between database rows and domain model objects.
    """

    def __init__(self):
        """Initialize repository with database connection."""
        self.db = get_db()

    def insert_correlation(self, correlation: InfluenceFactorCorrelation) -> None:
        """Insert a new influence factor correlation.

        Args:
            correlation: InfluenceFactorCorrelation object to insert

        Raises:
            sqlite3.IntegrityError: If correlation_id already exists or FK constraints fail
            ValueError: If correlation validation fails
        """
        query = """
            INSERT INTO influence_factor_correlations (
                correlation_id, factor_1_id, factor_2_id,
                correlation_strength, correlation_confidence,
                scenario_id, rationale
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        parameters = (
            correlation.correlation_id,
            correlation.factor_1_id,
            correlation.factor_2_id,
            correlation.correlation_strength,
            correlation.correlation_confidence,
            correlation.scenario_id,
            correlation.rationale,
        )
        self.db.execute_insert(query, parameters)

    def get_correlation(self, correlation_id: str) -> Optional[InfluenceFactorCorrelation]:
        """Retrieve correlation by ID.

        Args:
            correlation_id: Unique correlation identifier

        Returns:
            InfluenceFactorCorrelation object if found, None otherwise
        """
        query = "SELECT * FROM influence_factor_correlations WHERE correlation_id = ?"
        results = self.db.execute_query(query, (correlation_id,))

        if not results:
            return None

        row = results[0]
        return self._row_to_correlation(row)

    def get_correlations_for_scenario(self, scenario_id: str) -> list[InfluenceFactorCorrelation]:
        """Retrieve all correlations for a specific scenario.

        Args:
            scenario_id: Scenario identifier

        Returns:
            List of InfluenceFactorCorrelation objects
        """
        query = """
            SELECT * FROM influence_factor_correlations
            WHERE scenario_id = ?
            ORDER BY correlation_strength DESC
        """
        results = self.db.execute_query(query, (scenario_id,))
        return [self._row_to_correlation(row) for row in results]

    def get_correlations_for_factor(self, factor_id: str) -> list[InfluenceFactorCorrelation]:
        """Retrieve all correlations involving a specific influence factor.

        Args:
            factor_id: Factor identifier

        Returns:
            List of InfluenceFactorCorrelation objects where factor_id is either factor_1 or factor_2
        """
        query = """
            SELECT * FROM influence_factor_correlations
            WHERE factor_1_id = ? OR factor_2_id = ?
            ORDER BY correlation_strength DESC
        """
        results = self.db.execute_query(query, (factor_id, factor_id))
        return [self._row_to_correlation(row) for row in results]

    def get_correlation_between_factors(self, factor_1_id: str, factor_2_id: str) -> Optional[InfluenceFactorCorrelation]:
        """Retrieve correlation between two specific factors (order-independent).

        Args:
            factor_1_id: First factor identifier
            factor_2_id: Second factor identifier

        Returns:
            InfluenceFactorCorrelation object if found, None otherwise
        """
        query = """
            SELECT * FROM influence_factor_correlations
            WHERE (factor_1_id = ? AND factor_2_id = ?)
               OR (factor_1_id = ? AND factor_2_id = ?)
        """
        results = self.db.execute_query(query, (factor_1_id, factor_2_id, factor_2_id, factor_1_id))

        if not results:
            return None

        row = results[0]
        return self._row_to_correlation(row)

    def get_strong_correlations(self, scenario_id: str, threshold: float = 0.7) -> list[InfluenceFactorCorrelation]:
        """Retrieve strong correlations (strength >= threshold) for a scenario.

        Args:
            scenario_id: Scenario identifier
            threshold: Minimum correlation strength (default 0.7)

        Returns:
            List of InfluenceFactorCorrelation objects with strength >= threshold
        """
        query = """
            SELECT * FROM influence_factor_correlations
            WHERE scenario_id = ? AND correlation_strength >= ?
            ORDER BY correlation_strength DESC
        """
        results = self.db.execute_query(query, (scenario_id, threshold))
        return [self._row_to_correlation(row) for row in results]

    def delete_correlation(self, correlation_id: str) -> int:
        """Delete correlation by ID.

        Args:
            correlation_id: Unique correlation identifier

        Returns:
            Number of rows deleted (should be 1 if successful, 0 if not found)
        """
        query = "DELETE FROM influence_factor_correlations WHERE correlation_id = ?"
        return self.db.execute_delete(query, (correlation_id,))

    def get_correlation_model(self, scenario_id: str) -> CorrelationModel:
        """Retrieve complete correlation model for a scenario.

        Builds a CorrelationModel object with all correlations for the scenario.

        Args:
            scenario_id: Scenario identifier

        Returns:
            CorrelationModel object with all correlations
        """
        correlations = self.get_correlations_for_scenario(scenario_id)
        return CorrelationModel(
            scenario_id=scenario_id,
            correlations=correlations,
            model_notes=f"Correlation model for scenario {scenario_id} with {len(correlations)} correlations"
        )

    def _row_to_correlation(self, row) -> InfluenceFactorCorrelation:
        """Convert database row to InfluenceFactorCorrelation object.

        Args:
            row: sqlite3.Row object from query

        Returns:
            InfluenceFactorCorrelation object
        """
        return InfluenceFactorCorrelation(
            correlation_id=row['correlation_id'],
            factor_1_id=row['factor_1_id'],
            factor_2_id=row['factor_2_id'],
            correlation_strength=row['correlation_strength'],
            correlation_confidence=row['correlation_confidence'],
            scenario_id=row['scenario_id'],
            rationale=row['rationale'],
        )
