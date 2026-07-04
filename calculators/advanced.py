"""
New Calculators for V3:
- MLF Tracker
- Cold Stabilization (Würdig formula)
- Sorbate + SO₂ Combo
- Vintage Logbook helpers
- Multi-Vineyard Comparison helpers
"""
import math
from typing import List, Dict


# ─────────────────────────────────────────────────────────────────────────────
# MLF TRACKER
# ─────────────────────────────────────────────────────────────────────────────

def mlf_progress(malic_acid_initial: float, malic_acid_current: float) -> dict:
    """
    Calculate MLF (Malolactic Fermentation) progress.
    
    Malic acid (L-malic) is converted to lactic acid + CO₂.
    Typical starting malic: 1-5 g/L in wine.
    MLF is complete when malic acid < 0.1-0.2 g/L.
    
    Args:
        malic_acid_initial: Initial malic acid concentration in g/L
        malic_acid_current: Current malic acid concentration in g/L
    
    Returns:
        dict with progress percentage, TA reduction, and status
    """
    if malic_acid_initial <= 0:
        return {"error": "Initial malic acid must be > 0"}
    
    completed_pct = round(max(0, min(100, (1 - malic_acid_current / malic_acid_initial) * 100)), 1)
    
    # Each g/L malic converts to 0.67 g/L lactic (MW ratio) + CO₂
    # Net TA reduction: ~0.6 g/L per 1 g/L malic consumed
    malic_consumed = malic_acid_initial - malic_acid_current
    ta_reduction = round(malic_consumed * 0.6, 2)  # g/L TA reduction
    lactic_produced = round(malic_consumed * 0.67, 2)
    
    if malic_acid_current <= 0.15:
        status = "✅ Complete"
    elif malic_acid_current <= 0.5:
        status = "🟡 Nearly Complete"
    elif completed_pct >= 50:
        status = "🟠 In Progress"
    else:
        status = "🔴 Early Stage"
    
    return {
        "progress_pct": completed_pct,
        "malic_consumed_g_l": round(malic_consumed, 2),
        "lactic_produced_g_l": lactic_produced,
        "ta_reduction_g_l": ta_reduction,
        "status": status,
        "complete": malic_acid_current <= 0.15,
    }


def mlf_ta_ph_impact(malic_initial: float, malic_current: float, initial_ph: float, initial_ta: float) -> dict:
    """
    Estimate the impact of MLF on TA and pH.
    
    Args:
        malic_initial: Starting malic acid g/L
        malic_current: Current malic acid g/L
        initial_ph: Wine pH before MLF
        initial_ta: Wine TA before MLF in g/L
    
    Returns:
        dict with estimated new TA and pH
    """
    consumed = malic_initial - malic_current
    ta_drop = consumed * 0.6
    new_ta = round(max(0, initial_ta - ta_drop), 2)
    # pH rises approximately 0.1-0.3 per g/L malic consumed
    ph_rise = consumed * 0.12
    new_ph = round(min(4.5, initial_ph + ph_rise), 2)
    return {
        "estimated_new_ta": new_ta,
        "estimated_new_ph": new_ph,
        "ta_drop": round(ta_drop, 2),
        "ph_rise": round(ph_rise, 2),
    }


# ─────────────────────────────────────────────────────────────────────────────
# COLD STABILIZATION (Würdig Formula)
# ─────────────────────────────────────────────────────────────────────────────

def cold_stabilization(
    alcohol_pct: float,
    ta_g_l: float,
    volume_liters: float
) -> dict:
    """
    Calculate cold stabilization parameters using the Würdig formula.
    
    Cold stabilization precipitates potassium bitartrate (KHT) crystals
    to prevent tartrate deposits in the bottle.
    
    Würdig formula: Stabilization temp (°C) = (Alcohol% / 2) - 1
    
    Args:
        alcohol_pct: Wine alcohol % ABV
        ta_g_l: Titratable acidity g/L
        volume_liters: Volume in liters
    
    Returns:
        dict with stabilization temperature, duration, and energy estimate
    """
    stab_temp = round((alcohol_pct / 2) - 1, 1)
    
    # Duration: typically 8-14 days depending on TA and method
    # Higher TA = longer needed
    if ta_g_l > 8:
        duration_days = 14
    elif ta_g_l > 6:
        duration_days = 10
    else:
        duration_days = 7
    
    # Mini contact method: 3-4 hours with KHT seeds
    kht_seed_g_hl = 4.0  # typical seeding rate
    kht_seed_total = round(kht_seed_g_hl * volume_liters / 100, 1)
    
    # Expected TA reduction after stabilization
    ta_reduction_estimate = round(ta_g_l * 0.05, 2)  # ~5% typical reduction
    
    return {
        "stabilization_temp_c": stab_temp,
        "traditional_duration_days": duration_days,
        "mini_contact_duration_hours": "3-4",
        "kht_seed_g": kht_seed_total,
        "kht_seed_rate": f"{kht_seed_g_hl} g/hL",
        "expected_ta_reduction_g_l": ta_reduction_estimate,
        "note": f"Cool to {stab_temp}°C for {duration_days} days OR use mini-contact method (3-4h with {kht_seed_total}g KHT seeds)"
    }


