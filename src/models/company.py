"""Company entity models for ESRS environmental cost assessment.

References:
- ESRS Set 1 (ESRS E1-E5): European Sustainability Reporting Standards
- GHG Protocol Corporate Standard: Scope 1/2/3 emissions accounting
"""

from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class CompanyProfile:
    """Company master data and ESRS applicability.

    Represents a company's basic profile and which ESRS environmental
    topics are applicable based on double materiality assessment.

    Attributes:
        company_id: Unique identifier (e.g., LEI, internal ID)
        company_name: Legal company name
        industry_code: NACE Rev. 2 industry classification code
        annual_revenue_eur: Annual revenue in EUR (must be > 0)
        reporting_year: Reporting year (2020-2100)
        esrs_e1_applicable: E1 Climate Change applicable (0 or 1)
        esrs_e2_applicable: E2 Pollution applicable (0 or 1)
        esrs_e3_applicable: E3 Water and Marine Resources applicable (0 or 1)
        esrs_e4_applicable: E4 Biodiversity and Ecosystems applicable (0 or 1)
        esrs_e5_applicable: E5 Circular Economy applicable (0 or 1)

    Validation:
        - annual_revenue_eur must be > 0
        - reporting_year must be between 2020 and 2100
        - At least one ESRS topic must be applicable (sum of esrs_ex_applicable >= 1)
        - All esrs_ex_applicable flags must be 0 or 1
    """

    company_id: str
    company_name: str
    industry_code: str
    annual_revenue_eur: float
    reporting_year: int
    esrs_e1_applicable: int = 1
    esrs_e2_applicable: int = 0
    esrs_e3_applicable: int = 0
    esrs_e4_applicable: int = 0
    esrs_e5_applicable: int = 0

    def __post_init__(self):
        """Validate company profile data."""
        # Validate revenue
        if self.annual_revenue_eur <= 0:
            raise ValueError(f"annual_revenue_eur must be > 0, got {self.annual_revenue_eur}")

        # Validate reporting year
        if not (2020 <= self.reporting_year <= 2100):
            raise ValueError(f"reporting_year must be between 2020 and 2100, got {self.reporting_year}")

        # Validate ESRS applicability flags
        esrs_flags = [
            self.esrs_e1_applicable,
            self.esrs_e2_applicable,
            self.esrs_e3_applicable,
            self.esrs_e4_applicable,
            self.esrs_e5_applicable,
        ]

        for i, flag in enumerate(esrs_flags, start=1):
            if flag not in (0, 1):
                raise ValueError(f"esrs_e{i}_applicable must be 0 or 1, got {flag}")

        # At least one ESRS topic must be applicable
        if sum(esrs_flags) < 1:
            raise ValueError("At least one ESRS topic must be applicable (esrs_ex_applicable sum must be >= 1)")

    def get_applicable_topics(self) -> list[str]:
        """Return list of applicable ESRS environmental topic codes.

        Returns:
            List of strings like ['E1', 'E2', 'E5'] for applicable topics
        """
        topics = []
        if self.esrs_e1_applicable:
            topics.append("E1")
        if self.esrs_e2_applicable:
            topics.append("E2")
        if self.esrs_e3_applicable:
            topics.append("E3")
        if self.esrs_e4_applicable:
            topics.append("E4")
        if self.esrs_e5_applicable:
            topics.append("E5")
        return topics


