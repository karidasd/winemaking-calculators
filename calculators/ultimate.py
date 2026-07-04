"""
Ultimate Oenology Calculators for V4:
- Bottling Suite (Bottles/Cases needed, Thermal Expansion & Fill Levels)
- Oak & Tannin Dosage Calculator
- Rule-based Wine Fault Diagnosis Engine
- Greek Grape Varieties Database & Benchmarking
- Multi-vintage comparison helper data
"""

# Greek Varieties Database
GREEK_VARIETIES = {
    "Xinomavro": {
        "style": "Red",
        "description": "The king of Macedonian reds. High acidity, rich tannins, complex aromas of tomato, olive paste, and red fruits.",
        "optimal_brix": (22.5, 24.5),
        "optimal_ph": (3.15, 3.35),
        "optimal_ta": (6.5, 8.0),
        "optimal_yan": (180, 250),
        "target_molecular_so2": 0.5,
    },
    "Assyrtiko": {
        "style": "White",
        "description": "Santorini's iconic white. High acidity, low pH, high alcohol potential, and intense mineral/saline character.",
        "optimal_brix": (21.5, 23.5),
        "optimal_ph": (2.90, 3.10),
        "optimal_ta": (7.0, 9.0),
        "optimal_yan": (140, 200),
        "target_molecular_so2": 0.8,
    },
    "Agiorgitiko": {
        "style": "Red",
        "description": "Nemea's versatile red grape. Velvet tannins, moderate acidity, and deep red fruit aromas.",
        "optimal_brix": (23.0, 25.0),
        "optimal_ph": (3.40, 3.60),
        "optimal_ta": (5.0, 6.5),
        "optimal_yan": (160, 220),
        "target_molecular_so2": 0.5,
    },
    "Moschofilero": {
        "style": "Rosé/Blanc de Noirs",
        "description": "Mantineia's aromatic pink grape. Crisp acidity, low alcohol, and intense rose petal and citrus blossom aromas.",
        "optimal_brix": (19.5, 21.5),
        "optimal_ph": (3.00, 3.20),
        "optimal_ta": (6.5, 8.0),
        "optimal_yan": (150, 210),
        "target_molecular_so2": 0.8,
    },
    "Malagousia": {
        "style": "White",
        "description": "The rescued aromatic grape of Greece. Medium acidity, full body, intense aromas of peach, lime, and jasmine.",
        "optimal_brix": (21.0, 23.0),
        "optimal_ph": (3.20, 3.40),
        "optimal_ta": (5.5, 6.8),
        "optimal_yan": (150, 220),
        "target_molecular_so2": 0.8,
    },
    "Vidiano": {
        "style": "White",
        "description": "Crete's rising star. Creamy texture, medium-to-high acidity, apricot and mineral notes. Often oak-aged.",
        "optimal_brix": (22.0, 23.8),
        "optimal_ph": (3.15, 3.30),
        "optimal_ta": (6.0, 7.5),
        "optimal_yan": (140, 200),
        "target_molecular_so2": 0.8,
    },
    "Mavrotragano": {
        "style": "Red",
        "description": "Rare Cycladic red. Extremely dark color, dense tannins, high acidity, and complex dark forest fruit and mineral aromas.",
        "optimal_brix": (23.5, 25.5),
        "optimal_ph": (3.25, 3.45),
        "optimal_ta": (6.0, 7.5),
        "optimal_yan": (160, 230),
        "target_molecular_so2": 0.5,
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# 1. BOTTLING CALCULATOR SUITE
# ─────────────────────────────────────────────────────────────────────────────

def bottles_needed(volume_liters: float, bottle_size_ml: float = 750.0, loss_pct: float = 2.0) -> dict:
    """
    Calculate the number of bottles and cases needed, accounting for transfer/filtration losses.
    
    Args:
        volume_liters: Total bulk wine volume in liters.
        bottle_size_ml: Size of individual bottle in mL (default: 750).
        loss_pct: Expected loss percentage during bottling (default: 2.0%).
        
    Returns:
        dict with bottle count, cases, and exact volume losses.
    """
    net_volume = volume_liters * (1.0 - (loss_pct / 100.0))
    loss_volume = volume_liters - net_volume
    
    total_bottles = int(math.floor((net_volume * 1000.0) / bottle_size_ml))
    
    cases_of_12 = int(math.floor(total_bottles / 12))
    rem_bottles_12 = total_bottles % 12
    
    cases_of_6 = int(math.floor(total_bottles / 6))
    rem_bottles_6 = total_bottles % 6
    
    return {
        "original_volume_l": round(volume_liters, 1),
        "net_bottling_volume_l": round(net_volume, 1),
        "lost_volume_l": round(loss_volume, 2),
        "total_bottles": total_bottles,
        "cases_of_12": cases_of_12,
        "remaining_bottles_12": rem_bottles_12,
        "cases_of_6": cases_of_6,
        "remaining_bottles_6": rem_bottles_6,
    }


def thermal_expansion(volume_liters: float, bottling_temp_c: float, storage_temp_c: float) -> dict:
    """
    Calculate the thermal expansion or contraction of wine.
    Wine has an average coefficient of volumetric expansion (beta) of 0.0003 per °C
    (based on water-ethanol mixture).
    
    Args:
        volume_liters: Bottling volume in liters.
        bottling_temp_c: Temperature at bottling (°C).
        storage_temp_c: Maximum expected storage or transit temperature (°C).
        
    Returns:
        dict containing volume change and headspace advice.
    """
    # beta coefficient for wine (mostly water + ~12-15% alcohol)
    beta = 0.0003
    temp_diff = storage_temp_c - bottling_temp_c
    volume_change_l = volume_liters * beta * temp_diff
    
    # Per bottle calculation (assuming standard 750ml bottle)
    per_bottle_change_ml = 750.0 * beta * temp_diff
    
    is_expansion = temp_diff > 0
    
    if is_expansion and per_bottle_change_ml > 8.0:
        warning = f"⚠️ High risk of cork push! Headspace will contract by {round(per_bottle_change_ml, 1)} mL. Ensure vacuum corking or increase headspace."
    elif is_expansion:
        warning = f"Notice: Wine will expand by {round(per_bottle_change_ml, 1)} mL per bottle. Normal headspace is 10-15 mL."
    else:
        warning = f"Wine will contract by {round(abs(per_bottle_change_ml), 1)} mL per bottle. Risk of oxidation if headspace is too large."
        
    return {
        "volume_change_l": round(volume_change_l, 2),
        "per_bottle_change_ml": round(per_bottle_change_ml, 2),
        "temp_diff_c": temp_diff,
        "is_expansion": is_expansion,
        "warning": warning,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 2. OAK & TANNIN DOSAGE
# ─────────────────────────────────────────────────────────────────────────────

def oak_dosage(volume_liters: float, dosage_g_l: float, format_type: str = "chips") -> dict:
    """
    Calculate oak alternative additions (chips, staves, cubes).
    
    Rates:
        - Chips: 1 - 4 g/L (Extraction: 1 - 3 months)
        - Cubes/Blocks: 2 - 6 g/L (Extraction: 3 - 6 months)
        - Staves: 1 stave per 100 - 200 L (Extraction: 6 - 12 months)
    """
    total_g = dosage_g_l * volume_liters
    total_kg = total_g / 1000.0
    
    times = {
        "chips": "1 - 3 months",
        "cubes": "3 - 6 months",
        "staves": "6 - 12 months",
    }
    
    notes = {
        "chips": "Fast extraction, high impact, short lifespan.",
        "cubes": "Moderate-to-slow extraction, good structural integration, mimics barrel aging.",
        "staves": "Slowest extraction, best oak integration, long-term aging.",
    }
    
    result = {
        "total_grams": round(total_g, 1),
        "total_kg": round(total_kg, 3),
        "extraction_time": times.get(format_type, "N/A"),
        "note": notes.get(format_type, ""),
    }
    
    if format_type == "staves":
        # Average stave weighs ~250g
        staves_needed = round(total_g / 250.0, 1)
        result["staves_needed"] = staves_needed
        
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 3. WINE FAULT DIAGNOSIS ENGINE
# ─────────────────────────────────────────────────────────────────────────────

WINE_FAULTS = [
    {
        "id": "volatile_acidity",
        "name": "Volatile Acidity (VA) / Vinegar Taint",
        "symptoms": ["vinegar", "nail polish remover", "acetone", "sour smell"],
        "cause": "Acetobacter or wild yeast converting ethanol to acetic acid & ethyl acetate, usually due to oxygen exposure.",
        "prevention": "Maintain free SO₂ levels (>0.5 mg/L molecular), minimize headspace/oxygen exposure, cool cellar temperatures.",
        "treatment": "Sterile filtration, blending with low-VA wine, or Reverse Osmosis (RO) filtration (commercial)."
    },
    {
        "id": "h2s",
        "name": "Hydrogen Sulfide (H2S) / Reduction",
        "symptoms": ["rotten eggs", "sewer", "cabbage", "burnt rubber", "garlic"],
        "cause": "Yeast stress due to nitrogen deficiency (low YAN), high fermentation temperatures, or contact with sulfur residues.",
        "prevention": "Ensure adequate YAN (>150 mg/L) at inoculation, control fermentation temperatures, rack off heavy lees.",
        "treatment": "Aeration (if early), addition of copper sulfate (CuSO₄·5H₂O) up to legal limit, or yeast hull addition."
    },
    {
        "id": "brett",
        "name": "Brettanomyces (Brett) Taint",
        "symptoms": ["band-aid", "horse blanket", "barnyard", "medicine", "leather", "sweaty saddle"],
        "cause": "Contamination by Brettanomyces yeast, which metabolizes cinnamic acids into volatile phenols (4-EP, 4-EG).",
        "prevention": "Strict hygiene, keep pH low (<3.5), maintain proper molecular SO₂ (>0.5 mg/L), avoid warm storage.",
        "treatment": "Sterile filtration (0.45 micron), Chitosan addition, or blending. Cannot be easily removed once strong."
    },
    {
        "id": "cork_taint",
        "name": "Cork Taint (TCA)",
        "symptoms": ["musty", "cardboard", "wet dog", "corked", "flat fruit"],
        "cause": "2,4,6-Trichloroanisole (TCA) produced by mold reacting with chlorophenols in corks or winery wood structures.",
        "prevention": "Purchase batch-tested corks, avoid chlorine-based winery cleaners, check wood structures.",
        "treatment": "Practically impossible to remove cleanly. Food-grade plastic wrap (polyethylene) contact is a controversial cellar trick."
    },
    {
        "id": "oxidation",
        "name": "Oxidation / Acetaldehyde",
        "symptoms": ["sherry", "bruised apple", "flat taste", "brown color", "nutty"],
        "cause": "Excessive exposure to oxygen causing oxidation of phenols and formation of acetaldehyde.",
        "prevention": "Inert gas cover (nitrogen/argon), keep vessels full, maintain correct free SO₂ during aging.",
        "treatment": "Ascorbic acid / SO₂ additions, fining with PVPP or casein to remove oxidized color/phenols, blending."
    }
]

def diagnose_fault(symptoms: list) -> list:
    """
    Diagnose potential wine faults based on observed symptoms.
    
    Args:
        symptoms: List of symptom keywords matching WINE_FAULTS criteria.
        
    Returns:
        List of matching faults with match confidence score.
    """
    matches = []
    if not symptoms:
        return []
        
    symptoms_set = set([s.lower() for s in symptoms])
    
    for fault in WINE_FAULTS:
        fault_syms = set(fault["symptoms"])
        common = symptoms_set.intersection(fault_syms)
        if common:
            confidence = round((len(common) / len(symptoms_set)) * 100, 1)
            matches.append({
                "name": fault["name"],
                "confidence": confidence,
                "common_symptoms": list(common),
                "cause": fault["cause"],
                "prevention": fault["prevention"],
                "treatment": fault["treatment"],
            })
            
    # Sort by confidence
    matches.sort(key=lambda x: x["confidence"], reverse=True)
    return matches
