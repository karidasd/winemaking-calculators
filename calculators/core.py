"""
🍷 Winemaking Calculators — Core Library
=========================================
All winemaking formulas in clean, well-documented Python functions.
References: Boulton et al., "Principles and Practices of Winemaking" (2013)
            Zoecklein et al., "Wine Analysis and Production" (1995)
"""

import math


# ─────────────────────────────────────────────────────────────────────────────
# 1. SO2 CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────

def molecular_so2(free_so2: float, ph: float) -> float:
    """
    Calculate the molecular (active) SO2 from free SO2 and pH.
    
    Molecular SO2 is the antimicrobial form. Target: 0.5–0.8 mg/L for red,
    0.8 mg/L for white/rosé wines.
    
    Formula: Molecular SO2 = Free SO2 / (1 + 10^(pH - 1.81))
    
    Args:
        free_so2: Free SO2 in mg/L
        ph: Wine pH
    
    Returns:
        Molecular SO2 in mg/L
    
    Example:
        >>> molecular_so2(30, 3.6)
        0.68
    """
    return round(free_so2 / (1 + 10 ** (ph - 1.81)), 2)


def so2_needed_for_molecular(target_molecular: float, ph: float, current_free_so2: float = 0) -> float:
    """
    Calculate free SO2 needed to achieve a target molecular SO2 level.
    
    Args:
        target_molecular: Target molecular SO2 in mg/L (typically 0.5–0.8)
        ph: Wine pH
        current_free_so2: Current free SO2 in mg/L (default: 0)
    
    Returns:
        SO2 addition needed in mg/L
    """
    required_free = round(target_molecular * (1 + 10 ** (ph - 1.81)), 1)
    addition = max(0, required_free - current_free_so2)
    return addition


