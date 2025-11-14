"""Repository for climate scenario data persistence.

Provides CRUD operations for ClimateScenario entities with proper
transaction handling and validation.
"""

from typing import Optional
from ..models.scenario import ClimateScenario
from .database import get_db


class ScenarioRepository:
    """Data access layer for climate scenario entities.

    Handles persistence of ClimateScenario objects to SQLite,
    mapping between database rows and domain model objects.
    """

    def __init__(self):
        """Initialize repository with database connection."""
        self.db = get_db()

    def insert_scenario(self, scenario: ClimateScenario) -> None:
        """Insert a new climate scenario.

        Args:
            scenario: ClimateScenario object to insert

        Raises:
            sqlite3.IntegrityError: If scenario_id already exists
            ValueError: If scenario validation fails
        """
        query = """
            INSERT INTO climate_scenarios (
                scenario_id, scenario_name, scenario_source, temperature_pathway,
                baseline_year, target_year, co2_price_baseline_eur_per_tco2e,
                co2_price_target_eur_per_tco2e, policy_stringency_level,
                physical_climate_impact_level, energy_price_multiplier,
                technology_cost_reduction_pct, scenario_documentation_reference
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        parameters = (
            scenario.scenario_id,
            scenario.scenario_name,
            scenario.scenario_source,
            scenario.temperature_pathway,
            scenario.baseline_year,
            scenario.target_year,
            scenario.co2_price_baseline_eur_per_tco2e,
            scenario.co2_price_target_eur_per_tco2e,
            scenario.policy_stringency_level,
            scenario.physical_climate_impact_level,
            scenario.energy_price_multiplier,
            scenario.technology_cost_reduction_pct,
            scenario.scenario_documentation_reference,
        )
        self.db.execute_insert(query, parameters)

    def get_scenario(self, scenario_id: str) -> Optional[ClimateScenario]:
        """Retrieve climate scenario by ID.

        Args:
            scenario_id: Unique scenario identifier

        Returns:
            ClimateScenario object if found, None otherwise
        """
        query = "SELECT * FROM climate_scenarios WHERE scenario_id = ?"
        results = self.db.execute_query(query, (scenario_id,))

        if not results:
            return None

        row = results[0]
        return self._row_to_scenario(row)

    def update_scenario(self, scenario: ClimateScenario) -> int:
        """Update existing climate scenario.

        Args:
            scenario: ClimateScenario object with updated data

        Returns:
            Number of rows updated (should be 1 if successful, 0 if not found)

        Raises:
            ValueError: If scenario validation fails
        """
        query = """
            UPDATE climate_scenarios SET
                scenario_name = ?,
                scenario_source = ?,
                temperature_pathway = ?,
                baseline_year = ?,
                target_year = ?,
                co2_price_baseline_eur_per_tco2e = ?,
                co2_price_target_eur_per_tco2e = ?,
                policy_stringency_level = ?,
                physical_climate_impact_level = ?,
                energy_price_multiplier = ?,
                technology_cost_reduction_pct = ?,
                scenario_documentation_reference = ?
            WHERE scenario_id = ?
        """
        parameters = (
            scenario.scenario_name,
            scenario.scenario_source,
            scenario.temperature_pathway,
            scenario.baseline_year,
            scenario.target_year,
            scenario.co2_price_baseline_eur_per_tco2e,
            scenario.co2_price_target_eur_per_tco2e,
            scenario.policy_stringency_level,
            scenario.physical_climate_impact_level,
            scenario.energy_price_multiplier,
            scenario.technology_cost_reduction_pct,
            scenario.scenario_documentation_reference,
            scenario.scenario_id,
        )
        return self.db.execute_update(query, parameters)

    def delete_scenario(self, scenario_id: str) -> int:
        """Delete climate scenario by ID.

        Note: This will cascade delete related influence_factors, correlations,
        and cost_assessment_results due to FK constraints.

        Args:
            scenario_id: Unique scenario identifier

        Returns:
            Number of rows deleted (should be 1 if successful, 0 if not found)
        """
        query = "DELETE FROM climate_scenarios WHERE scenario_id = ?"
        return self.db.execute_delete(query, (scenario_id,))

    def list_all_scenarios(self) -> list[ClimateScenario]:
        """Retrieve all climate scenarios.

        Returns:
            List of ClimateScenario objects, ordered by scenario_name
        """
        query = "SELECT * FROM climate_scenarios ORDER BY scenario_name"
        results = self.db.execute_query(query)
        return [self._row_to_scenario(row) for row in results]

    def list_scenarios_by_source(self, source: str) -> list[ClimateScenario]:
        """Retrieve climate scenarios filtered by source.

        Args:
            source: Scenario source (IEA, NGFS, IPCC, custom, etc.)

        Returns:
            List of ClimateScenario objects for this source
        """
        query = "SELECT * FROM climate_scenarios WHERE scenario_source = ? ORDER BY scenario_name"
        results = self.db.execute_query(query, (source,))
        return [self._row_to_scenario(row) for row in results]

    def list_scenarios_by_pathway(self, pathway: str) -> list[ClimateScenario]:
        """Retrieve climate scenarios filtered by temperature pathway.

        Args:
            pathway: Temperature pathway (1.5C, 2C, 3C, 4C+)

        Returns:
            List of ClimateScenario objects for this pathway
        """
        query = "SELECT * FROM climate_scenarios WHERE temperature_pathway = ? ORDER BY scenario_name"
        results = self.db.execute_query(query, (pathway,))
        return [self._row_to_scenario(row) for row in results]

    def _row_to_scenario(self, row) -> ClimateScenario:
        """Convert database row to ClimateScenario object.

        Args:
            row: sqlite3.Row object from query

        Returns:
            ClimateScenario object
        """
        return ClimateScenario(
            scenario_id=row['scenario_id'],
            scenario_name=row['scenario_name'],
            scenario_source=row['scenario_source'],
            temperature_pathway=row['temperature_pathway'],
            baseline_year=row['baseline_year'],
            target_year=row['target_year'],
            co2_price_baseline_eur_per_tco2e=row['co2_price_baseline_eur_per_tco2e'],
            co2_price_target_eur_per_tco2e=row['co2_price_target_eur_per_tco2e'],
            policy_stringency_level=row['policy_stringency_level'],
            physical_climate_impact_level=row['physical_climate_impact_level'],
            energy_price_multiplier=row['energy_price_multiplier'],
            technology_cost_reduction_pct=row['technology_cost_reduction_pct'],
            scenario_documentation_reference=row['scenario_documentation_reference'],
        )
