"""
app.py — NYC 311 Service Requests Dashboard
EDA Course Project  |  SAP ID: 70176600
Dataset: rows.csv  (Open Data NYC)
Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np

from filters import load_data, apply_filters, get_top_n
import charts as ch

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="NYC 311 Dashboard | SAP 70176600",
    page_icon="🗽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── global ── */
html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

/* ── header ── */
.dash-title {
    background: linear-gradient(135deg, #1565C0 0%, #0288D1 100%);
    color: white;
    padding: 1.2rem 2rem;
    border-radius: 12px;
    margin-bottom: 1rem;
}
.dash-title h1 { margin: 0; font-size: 1.8rem; }
.dash-title p  { margin: 0; opacity: 0.9; font-size: 0.95rem; }

/* ── KPI cards ── */
.kpi-card {
    background: white;
    border: 1px solid #E0E6EF;
    border-left: 5px solid #1565C0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 6px rgba(0,0,0,.06);
}
.kpi-label { color: #757575; font-size: 0.82rem; font-weight: 600; text-transform: uppercase; letter-spacing: .05em; }
.kpi-value { color: #1565C0; font-size: 2rem; font-weight: 700; line-height: 1.2; }
.kpi-sub   { color: #9E9E9E; font-size: 0.78rem; margin-top: 2px; }

/* ── section headers ── */
.section-header {
    color: #1A237E;
    font-size: 1.05rem;
    font-weight: 700;
    border-bottom: 2px solid #1565C0;
    padding-bottom: 4px;
    margin: 1.2rem 0 0.8rem 0;
}
</style>
""", unsafe_allow_html=True)

# ─── LOAD DATA ───────────────────────────────────────────────────────────────

df = load_data("data/rows.csv")

# ─── HEADER ──────────────────────────────────────────────────────────────────

