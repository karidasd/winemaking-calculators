import streamlit as st
import sys, os, math, json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculators import *
from translations import t, TRANSLATIONS
from pdf_report import generate_pdf
from ai_modules.ml_models import predict_fermentation_curve
from ai_modules.llm_agents import generate_blending_advice

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🍷 Winemaking Calculators",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── PWA Manifest injection ───────────────────────────────────────────────────
st.markdown("""
<link rel="manifest" href="data:application/json;base64,eyJuYW1lIjoiV2luZW1ha2luZyBDYWxjdWxhdG9ycyIsInNob3J0X25hbWUiOiJXaW5lQ2FsYyIsInN0YXJ0X3VybCI6Ii8iLCJkaXNwbGF5Ijoic3RhbmRhbG9uZSIsImJhY2tncm91bmRfY29sb3IiOiIjMGEwNjA4IiwidGhlbWVfY29sb3IiOiI3YjFmMzUiLCJpY29ucyI6W3sic3JjIjoiaHR0cHM6Ly9jZG4uanNkZWxpdnIubmV0L2VtcGppLzE0LjAuMC9zdmcvMWY3Nzcuc3ZnIiwic2l6ZXMiOiIxOTJ4MTkyIiwidHlwZSI6ImltYWdlL3N2Zyt4bWwifV19" />
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="WineCalc">
<meta name="theme-color" content="#7b1f35">
""", unsafe_allow_html=True)

