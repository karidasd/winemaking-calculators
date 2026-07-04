import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculators import *

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🍷 Winemaking Calculators",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Built with ❤️ by DarkAIs | karidasd"}
)

# ─── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');

  .stApp { background: linear-gradient(135deg, #0a0608 0%, #1a0a10 50%, #0d0d14 100%); color: #e8d5b7; }
  h1, h2, h3 { font-family: 'Playfair Display', serif !important; }
  p, div, label, span { font-family: 'Inter', sans-serif !important; }

  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a0a10 0%, #0d0d14 100%);
    border-right: 1px solid #3d1a26;
  }

  .hero {
    background: linear-gradient(135deg, rgba(120,30,50,0.4) 0%, rgba(30,20,60,0.4) 100%);
    border: 1px solid rgba(180,100,80,0.3);
    border-radius: 16px;
    padding: 32px;
    text-align: center;
    margin-bottom: 32px;
    backdrop-filter: blur(10px);
  }
  .hero h1 { color: #c9956a !important; font-size: 2.6rem; margin-bottom: 8px; text-shadow: 0 0 30px rgba(180,100,80,0.5); }
  .hero p { color: #b0926a; font-size: 1.1rem; }

  .result-card {
    background: linear-gradient(135deg, rgba(80,20,35,0.5) 0%, rgba(20,15,40,0.5) 100%);
    border: 1px solid rgba(180,100,80,0.4);
    border-radius: 12px;
    padding: 20px 24px;
    margin-top: 20px;
  }
  .result-card h3 { color: #c9956a !important; font-size: 1rem; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }
  .metric-row { display: flex; align-items: baseline; gap: 8px; margin: 8px 0; }
  .metric-value { color: #e8c89a; font-size: 2rem; font-weight: 700; font-family: 'Playfair Display', serif; }
  .metric-unit { color: #8a7060; font-size: 0.9rem; }
  .metric-label { color: #a08060; font-size: 0.85rem; margin-left: auto; }

  .info-box {
    background: rgba(30, 60, 40, 0.3);
    border-left: 3px solid #4a9960;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-top: 16px;
    color: #90c090;
    font-size: 0.88rem;
  }
  .warning-box {
    background: rgba(80, 50, 20, 0.3);
    border-left: 3px solid #c09030;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-top: 16px;
    color: #c0a060;
    font-size: 0.88rem;
  }

  .stButton > button {
    background: linear-gradient(135deg, #7b1f35 0%, #3d1a60 100%);
    color: #e8d5b7;
    border: 1px solid rgba(180,100,80,0.5);
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    padding: 0.6rem 2rem;
    transition: all 0.3s ease;
    width: 100%;
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, #9b2f45 0%, #5d2a80 100%);
    border-color: #c9956a;
    box-shadow: 0 0 20px rgba(180,100,80,0.3);
    transform: translateY(-1px);
  }

  .stSelectbox > div > div { background: rgba(30,15,25,0.8) !important; border-color: rgba(180,100,80,0.3) !important; }
  .stNumberInput > div > div > input { background: rgba(30,15,25,0.8) !important; border-color: rgba(180,100,80,0.3) !important; color: #e8d5b7 !important; }
  .stSlider > div > div > div { background: rgba(180,100,80,0.3) !important; }

  [data-testid="stMetricValue"] { color: #c9956a !important; font-family: 'Playfair Display', serif !important; }
  [data-testid="stMetricLabel"] { color: #8a7060 !important; }
  .stTabs [data-baseweb="tab"] { color: #b0926a; font-family: 'Inter', sans-serif; }
  .stTabs [aria-selected="true"] { color: #c9956a !important; border-bottom-color: #c9956a !important; }

  .divider { border: none; border-top: 1px solid rgba(180,100,80,0.2); margin: 24px 0; }
  footer { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🍷 Winemaking Calculators</h1>
  <p>Professional tools for oenologists & winemakers — Science behind every bottle</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍇 Navigation")
    calculator = st.radio(
        "Choose Calculator",
        [
            "🧪 SO₂ Manager",
            "🍬 Sugar & Alcohol",
            "🧊 Acidity Adjustment",
            "🌱 Yeast & Nutrients",
            "🔀 Blending Tool",
            "🧹 Fining Agents",
            "🫧 Dissolved CO₂",
            "🟤 H₂S Treatment",
        ],
        label_visibility="collapsed"
    )
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color: #6a5040; font-size: 0.8rem; padding: 8px;'>
    📚 <strong style='color:#a08060'>References:</strong><br>
    Boulton et al. (2013)<br>
    Zoecklein et al. (1995)<br>
    OIV International Standards
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. SO₂ MANAGER
# ─────────────────────────────────────────────────────────────────────────────
if calculator == "🧪 SO₂ Manager":
    st.markdown("## 🧪 SO₂ Manager")
    st.markdown("*Calculate molecular SO₂ and the additions needed to protect your wine.*")
    
    tab1, tab2 = st.tabs(["📊 Current SO₂ Status", "➕ SO₂ Addition Calculator"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1: free_so2 = st.number_input("Free SO₂ (mg/L)", min_value=0.0, max_value=200.0, value=25.0, step=1.0)
        with c2: ph = st.number_input("Wine pH", min_value=2.8, max_value=4.5, value=3.5, step=0.05)
        with c3: wine_style = st.selectbox("Wine Style", ["Red", "White/Rosé", "Sweet"])

        mol_so2 = molecular_so2(free_so2, ph)
        targets = {"Red": 0.5, "White/Rosé": 0.8, "Sweet": 0.8}
        target = targets[wine_style]

        st.markdown(f"""
        <div class="result-card">
          <h3>📊 Result</h3>
          <div class="metric-row">
            <span class="metric-value">{mol_so2}</span>
            <span class="metric-unit">mg/L</span>
            <span class="metric-label">Molecular SO₂</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if mol_so2 >= target:
            st.success(f"✅ Molecular SO₂ is adequate (target: ≥{target} mg/L for {wine_style})")
        else:
            deficit = round(target - mol_so2, 2)
            needed = so2_needed_for_molecular(target, ph, free_so2)
            st.warning(f"⚠️ Molecular SO₂ is LOW by {deficit} mg/L — add {needed} mg/L free SO₂")

        col1, col2, col3 = st.columns(3)
        col1.metric("Molecular SO₂", f"{mol_so2} mg/L")
        col2.metric("Target", f"{target} mg/L")
        col3.metric("Wine pH", f"{ph}")

    with tab2:
        c1, c2, c3 = st.columns(3)
        with c1: target_mol = st.number_input("Target Molecular SO₂ (mg/L)", min_value=0.1, max_value=2.0, value=0.5, step=0.1)
        with c2: ph2 = st.number_input("Wine pH", min_value=2.8, max_value=4.5, value=3.5, step=0.05, key="ph2")
        with c3: current_free = st.number_input("Current Free SO₂ (mg/L)", min_value=0.0, max_value=200.0, value=10.0, step=1.0)
        volume = st.number_input("Tank Volume (Liters)", min_value=1.0, max_value=500000.0, value=1000.0, step=100.0)

        addition = so2_needed_for_molecular(target_mol, ph2, current_free)
        amounts = so2_addition_grams(addition, volume)

        st.markdown(f"""<div class="result-card"><h3>📦 Addition Required: +{addition} mg/L Free SO₂</h3></div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Liquid SO₂", f"{amounts['liquid_so2_g']} g")
        c2.metric("K₂S₂O₅ (Metabisulfite)", f"{amounts['potassium_metabisulfite_g']} g")
        c3.metric("NaHSO₃", f"{amounts['sodium_metabisulfite_g']} g")


# ─────────────────────────────────────────────────────────────────────────────
# 2. SUGAR & ALCOHOL
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == "🍬 Sugar & Alcohol":
    st.markdown("## 🍬 Sugar & Alcohol")
    tab1, tab2, tab3 = st.tabs(["🔢 Brix Conversions", "🍚 Chaptalization", "⚖️ SG to Brix"])

    with tab1:
        brix_val = st.slider("Brix (°Bx)", min_value=14.0, max_value=32.0, value=24.0, step=0.5)
        pa = brix_to_potential_alcohol(brix_val)
        sugar_gl = brix_to_sugar(brix_val)
        c1, c2, c3 = st.columns(3)
        c1.metric("Potential Alcohol", f"{pa}% ABV")
        c2.metric("Sugar Content", f"{sugar_gl} g/L")
        c3.metric("Brix", f"{brix_val}°Bx")
        st.markdown(f"""
        <div class="info-box">
          At <strong>{brix_val}°Bx</strong>, the must contains approximately <strong>{sugar_gl}g/L</strong> of sugar,
          which will ferment to approximately <strong>{pa}% ABV</strong>.
        </div>""", unsafe_allow_html=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            current_brix = st.number_input("Current Brix (°Bx)", 14.0, 30.0, 20.0, 0.5)
            target_brix = st.number_input("Target Brix (°Bx)", 14.0, 32.0, 24.0, 0.5)
        with c2:
            vol = st.number_input("Must Volume (L)", 1.0, 500000.0, 1000.0, 100.0)
            sugar_type = st.selectbox("Sugar Type", ["sucrose", "glucose_fructose"])
        result = chaptalization(current_brix, target_brix, vol, sugar_type)
        if result["sugar_kg"] > 0:
            c1, c2 = st.columns(2)
            c1.metric("Sugar to Add", f"{result['sugar_kg']} kg")
            c2.metric("In Grams", f"{result['sugar_g']} g")
            st.markdown(f'<div class="info-box">💡 {result["note"]}</div>', unsafe_allow_html=True)
        else:
            st.success("✅ Must is already at or above target Brix.")

    with tab3:
        sg = st.number_input("Specific Gravity", 1.000, 1.140, 1.090, 0.001, format="%.3f")
        brix_from_sg = specific_gravity_to_brix(sg)
        pa_from_sg = brix_to_potential_alcohol(brix_from_sg)
        c1, c2, c3 = st.columns(3)
        c1.metric("Brix", f"{brix_from_sg}°Bx")
        c2.metric("Potential Alcohol", f"{pa_from_sg}% ABV")
        c3.metric("Sugar", f"{brix_to_sugar(brix_from_sg)} g/L")


# ─────────────────────────────────────────────────────────────────────────────
# 3. ACIDITY ADJUSTMENT
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == "🧊 Acidity Adjustment":
    st.markdown("## 🧊 Acidity Adjustment")
    tab1, tab2 = st.tabs(["🔺 Acidification (Tartaric Acid)", "🔻 Deacidification (CaCO₃)"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1: curr_ta = st.number_input("Current TA (g/L)", 3.0, 12.0, 5.5, 0.1)
        with c2: tgt_ta = st.number_input("Target TA (g/L)", 3.0, 12.0, 7.0, 0.1)
        with c3: vol_acid = st.number_input("Volume (L)", 1.0, 500000.0, 1000.0, 100.0)
        result = tartaric_acid_addition(curr_ta, tgt_ta, vol_acid)
        if result["total_g"] > 0:
            c1, c2 = st.columns(2)
            c1.metric("Addition Rate", f"{result['g_per_liter']} g/L")
            c2.metric("Total Tartaric Acid", f"{result['total_kg']} kg")
            st.markdown(f'<div class="info-box">💡 {result["note"]}</div>', unsafe_allow_html=True)
        else:
            st.success("✅ Wine is already at or above target TA.")

    with tab2:
        c1, c2, c3 = st.columns(3)
        with c1: curr_ta2 = st.number_input("Current TA (g/L)", 3.0, 15.0, 9.0, 0.1, key="ta2")
        with c2: tgt_ta2 = st.number_input("Target TA (g/L)", 3.0, 12.0, 6.5, 0.1, key="tgt_ta2")
        with c3: vol_deacid = st.number_input("Volume (L)", 1.0, 500000.0, 1000.0, 100.0, key="vol_deacid")
        result2 = deacidification_caco3(curr_ta2, tgt_ta2, vol_deacid)
        if result2["total_g"] > 0:
            c1, c2 = st.columns(2)
            c1.metric("CaCO₃ Rate", f"{result2['g_per_liter']} g/L")
            c2.metric("Total CaCO₃", f"{result2['total_kg']} kg")
            st.markdown(f'<div class="info-box">💡 {result2["note"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="warning-box">⚠️ Add CaCO₃ slowly and mix thoroughly. Check TA after treatment.</div>', unsafe_allow_html=True)
        else:
            st.success("✅ TA already at or below target.")


# ─────────────────────────────────────────────────────────────────────────────
# 4. YEAST & NUTRIENTS
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == "🌱 Yeast & Nutrients":
    st.markdown("## 🌱 Yeast & Nutrients")
    tab1, tab2 = st.tabs(["🧫 Yeast Rehydration", "🌾 DAP / Nitrogen (YAN)"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1: vol_yeast = st.number_input("Must Volume (L)", 1.0, 500000.0, 1000.0, 100.0)
        with c2: yeast_rate = st.number_input("Inoculation Rate (g/hL)", 10.0, 40.0, 20.0, 1.0)
        result = yeast_starter_rehydration(vol_yeast, yeast_rate)
        c1, c2, c3 = st.columns(3)
        c1.metric("Yeast", f"{result['yeast_g']} g")
        c2.metric("GO-FERM", f"{result['go_ferm_g']} g")
        c3.metric("Water (37-40°C)", f"{result['rehydration_water_ml']} mL")
        st.markdown(f'<div class="info-box">💡 {result["note"]}</div>', unsafe_allow_html=True)

    with tab2:
        c1, c2, c3 = st.columns(3)
        with c1: curr_yan = st.number_input("Current YAN (mg/L)", 0.0, 400.0, 80.0, 10.0)
        with c2: tgt_yan = st.number_input("Target YAN (mg/L)", 100.0, 400.0, 200.0, 10.0)
        with c3: vol_yan = st.number_input("Volume (L)", 1.0, 500000.0, 1000.0, 100.0)
        result = dap_addition(curr_yan, tgt_yan, vol_yan)
        if result["total_dap_g"] > 0:
            c1, c2 = st.columns(2)
            c1.metric("DAP Total", f"{result['total_dap_g']} g")
            c2.metric("Fermaid-O Alternative", f"{result['total_fermaid_o_g']} g")
            st.markdown(f'<div class="info-box">💡 {result["note"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="warning-box">⚠️ Add nutrients in multiple additions: 1/3 at inoculation, 1/3 at 1/3 depletion, 1/3 at 2/3 depletion.</div>', unsafe_allow_html=True)
        else:
            st.success("✅ YAN is sufficient for healthy fermentation.")


# ─────────────────────────────────────────────────────────────────────────────
# 5. BLENDING TOOL
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == "🔀 Blending Tool":
    st.markdown("## 🔀 Blending Tool")
    tab1, tab2 = st.tabs(["🧮 Blend Result Calculator", "🎯 Pearson's Square (Target Blend)"])

    with tab1:
        parameter = st.selectbox("Parameter to Calculate", ["alcohol", "brix", "ta", "ph", "residual_sugar"])
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Wine A**")
            val_a = st.number_input(f"Wine A — {parameter}", value=14.0, step=0.1, key="val_a")
            vol_a = st.number_input("Wine A Volume (L)", value=500.0, step=50.0, key="vol_a")
        with c2:
            st.markdown("**Wine B**")
            val_b = st.number_input(f"Wine B — {parameter}", value=12.0, step=0.1, key="val_b")
            vol_b = st.number_input("Wine B Volume (L)", value=500.0, step=50.0, key="vol_b")
        result = blend_calculator(val_a, vol_a, val_b, vol_b, parameter)
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Blend {parameter}", f"{result['blend_value']}")
        c2.metric("Total Volume", f"{result['total_volume_l']} L")
        c3.metric("Ratio A:B", f"{result['ratio_a_pct']}% : {result['ratio_b_pct']}%")

    with tab2:
        st.markdown("*Enter target value — Pearson's Square will calculate exact volumes needed.*")
        c1, c2, c3 = st.columns(3)
        with c1: tgt_val = st.number_input("Target Value", value=13.0, step=0.1)
        with c2: wine_a_val = st.number_input("Wine A Value", value=15.0, step=0.1, key="pa_a")
        with c3: wine_b_val = st.number_input("Wine B Value", value=11.0, step=0.1, key="pa_b")
        total_vol = st.number_input("Total Desired Volume (L)", value=1000.0, step=100.0)
        result = pearson_square(tgt_val, wine_a_val, wine_b_val, total_vol)
        if "error" not in result:
            c1, c2 = st.columns(2)
            c1.metric("Wine A Volume", f"{result['wine_a_liters']} L ({result['wine_a_pct']}%)")
            c2.metric("Wine B Volume", f"{result['wine_b_liters']} L ({result['wine_b_pct']}%)")
        else:
            st.error(result["error"])


# ─────────────────────────────────────────────────────────────────────────────
# 6. FINING AGENTS
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == "🧹 Fining Agents":
    st.markdown("## 🧹 Fining Agents")
    agent_options = list(FINING_AGENTS.keys())
    agent_labels = {k: f"{k.replace('_', ' ').title()} — {v['purpose']}" for k, v in FINING_AGENTS.items()}
    selected_agent = st.selectbox("Select Fining Agent", agent_options, format_func=lambda x: agent_labels[x])
    agent_info = FINING_AGENTS[selected_agent]
    low, high = agent_info["typical_range"]
    c1, c2 = st.columns(2)
    with c1:
        rate = st.slider(f"Rate ({agent_info['unit']})", float(low), float(high * 2), float((low + high) / 2), 1.0)
    with c2:
        vol_fining = st.number_input("Wine Volume (L)", 1.0, 500000.0, 1000.0, 100.0)
    result = fining_addition(selected_agent, rate, vol_fining)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Amount", f"{result['total_amount']} {result['unit'].split('/')[0]}")
    c2.metric("Rate Applied", result["rate"])
    c3.metric("Volume", f"{vol_fining} L")
    st.markdown(f'<div class="info-box">💡 Purpose: {result["purpose"]}<br>Typical range: {low}–{high} {agent_info["unit"]}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 7. DISSOLVED CO₂
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == "🫧 Dissolved CO₂":
    st.markdown("## 🫧 Dissolved CO₂ Calculator")
    c1, c2 = st.columns(2)
    with c1: temp = st.slider("Wine Temperature (°C)", 0.0, 30.0, 12.0, 0.5)
    with c2: wine_type_co2 = st.selectbox("Wine Type", ["still", "frizzante", "sparkling"])
    result = dissolved_co2(temp, wine_type_co2)
    c1, c2, c3 = st.columns(3)
    c1.metric("Temperature", f"{temp}°C")
    c2.metric("Henry's Constant", f"{result['henry_constant']}")
    c3.metric("Target CO₂ Range", f"{result['target_range_g_l'][0]}–{result['target_range_g_l'][1]} g/L")
    st.markdown(f'<div class="info-box">💡 {result["note"]}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 8. H₂S TREATMENT
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == "🟤 H₂S Treatment":
    st.markdown("## 🟤 H₂S Treatment (Copper Sulfate)")
    st.markdown("*Treat hydrogen sulfide (rotten egg smell) with copper sulfate.*")
    c1, c2 = st.columns(2)
    with c1:
        intensity = st.selectbox("H₂S Intensity", ["light", "medium", "strong"],
                                  format_func=lambda x: {"light": "🟡 Light (slight smell)", "medium": "🟠 Medium (clear smell)", "strong": "🔴 Strong (intense smell)"}[x])
    with c2:
        vol_h2s = st.number_input("Wine Volume (L)", 1.0, 500000.0, 1000.0, 100.0)
    result = copper_sulfate_addition(intensity, vol_h2s)
    c1, c2, c3 = st.columns(3)
    c1.metric("Copper Addition", f"{result['copper_mg_l']} mg/L Cu")
    c2.metric("Total Cu", f"{result['total_copper_mg']} mg")
    c3.metric("CuSO₄·5H₂O", f"{result['cuso4_5h2o_mg']} mg")
    st.markdown(f'<div class="info-box">💡 {result["note"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="warning-box">⚠️ {result["legal_limit_note"]}<br>Always bench trial before full addition. Remove excess copper with bentonite if needed.</div>', unsafe_allow_html=True)

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("""
<p style='text-align:center; color: #4a3020; font-size: 0.8rem;'>
  🍷 Winemaking Calculators | Built with ❤️ by 
  <a href='https://github.com/karidasd' style='color: #7a5040;'>DarkAIs</a> | 
  For educational purposes — always verify with certified oenologist
</p>
""", unsafe_allow_html=True)