def so2_addition_grams(addition_mg_l: float, volume_liters: float, efficiency: float = 1.0) -> dict:
    """
    Calculate grams of SO2 to add from different sources.
    
    Args:
        addition_mg_l: Required SO2 addition in mg/L
        volume_liters: Volume of wine/must in liters
        efficiency: SO2 efficiency (1.0 = 100% for liquid SO2, 0.57 for K2S2O5)
    
    Returns:
        dict with amounts for different SO2 sources
    """
    total_so2_mg = addition_mg_l * volume_liters
    return {
        "liquid_so2_g": round(total_so2_mg / 1000, 2),
        "potassium_metabisulfite_g": round(total_so2_mg / 570, 2),  # K2S2O5: 57% SO2
        "sodium_metabisulfite_g": round(total_so2_mg / 642, 2),     # NaHSO3: 64.2% SO2
        "sulfite_tablets_g": round(total_so2_mg / 570, 2),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. ALCOHOL & SUGAR CALCULATORS
# ─────────────────────────────────────────────────────────────────────────────

def brix_to_potential_alcohol(brix: float) -> float:
    """
    Estimate potential alcohol from Brix (sugar content).
    
    Formula: PA% = Brix × 0.55 (simplified)
    More accurate: PA% = (Brix × 0.5765) - 0.65
    
    Args:
        brix: Sugar content in degrees Brix (°Bx)
    
    Returns:
        Potential alcohol % by volume (ABV)
    
    Example:
        >>> brix_to_potential_alcohol(24)
        13.24
    """
    return round((brix * 0.5765) - 0.65, 2)


def brix_to_sugar(brix: float) -> float:
    """Convert Brix to grams of sugar per liter."""
    return round(brix * 10, 1)


def specific_gravity_to_brix(sg: float) -> float:
    """
    Convert Specific Gravity (SG) to Brix.
    
    Formula: Brix = (SG - 1) × 1000 / 4 (simplified Plato approximation)
    
    Args:
        sg: Specific Gravity (e.g., 1.090)
    
    Returns:
        Degrees Brix
    """
    return round(((182.4601 * sg - 775.6821) * sg + 1262.7794) * sg - 669.5622, 2)


def chaptalization(
    current_brix: float,
    target_brix: float,
    volume_liters: float,
    sugar_type: str = "sucrose"
) -> dict:
    """
    Calculate sugar addition needed to reach target Brix (chaptalization).
    
    Args:
        current_brix: Current must Brix
        target_brix: Desired Brix after sugar addition
        volume_liters: Volume of must in liters
        sugar_type: 'sucrose' or 'glucose_fructose' (rectified grape must)
    
    Returns:
        dict with kg and g of sugar to add
    """
    # 1 kg sucrose in 1L raises ~9°Bx; per liter: grams per liter per degree
    brix_diff = target_brix - current_brix
    if brix_diff <= 0:
        return {"sugar_kg": 0, "sugar_g": 0, "note": "Must is already at or above target Brix."}
    
    # Approximately 17g of sugar per liter raises Brix by 1°
    grams_per_liter = brix_diff * 17.0
    total_grams = grams_per_liter * volume_liters
    return {
        "sugar_kg": round(total_grams / 1000, 3),
        "sugar_g": round(total_grams, 1),
        "note": f"Add {round(total_grams/1000, 3)} kg of {sugar_type} to raise from {current_brix}°Bx to {target_brix}°Bx"
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. ACIDITY CALCULATORS
# ─────────────────────────────────────────────────────────────────────────────

def tartaric_acid_addition(
    current_ta: float,
    target_ta: float,
    volume_liters: float
) -> dict:
    """
    Calculate tartaric acid addition for acidification.
    
    Args:
        current_ta: Current titratable acidity in g/L
        target_ta: Target titratable acidity in g/L
        volume_liters: Volume of must/wine in liters
    
    Returns:
        dict with grams and kg of tartaric acid to add
    """
    ta_diff = target_ta - current_ta
    if ta_diff <= 0:
        return {"g_per_liter": 0, "total_g": 0, "total_kg": 0, "note": "Wine already at or above target TA."}
    
    # 1g/L tartaric acid raises TA by ~0.75 g/L (practical coefficient)
    g_per_liter = round(ta_diff / 0.75, 2)
    total_g = round(g_per_liter * volume_liters, 1)
    return {
        "g_per_liter": g_per_liter,
        "total_g": total_g,
        "total_kg": round(total_g / 1000, 3),
        "note": f"Add {g_per_liter}g/L ({total_g}g total) of tartaric acid"
    }


def deacidification_caco3(
    current_ta: float,
    target_ta: float,
    volume_liters: float
) -> dict:
    """
    Calculate calcium carbonate (CaCO3) needed for deacidification.
    
    Args:
        current_ta: Current titratable acidity in g/L
        target_ta: Target titratable acidity in g/L
        volume_liters: Volume in liters
    
    Returns:
        dict with CaCO3 addition
    """
    reduction = current_ta - target_ta
    if reduction <= 0:
        return {"g_per_liter": 0, "total_g": 0, "note": "TA already at or below target."}
    
    # 1g/L CaCO3 reduces TA by ~1.5 g/L
    g_per_liter = round(reduction / 1.5, 2)
    total_g = round(g_per_liter * volume_liters, 1)
    return {
        "g_per_liter": g_per_liter,
        "total_g": total_g,
        "total_kg": round(total_g / 1000, 3),
        "note": f"Add {g_per_liter}g/L ({total_g}g total) of CaCO3"
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. NUTRIENT & YEAST CALCULATORS
# ─────────────────────────────────────────────────────────────────────────────

def yeast_starter_rehydration(
    volume_liters: float,
    yeast_rate_g_hl: float = 20
) -> dict:
    """
    Calculate yeast and Go-Ferm amounts for rehydration.
    
    Args:
        volume_liters: Volume of must in liters
        yeast_rate_g_hl: Inoculation rate in g/hL (default: 20g/hL)
    
    Returns:
        dict with yeast, Go-Ferm, and water amounts
    """
    volume_hl = volume_liters / 100
    yeast_g = round(yeast_rate_g_hl * volume_hl, 1)
    go_ferm_g = round(yeast_g * 1.25, 1)  # GO-FERM: 1.25x yeast weight
    water_ml = round(yeast_g * 10, 0)     # 10mL per gram of yeast (37-40°C)
    return {
        "yeast_g": yeast_g,
        "go_ferm_g": go_ferm_g,
        "rehydration_water_ml": water_ml,
        "water_temp_c": "37-40°C",
        "note": f"Rehydrate {yeast_g}g yeast in {water_ml}mL water at 37-40°C with {go_ferm_g}g GO-FERM"
    }


def dap_addition(
    current_yan: float,
    target_yan: float,
    volume_liters: float
) -> dict:
    """
    Calculate DAP (Diammonium Phosphate) addition for YAN management.
    
    Args:
        current_yan: Current YAN (Yeast Assimilable Nitrogen) in mg/L
        target_yan: Target YAN in mg/L (typically 150-250 mg/L)
        volume_liters: Volume of must in liters
    
    Returns:
        dict with DAP and Fermaid amounts
    """
    yan_diff = target_yan - current_yan
    if yan_diff <= 0:
        return {"dap_g": 0, "note": "YAN already sufficient."}
    
    # DAP provides 210mg YAN per gram per liter
    dap_g_l = round(yan_diff / 210, 2)
    total_dap_g = round(dap_g_l * volume_liters, 1)
    
    # Fermaid-O alternative (organic) provides 40mg YAN per gram
    fermaid_o_g_l = round(yan_diff / 40, 2)
    total_fermaid_o_g = round(fermaid_o_g_l * volume_liters, 1)
    
    return {
        "dap_g_per_liter": dap_g_l,
        "total_dap_g": total_dap_g,
        "fermaid_o_g_per_liter": fermaid_o_g_l,
        "total_fermaid_o_g": total_fermaid_o_g,
        "note": f"Need {yan_diff}mg/L additional YAN: Add {total_dap_g}g DAP OR {total_fermaid_o_g}g Fermaid-O"
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. BLENDING CALCULATOR (Pearson's Square)
# ─────────────────────────────────────────────────────────────────────────────

def blend_calculator(
    wine_a_value: float,
    wine_a_volume: float,
    wine_b_value: float,
    wine_b_volume: float,
    parameter: str = "alcohol"
) -> dict:
    """
    Calculate the resulting value after blending two wines.
    
    Args:
        wine_a_value: Value of Wine A (alcohol%, Brix, TA, pH etc.)
        wine_a_volume: Volume of Wine A in liters
        wine_b_value: Value of Wine B
        wine_b_volume: Volume of Wine B in liters
        parameter: Name of parameter being calculated
    
    Returns:
        dict with blend result and ratio
    """
    total_volume = wine_a_volume + wine_b_volume
    blend_value = ((wine_a_value * wine_a_volume) + (wine_b_value * wine_b_volume)) / total_volume
    ratio_a = round((wine_a_volume / total_volume) * 100, 1)
    ratio_b = round((wine_b_volume / total_volume) * 100, 1)
    return {
        "blend_value": round(blend_value, 2),
        "total_volume_l": round(total_volume, 1),
        "ratio_a_pct": ratio_a,
        "ratio_b_pct": ratio_b,
        "parameter": parameter,
        "note": f"Blend of {ratio_a}% Wine A + {ratio_b}% Wine B → {parameter}: {round(blend_value, 2)}"
    }


def pearson_square(
    target_value: float,
    wine_a_value: float,
    wine_b_value: float,
    total_volume: float
) -> dict:
    """
    Use Pearson's Square to find the ratio needed to hit a target value.
    
    Args:
        target_value: Desired value in the final blend
        wine_a_value: Value of Wine A
        wine_b_value: Value of Wine B
        total_volume: Total desired volume in liters
    
    Returns:
        dict with volumes of each wine to use
    """
    if wine_a_value == wine_b_value:
        return {"error": "Both wines have the same value — cannot calculate blend ratio."}
    
    parts_a = abs(wine_b_value - target_value)
    parts_b = abs(wine_a_value - target_value)
    total_parts = parts_a + parts_b
    
    vol_a = round((parts_a / total_parts) * total_volume, 1)
    vol_b = round((parts_b / total_parts) * total_volume, 1)
    
    return {
        "wine_a_liters": vol_a,
        "wine_b_liters": vol_b,
        "wine_a_pct": round((vol_a / total_volume) * 100, 1),
        "wine_b_pct": round((vol_b / total_volume) * 100, 1),
        "total_volume_l": total_volume,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. FINING AGENTS CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────

FINING_AGENTS = {
    "bentonite": {"unit": "g/hL", "typical_range": (50, 150), "purpose": "Protein stability, heat stability"},
    "egg_white": {"unit": "whites/barrel (225L)", "typical_range": (1, 6), "purpose": "Tannin reduction, softening"},
    "activated_carbon": {"unit": "g/hL", "typical_range": (10, 50), "purpose": "Color/aroma correction"},
    "gelatine": {"unit": "g/hL", "typical_range": (3, 10), "purpose": "Tannin reduction, clarification"},
    "isinglass": {"unit": "g/hL", "typical_range": (2, 5), "purpose": "Clarification, fine lees removal"},
    "potassium_caseinate": {"unit": "g/hL", "typical_range": (25, 100), "purpose": "Oxidation treatment, color stability"},
}


def fining_addition(
    agent: str,
    rate_per_hl: float,
    volume_liters: float
) -> dict:
    """
    Calculate fining agent addition for a given tank volume.
    
    Args:
        agent: Name of fining agent (see FINING_AGENTS for options)
        rate_per_hl: Application rate per hectoliter
        volume_liters: Volume of wine in liters
    
    Returns:
        dict with total amount to add
    """
    volume_hl = volume_liters / 100
    total = round(rate_per_hl * volume_hl, 2)
    agent_info = FINING_AGENTS.get(agent, {})
    return {
        "agent": agent,
        "rate": f"{rate_per_hl} {agent_info.get('unit', 'g/hL')}",
        "total_amount": total,
        "unit": agent_info.get("unit", "g"),
        "purpose": agent_info.get("purpose", ""),
        "typical_range": agent_info.get("typical_range", ()),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 7. DISSOLVED CO2 CALCULATOR
# ─────────────────────────────────────────────────────────────────────────────

def dissolved_co2(temperature_c: float, wine_type: str = "still") -> dict:
    """
    Estimate dissolved CO2 at a given temperature (Henry's Law).
    
    Args:
        temperature_c: Wine temperature in Celsius
        wine_type: 'still', 'sparkling', or 'frizzante'
    
    Returns:
        dict with dissolved CO2 levels and recommendations
    """
    targets = {
        "still": (0.2, 0.6),
        "frizzante": (1.0, 2.5),
        "sparkling": (3.5, 6.5),
    }
    # Henry's constant for CO2 (approximate, g/L/atm)
    henry_k = round(0.76 * math.exp(-0.0267 * temperature_c), 3)
    target_range = targets.get(wine_type, (0.2, 0.6))
    return {
        "temperature_c": temperature_c,
        "henry_constant": henry_k,
        "target_range_g_l": target_range,
        "wine_type": wine_type,
        "note": f"At {temperature_c}°C, target CO2 for {wine_type}: {target_range[0]}–{target_range[1]} g/L"
    }


# ─────────────────────────────────────────────────────────────────────────────
# 8. COPPER FINING (H2S TREATMENT)
# ─────────────────────────────────────────────────────────────────────────────

def copper_sulfate_addition(
    h2s_intensity: str,  # 'light', 'medium', 'strong'
    volume_liters: float
) -> dict:
    """
    Calculate copper sulfate addition to treat hydrogen sulfide (H2S).
    
    Args:
        h2s_intensity: Intensity of H2S smell ('light', 'medium', 'strong')
        volume_liters: Volume of wine in liters
    
    Returns:
        dict with copper sulfate addition (max legal limit: 1mg/L Cu in EU)
    """
    rates = {"light": 0.2, "medium": 0.5, "strong": 1.0}
    rate_mg_l = rates.get(h2s_intensity, 0.5)
    total_mg = rate_mg_l * volume_liters
    # CuSO4·5H2O: 25.5% Cu
    cuso4_5h2o_mg = total_mg / 0.255
    return {
        "copper_mg_l": rate_mg_l,
        "total_copper_mg": round(total_mg, 1),
        "cuso4_5h2o_mg": round(cuso4_5h2o_mg, 1),
        "cuso4_5h2o_g": round(cuso4_5h2o_mg / 1000, 4),
        "legal_limit_note": "EU legal limit: max 1mg/L copper in final wine",
        "note": f"Add {round(cuso4_5h2o_mg, 1)}mg CuSO4·5H2O ({rate_mg_l}mg/L Cu) for {h2s_intensity} H2S treatment"
    }