@dataclass
class CompanyReportData:
    """Company environmental performance data from sustainability reports.

    Contains the actual environmental metrics reported by a company for a
    specific reporting year. This is the input data for financial cost assessment.

    Attributes:
        record_id: Unique record identifier (company_id + reporting_year)
        company_id: Foreign key to CompanyProfile
        reporting_year: Reporting year for this data
        scope_1_emissions_tco2e: Direct GHG emissions in tCO2e (>= 0)
        scope_2_location_tco2e: Location-based indirect emissions in tCO2e (>= 0)
        scope_2_market_tco2e: Market-based indirect emissions in tCO2e (>= 0)
        scope_3_emissions_tco2e: Value chain emissions in tCO2e (>= 0 or null)
        carbon_intensity_tco2e_per_eur: Emissions intensity (tCO2e/EUR revenue, >= 0)
        pollution_metrics: JSON string with pollution data (e.g., NOx, SOx, PM10)
        water_consumption_m3: Water consumption in cubic meters (>= 0 or null)
        water_discharge_m3: Water discharge in cubic meters (>= 0 or null)
        biodiversity_land_use_ha: Land use in hectares (>= 0 or null)
        biodiversity_habitat_impact_score: Habitat impact score 0-10 (or null)
        waste_generation_tonnes: Total waste generated in tonnes (>= 0 or null)
        recycling_rate_pct: Recycling rate percentage 0-100 (or null)
        material_recovery_pct: Material recovery percentage 0-100 (or null)
        data_quality_indicator: Data quality level (measured/estimated/modeled/incomplete)
        report_source_reference: Source document reference (URL, report title, etc.)

    Validation:
        - All emissions values >= 0
        - Percentages between 0 and 100
        - reporting_year between 2020 and 2100
        - data_quality_indicator in allowed values
    """

    record_id: str
    company_id: str
    reporting_year: int
    scope_1_emissions_tco2e: float
    scope_2_location_tco2e: float
    scope_2_market_tco2e: float
    scope_3_emissions_tco2e: Optional[float]
    carbon_intensity_tco2e_per_eur: float
    data_quality_indicator: str
    report_source_reference: str
    pollution_metrics: Optional[str] = None
    water_consumption_m3: Optional[float] = None
    water_discharge_m3: Optional[float] = None
    biodiversity_land_use_ha: Optional[float] = None
    biodiversity_habitat_impact_score: Optional[float] = None
    waste_generation_tonnes: Optional[float] = None
    recycling_rate_pct: Optional[float] = None
    material_recovery_pct: Optional[float] = None

    def __post_init__(self):
        """Validate company report data."""
        # Validate reporting year
        if not (2020 <= self.reporting_year <= 2100):
            raise ValueError(f"reporting_year must be between 2020 and 2100, got {self.reporting_year}")

        # Validate emissions (non-negative)
        if self.scope_1_emissions_tco2e < 0:
            raise ValueError(f"scope_1_emissions_tco2e must be >= 0, got {self.scope_1_emissions_tco2e}")
        if self.scope_2_location_tco2e < 0:
            raise ValueError(f"scope_2_location_tco2e must be >= 0, got {self.scope_2_location_tco2e}")
        if self.scope_2_market_tco2e < 0:
            raise ValueError(f"scope_2_market_tco2e must be >= 0, got {self.scope_2_market_tco2e}")
        if self.scope_3_emissions_tco2e is not None and self.scope_3_emissions_tco2e < 0:
            raise ValueError(f"scope_3_emissions_tco2e must be >= 0, got {self.scope_3_emissions_tco2e}")

        # Validate carbon intensity
        if self.carbon_intensity_tco2e_per_eur < 0:
            raise ValueError(f"carbon_intensity_tco2e_per_eur must be >= 0, got {self.carbon_intensity_tco2e_per_eur}")

        # Validate percentages
        if self.recycling_rate_pct is not None and not (0 <= self.recycling_rate_pct <= 100):
            raise ValueError(f"recycling_rate_pct must be 0-100, got {self.recycling_rate_pct}")
        if self.material_recovery_pct is not None and not (0 <= self.material_recovery_pct <= 100):
            raise ValueError(f"material_recovery_pct must be 0-100, got {self.material_recovery_pct}")

        # Validate biodiversity impact score if present
        if self.biodiversity_habitat_impact_score is not None:
            if not (0 <= self.biodiversity_habitat_impact_score <= 10):
                raise ValueError(f"biodiversity_habitat_impact_score must be 0-10, got {self.biodiversity_habitat_impact_score}")

        # Validate data quality indicator
        allowed_quality = ["measured", "estimated", "modeled", "incomplete"]
        if self.data_quality_indicator not in allowed_quality:
            raise ValueError(f"data_quality_indicator must be one of {allowed_quality}, got '{self.data_quality_indicator}'")

        # Validate non-negative values for optional metrics
        if self.water_consumption_m3 is not None and self.water_consumption_m3 < 0:
            raise ValueError(f"water_consumption_m3 must be >= 0, got {self.water_consumption_m3}")
        if self.water_discharge_m3 is not None and self.water_discharge_m3 < 0:
            raise ValueError(f"water_discharge_m3 must be >= 0, got {self.water_discharge_m3}")
        if self.biodiversity_land_use_ha is not None and self.biodiversity_land_use_ha < 0:
            raise ValueError(f"biodiversity_land_use_ha must be >= 0, got {self.biodiversity_land_use_ha}")
        if self.waste_generation_tonnes is not None and self.waste_generation_tonnes < 0:
            raise ValueError(f"waste_generation_tonnes must be >= 0, got {self.waste_generation_tonnes}")

    def get_total_emissions_tco2e(self) -> float:
        """Calculate total GHG emissions (Scope 1 + 2 market + 3).

        Uses market-based Scope 2 emissions as per GHG Protocol guidance.
        If Scope 3 is null, returns only Scope 1 + 2.

        Returns:
            Total emissions in tCO2e
        """
        total = self.scope_1_emissions_tco2e + self.scope_2_market_tco2e
        if self.scope_3_emissions_tco2e is not None:
            total += self.scope_3_emissions_tco2e
        return total

    def get_pollution_metrics_dict(self) -> Optional[dict]:
        """Parse pollution_metrics JSON string to dictionary.

        Returns:
            Dictionary with pollution metrics (e.g., {'NOx_tonnes': 100}) or None
        """
        if self.pollution_metrics is None:
            return None
        try:
            return json.loads(self.pollution_metrics)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in pollution_metrics: {self.pollution_metrics}")
