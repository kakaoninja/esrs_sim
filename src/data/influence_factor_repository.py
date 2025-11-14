"""Repository for influence factor data persistence.

Provides CRUD operations for InfluenceFactor and InfluenceFactorValue entities
with proper transaction handling and validation.
"""

from typing import Optional
from ..models.influence_factor import InfluenceFactor, InfluenceFactorValue
from .database import get_db


class InfluenceFactorRepository:
    """Data access layer for influence factor entities.

    Handles persistence of InfluenceFactor and InfluenceFactorValue objects,
    mapping between database rows and domain model objects.
    """

    def __init__(self):
        """Initialize repository with database connection."""
        self.db = get_db()

    # InfluenceFactor operations

    def insert_influence_factor(self, factor: InfluenceFactor) -> None:
        """Insert a new influence factor.

        Args:
            factor: InfluenceFactor object to insert

        Raises:
            sqlite3.IntegrityError: If factor_id already exists or scenario_id FK fails
            ValueError: If factor validation fails
        """
        query = """
            INSERT INTO influence_factors (
                factor_id, factor_name, factor_type, esrs_topic, unit,
                scenario_id, baseline_value, target_value, confidence_level,
                data_source_reference
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        parameters = (
            factor.factor_id,
            factor.factor_name,
            factor.factor_type,
            factor.esrs_topic,
            factor.unit,
            factor.scenario_id,
            factor.baseline_value,
            factor.target_value,
            factor.confidence_level,
            factor.data_source_reference,
        )
        self.db.execute_insert(query, parameters)

    def get_influence_factor(self, factor_id: str) -> Optional[InfluenceFactor]:
        """Retrieve influence factor by ID.

        Args:
            factor_id: Unique factor identifier

        Returns:
            InfluenceFactor object if found, None otherwise
        """
        query = "SELECT * FROM influence_factors WHERE factor_id = ?"
        results = self.db.execute_query(query, (factor_id,))

        if not results:
            return None

        row = results[0]
        return self._row_to_influence_factor(row)

    def get_factors_for_scenario(self, scenario_id: str, esrs_topic: Optional[str] = None) -> list[InfluenceFactor]:
        """Retrieve all influence factors for a scenario, optionally filtered by ESRS topic.

        Args:
            scenario_id: Scenario identifier
            esrs_topic: Optional ESRS topic filter (E1, E2, E3, E4, E5)

        Returns:
            List of InfluenceFactor objects
        """
        if esrs_topic is not None:
            query = """
                SELECT * FROM influence_factors
                WHERE scenario_id = ? AND esrs_topic = ?
                ORDER BY factor_name
            """
            results = self.db.execute_query(query, (scenario_id, esrs_topic))
        else:
            query = """
                SELECT * FROM influence_factors
                WHERE scenario_id = ?
                ORDER BY esrs_topic, factor_name
            """
            results = self.db.execute_query(query, (scenario_id,))

        return [self._row_to_influence_factor(row) for row in results]

    def get_factors_by_type(self, factor_type: str, scenario_id: Optional[str] = None) -> list[InfluenceFactor]:
        """Retrieve influence factors by type, optionally filtered by scenario.

        Args:
            factor_type: Factor type (carbon_pricing, regulatory, etc.)
            scenario_id: Optional scenario filter

        Returns:
            List of InfluenceFactor objects
        """
        if scenario_id is not None:
            query = """
                SELECT * FROM influence_factors
                WHERE factor_type = ? AND scenario_id = ?
                ORDER BY factor_name
            """
            results = self.db.execute_query(query, (factor_type, scenario_id))
        else:
            query = """
                SELECT * FROM influence_factors
                WHERE factor_type = ?
                ORDER BY scenario_id, factor_name
            """
            results = self.db.execute_query(query, (factor_type,))

        return [self._row_to_influence_factor(row) for row in results]

    def delete_influence_factor(self, factor_id: str) -> int:
        """Delete influence factor by ID.

        Note: This will cascade delete related influence_factor_values and
        correlations due to FK constraints.

        Args:
            factor_id: Unique factor identifier

        Returns:
            Number of rows deleted (should be 1 if successful, 0 if not found)
        """
        query = "DELETE FROM influence_factors WHERE factor_id = ?"
        return self.db.execute_delete(query, (factor_id,))

    def _row_to_influence_factor(self, row) -> InfluenceFactor:
        """Convert database row to InfluenceFactor object.

        Args:
            row: sqlite3.Row object from query

        Returns:
            InfluenceFactor object
        """
        return InfluenceFactor(
            factor_id=row['factor_id'],
            factor_name=row['factor_name'],
            factor_type=row['factor_type'],
            esrs_topic=row['esrs_topic'],
            unit=row['unit'],
            scenario_id=row['scenario_id'],
            baseline_value=row['baseline_value'],
            target_value=row['target_value'],
            confidence_level=row['confidence_level'],
            data_source_reference=row['data_source_reference'],
        )

    # InfluenceFactorValue operations

    def insert_factor_value(self, value: InfluenceFactorValue) -> None:
        """Insert a new influence factor time-series value.

        Args:
            value: InfluenceFactorValue object to insert

        Raises:
            sqlite3.IntegrityError: If value_id already exists or factor_id FK fails
            ValueError: If value validation fails
        """
        query = """
            INSERT INTO influence_factor_values (
                value_id, factor_id, year, value, notes
            ) VALUES (?, ?, ?, ?, ?)
        """
        parameters = (
            value.value_id,
            value.factor_id,
            value.year,
            value.value,
            value.notes,
        )
        self.db.execute_insert(query, parameters)

    def get_factor_value(self, value_id: str) -> Optional[InfluenceFactorValue]:
        """Retrieve influence factor value by ID.

        Args:
            value_id: Unique value identifier

        Returns:
            InfluenceFactorValue object if found, None otherwise
        """
        query = "SELECT * FROM influence_factor_values WHERE value_id = ?"
        results = self.db.execute_query(query, (value_id,))

        if not results:
            return None

        row = results[0]
        return self._row_to_factor_value(row)

    def get_values_for_factor(self, factor_id: str) -> list[InfluenceFactorValue]:
        """Retrieve all time-series values for a specific influence factor.

        Args:
            factor_id: Factor identifier

        Returns:
            List of InfluenceFactorValue objects, ordered by year
        """
        query = """
            SELECT * FROM influence_factor_values
            WHERE factor_id = ?
            ORDER BY year
        """
        results = self.db.execute_query(query, (factor_id,))
        return [self._row_to_factor_value(row) for row in results]

    def get_value_for_year(self, factor_id: str, year: int) -> Optional[InfluenceFactorValue]:
        """Retrieve influence factor value for a specific year.

        Args:
            factor_id: Factor identifier
            year: Year to retrieve

        Returns:
            InfluenceFactorValue object if found, None otherwise
        """
        query = """
            SELECT * FROM influence_factor_values
            WHERE factor_id = ? AND year = ?
        """
        results = self.db.execute_query(query, (factor_id, year))

        if not results:
            return None

        row = results[0]
        return self._row_to_factor_value(row)

    def delete_factor_value(self, value_id: str) -> int:
        """Delete influence factor value by ID.

        Args:
            value_id: Unique value identifier

        Returns:
            Number of rows deleted (should be 1 if successful, 0 if not found)
        """
        query = "DELETE FROM influence_factor_values WHERE value_id = ?"
        return self.db.execute_delete(query, (value_id,))

    def _row_to_factor_value(self, row) -> InfluenceFactorValue:
        """Convert database row to InfluenceFactorValue object.

        Args:
            row: sqlite3.Row object from query

        Returns:
            InfluenceFactorValue object
        """
        return InfluenceFactorValue(
            value_id=row['value_id'],
            factor_id=row['factor_id'],
            year=row['year'],
            value=row['value'],
            notes=row['notes'],
        )
