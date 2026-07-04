"""Winemaking Calculators Package"""
from .core import (
    molecular_so2,
    so2_needed_for_molecular,
    so2_addition_grams,
    brix_to_potential_alcohol,
    brix_to_sugar,
    specific_gravity_to_brix,
    chaptalization,
    tartaric_acid_addition,
    deacidification_caco3,
    yeast_starter_rehydration,
    dap_addition,
    blend_calculator,
    pearson_square,
    fining_addition,
    dissolved_co2,
    copper_sulfate_addition,
    FINING_AGENTS,
)
__version__ = "1.0.0"
__all__ = [
    "molecular_so2", "so2_needed_for_molecular", "so2_addition_grams",
    "brix_to_potential_alcohol", "brix_to_sugar", "specific_gravity_to_brix",
    "chaptalization", "tartaric_acid_addition", "deacidification_caco3",
    "yeast_starter_rehydration", "dap_addition",
    "blend_calculator", "pearson_square",
    "fining_addition", "FINING_AGENTS",
    "dissolved_co2", "copper_sulfate_addition",
]
