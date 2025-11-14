"""Unit tests for data interpolation service.

Tests interpolation logic for handling missing data per user specification:
"c use interpolation" (from clarification Q2)

Uses SciPy for scientific interpolation methods.

Test cases cover:
- Linear interpolation (default)
- Quadratic and cubic interpolation
- Edge cases (single point, all missing, boundary extrapolation)
- Interpolation flagging for transparency
"""

import pytest
import numpy as np
from src.interpolation.interpolator import Interpolator, InterpolationResult


class TestInterpolator:
    """Test suite for Interpolator service."""

    @pytest.fixture
    def interpolator(self):
        """Create interpolator instance with linear method (default)."""
        return Interpolator(method="linear")

    def test_interpolator_initialization(self, interpolator):
        """Test Interpolator can be instantiated."""
        assert interpolator is not None
        assert interpolator.method == "linear"

    def test_linear_interpolation_single_gap(self, interpolator):
        """Test linear interpolation for a single missing value.

        Data: [2020: 100, 2021: ?, 2022: 120]
        Expected: 2021 = 110 (linear interpolation)
        """
        years = np.array([2020, 2021, 2022])
        values = np.array([100.0, np.nan, 120.0])

        result = interpolator.interpolate(years, values)

        assert isinstance(result, InterpolationResult)
        assert len(result.interpolated_values) == 3
        assert result.interpolated_values[0] == pytest.approx(100.0)
        assert result.interpolated_values[1] == pytest.approx(110.0)  # Interpolated
        assert result.interpolated_values[2] == pytest.approx(120.0)
        assert result.interpolated_indices == [1]  # Index 1 was interpolated

    def test_linear_interpolation_multiple_gaps(self, interpolator):
        """Test linear interpolation for multiple missing values.

        Data: [2020: 100, 2021: ?, 2022: ?, 2023: 130]
        Expected: 2021 = 110, 2022 = 120 (linear)
        """
        years = np.array([2020, 2021, 2022, 2023])
        values = np.array([100.0, np.nan, np.nan, 130.0])

        result = interpolator.interpolate(years, values)

        assert result.interpolated_values[1] == pytest.approx(110.0)
        assert result.interpolated_values[2] == pytest.approx(120.0)
        assert result.interpolated_indices == [1, 2]

    def test_no_interpolation_needed(self, interpolator):
        """Test case where all data is present (no NaN values)."""
        years = np.array([2020, 2021, 2022])
        values = np.array([100.0, 110.0, 120.0])

        result = interpolator.interpolate(years, values)

        np.testing.assert_array_almost_equal(result.interpolated_values, values)
        assert result.interpolated_indices == []  # No interpolation needed

    def test_quadratic_interpolation(self):
        """Test quadratic interpolation method.

        Quadratic better fits non-linear trends than linear.
        """
        interpolator = Interpolator(method="quadratic")

        years = np.array([2020, 2021, 2022, 2023, 2024])
        values = np.array([100.0, np.nan, 121.0, np.nan, 156.0])  # Quadratic-ish growth

        result = interpolator.interpolate(years, values)

        # Check that interpolation completed (exact values depend on scipy implementation)
        assert not np.isnan(result.interpolated_values).any()
        assert 1 in result.interpolated_indices
        assert 3 in result.interpolated_indices

    def test_cubic_interpolation(self):
        """Test cubic interpolation method.

        Cubic provides smoothest interpolation for complex trends.
        """
        interpolator = Interpolator(method="cubic")

        years = np.array([2020, 2021, 2022, 2023, 2024, 2025])
        values = np.array([100.0, np.nan, 121.0, np.nan, 156.0, 180.0])

        result = interpolator.interpolate(years, values)

        assert not np.isnan(result.interpolated_values).any()
        assert result.interpolated_indices == [1, 3]

    def test_edge_case_first_value_missing(self, interpolator):
        """Test edge case: first value is missing (requires extrapolation or error).

        For safety, should either extrapolate or raise error.
        We'll extrapolate using nearest value.
        """
        years = np.array([2020, 2021, 2022])
        values = np.array([np.nan, 110.0, 120.0])

        result = interpolator.interpolate(years, values)

        # Should handle gracefully (extrapolation or fill with nearest)
        assert not np.isnan(result.interpolated_values).any()

    def test_edge_case_last_value_missing(self, interpolator):
        """Test edge case: last value is missing (extrapolation)."""
        years = np.array([2020, 2021, 2022])
        values = np.array([100.0, 110.0, np.nan])

        result = interpolator.interpolate(years, values)

        # Should extrapolate or use nearest value
        assert not np.isnan(result.interpolated_values).any()

    def test_edge_case_single_valid_point(self, interpolator):
        """Test edge case: only one valid data point.

        Should fill all NaN with that single value (constant fill).
        """
        years = np.array([2020, 2021, 2022])
        values = np.array([np.nan, 110.0, np.nan])

        result = interpolator.interpolate(years, values)

        # All values should be 110.0 (constant fill)
        np.testing.assert_array_almost_equal(result.interpolated_values, [110.0, 110.0, 110.0])

    def test_edge_case_all_missing(self, interpolator):
        """Test edge case: all values are NaN.

        Should raise error or return zeros/original NaNs with warning.
        """
        years = np.array([2020, 2021, 2022])
        values = np.array([np.nan, np.nan, np.nan])

        with pytest.raises(ValueError, match="Cannot interpolate.*all values are missing"):
            interpolator.interpolate(years, values)

    def test_interpolation_result_structure(self, interpolator):
        """Test InterpolationResult has expected structure."""
        years = np.array([2020, 2021])
        values = np.array([100.0, 110.0])

        result = interpolator.interpolate(years, values)

        assert hasattr(result, 'interpolated_values')
        assert hasattr(result, 'interpolated_indices')
        assert hasattr(result, 'method_used')
        assert isinstance(result.interpolated_values, np.ndarray)
        assert isinstance(result.interpolated_indices, list)
        assert result.method_used == "linear"

    def test_non_uniform_time_series(self, interpolator):
        """Test interpolation with non-uniform time intervals.

        Years: [2020, 2022, 2025] (gaps of 2 and 3 years)
        """
        years = np.array([2020, 2022, 2025])
        values = np.array([100.0, np.nan, 150.0])

        result = interpolator.interpolate(years, values)

        # Linear interpolation: 2022 should be between 100 and 150
        # x=2022 is 2 out of 5 years → 100 + (150-100) * 2/5 = 120
        assert result.interpolated_values[1] == pytest.approx(120.0, rel=1e-2)

    def test_interpolate_carbon_prices_realistic(self, interpolator):
        """Test realistic scenario: interpolating carbon prices.

        Scenario: IEA NZ2050 with some missing years
        """
        years = np.array([2024, 2025, 2026, 2027, 2028, 2029, 2030])
        prices = np.array([80.0, np.nan, 95.0, np.nan, 115.0, np.nan, 130.0])

        result = interpolator.interpolate(years, prices)

        # All prices should be filled
        assert not np.isnan(result.interpolated_values).any()
        # Interpolated indices: 1, 3, 5
        assert set(result.interpolated_indices) == {1, 3, 5}
        # Values should be monotonically increasing (carbon price trend)
        assert np.all(np.diff(result.interpolated_values) > 0)
