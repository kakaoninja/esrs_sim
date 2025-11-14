"""Carbon pricing cost calculator for ESRS E1 Climate Change.

Calculates financial costs from carbon pricing under different climate scenarios.
Uses GHG Protocol methodology for emissions accounting (Scope 1+2+3).

Produces 95% confidence intervals using Monte Carlo simulation with correlation support.

References:
- GHG Protocol Corporate Standard: https://ghgprotocol.org/corporate-standard
- ESRS E1: Climate change financial impact assessment
- IEA/NGFS scenarios: Carbon price projections
- Uncertainty quantification: Monte Carlo with correlated sampling
"""

import math
import numpy as np
from typing import Optional
from ..models.company import CompanyReportData
from ..models.scenario import ClimateScenario
from ..models.cost import CostCategory


class CarbonPricingCalculator:
    """Calculator for carbon pricing costs under climate scenarios.

    Calculates the financial cost of carbon emissions based on:
    - Company's total GHG emissions (Scope 1+2+3)
    - Scenario-specific carbon price projections
    - Time horizon from baseline to target year

    Confidence levels decrease with longer projection horizons to reflect
    uncertainty in future carbon prices and emission levels.
    """

    # Base confidence level for baseline year (high confidence in current data)
    BASE_CONFIDENCE = 0.95

    # Confidence degradation per year of projection (reflects uncertainty)
    # 0.025/year decay: 6-year projection → 0.80 confidence, 10-year → 0.70
    CONFIDENCE_DECAY_PER_YEAR = 0.025

    # Emissions uncertainty by data quality (standard deviation as fraction of emissions)
    EMISSIONS_UNCERTAINTY = {
        "measured": 0.05,    # ±5% for high-quality measured data
        "estimated": 0.10,   # ±10% for estimated data
        "modeled": 0.15,     # ±15% for modeled data
        "incomplete": 0.20   # ±20% for incomplete data
    }

    # CO2 price uncertainty
    PRICE_UNCERTAINTY_BASELINE = 0.05  # ±5% for current year price (market volatility)
    PRICE_UNCERTAINTY_PER_YEAR = 0.02  # +2% per year for projection uncertainty

    # Monte Carlo simulation parameters
    MC_ITERATIONS = 10000  # Number of Monte Carlo samples for CI calculation
    MC_RANDOM_SEED = 42    # Default seed for reproducibility (None = random)

    # Correlation between emissions and CO2 price uncertainties
    # Negative correlation: higher carbon prices → emissions reduction efforts
    # Range: -1.0 (perfect negative) to +1.0 (perfect positive)
    # Default: -0.3 (moderate negative correlation)
    EMISSIONS_PRICE_CORRELATION = -0.3

    def __init__(
        self,
        mc_iterations: int = 10000,
        emissions_price_correlation: Optional[float] = None,
        random_seed: Optional[int] = 42
    ):
        """Initialize carbon pricing calculator with Monte Carlo configuration.

        Args:
            mc_iterations: Number of Monte Carlo iterations for CI calculation
            emissions_price_correlation: Correlation between emissions and price uncertainties
                                        (-1.0 to +1.0). If None, uses class default.
            random_seed: Random seed for reproducibility. If None, results are non-deterministic.
        """
        self.mc_iterations = mc_iterations
        self.emissions_price_correlation = (
            emissions_price_correlation if emissions_price_correlation is not None
            else self.EMISSIONS_PRICE_CORRELATION
        )
        self.random_seed = random_seed

        # Validate correlation
        if not (-1.0 <= self.emissions_price_correlation <= 1.0):
            raise ValueError(
                f"emissions_price_correlation must be between -1.0 and 1.0, "
                f"got {self.emissions_price_correlation}"
            )

    def calculate_carbon_cost(
        self,
        company_data: CompanyReportData,
        scenario: ClimateScenario,
        target_year: int
    ) -> CostCategory:
        """Calculate carbon pricing cost for a company under a scenario.

        Args:
            company_data: Company's environmental report data
            scenario: Climate scenario with carbon price projections
            target_year: Year to calculate cost for (2024-2100)

        Returns:
            CostCategory object with carbon pricing cost, confidence, and metadata

        Calculation:
            1. Total emissions = Scope 1 + Scope 2 (market-based) + Scope 3
            2. Carbon price = scenario.get_co2_price_for_year(target_year)
            3. Carbon cost = total emissions * carbon price
            4. Confidence = base confidence - (years from baseline * decay rate)
        """
        # Step 1: Calculate total GHG emissions
        total_emissions_tco2e = self._calculate_total_emissions(company_data)

        # Step 2: Get carbon price for target year (with interpolation if needed)
        carbon_price_eur_per_tco2e = scenario.get_co2_price_for_year(target_year)

        # Step 3: Calculate carbon cost
        carbon_cost_eur = total_emissions_tco2e * carbon_price_eur_per_tco2e

        # Step 4: Calculate cost horizon and confidence level
        cost_horizon_years = target_year - company_data.reporting_year
        confidence_level = self._calculate_confidence_level(cost_horizon_years)

        # Step 5: Calculate 95% confidence interval
        ci_lower, ci_upper = self._calculate_confidence_interval(
            median_cost=carbon_cost_eur,
            emissions=total_emissions_tco2e,
            price=carbon_price_eur_per_tco2e,
            data_quality=company_data.data_quality_indicator,
            cost_horizon_years=cost_horizon_years,
            scenario=scenario
        )

        # Step 6: Build calculation method documentation
        calculation_method = (
            f"Carbon cost = {total_emissions_tco2e:,.0f} tCO2e * "
            f"€{carbon_price_eur_per_tco2e:.2f}/tCO2e (year {target_year}). "
            f"Emissions: Scope 1 ({company_data.scope_1_emissions_tco2e:,.0f}) + "
            f"Scope 2 market ({company_data.scope_2_market_tco2e:,.0f}) + "
            f"Scope 3 ({company_data.scope_3_emissions_tco2e or 0:,.0f}) tCO2e. "
            f"Scenario: {scenario.scenario_name} ({scenario.scenario_source}). "
            f"95% CI via Monte Carlo ({self.mc_iterations:,} iterations, "
            f"ρ={self.emissions_price_correlation:.2f}): [€{ci_lower:,.0f}, €{ci_upper:,.0f}]."
        )

        # Step 7: Create and return CostCategory result with confidence intervals
        return CostCategory(
            category_name="carbon_pricing",
            esrs_topic="E1",
            amount_eur=carbon_cost_eur,
            amount_eur_lower=ci_lower,
            amount_eur_upper=ci_upper,
            confidence_level=confidence_level,
            cost_horizon_years=cost_horizon_years,
            calculation_method=calculation_method,
            influence_factors_applied=f'["{scenario.scenario_id}_carbon_price"]',
            suspicious_values=None,
            notes=f"GHG Protocol Scope 1+2+3 emissions. Carbon price from {scenario.scenario_source}.",
        )

    def _calculate_total_emissions(self, company_data: CompanyReportData) -> float:
        """Calculate total GHG emissions (Scope 1 + 2 market + 3).

        Uses market-based Scope 2 emissions as per GHG Protocol guidance.
        If Scope 3 is None, only Scope 1+2 is used.

        Args:
            company_data: Company environmental report data

        Returns:
            Total emissions in tCO2e
        """
        total = company_data.scope_1_emissions_tco2e + company_data.scope_2_market_tco2e

        if company_data.scope_3_emissions_tco2e is not None:
            total += company_data.scope_3_emissions_tco2e

        return total

    def _calculate_confidence_level(self, cost_horizon_years: int) -> float:
        """Calculate confidence level based on projection horizon.

        Confidence decreases linearly with time horizon to reflect:
        - Uncertainty in future carbon prices
        - Uncertainty in company's future emissions
        - Policy and market risks

        Args:
            cost_horizon_years: Years from baseline to target (0+ years)

        Returns:
            Confidence level (0.0-1.0), clamped to minimum 0.40
        """
        if cost_horizon_years <= 0:
            # Baseline year or past: highest confidence
            return self.BASE_CONFIDENCE

        # Linear decay with horizon
        confidence = self.BASE_CONFIDENCE - (cost_horizon_years * self.CONFIDENCE_DECAY_PER_YEAR)

        # Clamp to minimum 0.40 (don't go below 40% confidence even for far future)
        return max(confidence, 0.40)

    def _calculate_confidence_interval(
        self,
        median_cost: float,
        emissions: float,
        price: float,
        data_quality: str,
        cost_horizon_years: int,
        scenario: ClimateScenario
    ) -> tuple[float, float]:
        """Calculate 95% confidence interval using Monte Carlo simulation with correlations.

        Performs Monte Carlo sampling with correlated emissions and price uncertainties
        to generate empirical confidence intervals. Captures:
        1. Emissions measurement uncertainty (data quality dependent)
        2. CO2 price projection uncertainty (time horizon + scenario dependent)
        3. Correlation between emissions and price (e.g., high prices drive reduction)

        Monte Carlo approach enables:
        - Accurate modeling of parameter correlations
        - Non-normal distribution handling
        - Empirical confidence intervals from percentiles

        Args:
            median_cost: Median cost estimate (emissions × price)
            emissions: Total emissions in tCO2e
            price: CO2 price in EUR/tCO2e
            data_quality: Data quality indicator (measured/estimated/modeled/incomplete)
            cost_horizon_years: Years from baseline to target
            scenario: Climate scenario (for price volatility assessment)

        Returns:
            Tuple of (lower_bound, upper_bound) for 95% CI (2.5th and 97.5th percentiles)
        """
        # Handle zero cost edge case
        if median_cost == 0 or emissions == 0 or price == 0:
            return (0.0, 0.0)

        # 1. Calculate uncertainty parameters (standard deviations)

        # Emissions uncertainty (absolute)
        emissions_std_rel = self.EMISSIONS_UNCERTAINTY.get(data_quality, 0.15)
        emissions_std = emissions * emissions_std_rel

        # CO2 price uncertainty (absolute)
        price_std_rel = self.PRICE_UNCERTAINTY_BASELINE

        # Add projection uncertainty for future years
        if cost_horizon_years > 0:
            price_std_rel += cost_horizon_years * self.PRICE_UNCERTAINTY_PER_YEAR

        # Add extra uncertainty for volatile scenarios
        price_change_pct = abs(
            scenario.co2_price_target_eur_per_tco2e - scenario.co2_price_baseline_eur_per_tco2e
        ) / scenario.co2_price_baseline_eur_per_tco2e
        if price_change_pct > 0.5:
            price_std_rel += 0.05

        price_std = price * price_std_rel

        # 2. Build correlation matrix
        # [1.0,  ρ  ]
        # [ρ,    1.0]
        # where ρ = emissions_price_correlation
        correlation_matrix = np.array([
            [1.0, self.emissions_price_correlation],
            [self.emissions_price_correlation, 1.0]
        ])

        # 3. Build covariance matrix from correlation and standard deviations
        # Cov = D × Corr × D, where D is diagonal matrix of standard deviations
        std_vector = np.array([emissions_std, price_std])
        covariance_matrix = np.outer(std_vector, std_vector) * correlation_matrix

        # 4. Set random seed for reproducibility
        if self.random_seed is not None:
            np.random.seed(self.random_seed)

        # 5. Perform Monte Carlo sampling
        # Sample from bivariate normal distribution with correlation
        mean_vector = np.array([emissions, price])

        try:
            samples = np.random.multivariate_normal(
                mean=mean_vector,
                cov=covariance_matrix,
                size=self.mc_iterations
            )
        except np.linalg.LinAlgError:
            # Fallback if covariance matrix is singular (shouldn't happen with valid correlation)
            # Use independent sampling
            samples = np.column_stack([
                np.random.normal(emissions, emissions_std, self.mc_iterations),
                np.random.normal(price, price_std, self.mc_iterations)
            ])

        # Extract sampled emissions and prices
        sampled_emissions = samples[:, 0]
        sampled_prices = samples[:, 1]

        # Ensure non-negative samples (emissions and prices can't be negative)
        sampled_emissions = np.maximum(sampled_emissions, 0.0)
        sampled_prices = np.maximum(sampled_prices, 0.0)

        # 6. Calculate cost for each Monte Carlo sample
        sampled_costs = sampled_emissions * sampled_prices

        # 7. Extract 95% confidence interval from empirical distribution
        # 2.5th percentile (lower bound) and 97.5th percentile (upper bound)
        ci_lower = np.percentile(sampled_costs, 2.5)
        ci_upper = np.percentile(sampled_costs, 97.5)

        return (float(ci_lower), float(ci_upper))
