"""Repository for cost assessment result data persistence.

Provides CRUD operations for cost entities (CostCategory, CostCalculationConfiguration,
CostAssessmentResult) with proper transaction handling and validation.
"""

from typing import Optional
from ..models.cost import CostCategory, CostCalculationConfiguration, CostAssessmentResult
from .database import get_db


class CostRepository:
    """Data access layer for cost assessment entities.

    Handles persistence of cost calculation configurations, cost categories,
    and cost assessment results, mapping between database rows and domain models.
    """

    def __init__(self):
        """Initialize repository with database connection."""
        self.db = get_db()

    # CostCalculationConfiguration operations

    def insert_calculation_config(self, config: CostCalculationConfiguration) -> None:
        """Insert a new cost calculation configuration.

        Args:
            config: CostCalculationConfiguration object to insert

        Raises:
            sqlite3.IntegrityError: If config_id already exists or scenario_id FK fails
            ValueError: If config validation fails
        """
        query = """
            INSERT INTO cost_calculation_configurations (
                config_id, scenario_id, cost_horizon_years,
                interpolation_method, correlation_adjustment_enabled,
                suspicious_value_threshold, calculation_timestamp, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        parameters = (
            config.config_id,
            config.scenario_id,
            config.cost_horizon_years,
            config.interpolation_method,
            1 if config.correlation_adjustment_enabled else 0,  # Convert bool to int
            config.suspicious_value_threshold,
            config.calculation_timestamp,
            config.notes,
        )
        self.db.execute_insert(query, parameters)

    def get_calculation_config(self, config_id: str) -> Optional[CostCalculationConfiguration]:
        """Retrieve calculation configuration by ID.

        Args:
            config_id: Unique configuration identifier

        Returns:
            CostCalculationConfiguration object if found, None otherwise
        """
        query = "SELECT * FROM cost_calculation_configurations WHERE config_id = ?"
        results = self.db.execute_query(query, (config_id,))

        if not results:
            return None

        row = results[0]
        return self._row_to_config(row)

    def _row_to_config(self, row) -> CostCalculationConfiguration:
        """Convert database row to CostCalculationConfiguration object.

        Args:
            row: sqlite3.Row object from query

        Returns:
            CostCalculationConfiguration object
        """
        return CostCalculationConfiguration(
            config_id=row['config_id'],
            scenario_id=row['scenario_id'],
            cost_horizon_years=row['cost_horizon_years'],
            interpolation_method=row['interpolation_method'],
            correlation_adjustment_enabled=bool(row['correlation_adjustment_enabled']),
            suspicious_value_threshold=row['suspicious_value_threshold'],
            calculation_timestamp=row['calculation_timestamp'],
            notes=row['notes'],
        )

    # CostCategory operations

    def insert_cost_category(self, category: CostCategory) -> None:
        """Insert a new cost category.

        Args:
            category: CostCategory object to insert

        Raises:
            ValueError: If category validation fails
        """
        query = """
            INSERT INTO cost_categories (
                category_name, esrs_topic, amount_eur, confidence_level,
                cost_horizon_years, calculation_method, influence_factors_applied,
                suspicious_values, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        parameters = (
            category.category_name,
            category.esrs_topic,
            category.amount_eur,
            category.confidence_level,
            category.cost_horizon_years,
            category.calculation_method,
            category.influence_factors_applied,
            category.suspicious_values,
            category.notes,
        )
        self.db.execute_insert(query, parameters)

    # CostAssessmentResult operations

    def insert_assessment_result(self, result: CostAssessmentResult) -> None:
        """Insert a new cost assessment result.

        Note: This inserts the result record only. Cost categories must be
        inserted separately (they reference the result via calculation context).

        Args:
            result: CostAssessmentResult object to insert

        Raises:
            sqlite3.IntegrityError: If result_id already exists or FK constraints fail
            ValueError: If result validation fails
        """
        query = """
            INSERT INTO cost_assessment_results (
                result_id, company_id, scenario_id, reporting_year,
                assessment_timestamp, total_environmental_cost_eur,
                overall_confidence_level, e1_total_cost_eur, e2_total_cost_eur,
                e3_total_cost_eur, e4_total_cost_eur, e5_total_cost_eur,
                has_suspicious_values, calculation_notes, config_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        parameters = (
            result.result_id,
            result.company_id,
            result.scenario_id,
            result.reporting_year,
            result.assessment_timestamp,
            result.total_environmental_cost_eur,
            result.overall_confidence_level,
            result.e1_total_cost_eur,
            result.e2_total_cost_eur,
            result.e3_total_cost_eur,
            result.e4_total_cost_eur,
            result.e5_total_cost_eur,
            1 if result.has_suspicious_values else 0,  # Convert bool to int
            result.calculation_notes,
            result.config_id,
        )
        self.db.execute_insert(query, parameters)

    def get_assessment_result(self, result_id: str) -> Optional[CostAssessmentResult]:
        """Retrieve cost assessment result by ID.

        Note: This retrieves the result record without cost categories.
        Use get_full_assessment_result() to include categories.

        Args:
            result_id: Unique result identifier

        Returns:
            CostAssessmentResult object (without cost_categories) if found, None otherwise
        """
        query = "SELECT * FROM cost_assessment_results WHERE result_id = ?"
        results = self.db.execute_query(query, (result_id,))

        if not results:
            return None

        row = results[0]
        return self._row_to_result(row)

    def get_results_for_company(self, company_id: str, scenario_id: Optional[str] = None) -> list[CostAssessmentResult]:
        """Retrieve all assessment results for a company, optionally filtered by scenario.

        Args:
            company_id: Company identifier
            scenario_id: Optional scenario filter

        Returns:
            List of CostAssessmentResult objects (without cost_categories)
        """
        if scenario_id is not None:
            query = """
                SELECT * FROM cost_assessment_results
                WHERE company_id = ? AND scenario_id = ?
                ORDER BY assessment_timestamp DESC
            """
            results = self.db.execute_query(query, (company_id, scenario_id))
        else:
            query = """
                SELECT * FROM cost_assessment_results
                WHERE company_id = ?
                ORDER BY assessment_timestamp DESC
            """
            results = self.db.execute_query(query, (company_id,))

        return [self._row_to_result(row) for row in results]

    def get_results_for_scenario(self, scenario_id: str) -> list[CostAssessmentResult]:
        """Retrieve all assessment results for a scenario.

        Args:
            scenario_id: Scenario identifier

        Returns:
            List of CostAssessmentResult objects (without cost_categories)
        """
        query = """
            SELECT * FROM cost_assessment_results
            WHERE scenario_id = ?
            ORDER BY total_environmental_cost_eur DESC
        """
        results = self.db.execute_query(query, (scenario_id,))
        return [self._row_to_result(row) for row in results]

    def delete_assessment_result(self, result_id: str) -> int:
        """Delete cost assessment result by ID.

        Args:
            result_id: Unique result identifier

        Returns:
            Number of rows deleted (should be 1 if successful, 0 if not found)
        """
        query = "DELETE FROM cost_assessment_results WHERE result_id = ?"
        return self.db.execute_delete(query, (result_id,))

    def _row_to_result(self, row) -> CostAssessmentResult:
        """Convert database row to CostAssessmentResult object.

        Note: cost_categories list is empty - must be populated separately.

        Args:
            row: sqlite3.Row object from query

        Returns:
            CostAssessmentResult object with empty cost_categories list
        """
        return CostAssessmentResult(
            result_id=row['result_id'],
            company_id=row['company_id'],
            scenario_id=row['scenario_id'],
            reporting_year=row['reporting_year'],
            assessment_timestamp=row['assessment_timestamp'],
            cost_categories=[],  # Categories must be loaded separately
            total_environmental_cost_eur=row['total_environmental_cost_eur'],
            overall_confidence_level=row['overall_confidence_level'],
            e1_total_cost_eur=row['e1_total_cost_eur'],
            e2_total_cost_eur=row['e2_total_cost_eur'],
            e3_total_cost_eur=row['e3_total_cost_eur'],
            e4_total_cost_eur=row['e4_total_cost_eur'],
            e5_total_cost_eur=row['e5_total_cost_eur'],
            has_suspicious_values=bool(row['has_suspicious_values']),
            calculation_notes=row['calculation_notes'],
            config_id=row['config_id'],
        )
