"""Winemaking Calculators Package"""
from .core import (
    molecular_so2, so2_needed_for_molecular, so2_addition_grams,
    brix_to_potential_alcohol, brix_to_sugar, specific_gravity_to_brix,
    chaptalization, tartaric_acid_addition, deacidification_caco3,
    yeast_starter_rehydration, dap_addition,
    blend_calculator, pearson_square,
    fining_addition, FINING_AGENTS,
    dissolved_co2, copper_sulfate_addition,
)
from .advanced import (
    mlf_progress, mlf_ta_ph_impact,
    cold_stabilization, conductivity_test,
    sorbate_so2_combo,
    evaluate_vineyard, WINE_STYLE_TARGETS,
)
from .ultimate import (
    GREEK_VARIETIES,
    bottles_needed,
    thermal_expansion,
    oak_dosage,
    diagnose_fault,
    WINE_FAULTS,
)
__version__ = "4.0.0"