st.markdown("""
<div class="dash-title">
    <h1>🗽 NYC 311 Service Requests Dashboard</h1>
    <p>Exploratory Data Analysis  ·  SAP ID: 70176600  ·  Dataset: rows.csv (Open Data NYC)</p>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR FILTERS ─────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/311_logo.svg/200px-311_logo.svg.png",
             width=80)
    st.markdown("## 🔍 Filters")
    st.caption("All charts update simultaneously when any filter changes.")

    # 1. Date range
    if "created_date" in df.columns:
        min_d = df["created_date"].min().date()
        max_d = df["created_date"].max().date()
        date_range = st.date_input("📅 Date Range",
                                   value=(min_d, max_d),
                                   min_value=min_d, max_value=max_d)
    else:
        date_range = None

    # 2. Borough (category)
    boroughs_all = sorted(df["borough"].dropna().unique().tolist()) if "borough" in df.columns else []
    selected_boroughs = st.multiselect("🗺️ Borough", boroughs_all, default=boroughs_all,
                                       help="Select one or more boroughs")

    # 3. Complaint type multi-select
    top_types = df["complaint_type"].value_counts().head(30).index.tolist() if "complaint_type" in df.columns else []
    selected_types = st.multiselect("📋 Complaint Type (Top 30)",
                                    top_types, default=[],
                                    help="Leave empty to include all types")

    # 4. Resolution days slider
    if "resolution_days" in df.columns:
        max_days = float(df["resolution_days"].quantile(0.95))
        res_range = st.slider("⏱️ Resolution Days (0–95th %ile)",
                              0.0, max_days, (0.0, max_days), step=0.5)
    else:
        res_range = None

    # 5. Keyword search
    keyword = st.text_input("🔎 Keyword Search (Descriptor)", "",
                            placeholder="e.g. noise, water, heat…")

    # 6. Reset button
    if st.button("🔄 Reset All Filters"):
        st.rerun()

# ─── APPLY FILTERS ───────────────────────────────────────────────────────────

filter_dict = {
    "date_range":      date_range if isinstance(date_range, tuple) and len(date_range) == 2 else None,
    "boroughs":        selected_boroughs if selected_boroughs else None,
    "complaint_types": selected_types if selected_types else None,
    "res_days_range":  res_range,
    "keyword":         keyword if keyword.strip() else None,
}

fdf = apply_filters(df, filter_dict)

# ─── KPI CARDS ───────────────────────────────────────────────────────────────

total   = len(fdf)
avg_res = fdf["resolution_days"].mean() if "resolution_days" in fdf.columns else 0
top_c   = fdf["complaint_type"].value_counts().idxmax() if "complaint_type" in fdf.columns and total else "N/A"
top_b   = fdf["borough"].value_counts().idxmax() if "borough" in fdf.columns and total else "N/A"

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Total Records</div>
        <div class="kpi-value">{total:,}</div>
        <div class="kpi-sub">After applied filters</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Avg. Resolution Time</div>
        <div class="kpi-value">{avg_res:.1f} <span style="font-size:1rem">days</span></div>
        <div class="kpi-sub">Mean across closed cases</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Top Complaint</div>
        <div class="kpi-value" style="font-size:1.1rem">{top_c}</div>
        <div class="kpi-sub">Most frequent type</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">Busiest Borough</div>
        <div class="kpi-value" style="font-size:1.3rem">{top_b}</div>
        <div class="kpi-sub">Highest complaint volume</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── CHARTS ──────────────────────────────────────────────────────────────────

if total == 0:
    st.warning("⚠️ No records match the current filters. Please adjust your selections.")
    st.stop()

# Row 1 — Pie  +  Line
st.markdown('<p class="section-header">📊 Distribution & Trend Overview</p>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 2])
with col1:
    st.pyplot(ch.chart_pie(fdf), use_container_width=True)
with col2:
    st.pyplot(ch.chart_line(fdf), use_container_width=True)

# Row 2 — Bar  +  Histogram
st.markdown('<p class="section-header">📈 Complaint Types & Resolution Time</p>', unsafe_allow_html=True)
col3, col4 = st.columns(2)
with col3:
    st.pyplot(ch.chart_bar(fdf), use_container_width=True)
with col4:
    st.pyplot(ch.chart_histogram(fdf), use_container_width=True)

# Row 3 — Heatmap (full width)
st.markdown('<p class="section-header">🗓️ Temporal Patterns</p>', unsafe_allow_html=True)
st.pyplot(ch.chart_heatmap(fdf), use_container_width=True)

# Row 4 — Area  +  Count Plot
st.markdown('<p class="section-header">📉 Borough Trends & Status Breakdown</p>', unsafe_allow_html=True)
col5, col6 = st.columns(2)
with col5:
    st.pyplot(ch.chart_area(fdf), use_container_width=True)
with col6:
    st.pyplot(ch.chart_countplot(fdf), use_container_width=True)

# Row 5 — Box  +  Violin
st.markdown('<p class="section-header">📦 Resolution Time Distributions</p>', unsafe_allow_html=True)
col7, col8 = st.columns(2)
with col7:
    st.pyplot(ch.chart_box(fdf), use_container_width=True)
with col8:
    st.pyplot(ch.chart_violin(fdf), use_container_width=True)

# Row 6 — Scatter (full width)
st.markdown('<p class="section-header">🔵 Relationship Analysis</p>', unsafe_allow_html=True)
st.pyplot(ch.chart_scatter(fdf), use_container_width=True)

# ─── RAW DATA PREVIEW ────────────────────────────────────────────────────────

st.markdown('<p class="section-header">📄 Raw Data Preview</p>', unsafe_allow_html=True)
st.dataframe(fdf.head(500), use_container_width=True, height=280)
st.caption(f"Showing first 500 rows of {total:,} filtered records.")

# ─── FOOTER ──────────────────────────────────────────────────────────────────

st.markdown("""
<hr style="border:1px solid #E0E6EF; margin-top:2rem">
<p style="text-align:center; color:#9E9E9E; font-size:0.82rem">
    NYC 311 Dashboard · SAP ID 70176600 · EDA Course · Dataset: <code>rows.csv</code> (Open Data NYC)
</p>
""", unsafe_allow_html=True)
