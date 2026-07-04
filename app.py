import streamlit as st
import sys, os, math
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculators import *
from translations import t, TRANSLATIONS
from pdf_report import generate_pdf

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🍷 Winemaking Calculators",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Session State ─────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "fermentation_data" not in st.session_state:
    st.session_state.fermentation_data = []
if "pdf_calculations" not in st.session_state:
    st.session_state.pdf_calculations = []

# ─── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');
  .stApp { background: linear-gradient(135deg, #0a0608 0%, #1a0a10 50%, #0d0d14 100%); color: #e8d5b7; }
  h1,h2,h3 { font-family: 'Playfair Display', serif !important; }
  p,div,label,span { font-family: 'Inter', sans-serif !important; }
  [data-testid="stSidebar"] { background: linear-gradient(180deg, #1a0a10 0%, #0d0d14 100%); border-right: 1px solid #3d1a26; }
  .hero { background: linear-gradient(135deg, rgba(120,30,50,0.4) 0%, rgba(30,20,60,0.4) 100%); border: 1px solid rgba(180,100,80,0.3); border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 32px; backdrop-filter: blur(10px); }
  .hero h1 { color: #c9956a !important; font-size: 2.6rem; margin-bottom: 8px; text-shadow: 0 0 30px rgba(180,100,80,0.5); }
  .hero p { color: #b0926a; font-size: 1.1rem; }
  .result-card { background: linear-gradient(135deg, rgba(80,20,35,0.5) 0%, rgba(20,15,40,0.5) 100%); border: 1px solid rgba(180,100,80,0.4); border-radius: 12px; padding: 20px 24px; margin-top: 20px; }
  .action-item { background: rgba(20,40,25,0.4); border-left: 3px solid #4a9960; border-radius: 0 8px 8px 0; padding: 10px 16px; margin: 6px 0; color: #90c090; font-size: 0.9rem; }
  .action-item-warn { background: rgba(60,40,10,0.4); border-left: 3px solid #c09030; border-radius: 0 8px 8px 0; padding: 10px 16px; margin: 6px 0; color: #c0a060; font-size: 0.9rem; }
  .info-box { background: rgba(30,60,40,0.3); border-left: 3px solid #4a9960; border-radius: 0 8px 8px 0; padding: 12px 16px; margin-top: 16px; color: #90c090; font-size: 0.88rem; }
  .warning-box { background: rgba(80,50,20,0.3); border-left: 3px solid #c09030; border-radius: 0 8px 8px 0; padding: 12px 16px; margin-top: 16px; color: #c0a060; font-size: 0.88rem; }
  .stButton>button { background: linear-gradient(135deg, #7b1f35 0%, #3d1a60 100%); color: #e8d5b7; border: 1px solid rgba(180,100,80,0.5); border-radius: 8px; font-weight: 600; padding: 0.6rem 2rem; transition: all 0.3s ease; width: 100%; }
  .stButton>button:hover { background: linear-gradient(135deg, #9b2f45 0%, #5d2a80 100%); border-color: #c9956a; box-shadow: 0 0 20px rgba(180,100,80,0.3); transform: translateY(-1px); }
  [data-testid="stMetricValue"] { color: #c9956a !important; font-family: 'Playfair Display', serif !important; }
  .stTabs [aria-selected="true"] { color: #c9956a !important; border-bottom-color: #c9956a !important; }
  .divider { border: none; border-top: 1px solid rgba(180,100,80,0.2); margin: 24px 0; }
  footer { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # Language Toggle
    lang_btn = "🇬🇷 Ελληνικά" if st.session_state.lang == "en" else "🇬🇧 English"
    if st.button(lang_btn):
        st.session_state.lang = "el" if st.session_state.lang == "en" else "en"
        st.rerun()

    st.markdown(f"## {t('nav_title')}")
    calculator = st.radio("", [
        t("calc_so2"), t("calc_sugar"), t("calc_acid"), t("calc_yeast"),
        t("calc_blend"), t("calc_fining"), t("calc_co2"), t("calc_h2s"),
        t("calc_temp"), t("calc_ferment"), t("calc_harvest"), t("calc_export"),
    ], label_visibility="collapsed")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("""<div style='color:#6a5040;font-size:0.8rem;padding:8px;'>
    📚 <strong style='color:#a08060'>References:</strong><br>
    Boulton et al. (2013)<br>Zoecklein et al. (1995)<br>OIV International Standards</div>""",
    unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <h1>{t('app_title')}</h1>
  <p>{t('app_subtitle')}</p>
</div>""", unsafe_allow_html=True)

# ─── Helper to record calculation for PDF ─────────────────────────────────────
def record_calc(title: str, results: dict, note: str = ""):
    st.session_state.pdf_calculations.append({"title": title, "results": results, "note": note})

# ─────────────────────────────────────────────────────────────────────────────
# SO₂ MANAGER
# ─────────────────────────────────────────────────────────────────────────────
if calculator == t("calc_so2"):
    st.markdown(f"## {t('calc_so2')}")
    tab1, tab2 = st.tabs(["📊 Current Status", "➕ Addition Calculator"])
    with tab1:
        c1,c2,c3 = st.columns(3)
        with c1: free_so2 = st.number_input(t("free_so2"), 0.0, 200.0, 25.0, 1.0)
        with c2: ph = st.number_input(t("wine_ph"), 2.8, 4.5, 3.5, 0.05)
        with c3: wine_style = st.selectbox(t("wine_style"), ["Red","White/Rosé","Sweet"])
        mol = molecular_so2(free_so2, ph)
        targets = {"Red":0.5,"White/Rosé":0.8,"Sweet":0.8}
        target = targets[wine_style]
        c1,c2,c3 = st.columns(3)
        c1.metric(t("molecular_so2"), f"{mol} mg/L")
        c2.metric("Target", f"{target} mg/L")
        c3.metric(t("wine_ph"), f"{ph}")
        if mol >= target:
            st.success(f"{t('so2_adequate')} (≥{target} mg/L)")
        else:
            needed = so2_needed_for_molecular(target, ph, free_so2)
            st.warning(f"{t('so2_low')} — add {needed} mg/L free SO₂")
        record_calc("SO₂ Status", {"Free SO₂": f"{free_so2} mg/L", "pH": ph, "Molecular SO₂": f"{mol} mg/L", "Target": f"{target} mg/L", "Status": "✅ OK" if mol >= target else "⚠️ LOW"})

    with tab2:
        c1,c2,c3 = st.columns(3)
        with c1: tgt_mol = st.number_input(t("target_mol_so2"), 0.1, 2.0, 0.5, 0.1)
        with c2: ph2 = st.number_input(t("wine_ph"), 2.8, 4.5, 3.5, 0.05, key="ph2")
        with c3: curr_free = st.number_input(t("current_free_so2"), 0.0, 200.0, 10.0, 1.0)
        vol = st.number_input(t("volume_l"), 1.0, 500000.0, 1000.0, 100.0, key="vol_so2")
        add = so2_needed_for_molecular(tgt_mol, ph2, curr_free)
        amounts = so2_addition_grams(add, vol)
        c1,c2,c3 = st.columns(3)
        c1.metric("Liquid SO₂", f"{amounts['liquid_so2_g']} g")
        c2.metric("K₂S₂O₅", f"{amounts['potassium_metabisulfite_g']} g")
        c3.metric("NaHSO₃", f"{amounts['sodium_metabisulfite_g']} g")
        record_calc("SO₂ Addition", {"Addition needed": f"{add} mg/L", "Volume": f"{vol} L", "Liquid SO₂": f"{amounts['liquid_so2_g']} g", "K₂S₂O₅": f"{amounts['potassium_metabisulfite_g']} g"})

# ─────────────────────────────────────────────────────────────────────────────
# SUGAR & ALCOHOL
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_sugar"):
    st.markdown(f"## {t('calc_sugar')}")
    tab1,tab2,tab3 = st.tabs(["🔢 Brix Conversions","🍚 Chaptalization","⚖️ SG → Brix"])
    with tab1:
        brix_v = st.slider(t("brix"), 14.0, 32.0, 24.0, 0.5)
        pa = brix_to_potential_alcohol(brix_v)
        sugar = brix_to_sugar(brix_v)
        c1,c2,c3 = st.columns(3)
        c1.metric(t("pot_alcohol"), f"{pa}% ABV")
        c2.metric(t("sugar_content"), f"{sugar} g/L")
        c3.metric("Brix", f"{brix_v}°Bx")
        record_calc("Brix Conversion", {"Brix": f"{brix_v}°Bx", "Potential Alcohol": f"{pa}% ABV", "Sugar": f"{sugar} g/L"})
    with tab2:
        c1,c2 = st.columns(2)
        with c1:
            cb = st.number_input(t("current_brix"), 14.0, 30.0, 20.0, 0.5)
            tb = st.number_input(t("target_brix"), 14.0, 32.0, 24.0, 0.5)
        with c2:
            vl = st.number_input(t("volume_l"), 1.0, 500000.0, 1000.0, 100.0, key="chap_vol")
            st_type = st.selectbox(t("sugar_type"), ["sucrose","glucose_fructose"])
        res = chaptalization(cb, tb, vl, st_type)
        if res["sugar_kg"] > 0:
            c1,c2 = st.columns(2)
            c1.metric(t("sugar_to_add"), f"{res['sugar_kg']} kg")
            c2.metric("In Grams", f"{res['sugar_g']} g")
            st.markdown(f'<div class="info-box">💡 {res["note"]}</div>', unsafe_allow_html=True)
            record_calc("Chaptalization", {"Current Brix": f"{cb}°Bx", "Target Brix": f"{tb}°Bx", "Sugar": f"{res['sugar_kg']} kg ({res['sugar_g']}g)"})
        else:
            st.success("✅ Must already at or above target Brix.")
    with tab3:
        sg = st.number_input("Specific Gravity", 1.000, 1.140, 1.090, 0.001, format="%.3f")
        bfsg = specific_gravity_to_brix(sg)
        c1,c2,c3 = st.columns(3)
        c1.metric("Brix", f"{bfsg}°Bx")
        c2.metric(t("pot_alcohol"), f"{brix_to_potential_alcohol(bfsg)}% ABV")
        c3.metric("Sugar", f"{brix_to_sugar(bfsg)} g/L")

# ─────────────────────────────────────────────────────────────────────────────
# ACIDITY
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_acid"):
    st.markdown(f"## {t('calc_acid')}")
    tab1,tab2 = st.tabs(["🔺 Acidification","🔻 Deacidification"])
    with tab1:
        c1,c2,c3 = st.columns(3)
        with c1: cta = st.number_input("Current TA (g/L)", 3.0, 12.0, 5.5, 0.1)
        with c2: tta = st.number_input("Target TA (g/L)", 3.0, 12.0, 7.0, 0.1)
        with c3: va = st.number_input(t("volume_l"), 1.0, 500000.0, 1000.0, 100.0, key="va")
        res = tartaric_acid_addition(cta, tta, va)
        if res["total_g"] > 0:
            c1,c2 = st.columns(2)
            c1.metric("Rate", f"{res['g_per_liter']} g/L")
            c2.metric("Total", f"{res['total_kg']} kg")
            st.markdown(f'<div class="info-box">💡 {res["note"]}</div>', unsafe_allow_html=True)
            record_calc("Tartaric Acid Addition", {"Current TA": f"{cta} g/L", "Target TA": f"{tta} g/L", "Rate": f"{res['g_per_liter']} g/L", "Total": f"{res['total_kg']} kg"})
    with tab2:
        c1,c2,c3 = st.columns(3)
        with c1: cta2 = st.number_input("Current TA (g/L)", 3.0, 15.0, 9.0, 0.1, key="cta2")
        with c2: tta2 = st.number_input("Target TA (g/L)", 3.0, 12.0, 6.5, 0.1, key="tta2")
        with c3: vd = st.number_input(t("volume_l"), 1.0, 500000.0, 1000.0, 100.0, key="vd")
        res2 = deacidification_caco3(cta2, tta2, vd)
        if res2["total_g"] > 0:
            c1,c2 = st.columns(2)
            c1.metric("CaCO₃ Rate", f"{res2['g_per_liter']} g/L")
            c2.metric("Total CaCO₃", f"{res2['total_kg']} kg")
            st.markdown(f'<div class="info-box">💡 {res2["note"]}</div>', unsafe_allow_html=True)
            record_calc("CaCO₃ Deacidification", {"Current TA": f"{cta2} g/L", "Target TA": f"{tta2} g/L", "CaCO₃ Rate": f"{res2['g_per_liter']} g/L", "Total": f"{res2['total_kg']} kg"})

# ─────────────────────────────────────────────────────────────────────────────
# YEAST & NUTRIENTS
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_yeast"):
    st.markdown(f"## {t('calc_yeast')}")
    tab1,tab2 = st.tabs(["🧫 Yeast Rehydration","🌾 YAN / DAP"])
    with tab1:
        c1,c2 = st.columns(2)
        with c1: vy = st.number_input(t("volume_l"), 1.0, 500000.0, 1000.0, 100.0, key="vy")
        with c2: yr = st.number_input("Inoculation Rate (g/hL)", 10.0, 40.0, 20.0, 1.0)
        res = yeast_starter_rehydration(vy, yr)
        c1,c2,c3 = st.columns(3)
        c1.metric("Yeast", f"{res['yeast_g']} g")
        c2.metric("GO-FERM", f"{res['go_ferm_g']} g")
        c3.metric("Water (37-40°C)", f"{res['rehydration_water_ml']} mL")
        st.markdown(f'<div class="info-box">💡 {res["note"]}</div>', unsafe_allow_html=True)
        record_calc("Yeast Rehydration", {"Volume": f"{vy} L", "Yeast": f"{res['yeast_g']} g", "GO-FERM": f"{res['go_ferm_g']} g", "Water": f"{res['rehydration_water_ml']} mL @ 37-40°C"})
    with tab2:
        c1,c2,c3 = st.columns(3)
        with c1: cy = st.number_input("Current YAN (mg/L)", 0.0, 400.0, 80.0, 10.0)
        with c2: ty = st.number_input("Target YAN (mg/L)", 100.0, 400.0, 200.0, 10.0)
        with c3: vyn = st.number_input(t("volume_l"), 1.0, 500000.0, 1000.0, 100.0, key="vyn")
        res = dap_addition(cy, ty, vyn)
        if res["total_dap_g"] > 0:
            c1,c2 = st.columns(2)
            c1.metric("DAP Total", f"{res['total_dap_g']} g")
            c2.metric("Fermaid-O Alt.", f"{res['total_fermaid_o_g']} g")
            st.markdown(f'<div class="info-box">💡 {res["note"]}</div>', unsafe_allow_html=True)
            record_calc("YAN / DAP Addition", {"Current YAN": f"{cy} mg/L", "Target YAN": f"{ty} mg/L", "DAP": f"{res['total_dap_g']} g", "Fermaid-O": f"{res['total_fermaid_o_g']} g"})

# ─────────────────────────────────────────────────────────────────────────────
# BLENDING
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_blend"):
    st.markdown(f"## {t('calc_blend')}")
    tab1,tab2 = st.tabs(["🧮 Blend Result","🎯 Pearson's Square"])
    with tab1:
        param = st.selectbox("Parameter", ["alcohol","brix","ta","ph","residual_sugar"])
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**Wine A**")
            va2 = st.number_input(f"Wine A — {param}", value=14.0, step=0.1, key="va2")
            vola = st.number_input("Wine A Volume (L)", value=500.0, step=50.0, key="vola")
        with c2:
            st.markdown("**Wine B**")
            vb2 = st.number_input(f"Wine B — {param}", value=12.0, step=0.1, key="vb2")
            volb = st.number_input("Wine B Volume (L)", value=500.0, step=50.0, key="volb")
        res = blend_calculator(va2, vola, vb2, volb, param)
        c1,c2,c3 = st.columns(3)
        c1.metric(f"Blend {param}", f"{res['blend_value']}")
        c2.metric("Total Volume", f"{res['total_volume_l']} L")
        c3.metric("Ratio A:B", f"{res['ratio_a_pct']}% : {res['ratio_b_pct']}%")
        record_calc("Blend Calculation", {"Parameter": param, "Wine A": f"{va2} ({vola}L)", "Wine B": f"{vb2} ({volb}L)", "Blend Result": f"{res['blend_value']}", "Ratio": f"{res['ratio_a_pct']}% A : {res['ratio_b_pct']}% B"})
    with tab2:
        c1,c2,c3 = st.columns(3)
        with c1: tv = st.number_input("Target Value", value=13.0, step=0.1)
        with c2: av = st.number_input("Wine A Value", value=15.0, step=0.1, key="av")
        with c3: bv = st.number_input("Wine B Value", value=11.0, step=0.1, key="bv")
        tvol = st.number_input("Total Volume (L)", value=1000.0, step=100.0)
        res = pearson_square(tv, av, bv, tvol)
        if "error" not in res:
            c1,c2 = st.columns(2)
            c1.metric("Wine A", f"{res['wine_a_liters']} L ({res['wine_a_pct']}%)")
            c2.metric("Wine B", f"{res['wine_b_liters']} L ({res['wine_b_pct']}%)")

# ─────────────────────────────────────────────────────────────────────────────
# FINING AGENTS
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_fining"):
    st.markdown(f"## {t('calc_fining')}")
    agent_labels = {k: f"{k.replace('_',' ').title()} — {v['purpose']}" for k,v in FINING_AGENTS.items()}
    sel = st.selectbox("Agent", list(FINING_AGENTS.keys()), format_func=lambda x: agent_labels[x])
    ai = FINING_AGENTS[sel]
    low,high = ai["typical_range"]
    c1,c2 = st.columns(2)
    with c1: rate = st.slider(f"Rate ({ai['unit']})", float(low), float(high*2), float((low+high)/2), 1.0)
    with c2: vf = st.number_input(t("volume_l"), 1.0, 500000.0, 1000.0, 100.0, key="vf")
    res = fining_addition(sel, rate, vf)
    c1,c2,c3 = st.columns(3)
    c1.metric("Total", f"{res['total_amount']} {res['unit'].split('/')[0]}")
    c2.metric("Rate", res["rate"])
    c3.metric("Volume", f"{vf} L")
    record_calc(f"Fining — {sel.replace('_',' ').title()}", {"Agent": sel, "Rate": res["rate"], "Total": f"{res['total_amount']}", "Purpose": res["purpose"]})

# ─────────────────────────────────────────────────────────────────────────────
# CO₂
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_co2"):
    st.markdown(f"## {t('calc_co2')}")
    c1,c2 = st.columns(2)
    with c1: temp_co2 = st.slider("Temperature (°C)", 0.0, 30.0, 12.0, 0.5)
    with c2: wtype = st.selectbox("Wine Type", ["still","frizzante","sparkling"])
    res = dissolved_co2(temp_co2, wtype)
    c1,c2,c3 = st.columns(3)
    c1.metric("Temperature", f"{temp_co2}°C")
    c2.metric("Henry's Constant", f"{res['henry_constant']}")
    c3.metric("Target CO₂", f"{res['target_range_g_l'][0]}–{res['target_range_g_l'][1]} g/L")

# ─────────────────────────────────────────────────────────────────────────────
# H₂S TREATMENT
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_h2s"):
    st.markdown(f"## {t('calc_h2s')}")
    c1,c2 = st.columns(2)
    with c1:
        intensity = st.selectbox("H₂S Intensity", ["light","medium","strong"],
            format_func=lambda x: {"light":"🟡 Light","medium":"🟠 Medium","strong":"🔴 Strong"}[x])
    with c2: vh = st.number_input(t("volume_l"), 1.0, 500000.0, 1000.0, 100.0, key="vh")
    res = copper_sulfate_addition(intensity, vh)
    c1,c2,c3 = st.columns(3)
    c1.metric("Cu Addition", f"{res['copper_mg_l']} mg/L")
    c2.metric("Total Cu", f"{res['total_copper_mg']} mg")
    c3.metric("CuSO₄·5H₂O", f"{res['cuso4_5h2o_mg']} mg")
    st.markdown(f'<div class="warning-box">⚠️ {res["legal_limit_note"]}</div>', unsafe_allow_html=True)
    record_calc("H₂S Treatment (CuSO₄)", {"Intensity": intensity, "Cu": f"{res['copper_mg_l']} mg/L", "Total Cu": f"{res['total_copper_mg']} mg", "CuSO₄·5H₂O": f"{res['cuso4_5h2o_mg']} mg"})

# ─────────────────────────────────────────────────────────────────────────────
# 🌡️ TEMPERATURE CORRECTION
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_temp"):
    st.markdown(f"## {t('temp_title')}")
    st.markdown(f"*{t('temp_subtitle')}*")

    tab1, tab2 = st.tabs(["🔬 Refractometer Correction", "⚗️ Hydrometer Correction"])

    with tab1:
        st.markdown("*Refractometers are calibrated at 20°C. Correct for actual sample temperature.*")
        c1, c2 = st.columns(2)
        with c1: obs_brix = st.number_input(t("observed_brix"), 0.0, 40.0, 22.0, 0.1)
        with c2: samp_temp = st.number_input(t("sample_temp"), 5.0, 40.0, 25.0, 0.5)

        # ICUMSA refractometer temperature correction formula
        correction = (0.00030 * (samp_temp - 20)) * obs_brix + 0.0055 * (samp_temp - 20)
        corrected = round(obs_brix + correction, 2)
        pa_corrected = brix_to_potential_alcohol(corrected)

        c1, c2, c3 = st.columns(3)
        c1.metric("Observed Brix", f"{obs_brix}°Bx @ {samp_temp}°C")
        c2.metric(t("corrected_brix"), f"{corrected}°Bx @ 20°C", delta=f"{round(correction,2)}")
        c3.metric("Potential Alcohol", f"{pa_corrected}% ABV")

        if abs(samp_temp - 20) > 5:
            st.markdown(f'<div class="warning-box">⚠️ Temperature difference is {abs(samp_temp-20):.1f}°C — correction is significant. Always measure close to 20°C for best accuracy.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="info-box">💡 Temperature difference is small ({abs(samp_temp-20):.1f}°C). Correction applied: {round(correction,2):+.2f}°Bx</div>', unsafe_allow_html=True)
        record_calc("Refractometer Temp Correction", {"Observed Brix": f"{obs_brix}°Bx @ {samp_temp}°C", "Corrected Brix": f"{corrected}°Bx @ 20°C", "Potential Alcohol": f"{pa_corrected}% ABV"})

    with tab2:
        st.markdown("*Hydrometers are calibrated at 15°C or 20°C. Correct SG for temperature.*")
        c1, c2, c3 = st.columns(3)
        with c1: obs_sg = st.number_input("Observed SG", 0.990, 1.140, 1.090, 0.001, format="%.3f")
        with c2: sg_temp = st.number_input("Sample Temperature (°C)", 5.0, 40.0, 25.0, 0.5, key="sg_temp")
        with c3: calib_temp = st.selectbox("Hydrometer Calibrated At", [15.0, 20.0])

        # Standard SG temperature correction
        def correct_sg(sg, t_sample, t_ref):
            return round(sg * ((1.00130346 - 0.000134722124 * t_sample + 0.00000204052596 * t_sample**2 - 0.00000000232820948 * t_sample**3) /
                               (1.00130346 - 0.000134722124 * t_ref + 0.00000204052596 * t_ref**2 - 0.00000000232820948 * t_ref**3)), 4)

        corrected_sg = correct_sg(obs_sg, sg_temp, calib_temp)
        corrected_brix_sg = specific_gravity_to_brix(corrected_sg)
        c1, c2, c3 = st.columns(3)
        c1.metric("Observed SG", f"{obs_sg:.3f}")
        c2.metric("Corrected SG", f"{corrected_sg:.4f}", delta=f"{round(corrected_sg - obs_sg, 4):+.4f}")
        c3.metric("Corrected Brix", f"{corrected_brix_sg}°Bx")
        record_calc("Hydrometer SG Correction", {"Observed SG": f"{obs_sg:.3f} @ {sg_temp}°C", "Corrected SG": f"{corrected_sg:.4f}", "Corrected Brix": f"{corrected_brix_sg}°Bx"})

# ─────────────────────────────────────────────────────────────────────────────
# 📊 FERMENTATION TRACKER
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_ferment"):
    st.markdown(f"## {t('ferment_title')}")
    st.markdown(f"*{t('ferment_subtitle')}*")

    # Add new reading
    with st.expander(t("add_reading"), expanded=not st.session_state.fermentation_data):
        c1,c2,c3,c4 = st.columns([2,2,2,3])
        with c1: f_date = st.date_input(t("ferment_date"), value=date.today())
        with c2: f_brix = st.number_input(t("ferment_brix"), 0.0, 32.0, 20.0, 0.1, key="fb")
        with c3: f_temp = st.number_input(t("ferment_temp"), 5.0, 35.0, 18.0, 0.5, key="ft")
        with c4: f_note = st.text_input(t("ferment_notes"), placeholder="e.g. Added nutrients", key="fn")
        if st.button(t("add_reading")):
            st.session_state.fermentation_data.append({
                "date": str(f_date), "brix": f_brix, "temp": f_temp, "notes": f_note
            })
            st.rerun()

    if st.session_state.fermentation_data:
        df = pd.DataFrame(st.session_state.fermentation_data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        # Dual axis chart: Brix + Temperature
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["brix"], name="Brix (°Bx)",
            line=dict(color="#c9956a", width=3), mode="lines+markers",
            marker=dict(size=8, color="#c9956a"),
        ))
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["temp"], name="Temperature (°C)",
            line=dict(color="#5a8fd0", width=2, dash="dash"), mode="lines+markers",
            marker=dict(size=6, color="#5a8fd0"), yaxis="y2",
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(15,8,12,0.9)",
            plot_bgcolor="rgba(20,10,18,0.8)",
            font=dict(color="#c9956a", family="Inter"),
            title=dict(text="🍷 Fermentation Progress", font=dict(size=16, color="#c9956a")),
            xaxis=dict(title="Date", gridcolor="rgba(180,100,80,0.15)"),
            yaxis=dict(title="Brix (°Bx)", gridcolor="rgba(180,100,80,0.15)", color="#c9956a"),
            yaxis2=dict(title="Temperature (°C)", overlaying="y", side="right", color="#5a8fd0"),
            legend=dict(bgcolor="rgba(20,10,18,0.8)", bordercolor="rgba(180,100,80,0.3)"),
            hovermode="x unified",
        )
        # Danger zones
        fig.add_hrect(y0=0, y1=5, fillcolor="rgba(50,100,200,0.08)", line_width=0, annotation_text="Too Cold", annotation_position="top left")
        fig.add_hrect(y0=30, y1=35, fillcolor="rgba(200,50,50,0.08)", line_width=0, annotation_text="Too Hot", annotation_position="top left")

        st.plotly_chart(fig, use_container_width=True)

        # Predictions
        if len(df) >= 2:
            daily_drop = (df["brix"].iloc[0] - df["brix"].iloc[-1]) / max(1, (df["date"].iloc[-1] - df["date"].iloc[0]).days)
            days_left = df["brix"].iloc[-1] / max(0.01, daily_drop) if daily_drop > 0 else None
            c1,c2,c3 = st.columns(3)
            c1.metric("Current Brix", f"{df['brix'].iloc[-1]}°Bx")
            c2.metric("Daily Brix Drop", f"{round(daily_drop,2)}°Bx/day")
            if days_left:
                c3.metric("Est. Days to Dryness", f"~{int(days_left)} days")

        # Data Table
        st.dataframe(df.rename(columns={"date":"Date","brix":"Brix (°Bx)","temp":"Temp (°C)","notes":"Notes"}),
                     use_container_width=True, hide_index=True)

        col1, col2 = st.columns([1,1])
        with col1:
            if st.button(t("clear_data")):
                st.session_state.fermentation_data = []
                st.rerun()
    else:
        st.info("📋 No fermentation data yet. Add your first reading above!")

# ─────────────────────────────────────────────────────────────────────────────
# 🧮 HARVEST PLANNER
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_harvest"):
    st.markdown(f"## {t('harvest_title')}")
    st.markdown(f"*{t('harvest_subtitle')}*")

    c1, c2, c3 = st.columns(3)
    with c1:
        h_brix = st.number_input(t("harvest_brix"), 14.0, 32.0, 23.0, 0.5)
        h_ph = st.number_input(t("harvest_ph"), 2.8, 4.5, 3.4, 0.05)
    with c2:
        h_ta = st.number_input(t("harvest_ta"), 3.0, 12.0, 6.5, 0.1)
        h_yan = st.number_input(t("harvest_yan"), 0.0, 400.0, 90.0, 10.0)
    with c3:
        h_temp = st.number_input(t("harvest_temp"), 5.0, 30.0, 16.0, 0.5)
        h_vol = st.number_input("Volume (L)", 100.0, 500000.0, 5000.0, 500.0, key="hv")
        h_style = st.selectbox(t("harvest_style"), ["Red","White","Rosé","Sweet"])

    st.markdown(f"### {t('action_plan')}")

    # --- SO₂ ---
    target_mol = {"Red": 0.5, "White": 0.8, "Rosé": 0.8, "Sweet": 0.8}[h_style]
    so2_add = so2_needed_for_molecular(target_mol, h_ph, 0)
    so2_grams = so2_addition_grams(so2_add, h_vol)

    # --- Sugar ---
    target_alcohol = {"Red": 13.5, "White": 12.5, "Rosé": 12.0, "Sweet": 11.0}[h_style]
    target_brix_for_alcohol = round((target_alcohol + 0.65) / 0.5765, 1)
    chap = chaptalization(h_brix, target_brix_for_alcohol, h_vol) if h_brix < target_brix_for_alcohol else None

    # --- TA ---
    target_ta = {"Red": 6.0, "White": 7.0, "Rosé": 6.5, "Sweet": 7.5}[h_style]
    acid_res = tartaric_acid_addition(h_ta, target_ta, h_vol) if h_ta < target_ta else None
    deacid_res = deacidification_caco3(h_ta, target_ta, h_vol) if h_ta > target_ta else None

    # --- YAN ---
    target_yan = 200
    yan_res = dap_addition(h_yan, target_yan, h_vol)

    # --- Yeast ---
    yeast_res = yeast_starter_rehydration(h_vol)

    # Display action plan
    pa = brix_to_potential_alcohol(h_brix)
    st.markdown(f"""
    <div class="action-item">🍇 <strong>Must Analysis:</strong> {h_brix}°Bx → {pa}% potential ABV | pH {h_ph} | TA {h_ta} g/L | YAN {h_yan} mg/L</div>
    <div class="action-item">🧪 <strong>SO₂ at reception:</strong> Add {so2_add} mg/L free SO₂ → {so2_grams['potassium_metabisulfite_g']}g K₂S₂O₅ (target: {target_mol} mg/L molecular SO₂)</div>
    """, unsafe_allow_html=True)

    if chap and chap["sugar_kg"] > 0:
        st.markdown(f'<div class="action-item-warn">🍬 <strong>Chaptalization needed:</strong> Add {chap["sugar_kg"]} kg sugar to reach {target_brix_for_alcohol}°Bx (target: {target_alcohol}% ABV)</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="action-item">✅ <strong>Sugar:</strong> No chaptalization needed — {pa}% ABV is appropriate for {h_style}</div>', unsafe_allow_html=True)

    if acid_res and acid_res["total_g"] > 0:
        st.markdown(f'<div class="action-item-warn">🔺 <strong>Acidify:</strong> Add {acid_res["total_kg"]} kg tartaric acid ({acid_res["g_per_liter"]} g/L) to reach {target_ta} g/L TA</div>', unsafe_allow_html=True)
    elif deacid_res and deacid_res["total_g"] > 0:
        st.markdown(f'<div class="action-item-warn">🔻 <strong>Deacidify:</strong> Add {deacid_res["total_kg"]} kg CaCO₃ ({deacid_res["g_per_liter"]} g/L) to reduce TA to {target_ta} g/L</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="action-item">✅ <strong>Acidity:</strong> TA of {h_ta} g/L is within target range for {h_style}</div>', unsafe_allow_html=True)

    if yan_res["total_dap_g"] > 0:
        st.markdown(f'<div class="action-item-warn">🌾 <strong>Nutrients:</strong> YAN deficient — add {yan_res["total_dap_g"]}g DAP or {yan_res["total_fermaid_o_g"]}g Fermaid-O in 2-3 additions</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="action-item">✅ <strong>YAN:</strong> Nitrogen levels sufficient ({h_yan} mg/L)</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="action-item">🧫 <strong>Yeast inoculation:</strong> Rehydrate {yeast_res["yeast_g"]}g yeast + {yeast_res["go_ferm_g"]}g GO-FERM in {yeast_res["rehydration_water_ml"]}mL water at 37-40°C</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="action-item">🌡️ <strong>Fermentation temperature:</strong> Target {"18-22°C for Red" if h_style == "Red" else "14-18°C for White/Rosé"} | Cellar: {h_temp}°C {"✅" if (h_temp < 22) else "⚠️ Cool down!"}</div>', unsafe_allow_html=True)

    record_calc("Harvest Planner", {
        "Must": f"{h_brix}°Bx | pH {h_ph} | TA {h_ta}g/L | YAN {h_yan}mg/L",
        "Volume": f"{h_vol} L",
        "Style": h_style,
        "SO₂ Addition": f"{so2_add} mg/L ({so2_grams['potassium_metabisulfite_g']}g K₂S₂O₅)",
        "Chaptalization": f"{chap['sugar_kg']} kg" if chap and chap['sugar_kg']>0 else "Not needed",
        "Acidity": f"Add {acid_res['total_kg']}kg tartaric" if acid_res and acid_res['total_g']>0 else ("Deacidify" if deacid_res and deacid_res['total_g']>0 else "OK"),
        "YAN": f"Add {yan_res['total_dap_g']}g DAP" if yan_res['total_dap_g']>0 else "OK",
        "Yeast": f"{yeast_res['yeast_g']}g + {yeast_res['go_ferm_g']}g GO-FERM",
    })

# ─────────────────────────────────────────────────────────────────────────────
# 📄 EXPORT PDF
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_export"):
    st.markdown(f"## {t('export_title')}")
    st.markdown(f"*{t('export_subtitle')}*")

    if not st.session_state.pdf_calculations:
        st.info(f"📋 {t('no_calcs')}")
    else:
        st.success(f"✅ {len(st.session_state.pdf_calculations)} calculation(s) ready to export.")
        for i, calc in enumerate(st.session_state.pdf_calculations):
            with st.expander(f"📌 {calc['title']}"):
                for k, v in calc["results"].items():
                    st.markdown(f"**{k}:** {v}")
                if calc.get("note"):
                    st.markdown(f"*{calc['note']}*")

        try:
            pdf_bytes = generate_pdf(st.session_state.pdf_calculations)
            st.download_button(
                label=t("download_pdf"),
                data=pdf_bytes,
                file_name=f"winemaking_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            st.error(f"PDF generation error: {e}")

        if st.button("🗑️ Clear Session"):
            st.session_state.pdf_calculations = []
            st.rerun()

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown(f"""
<p style='text-align:center;color:#4a3020;font-size:0.8rem;'>
  🍷 Winemaking Calculators | Built with ❤️ by <a href='https://github.com/karidasd' style='color:#7a5040;'>DarkAIs</a> | {t('footer')}
</p>""", unsafe_allow_html=True)
