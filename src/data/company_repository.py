"""Repository for company data persistence (CompanyProfile and CompanyReportData).

Provides CRUD operations for company profiles and environmental report data
with proper transaction handling and validation.
"""

from typing import Optional
from ..models.company import CompanyProfile, CompanyReportData
from .database import get_db


class CompanyRepository:
    """Data access layer for company entities.

    Handles persistence of CompanyProfile and CompanyReportData to SQLite,
    mapping between database rows and domain model objects.
    """

    def __init__(self):
        """Initialize repository with database connection."""
        self.db = get_db()

    # CompanyProfile operations

    def insert_company_profile(self, profile: CompanyProfile) -> None:
        """Insert a new company profile.

        Args:
            profile: CompanyProfile object to insert

        Raises:
            sqlite3.IntegrityError: If company_id already exists
            ValueError: If profile validation fails
        """
        query = """
            INSERT INTO company_profiles (
                company_id, company_name, industry_code, annual_revenue_eur,
                reporting_year, esrs_e1_applicable, esrs_e2_applicable,
                esrs_e3_applicable, esrs_e4_applicable, esrs_e5_applicable
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        parameters = (
            profile.company_id,
            profile.company_name,
            profile.industry_code,
            profile.annual_revenue_eur,
            profile.reporting_year,
            profile.esrs_e1_applicable,
            profile.esrs_e2_applicable,
            profile.esrs_e3_applicable,
            profile.esrs_e4_applicable,
            profile.esrs_e5_applicable,
        )
        self.db.execute_insert(query, parameters)

    def get_company_profile(self, company_id: str) -> Optional[CompanyProfile]:
        """Retrieve company profile by ID.

        Args:
            company_id: Unique company identifier

        Returns:
            CompanyProfile object if found, None otherwise
        """
        query = """
            SELECT * FROM company_profiles WHERE company_id = ?
        """
        results = self.db.execute_query(query, (company_id,))

        if not results:
            return None

        row = results[0]
        return CompanyProfile(
            company_id=row['company_id'],
            company_name=row['company_name'],
            industry_code=row['industry_code'],
            annual_revenue_eur=row['annual_revenue_eur'],
            reporting_year=row['reporting_year'],
            esrs_e1_applicable=row['esrs_e1_applicable'],
            esrs_e2_applicable=row['esrs_e2_applicable'],
            esrs_e3_applicable=row['esrs_e3_applicable'],
            esrs_e4_applicable=row['esrs_e4_applicable'],
            esrs_e5_applicable=row['esrs_e5_applicable'],
        )

    def update_company_profile(self, profile: CompanyProfile) -> int:
        """Update existing company profile.

        Args:
            profile: CompanyProfile object with updated data

        Returns:
            Number of rows updated (should be 1 if successful, 0 if not found)

        Raises:
            ValueError: If profile validation fails
        """
        query = """
            UPDATE company_profiles SET
                company_name = ?,
                industry_code = ?,
                annual_revenue_eur = ?,
                reporting_year = ?,
                esrs_e1_applicable = ?,
                esrs_e2_applicable = ?,
                esrs_e3_applicable = ?,
                esrs_e4_applicable = ?,
                esrs_e5_applicable = ?
            WHERE company_id = ?
        """
        parameters = (
            profile.company_name,
            profile.industry_code,
            profile.annual_revenue_eur,
            profile.reporting_year,
            profile.esrs_e1_applicable,
            profile.esrs_e2_applicable,
            profile.esrs_e3_applicable,
            profile.esrs_e4_applicable,
            profile.esrs_e5_applicable,
            profile.company_id,
        )
        return self.db.execute_update(query, parameters)

    def delete_company_profile(self, company_id: str) -> int:
        """Delete company profile by ID.

        Note: This will cascade delete related company_report_data due to FK constraints.

        Args:
            company_id: Unique company identifier

        Returns:
            Number of rows deleted (should be 1 if successful, 0 if not found)
        """
        query = "DELETE FROM company_profiles WHERE company_id = ?"
        return self.db.execute_delete(query, (company_id,))

    def list_all_company_profiles(self) -> list[CompanyProfile]:
        """Retrieve all company profiles.

        Returns:
            List of CompanyProfile objects
        """
        query = "SELECT * FROM company_profiles ORDER BY company_name"
        results = self.db.execute_query(query)

        profiles = []
        for row in results:
            profiles.append(CompanyProfile(
                company_id=row['company_id'],
                company_name=row['company_name'],
                industry_code=row['industry_code'],
                annual_revenue_eur=row['annual_revenue_eur'],
                reporting_year=row['reporting_year'],
                esrs_e1_applicable=row['esrs_e1_applicable'],
                esrs_e2_applicable=row['esrs_e2_applicable'],
                esrs_e3_applicable=row['esrs_e3_applicable'],
                esrs_e4_applicable=row['esrs_e4_applicable'],
                esrs_e5_applicable=row['esrs_e5_applicable'],
            ))
        return profiles

    # CompanyReportData operations

    def insert_company_report_data(self, report: CompanyReportData) -> None:
        """Insert company environmental report data.

        Args:
            report: CompanyReportData object to insert

        Raises:
            sqlite3.IntegrityError: If record_id already exists or company_id FK fails
            ValueError: If report validation fails
        """
        query = """
            INSERT INTO company_report_data (
                record_id, company_id, reporting_year,
                scope_1_emissions_tco2e, scope_2_location_tco2e, scope_2_market_tco2e,
                scope_3_emissions_tco2e, carbon_intensity_tco2e_per_eur,
                pollution_metrics, water_consumption_m3, water_discharge_m3,
                biodiversity_land_use_ha, biodiversity_habitat_impact_score,
                waste_generation_tonnes, recycling_rate_pct, material_recovery_pct,
                data_quality_indicator, report_source_reference
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        parameters = (
            report.record_id,
            report.company_id,
            report.reporting_year,
            report.scope_1_emissions_tco2e,
            report.scope_2_location_tco2e,
            report.scope_2_market_tco2e,
            report.scope_3_emissions_tco2e,
            report.carbon_intensity_tco2e_per_eur,
            report.pollution_metrics,
            report.water_consumption_m3,
            report.water_discharge_m3,
            report.biodiversity_land_use_ha,
            report.biodiversity_habitat_impact_score,
            report.waste_generation_tonnes,
            report.recycling_rate_pct,
            report.material_recovery_pct,
            report.data_quality_indicator,
            report.report_source_reference,
        )
        self.db.execute_insert(query, parameters)

    def get_company_report_data(self, record_id: str) -> Optional[CompanyReportData]:
        """Retrieve company report data by record ID.

        Args:
            record_id: Unique record identifier

        Returns:
            CompanyReportData object if found, None otherwise
        """
        query = "SELECT * FROM company_report_data WHERE record_id = ?"
        results = self.db.execute_query(query, (record_id,))

        if not results:
            return None

        row = results[0]
        return self._row_to_report_data(row)

    def get_report_data_for_company(self, company_id: str, reporting_year: Optional[int] = None) -> list[CompanyReportData]:
        """Retrieve all report data for a company, optionally filtered by year.

        Args:
            company_id: Company identifier
            reporting_year: Optional year filter

        Returns:
            List of CompanyReportData objects
        """
        if reporting_year is not None:
            query = """
                SELECT * FROM company_report_data
                WHERE company_id = ? AND reporting_year = ?
                ORDER BY reporting_year DESC
            """
            results = self.db.execute_query(query, (company_id, reporting_year))
        else:
            query = """
                SELECT * FROM company_report_data
                WHERE company_id = ?
                ORDER BY reporting_year DESC
            """
            results = self.db.execute_query(query, (company_id,))

        return [self._row_to_report_data(row) for row in results]

    def delete_company_report_data(self, record_id: str) -> int:
        """Delete company report data by record ID.

        Args:
            record_id: Unique record identifier

        Returns:
            Number of rows deleted (should be 1 if successful, 0 if not found)
        """
        query = "DELETE FROM company_report_data WHERE record_id = ?"
        return self.db.execute_delete(query, (record_id,))

    def _row_to_report_data(self, row) -> CompanyReportData:
        """Convert database row to CompanyReportData object.

        Args:
            row: sqlite3.Row object from query

        Returns:
            CompanyReportData object
        """
        return CompanyReportData(
            record_id=row['record_id'],
            company_id=row['company_id'],
            reporting_year=row['reporting_year'],
            scope_1_emissions_tco2e=row['scope_1_emissions_tco2e'],
            scope_2_location_tco2e=row['scope_2_location_tco2e'],
            scope_2_market_tco2e=row['scope_2_market_tco2e'],
            scope_3_emissions_tco2e=row['scope_3_emissions_tco2e'],
            carbon_intensity_tco2e_per_eur=row['carbon_intensity_tco2e_per_eur'],
            pollution_metrics=row['pollution_metrics'],
            water_consumption_m3=row['water_consumption_m3'],
            water_discharge_m3=row['water_discharge_m3'],
            biodiversity_land_use_ha=row['biodiversity_land_use_ha'],
            biodiversity_habitat_impact_score=row['biodiversity_habitat_impact_score'],
            waste_generation_tonnes=row['waste_generation_tonnes'],
            recycling_rate_pct=row['recycling_rate_pct'],
            material_recovery_pct=row['material_recovery_pct'],
            data_quality_indicator=row['data_quality_indicator'],
            report_source_reference=row['report_source_reference'],
        )