# ─── Session State ─────────────────────────────────────────────────────────────
defaults = {
    "lang": "en",
    "fermentation_data": [],
    "pdf_calculations": [],
    "vintage_logbook": [],
    "vineyards": [],
    "vintage_history": [
        {"Year": 2023, "Variety": "Xinomavro", "Brix": 23.5, "pH": 3.22, "TA": 7.4},
        {"Year": 2024, "Variety": "Xinomavro", "Brix": 24.0, "pH": 3.28, "TA": 7.1},
        {"Year": 2025, "Variety": "Xinomavro", "Brix": 23.0, "pH": 3.19, "TA": 7.6},
        {"Year": 2023, "Variety": "Assyrtiko", "Brix": 22.0, "pH": 2.95, "TA": 8.2},
        {"Year": 2024, "Variety": "Assyrtiko", "Brix": 23.0, "pH": 3.02, "TA": 7.8},
        {"Year": 2025, "Variety": "Assyrtiko", "Brix": 22.5, "pH": 2.98, "TA": 8.0},
    ]
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap');
  .stApp { background: linear-gradient(135deg, #0a0608 0%, #1a0a10 50%, #0d0d14 100%); color: #e8d5b7; }
  h1,h2,h3 { font-family: 'Playfair Display', serif !important; }
  /* Removed global span/p overrides to prevent Streamlit layout breaking */
  [data-testid="stSidebar"] { background: linear-gradient(180deg, #1a0a10 0%, #0d0d14 100%); border-right: 1px solid #3d1a26; }
  .hero { background: linear-gradient(135deg, rgba(120,30,50,0.4) 0%, rgba(30,20,60,0.4) 100%); border: 1px solid rgba(180,100,80,0.3); border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 32px; backdrop-filter: blur(10px); }
  .hero h1 { color: #c9956a !important; font-size: 2.6rem; margin-bottom: 8px; text-shadow: 0 0 30px rgba(180,100,80,0.5); }
  .hero p { color: #b0926a; font-size: 1.1rem; }
  .result-card { background: linear-gradient(135deg, rgba(80,20,35,0.5) 0%, rgba(20,15,40,0.5) 100%); border: 1px solid rgba(180,100,80,0.4); border-radius: 12px; padding: 20px 24px; margin-top: 20px; }
  .action-item { background: rgba(20,40,25,0.4); border-left: 3px solid #4a9960; border-radius: 0 8px 8px 0; padding: 10px 16px; margin: 6px 0; color: #90c090; font-size: 0.9rem; }
  .action-item-warn { background: rgba(60,40,10,0.4); border-left: 3px solid #c09030; border-radius: 0 8px 8px 0; padding: 10px 16px; margin: 6px 0; color: #c0a060; font-size: 0.9rem; }
  .info-box { background: rgba(30,60,40,0.3); border-left: 3px solid #4a9960; border-radius: 0 8px 8px 0; padding: 12px 16px; margin-top: 16px; color: #90c090; font-size: 0.88rem; }
  .warning-box { background: rgba(80,50,20,0.3); border-left: 3px solid #c09030; border-radius: 0 8px 8px 0; padding: 12px 16px; margin-top: 16px; color: #c0a060; font-size: 0.88rem; }
  .danger-box { background: rgba(80,20,20,0.3); border-left: 3px solid #c03030; border-radius: 0 8px 8px 0; padding: 12px 16px; margin-top: 16px; color: #c06060; font-size: 0.88rem; }
  .grade-badge { display: inline-block; width: 40px; height: 40px; border-radius: 50%; text-align: center; line-height: 40px; font-weight: 700; font-size: 1.2rem; margin-right: 10px; }
  .grade-A { background: rgba(46,160,67,0.3); color: #3FB950; border: 2px solid #3FB950; }
  .grade-B { background: rgba(210,153,34,0.3); color: #D29922; border: 2px solid #D29922; }
  .grade-C { background: rgba(248,129,50,0.3); color: #FF8C42; border: 2px solid #FF8C42; }
  .grade-D { background: rgba(248,81,73,0.3); color: #F85149; border: 2px solid #F85149; }
  .logbook-entry { background: rgba(30,15,25,0.6); border: 1px solid rgba(180,100,80,0.25); border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; }
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
    lang_btn = "🇬🇷 Ελληνικά" if st.session_state.lang == "en" else "🇬🇧 English"
    if st.button(lang_btn):
        st.session_state.lang = "el" if st.session_state.lang == "en" else "en"
        st.rerun()
    st.markdown(f"## {t('nav_title')}")
    calculator = st.radio("", [
        t("calc_so2"), t("calc_sugar"), t("calc_acid"), t("calc_yeast"),
        t("calc_blend"), t("calc_fining"), t("calc_co2"), t("calc_h2s"),
        t("calc_temp"), t("calc_ferment"), t("calc_harvest"),
        t("calc_mlf"), t("calc_cold_stab"), t("calc_sorbate"),
        t("calc_vineyard_comp"), t("calc_logbook"),
        t("calc_bottling"), t("calc_oak"), t("calc_faults"), t("calc_greek"), t("calc_vintage_comp"),
        t("calc_ai_ferment"), t("calc_ai_blend"),
        t("calc_export"),
    ],label_visibility="collapsed")
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("""<div style='color:#6a5040;font-size:0.8rem;padding:8px;'>
    📚 <strong style='color:#a08060'>References:</strong><br>
    Boulton et al. (2013)<br>Zoecklein et al. (1995)<br>OIV International Standards<br>Würdig & Woller (1989)</div>""", unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <h1>{t('app_title')}</h1>
  <p>{t('app_subtitle')}</p>
</div>""", unsafe_allow_html=True)

def record_calc(title, results, note=""):
    st.session_state.pdf_calculations.append({"title": title, "results": results, "note": note})

# ─────────────────────────────────────────────────────────────────────────────
# 1. SO2 MANAGER
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
        c3.metric("pH", f"{ph}")
        if mol >= target: st.success(f"{t('so2_adequate')} (≥{target} mg/L)")
        else:
            needed = so2_needed_for_molecular(target, ph, free_so2)
            st.warning(f"{t('so2_low')} — add {needed} mg/L free SO₂")
        record_calc("SO₂ Status", {"Free SO₂": f"{free_so2} mg/L", "pH": ph, "Molecular SO₂": f"{mol} mg/L", "Status": "✅ OK" if mol >= target else "⚠️ LOW"})
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
        record_calc("SO₂ Addition", {"Addition": f"{add} mg/L", "Volume": f"{vol} L", "K₂S₂O₅": f"{amounts['potassium_metabisulfite_g']} g"})

# ─────────────────────────────────────────────────────────────────────────────
# 2. SUGAR & ALCOHOL
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_sugar"):
    st.markdown(f"## {t('calc_sugar')}")
    tab1,tab2,tab3 = st.tabs(["🔢 Brix Conversions","🍚 Chaptalization","⚖️ SG → Brix"])
    with tab1:
        brix_v = st.slider(t("brix"), 14.0, 32.0, 24.0, 0.5)
        pa = brix_to_potential_alcohol(brix_v)
        c1,c2,c3 = st.columns(3)
        c1.metric(t("pot_alcohol"), f"{pa}% ABV")
        c2.metric(t("sugar_content"), f"{brix_to_sugar(brix_v)} g/L")
        c3.metric("Brix", f"{brix_v}°Bx")
        record_calc("Brix Conversion", {"Brix": f"{brix_v}°Bx", "Potential Alcohol": f"{pa}% ABV", "Sugar": f"{brix_to_sugar(brix_v)} g/L"})
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
        else: st.success("✅ Already at target Brix.")
    with tab3:
        sg = st.number_input("Specific Gravity", 1.000, 1.140, 1.090, 0.001, format="%.3f")
        bfsg = specific_gravity_to_brix(sg)
        c1,c2,c3 = st.columns(3)
        c1.metric("Brix", f"{bfsg}°Bx")
        c2.metric(t("pot_alcohol"), f"{brix_to_potential_alcohol(bfsg)}% ABV")
        c3.metric("Sugar", f"{brix_to_sugar(bfsg)} g/L")

# ─────────────────────────────────────────────────────────────────────────────
# 3. ACIDITY
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
            record_calc("Tartaric Acid", {"Rate": f"{res['g_per_liter']} g/L", "Total": f"{res['total_kg']} kg"})
        else: st.success("✅ TA already adequate.")
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
        else: st.success("✅ TA at target.")

# ─────────────────────────────────────────────────────────────────────────────
# 4. YEAST & NUTRIENTS
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_yeast"):
    st.markdown(f"## {t('calc_yeast')}")
    tab1,tab2 = st.tabs(["🧫 Yeast Rehydration","🌾 YAN / DAP"])
    with tab1:
        c1,c2 = st.columns(2)
        with c1: vy = st.number_input(t("volume_l"), 1.0, 500000.0, 1000.0, 100.0, key="vy")
        with c2: yr = st.number_input("Rate (g/hL)", 10.0, 40.0, 20.0, 1.0)
        res = yeast_starter_rehydration(vy, yr)
        c1,c2,c3 = st.columns(3)
        c1.metric("Yeast", f"{res['yeast_g']} g")
        c2.metric("GO-FERM", f"{res['go_ferm_g']} g")
        c3.metric("Water", f"{res['rehydration_water_ml']} mL")
        st.markdown(f'<div class="info-box">💡 {res["note"]}</div>', unsafe_allow_html=True)
        record_calc("Yeast Rehydration", {"Yeast": f"{res['yeast_g']} g", "GO-FERM": f"{res['go_ferm_g']} g", "Water": f"{res['rehydration_water_ml']} mL @ 37-40°C"})
    with tab2:
        c1,c2,c3 = st.columns(3)
        with c1: cy = st.number_input("Current YAN (mg/L)", 0.0, 400.0, 80.0, 10.0)
        with c2: ty = st.number_input("Target YAN (mg/L)", 100.0, 400.0, 200.0, 10.0)
        with c3: vyn = st.number_input(t("volume_l"), 1.0, 500000.0, 1000.0, 100.0, key="vyn")
        res = dap_addition(cy, ty, vyn)
        if res["total_dap_g"] > 0:
            c1,c2 = st.columns(2)
            c1.metric("DAP", f"{res['total_dap_g']} g")
            c2.metric("Fermaid-O", f"{res['total_fermaid_o_g']} g")
            st.markdown(f'<div class="info-box">💡 {res["note"]}</div>', unsafe_allow_html=True)
        else: st.success("✅ YAN sufficient.")

# ─────────────────────────────────────────────────────────────────────────────
# 5. BLENDING
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
            vola = st.number_input("Wine A Vol (L)", value=500.0, step=50.0, key="vola")
        with c2:
            st.markdown("**Wine B**")
            vb2 = st.number_input(f"Wine B — {param}", value=12.0, step=0.1, key="vb2")
            volb = st.number_input("Wine B Vol (L)", value=500.0, step=50.0, key="volb")
        res = blend_calculator(va2, vola, vb2, volb, param)
        c1,c2,c3 = st.columns(3)
        c1.metric(f"Blend", f"{res['blend_value']}")
        c2.metric("Total Vol", f"{res['total_volume_l']} L")
        c3.metric("Ratio A:B", f"{res['ratio_a_pct']}% : {res['ratio_b_pct']}%")
    with tab2:
        c1,c2,c3 = st.columns(3)
        with c1: tv = st.number_input("Target", value=13.0, step=0.1)
        with c2: av = st.number_input("Wine A Value", value=15.0, step=0.1, key="av")
        with c3: bv = st.number_input("Wine B Value", value=11.0, step=0.1, key="bv")
        tvol = st.number_input("Total Vol (L)", value=1000.0, step=100.0)
        res = pearson_square(tv, av, bv, tvol)
        if "error" not in res:
            c1,c2 = st.columns(2)
            c1.metric("Wine A", f"{res['wine_a_liters']} L ({res['wine_a_pct']}%)")
            c2.metric("Wine B", f"{res['wine_b_liters']} L ({res['wine_b_pct']}%)")

# ─────────────────────────────────────────────────────────────────────────────
# 6. FINING AGENTS
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

# ─────────────────────────────────────────────────────────────────────────────
# 7. DISSOLVED CO2
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_co2"):
    st.markdown(f"## {t('calc_co2')}")
    c1,c2 = st.columns(2)
    with c1: temp_co2 = st.slider("Temperature (°C)", 0.0, 30.0, 12.0, 0.5)
    with c2: wtype = st.selectbox("Wine Type", ["still","frizzante","sparkling"])
    res = dissolved_co2(temp_co2, wtype)
    c1,c2,c3 = st.columns(3)
    c1.metric("Temperature", f"{temp_co2}°C")
    c2.metric("Henry's K", f"{res['henry_constant']}")
    c3.metric("Target CO₂", f"{res['target_range_g_l'][0]}–{res['target_range_g_l'][1]} g/L")

# ─────────────────────────────────────────────────────────────────────────────
# 8. H₂S TREATMENT
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_h2s"):
    st.markdown(f"## {t('calc_h2s')}")
    c1,c2 = st.columns(2)
    with c1: intensity = st.selectbox("H₂S Intensity", ["light","medium","strong"], format_func=lambda x: {"light":"🟡 Light","medium":"🟠 Medium","strong":"🔴 Strong"}[x])
    with c2: vh = st.number_input(t("volume_l"), 1.0, 500000.0, 1000.0, 100.0, key="vh")
    res = copper_sulfate_addition(intensity, vh)
    c1,c2,c3 = st.columns(3)
    c1.metric("Cu/L", f"{res['copper_mg_l']} mg/L")
    c2.metric("Total Cu", f"{res['total_copper_mg']} mg")
    c3.metric("CuSO₄·5H₂O", f"{res['cuso4_5h2o_mg']} mg")
    st.markdown(f'<div class="warning-box">⚠️ {res["legal_limit_note"]}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 9. TEMPERATURE CORRECTION
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_temp"):
    st.markdown(f"## {t('temp_title')}")
    tab1, tab2 = st.tabs(["🔬 Refractometer", "⚗️ Hydrometer"])
    with tab1:
        c1,c2 = st.columns(2)
        with c1: obs_brix = st.number_input(t("observed_brix"), 0.0, 40.0, 22.0, 0.1)
        with c2: samp_temp = st.number_input(t("sample_temp"), 5.0, 40.0, 25.0, 0.5)
        correction = (0.00030 * (samp_temp - 20)) * obs_brix + 0.0055 * (samp_temp - 20)
        corrected = round(obs_brix + correction, 2)
        c1,c2,c3 = st.columns(3)
        c1.metric("Observed", f"{obs_brix}°Bx")
        c2.metric(t("corrected_brix"), f"{corrected}°Bx", delta=f"{round(correction,2)}")
        c3.metric("Potential Alcohol", f"{brix_to_potential_alcohol(corrected)}% ABV")
    with tab2:
        c1,c2,c3 = st.columns(3)
        with c1: obs_sg = st.number_input("Observed SG", 0.990, 1.140, 1.090, 0.001, format="%.3f")
        with c2: sg_temp = st.number_input("Sample Temp (°C)", 5.0, 40.0, 25.0, 0.5, key="sg_temp")
        with c3: calib_temp = st.selectbox("Calibrated At", [15.0, 20.0])
        def correct_sg(sg, ts, tr):
            return round(sg * ((1.00130346 - 0.000134722124*ts + 0.00000204052596*ts**2 - 0.00000000232820948*ts**3) /
                               (1.00130346 - 0.000134722124*tr + 0.00000204052596*tr**2 - 0.00000000232820948*tr**3)), 4)
        csg = correct_sg(obs_sg, sg_temp, calib_temp)
        c1,c2,c3 = st.columns(3)
        c1.metric("Observed SG", f"{obs_sg:.3f}")
        c2.metric("Corrected SG", f"{csg:.4f}", delta=f"{round(csg-obs_sg,4):+.4f}")
        c3.metric("Corrected Brix", f"{specific_gravity_to_brix(csg)}°Bx")

# ─────────────────────────────────────────────────────────────────────────────
# 10. FERMENTATION TRACKER
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_ferment"):
    st.markdown(f"## {t('ferment_title')}")
    with st.expander(t("add_reading"), expanded=not st.session_state.fermentation_data):
        c1,c2,c3,c4 = st.columns([2,2,2,3])
        with c1: f_date = st.date_input(t("ferment_date"), value=date.today())
        with c2: f_brix = st.number_input(t("ferment_brix"), 0.0, 32.0, 20.0, 0.1, key="fb")
        with c3: f_temp = st.number_input(t("ferment_temp"), 5.0, 35.0, 18.0, 0.5, key="ft")
        with c4: f_note = st.text_input(t("ferment_notes"), placeholder="e.g. Added nutrients", key="fn")
        if st.button(t("add_reading")):
            st.session_state.fermentation_data.append({"date": str(f_date), "brix": f_brix, "temp": f_temp, "notes": f_note})
            st.rerun()
    if st.session_state.fermentation_data:
        df = pd.DataFrame(st.session_state.fermentation_data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["date"], y=df["brix"], name="Brix (°Bx)", line=dict(color="#c9956a", width=3), mode="lines+markers", marker=dict(size=8)))
        fig.add_trace(go.Scatter(x=df["date"], y=df["temp"], name="Temp (°C)", line=dict(color="#5a8fd0", width=2, dash="dash"), mode="lines+markers", yaxis="y2"))
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(15,8,12,0.9)", plot_bgcolor="rgba(20,10,18,0.8)", font=dict(color="#c9956a"),
                          title="🍷 Fermentation Progress", xaxis=dict(gridcolor="rgba(180,100,80,0.15)"),
                          yaxis=dict(title="Brix", gridcolor="rgba(180,100,80,0.15)", color="#c9956a"),
                          yaxis2=dict(title="Temp (°C)", overlaying="y", side="right", color="#5a8fd0"), hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        if len(df) >= 2:
            dd = (df["brix"].iloc[0] - df["brix"].iloc[-1]) / max(1, (df["date"].iloc[-1] - df["date"].iloc[0]).days)
            dl = df["brix"].iloc[-1] / max(0.01, dd) if dd > 0 else None
            c1,c2,c3 = st.columns(3)
            c1.metric("Current Brix", f"{df['brix'].iloc[-1]}°Bx")
            c2.metric("Daily Drop", f"{round(dd,2)}°Bx/day")
            if dl: c3.metric("Est. Days to Dry", f"~{int(dl)} days")
        st.dataframe(df.rename(columns={"date":"Date","brix":"Brix","temp":"Temp","notes":"Notes"}), use_container_width=True, hide_index=True)
        if st.button(t("clear_data")): st.session_state.fermentation_data = []; st.rerun()
    else: st.info("📋 No data yet. Add your first reading!")

# ─────────────────────────────────────────────────────────────────────────────
# 11. HARVEST PLANNER
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_harvest"):
    st.markdown(f"## {t('harvest_title')}")
    c1,c2,c3 = st.columns(3)
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
    target_mol = {"Red":0.5,"White":0.8,"Rosé":0.8,"Sweet":0.8}[h_style]
    so2_add = so2_needed_for_molecular(target_mol, h_ph, 0)
    so2_grams = so2_addition_grams(so2_add, h_vol)
    target_brix_for_alc = round(({"Red":13.5,"White":12.5,"Rosé":12.0,"Sweet":11.0}[h_style] + 0.65) / 0.5765, 1)
    chap = chaptalization(h_brix, target_brix_for_alc, h_vol) if h_brix < target_brix_for_alc else None
    target_ta = {"Red":6.0,"White":7.0,"Rosé":6.5,"Sweet":7.5}[h_style]
    acid_res = tartaric_acid_addition(h_ta, target_ta, h_vol) if h_ta < target_ta else None
    deacid_res = deacidification_caco3(h_ta, target_ta, h_vol) if h_ta > target_ta else None
    yan_res = dap_addition(h_yan, 200, h_vol)
    yeast_res = yeast_starter_rehydration(h_vol)
    pa = brix_to_potential_alcohol(h_brix)
    st.markdown(f'<div class="action-item">🍇 <strong>Must:</strong> {h_brix}°Bx → {pa}% ABV | pH {h_ph} | TA {h_ta} g/L | YAN {h_yan} mg/L</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="action-item">🧪 <strong>SO₂:</strong> Add {so2_add} mg/L → {so2_grams["potassium_metabisulfite_g"]}g K₂S₂O₅</div>', unsafe_allow_html=True)
    if chap and chap["sugar_kg"] > 0:
        st.markdown(f'<div class="action-item-warn">🍬 <strong>Chaptalize:</strong> Add {chap["sugar_kg"]} kg sugar</div>', unsafe_allow_html=True)
    if acid_res and acid_res["total_g"] > 0:
        st.markdown(f'<div class="action-item-warn">🔺 <strong>Acidify:</strong> {acid_res["total_kg"]} kg tartaric acid</div>', unsafe_allow_html=True)
    elif deacid_res and deacid_res["total_g"] > 0:
        st.markdown(f'<div class="action-item-warn">🔻 <strong>Deacidify:</strong> {deacid_res["total_kg"]} kg CaCO₃</div>', unsafe_allow_html=True)
    if yan_res["total_dap_g"] > 0:
        st.markdown(f'<div class="action-item-warn">🌾 <strong>Nutrients:</strong> {yan_res["total_dap_g"]}g DAP or {yan_res["total_fermaid_o_g"]}g Fermaid-O</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="action-item">🧫 <strong>Yeast:</strong> {yeast_res["yeast_g"]}g + {yeast_res["go_ferm_g"]}g GO-FERM in {yeast_res["rehydration_water_ml"]}mL water @ 37-40°C</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 12. MLF TRACKER
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_mlf"):
    st.markdown("## 🧫 MLF Tracker (Malolactic Fermentation)")
    tab1, tab2 = st.tabs(["📊 Progress", "🔬 TA & pH Impact"])
    with tab1:
        c1,c2 = st.columns(2)
        with c1:
            malic_init = st.number_input("Initial Malic Acid (g/L)", 0.5, 8.0, 3.0, 0.1)
            malic_curr = st.number_input("Current Malic Acid (g/L)", 0.0, 8.0, 1.5, 0.1)
        with c2:
            st.markdown("**Chromatography Guide:**")
            st.markdown("- 🔴 Dark spot = High malic\n- 🟡 Faint spot = Nearly complete\n- ✅ No spot = Complete (<0.15 g/L)")
        res = mlf_progress(malic_init, malic_curr)
        st.markdown(f"### {res['status']}")
        st.progress(res["progress_pct"] / 100)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Progress", f"{res['progress_pct']}%")
        c2.metric("Malic Consumed", f"{res['malic_consumed_g_l']} g/L")
        c3.metric("Lactic Produced", f"{res['lactic_produced_g_l']} g/L")
        c4.metric("TA Reduction", f"{res['ta_reduction_g_l']} g/L")
    with tab2:
        c1,c2 = st.columns(2)
        with c1:
            mi2 = st.number_input("Initial Malic (g/L)", 0.5, 8.0, 3.0, 0.1, key="mi2")
            mc2 = st.number_input("Current Malic (g/L)", 0.0, 8.0, 1.5, 0.1, key="mc2")
        with c2:
            init_ph2 = st.number_input("Initial pH", 2.8, 4.0, 3.2, 0.05, key="initph")
            init_ta2 = st.number_input("Initial TA (g/L)", 4.0, 12.0, 7.5, 0.1, key="inita")
        impact = mlf_ta_ph_impact(mi2, mc2, init_ph2, init_ta2)
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Initial TA", f"{init_ta2} g/L")
        c2.metric("Estimated TA", f"{impact['estimated_new_ta']} g/L", delta=f"-{impact['ta_drop']}")
        c3.metric("Initial pH", f"{init_ph2}")
        c4.metric("Estimated pH", f"{impact['estimated_new_ph']}", delta=f"+{impact['ph_rise']}")

# ─────────────────────────────────────────────────────────────────────────────
# 13. COLD STABILIZATION
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_cold_stab"):
    st.markdown("## ❄️ Cold Stabilization")
    tab1, tab2 = st.tabs(["Target parameters", "Conductivity stability"])
    with tab1:
        c1,c2,c3 = st.columns(3)
        with c1: alc = st.number_input("Alcohol (% ABV)", 8.0, 17.0, 13.0, 0.1)
        with c2: ta_cs = st.number_input("TA (g/L)", 3.0, 12.0, 6.5, 0.1)
        with c3: vol_cs = st.number_input(t("volume_l"), 100.0, 500000.0, 5000.0, 500.0, key="vol_cs")
        res = cold_stabilization(alc, ta_cs, vol_cs)
        c1,c2,c3 = st.columns(3)
        c1.metric("Stabilization Temp", f"{res['stabilization_temp_c']}°C")
        c2.metric("Traditional Duration", f"{res['traditional_duration_days']} days")
        c3.metric("Mini-Contact Duration", f"{res['mini_contact_duration_hours']} hours")
        st.markdown(f'<div class="info-box">💡 Add {res["kht_seed_g"]} g of KHT seeds at {res["stabilization_temp_c"]}°C.</div>', unsafe_allow_html=True)
    with tab2:
        c1,c2 = st.columns(2)
        with c1: cond_before = st.number_input("Conductivity before stabilizing (mS/cm)", 0.5, 5.0, 2.0, 0.01)
        with c2: cond_after = st.number_input("Conductivity after stabilizing (mS/cm)", 0.5, 5.0, 1.85, 0.01)
        res2 = conductivity_test(cond_before, cond_after)
        st.markdown(f"### {res2['verdict']}")
        c1,c2 = st.columns(2)
        c1.metric("Conductivity drop", f"{res2['conductivity_drop_ms']} mS/cm")
        c2.metric("Drop %", f"{res2['conductivity_drop_pct']}%")

# ─────────────────────────────────────────────────────────────────────────────
# 14. SORBATE + SO₂
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_sorbate"):
    st.markdown("## 🍯 Sorbate + SO₂ Combo")
    c1,c2,c3,c4 = st.columns(4)
    with c1: rs = st.number_input("Residual Sugar (g/L)", 5.0, 300.0, 40.0, 5.0)
    with c2: ph_sorb = st.number_input("pH", 2.8, 4.5, 3.3, 0.05, key="ph_sorb")
    with c3: vol_sorb = st.number_input(t("volume_l"), 100.0, 500000.0, 1000.0, 100.0, key="vol_sorb")
    with c4: style_sorb = st.selectbox("Style", ["off-dry","demi-sec","sweet"])
    res = sorbate_so2_combo(rs, ph_sorb, vol_sorb, style_sorb)
    c1,c2,c3 = st.columns(3)
    c1.metric("K-Sorbate to add", f"{res['potassium_sorbate_total_g']} g")
    c2.metric("K-Sorbate Rate", f"{res['potassium_sorbate_mg_l']} mg/L")
    c3.metric("Free SO₂ needed", f"{res['free_so2_needed_mg_l']} mg/L")
    st.markdown(f'<div class="danger-box">⚠️ {res["warning"]}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 15. VINEYARD COMPARISON
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_vineyard_comp"):
    st.markdown("## 🗺️ Vineyard Comparison")
    target_style = st.selectbox("Target Style", ["Red","White","Rosé","Sweet"])
    n_vineyards = st.slider("Vineyards to compare", 2, 5, 3)
    vineyard_data = []
    cols = st.columns(n_vineyards)
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"**Vineyard {i+1}**")
            vname = st.text_input("Name", f"Lot {i+1}", key=f"vname_{i}")
            vbrix = st.number_input("Brix", 14.0, 36.0, 22.0+i*0.5, 0.5, key=f"vbrix_{i}")
            vph = st.number_input("pH", 2.8, 4.5, 3.3+i*0.05, 0.05, key=f"vph_{i}")
            vta = st.number_input("TA (g/L)", 3.0, 12.0, 6.5-i*0.2, 0.1, key=f"vta_{i}")
            vyan = st.number_input("YAN (mg/L)", 0.0, 400.0, 120.0+i*20, 10.0, key=f"vyan_{i}")
            vineyard_data.append({"name": vname, "brix": vbrix, "ph": vph, "ta": vta, "yan": vyan})
    results_v = [evaluate_vineyard(v["name"], v["brix"], v["ph"], v["ta"], v["yan"], target_style) for v in vineyard_data]
    results_v.sort(key=lambda x: x["score"], reverse=True)
    st.markdown("### 🏆 Rankings")
    for r in results_v:
        st.markdown(f"<div class='logbook-entry'><span class='grade-badge grade-{r['grade']}'>{r['grade']}</span> <strong>{r['name']}</strong> — Score: {r['score']}/100</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 16. VINTAGE LOGBOOK
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_logbook"):
    st.markdown("## 📓 Vintage Logbook")
    with st.expander("➕ Add Logbook Entry", expanded=not st.session_state.vintage_logbook):
        c1,c2,c3 = st.columns(3)
        with c1:
            log_date = st.date_input("Date", value=date.today(), key="log_date")
            log_lot = st.text_input("Lot / Tank", placeholder="e.g. Tank 1", key="log_lot")
        with c2:
            log_category = st.selectbox("Category", ["📥 Reception","🧪 Chemistry","➕ Treatment","🌡️ Temperature","📊 Analysis","🚰 Racking","📝 Note"])
            log_operator = st.text_input("Operator", placeholder="Name", key="log_op")
        with c3: log_entry = st.text_area("Description", key="log_entry")
        if st.button("Save Entry"):
            if log_entry.strip():
                st.session_state.vintage_logbook.append({"date": str(log_date), "lot": log_lot, "category": log_category, "operator": log_operator, "entry": log_entry})
                st.success("Saved!")
                st.rerun()
    if st.session_state.vintage_logbook:
        st.dataframe(pd.DataFrame(st.session_state.vintage_logbook), use_container_width=True)
        if st.button("Clear Logbook"): st.session_state.vintage_logbook = []; st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# 17. BOTTLING SUITE (V4)
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_bottling"):
    st.markdown(f"## {t('bottling_title')}")
    st.markdown(f"*{t('bottling_subtitle')}*")
    
    tab1, tab2 = st.tabs(["📦 Bottle & Case Needs", "🌡️ Thermal Expansion"])
    
    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1: total_volume = st.number_input("Total Bulk Volume (L)", 10.0, 100000.0, 1000.0, 100.0)
        with c2: bottle_size = st.selectbox("Bottle Size (mL)", [750.0, 375.0, 1500.0, 500.0])
        with c3: loss_rate = st.slider("Expected Loss (%)", 0.0, 10.0, 2.0, 0.5)
        
        bn = bottles_needed(total_volume, bottle_size, loss_rate)
        
        st.markdown(f"""
        <div class="result-card">
          <h3>📦 Packaging Breakdown</h3>
          <div class="metric-row">
            <span class="metric-value">{bn['total_bottles']}</span>
            <span class="metric-unit">bottles</span>
          </div>
          <p style="color:#8B949E; margin-top:8px;">
            Estimated loss: <strong>{bn['lost_volume_l']} L</strong> | Net bottling volume: <strong>{bn['net_bottling_volume_l']} L</strong>
          </p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.metric("Cases of 12", f"{bn['cases_of_12']} cases (+ {bn['remaining_bottles_12']} bottles)")
        c2.metric("Cases of 6", f"{bn['cases_of_6']} cases (+ {bn['remaining_bottles_6']} bottles)")
        
        record_calc("Bottling Plan", {
            "Total Volume": f"{total_volume} L",
            "Bottle Size": f"{bottle_size} mL",
            "Total Bottles Required": bn['total_bottles'],
            "12-bottle Cases": bn['cases_of_12'],
        })

    with tab2:
        st.markdown("*Calculate expansion/contraction risks based on temperature change.*")
        c1, c2, c3 = st.columns(3)
        with c1: vol_exp = st.number_input("Bulk Volume (L)", 10.0, 100000.0, 1000.0, 100.0, key="vol_exp")
        with c2: temp_bot = st.number_input("Bottling Temp (°C)", 5.0, 30.0, 14.0, 1.0)
        with c3: temp_store = st.number_input("Max Storage/Transit Temp (°C)", 5.0, 45.0, 32.0, 1.0)
        
        exp = thermal_expansion(vol_exp, temp_bot, temp_store)
        
        c1, c2 = st.columns(2)
        c1.metric("Total Volume Change", f"{exp['volume_change_l']:+.2f} L")
        c2.metric("Change per 750ml Bottle", f"{exp['per_bottle_change_ml']:+.2f} mL")
        
        if exp["is_expansion"]:
            st.warning(exp["warning"])
        else:
            st.info(exp["warning"])

# ─────────────────────────────────────────────────────────────────────────────
# 18. OAK & TANNINS (V4)
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_oak"):
    st.markdown(f"## {t('oak_title')}")
    st.markdown(f"*{t('oak_subtitle')}*")
    
    c1, c2, c3 = st.columns(3)
    with c1: volume_oak = st.number_input("Wine Volume (L)", 10.0, 500000.0, 1000.0, 100.0, key="vol_oak")
    with c2: format_oak = st.selectbox("Oak Alternative Format", ["chips", "cubes", "staves"])
    with c3:
        default_rate = {"chips": 2.0, "cubes": 4.0, "staves": 1.5}[format_oak]
        rate_oak = st.number_input("Dosage Rate (g/L)", 0.1, 10.0, default_rate, 0.1)
        
    od = oak_dosage(volume_oak, rate_oak, format_oak)
    
    st.markdown(f"""
    <div class="result-card">
      <h3>🪵 Oak Dose Plan</h3>
      <div class="metric-row">
        <span class="metric-value">{od['total_kg']}</span>
        <span class="metric-unit">kg total</span>
      </div>
      <p style="color:#c9956a; font-weight:600; margin-top:8px;">
        Format: {format_oak.title()} | Extraction Time: {od['extraction_time']}
      </p>
      <p style="color:#8B949E; font-size:0.9rem;">
        {od['note']}
      </p>
    </div>
    """, unsafe_allow_html=True)
    
    if "staves_needed" in od:
        st.metric("Estimated Staves Needed", f"{od['staves_needed']} (assuming ~250g per stave)")
        
    record_calc("Oak Treatment Plan", {
        "Format": format_oak.title(),
        "Dosage Rate": f"{rate_oak} g/L",
        "Total Oak": f"{od['total_kg']} kg",
        "Extraction time": od['extraction_time']
    })

# ─────────────────────────────────────────────────────────────────────────────
# 19. WINE FAULT DIAGNOSIS (V4)
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_faults"):
    st.markdown(f"## {t('calc_faults')}")
    st.markdown(f"*{t('faults_subtitle')}*")
    
    st.markdown("### 👃 Select Symptoms Observed:")
    
    symptoms_pool = []
    for f in WINE_FAULTS:
        symptoms_pool.extend(f["symptoms"])
    symptoms_pool = sorted(list(set(symptoms_pool)))
    
    selected_syms = st.multiselect("Symptoms", [s.replace("_", " ").title() for s in symptoms_pool])
    
    if selected_syms:
        # Convert back to internal symptom keys
        internal_syms = [s.lower().replace(" ", "_") for s in selected_syms]
        diagnoses = diagnose_fault(internal_syms)
        
        if diagnoses:
            st.markdown("### 📋 Diagnosis Report")
            for d in diagnoses:
                st.markdown(f"""
                <div class="logbook-entry" style="border-left: 4px solid #c03030;">
                  <h4 style="color:#FF6B6B; font-family:'Inter',sans-serif; margin-bottom:6px;">
                    {d['name']} ({d['confidence']}% Confidence)
                  </h4>
                  <p><strong>Common symptoms match:</strong> {", ".join(d['common_symptoms'])}</p>
                  <p style="margin-top:6px;"><strong>Cause:</strong> {d['cause']}</p>
                  <p style="color:#90c090; margin-top:6px;"><strong>💡 Prevention:</strong> {d['prevention']}</p>
                  <p style="color:#c0a060; margin-top:4px;"><strong>🧪 Cellar Treatment:</strong> {d['treatment']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No matching faults found for the selected symptoms.")
    else:
        st.info("Select one or more symptoms from the dropdown above to run diagnosis.")

# ─────────────────────────────────────────────────────────────────────────────
# 20. GREEK VARIETIES (V4)
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_greek"):
    st.markdown(f"## {t('greek_title')}")
    st.markdown(f"*{t('greek_subtitle')}*")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        selected_variety = st.selectbox("Greek Grape Variety", list(GREEK_VARIETIES.keys()))
        var_data = GREEK_VARIETIES[selected_variety]
        st.markdown(f"""
        <div class="result-card">
          <h3 style="color:#c9956a !important; margin-bottom:8px;">{selected_variety} ({var_data['style']})</h3>
          <p style="font-size:0.92rem; color:#e8d5b7; line-height:1.5;">{var_data['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("### 📊 Benchmark Your Lot Metric")
        c1, c2, c3 = st.columns(3)
        with c1: my_brix = st.number_input("My Lot Brix", 14.0, 35.0, 23.0)
        with c2: my_ph = st.number_input("My Lot pH", 2.8, 4.5, 3.25)
        with c3: my_ta = st.number_input("My Lot TA (g/L)", 3.0, 12.0, 7.0)
        
        # Benchmarking visualization
        metrics = ["Brix", "pH", "TA"]
        my_vals = [my_brix, my_ph, my_ta]
        opt_ranges = [var_data["optimal_brix"], var_data["optimal_ph"], var_data["optimal_ta"]]
        
        st.markdown("#### Comparison to Optimal Harvest Range:")
        for met, val, (lo, hi) in zip(metrics, my_vals, opt_ranges):
            status = "🟢 Within Range"
            color = "#3FB950"
            if val < lo:
                status = f"🔻 Low (optimal: {lo}-{hi})"
                color = "#FF8C42"
            elif val > hi:
                status = f"🔺 High (optimal: {lo}-{hi})"
                color = "#F85149"
                
            st.markdown(f"""
            <div style="background:rgba(30,15,25,0.4); border-left:3px solid {color}; padding:8px 12px; margin-bottom:6px; border-radius: 0 6px 6px 0;">
              <strong style="color:#c9956a;">{met}:</strong> {val} | <span style="color:{color}; font-weight:600;">{status}</span>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 21. VINTAGE COMPARISON (V4)
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_vintage_comp"):
    st.markdown(f"## 📊 Vintage Comparison Dashboard")
    st.markdown("*Track and analyze vintage variations over multiple harvest years.*")
    
    with st.expander("➕ Add Historic Vintage Log"):
        c1, c2, c3, c4 = st.columns(4)
        with c1: v_year = st.number_input("Year", 2000, 2030, 2026)
        with c2: v_var = st.selectbox("Variety", list(GREEK_VARIETIES.keys()))
        with c3: v_brix = st.number_input("Harvest Brix", 14.0, 35.0, 23.0, key="vbrix")
        with c4: v_ph = st.number_input("Harvest pH", 2.8, 4.5, 3.2, key="vph")
        v_ta = st.number_input("Harvest TA (g/L)", 3.0, 12.0, 7.0, key="vta")
        
        if st.button("Add Vintage Data"):
            st.session_state.vintage_history.append({
                "Year": v_year, "Variety": v_var, "Brix": v_brix, "pH": v_ph, "TA": v_ta
            })
            st.success("Vintage data added!")
            st.rerun()
            
    if st.session_state.vintage_history:
        df_hist = pd.DataFrame(st.session_state.vintage_history)
        df_hist = df_hist.sort_values("Year")
        
        vars_available = df_hist["Variety"].unique()
        sel_var = st.selectbox("Select Variety to Plot", vars_available)
        
        df_filtered = df_hist[df_hist["Variety"] == sel_var]
        
        if not df_filtered.empty:
            fig = px.line(df_filtered, x="Year", y=["Brix", "TA", "pH"], markers=True, 
                          title=f"📈 Vintage Trends for {sel_var}",
                          color_discrete_sequence=["#c9956a", "#5a8fd0", "#6aad6a"])
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(15,8,12,0.9)", plot_bgcolor="rgba(20,10,18,0.8)", font=dict(color="#c9956a"))
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        else:
            st.info("No historical logs found for this variety.")

# ─────────────────────────────────────────────────────────────────────────────
# 22. AI FERMENTATION PREDICTOR (SCIKIT-LEARN)
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_ai_ferment"):
    st.markdown(f"## 🤖 AI Fermentation Predictor")
    st.markdown("*Machine Learning forecasting using Polynomial Regression.*")
    
    if not st.session_state.fermentation_data:
        st.warning("⚠️ No fermentation data found. Please add data in the 'Fermentation Tracker' first.")
    else:
        df = pd.DataFrame(st.session_state.fermentation_data)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        
        # Convert dates to 'days since start'
        start_date = df["date"].iloc[0]
        hist_data = []
        for i, row in df.iterrows():
            days_passed = (row["date"] - start_date).days
            hist_data.append({"day": days_passed, "brix": float(row["brix"])})
            
        current_brix = hist_data[-1]["brix"]
        
        c1, c2 = st.columns(2)
        with c1: target_brix = st.number_input("Target Brix (Dryness)", -2.0, 5.0, 0.0, 0.5)
        with c2:
            st.markdown(f"**Current Brix:** {current_brix}°Bx")
            st.markdown(f"**Days active:** {hist_data[-1]['day']} days")
            
        if st.button("🚀 Run AI Forecast"):
            with st.spinner("Training model..."):
                res = predict_fermentation_curve(hist_data, current_brix, target_brix)
                
            if "error" in res:
                st.error(res["error"])
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Predicted Days to Dry (Total)", f"~{res['days_to_dry_total']} days" if res['days_to_dry_total'] else "Unknown")
                c2.metric("Days Remaining", f"~{res['days_remaining']} days" if res['days_remaining'] else "Unknown")
                
                risk_color = {"Low": "green", "Medium": "orange", "High": "red"}[res["stuck_risk"]]
                c3.markdown(f"**Stuck Risk:** <span style='color:{risk_color}; font-weight:bold;'>{res['stuck_risk']}</span>", unsafe_allow_html=True)
                
                # Plot
                pred_df = pd.DataFrame(res["projected_curve"])
                fig = go.Figure()
                # Actual
                fig.add_trace(go.Scatter(x=[d['day'] for d in hist_data], y=[d['brix'] for d in hist_data], 
                                         name="Actual Brix", line=dict(color="#3FB950", width=3), mode="lines+markers"))
                # Predicted
                if not pred_df.empty:
                    fig.add_trace(go.Scatter(x=pred_df["day"], y=pred_df["brix"], 
                                             name="AI Forecast", line=dict(color="#c9956a", width=2, dash="dot"), mode="lines"))
                
                fig.add_hline(y=target_brix, line_dash="dash", line_color="red", annotation_text="Target")
                fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(15,8,12,0.9)", plot_bgcolor="rgba(20,10,18,0.8)",
                                  title="AI Forecast: Sugar Depletion Curve", xaxis_title="Days", yaxis_title="Brix")
                st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# 23. AI MASTER BLENDER (LLM / BYOK)
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_ai_blend"):
    st.markdown(f"## 🧠 AI Master Blender (Agentic)")
    st.markdown("*LLM-powered blend optimization. Requires API Key (OpenAI or DeepSeek).*")
    
    api_key = st.text_input("Enter API Key (sk-...)", type="password", help="Your key is not stored. It is only used for this session.")
    
    target_style = st.text_area("Describe your target wine style", placeholder="e.g. A Bordeaux-style blend with high tannins, good acidity, and dark fruit notes.")
    
    st.markdown("### Input Base Wines (Lots)")
    lots = st.text_area("Describe your available lots", height=150,
                        placeholder="Lot A: Cabernet Sauvignon, 14% ABV, pH 3.6, high pyrazines.\nLot B: Merlot, 14.5% ABV, pH 3.8, very fruity and soft.\nLot C: Petit Verdot, 13.5% ABV, high acidity, intense color.")
                        
    if st.button("🔮 Generate Blend Strategy"):
        if not api_key:
            st.error("Please enter an API Key to use the Agentic Master Blender.")
        elif not target_style or not lots:
            st.warning("Please fill in both the target style and the available lots.")
        else:
            with st.spinner("AI is analyzing profiles..."):
                res = generate_blending_advice(api_key, lots, target_style)
                
            if "error" in res:
                st.error(f"Error from AI: {res['error']}")
            else:
                st.markdown("### 🧑‍🔬 AI Master Blender Recommendation")
                st.markdown(f"<div class='result-card' style='font-family: Inter;'>{res['result']}</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 24. EXPORT PDF
# ─────────────────────────────────────────────────────────────────────────────
elif calculator == t("calc_export"):
    st.markdown(f"## {t('export_title')}")
    st.markdown(f"*{t('export_subtitle')}*")
    if not st.session_state.pdf_calculations:
        st.info(f"📋 {t('no_calcs')}")
    else:
        st.success(f"✅ {len(st.session_state.pdf_calculations)} calculation(s) ready.")
        for calc in st.session_state.pdf_calculations:
            with st.expander(f"📌 {calc['title']}"):
                for k,v in calc["results"].items():
                    st.markdown(f"**{k}:** {v}")
        try:
            pdf_bytes = generate_pdf(st.session_state.pdf_calculations)
            st.download_button(label=t("download_pdf"), data=pdf_bytes,
                               file_name=f"winemaking_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                               mime="application/pdf")
        except Exception as e:
            st.error(f"PDF error: {e}")
        if st.button("🗑️ Clear"):
            st.session_state.pdf_calculations = []
            st.rerun()

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown(f"""
<p style='text-align:center;color:#4a3020;font-size:0.8rem;'>
  🍷 Winemaking Calculators v4.0 | Built with ❤️ by <a href='https://github.com/karidasd' style='color:#7a5040;'>DarkAIs</a> | {t('footer')}
</p>""", unsafe_allow_html=True)