def conductivity_test(
    before_cooling_ms: float,
    after_cooling_ms: float
) -> dict:
    """
    Evaluate tartrate stability using conductivity test.
    
    Args:
        before_cooling_ms: Conductivity before cold stabilization (mS/cm)
        after_cooling_ms: Conductivity after cold stabilization (mS/cm)
    
    Returns:
        dict with stability verdict
    """
    drop = before_cooling_ms - after_cooling_ms
    drop_pct = round((drop / before_cooling_ms) * 100, 1) if before_cooling_ms > 0 else 0
    
    if drop_pct < 3:
        verdict = "✅ Tartrate Stable"
        action = "Wine is tartrate stable. No further treatment needed."
    elif drop_pct < 5:
        verdict = "🟡 Borderline"
        action = "Consider additional cold stabilization or mini-contact treatment."
    else:
        verdict = "🔴 Unstable"
        action = "Further cold stabilization required. Extend treatment."
    
    return {
        "conductivity_drop_ms": round(drop, 3),
        "conductivity_drop_pct": drop_pct,
        "verdict": verdict,
        "action": action,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SORBATE + SO₂ COMBO (Sweet Wines)
# ─────────────────────────────────────────────────────────────────────────────

def sorbate_so2_combo(
    residual_sugar_g_l: float,
    ph: float,
    volume_liters: float,
    wine_style: str = "sweet"
) -> dict:
    """
    Calculate combined Potassium Sorbate + SO₂ for arresting fermentation.
    
    Sorbate prevents yeast re-fermentation of residual sugars.
    Must always be used WITH adequate SO₂ to prevent geranium off-odor.
    
    EU Legal Limits:
    - Potassium Sorbate: max 200 mg/L as sorbic acid
    - Sorbate active only above ~0.5 mg/L molecular SO₂
    
    Args:
        residual_sugar_g_l: Residual sugar in g/L
        ph: Wine pH
        volume_liters: Volume in liters
        wine_style: 'sweet', 'demi-sec', 'off-dry'
    
    Returns:
        dict with sorbate and SO₂ additions
    """
    # Sorbate rate by style
    rates = {
        "off-dry": 100,    # mg/L sorbic acid
        "demi-sec": 150,
        "sweet": 200,      # EU max
    }
    sorbate_mg_l = rates.get(wine_style, 150)
    
    # Potassium sorbate: 74% sorbic acid
    k_sorbate_mg_l = round(sorbate_mg_l / 0.74, 1)
    k_sorbate_total_g = round(k_sorbate_mg_l * volume_liters / 1000, 2)
    
    # SO₂: need molecular SO₂ > 0.5 mg/L
    target_mol_so2 = 0.6  # slightly above minimum for margin
    free_so2_needed = so2_needed_for_molecular(target_mol_so2, ph)
    so2_amounts = so2_addition_grams(free_so2_needed, volume_liters)
    
    return {
        "sorbic_acid_mg_l": sorbate_mg_l,
        "potassium_sorbate_mg_l": k_sorbate_mg_l,
        "potassium_sorbate_total_g": k_sorbate_total_g,
        "free_so2_needed_mg_l": free_so2_needed,
        "k2s2o5_g": so2_amounts["potassium_metabisulfite_g"],
        "eu_legal_limit": "200 mg/L sorbic acid",
        "warning": "⚠️ Never use sorbate without adequate SO₂ — geranium taint risk!",
        "note": f"Add {k_sorbate_total_g}g K-Sorbate + {so2_amounts['potassium_metabisulfite_g']}g K₂S₂O₅ to {volume_liters}L"
    }


# ─────────────────────────────────────────────────────────────────────────────
# VINEYARD COMPARISON HELPERS
# ─────────────────────────────────────────────────────────────────────────────

WINE_STYLE_TARGETS = {
    "Red": {
        "brix": (22, 26), "ph": (3.3, 3.7), "ta": (5.5, 7.5),
        "yan": (150, 300), "alcohol": (12.5, 15.0),
    },
    "White": {
        "brix": (19, 24), "ph": (3.0, 3.5), "ta": (6.0, 8.5),
        "yan": (120, 250), "alcohol": (11.0, 13.5),
    },
    "Rosé": {
        "brix": (20, 23), "ph": (3.1, 3.6), "ta": (5.5, 7.5),
        "yan": (120, 250), "alcohol": (11.5, 13.5),
    },
    "Sweet": {
        "brix": (26, 35), "ph": (3.0, 3.5), "ta": (6.0, 10.0),
        "yan": (100, 200), "alcohol": (8.0, 13.0),
    },
}


def evaluate_vineyard(
    name: str,
    brix: float,
    ph: float,
    ta: float,
    yan: float,
    style: str = "Red"
) -> dict:
    """
    Score a vineyard/lot against optimal ranges for a given wine style.
    
    Returns a score 0-100 and flags per parameter.
    """
    targets = WINE_STYLE_TARGETS.get(style, WINE_STYLE_TARGETS["Red"])
    flags = {}
    scores = []
    
    params = {
        "brix": (brix, targets["brix"]),
        "ph": (ph, targets["ph"]),
        "ta": (ta, targets["ta"]),
        "yan": (yan, targets["yan"]),
    }
    
    for param, (val, (lo, hi)) in params.items():
        if lo <= val <= hi:
            flags[param] = "✅"
            scores.append(100)
        elif val < lo:
            deficit_pct = (lo - val) / lo * 100
            flags[param] = f"🔻 Low ({val})"
            scores.append(max(0, 100 - deficit_pct * 2))
        else:
            excess_pct = (val - hi) / hi * 100
            flags[param] = f"🔺 High ({val})"
            scores.append(max(0, 100 - excess_pct * 2))
    
    overall = round(sum(scores) / len(scores), 1)
    pa = brix_to_potential_alcohol(brix)
    
    return {
        "name": name,
        "score": overall,
        "brix": brix,
        "ph": ph,
        "ta": ta,
        "yan": yan,
        "potential_alcohol": pa,
        "style": style,
        "flags": flags,
        "grade": "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 50 else "D",
    }


# Import so2_needed_for_molecular from core for sorbate calc
from .core import so2_needed_for_molecular, so2_addition_grams, brix_to_potential_alcohol
