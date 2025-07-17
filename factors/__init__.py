"""
Factors package for CFB Contrarian Predictor.
Contains all factor calculators and the factor registry.
"""

from factors.base_calculator import BaseFactorCalculator
from factors.factor_registry import factor_registry

__all__ = ['BaseFactorCalculator', 'factor_registry']