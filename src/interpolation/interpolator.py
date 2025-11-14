"""Data interpolation service for handling missing values.

Uses SciPy's interpolation methods per user specification: "c use interpolation"

Supports linear, quadratic, and cubic interpolation for time-series data.
Flags interpolated values for transparency.

References:
- SciPy interpolate documentation: https://docs.scipy.org/doc/scipy/reference/interpolate.html
- Constitution Principle III: Interpolation for missing data
"""

from dataclasses import dataclass
from typing import Literal
import numpy as np
from scipy import interpolate


@dataclass
class InterpolationResult:
    """Result of interpolation with flagged interpolated indices.

    Attributes:
        interpolated_values: Array of values with NaNs filled by interpolation
        interpolated_indices: List of indices that were interpolated (for transparency)
        method_used: Interpolation method used (linear/quadratic/cubic)
    """

    interpolated_values: np.ndarray
    interpolated_indices: list[int]
    method_used: str


class Interpolator:
    """Interpolator for time-series data with missing values.

    Handles missing data (NaN) using SciPy interpolation methods.
    Provides transparency by flagging which values were interpolated.

    Supported methods:
    - linear: Linear interpolation between points
    - quadratic: Quadratic spline interpolation
    - cubic: Cubic spline interpolation
    """

    def __init__(self, method: Literal["linear", "quadratic", "cubic"] = "linear"):
        """Initialize interpolator with specified method.

        Args:
            method: Interpolation method (default: linear)
        """
        self.method = method

    def interpolate(self, x: np.ndarray, y: np.ndarray) -> InterpolationResult:
        """Interpolate missing values (NaN) in time-series data.

        Args:
            x: Independent variable (e.g., years) - must be sorted, no duplicates
            y: Dependent variable (e.g., carbon prices) - may contain NaN

        Returns:
            InterpolationResult with interpolated values and flagged indices

        Raises:
            ValueError: If all values are NaN or insufficient data for interpolation
        """
        # Validate inputs
        if len(x) != len(y):
            raise ValueError(f"x and y must have same length, got {len(x)} and {len(y)}")

        # Find NaN indices (these will be interpolated)
        nan_mask = np.isnan(y)
        interpolated_indices = np.where(nan_mask)[0].tolist()

        # If no NaN values, return original data
        if not any(nan_mask):
            return InterpolationResult(
                interpolated_values=y.copy(),
                interpolated_indices=[],
                method_used=self.method
            )

        # Check if all values are NaN
        if all(nan_mask):
            raise ValueError("Cannot interpolate: all values are missing (NaN)")

        # Get valid (non-NaN) points
        valid_mask = ~nan_mask
        x_valid = x[valid_mask]
        y_valid = y[valid_mask]

        # Handle edge case: only one valid point
        if len(x_valid) == 1:
            # Constant fill: use the single valid value for all points
            interpolated_values = np.full_like(y, y_valid[0])
            return InterpolationResult(
                interpolated_values=interpolated_values,
                interpolated_indices=interpolated_indices,
                method_used="constant (single point)"
            )

        # Handle edge case: insufficient points for quadratic/cubic
        effective_method = self.method
        if self.method == "quadratic" and len(x_valid) < 3:
            effective_method = "linear"
        elif self.method == "cubic" and len(x_valid) < 4:
            effective_method = "quadratic" if len(x_valid) >= 3 else "linear"

        # Create interpolation function
        interp_func = interpolate.interp1d(
            x_valid,
            y_valid,
            kind=effective_method,
            fill_value="extrapolate",  # Allow extrapolation for edge cases
            bounds_error=False
        )

        # Interpolate all points (including valid ones, for consistency)
        interpolated_values = interp_func(x)

        return InterpolationResult(
            interpolated_values=interpolated_values,
            interpolated_indices=interpolated_indices,
            method_used=effective_method
        )
