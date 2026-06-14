"""
filters.py - Data loading, cleaning, and filtering functions
NYC 311 Service Requests Dashboard
SAP ID: 70176600
"""

import pandas as pd
import numpy as np
import streamlit as st


# ─── DATA LOADING & CLEANING ────────────────────────────────────────────────

@st.cache_data(show_spinner="Loading dataset…")
def load_data(filepath: str = "data/rows.csv") -> pd.DataFrame:
    """Load and clean the NYC 311 dataset."""
    df = pd.read_csv(filepath, low_memory=False)

    # Standardise column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("-", "_")

    # Parse dates
    for col in ["created_date", "closed_date", "resolution_action_updated_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Derived columns
    if "created_date" in df.columns:
        df["year"]  = df["created_date"].dt.year
        df["month"] = df["created_date"].dt.month
        df["month_name"] = df["created_date"].dt.strftime("%b")
        df["day_of_week"] = df["created_date"].dt.day_name()
        df["hour"] = df["created_date"].dt.hour

    if "created_date" in df.columns and "closed_date" in df.columns:
        df["resolution_days"] = (
            df["closed_date"] - df["created_date"]
        ).dt.total_seconds() / 86400
        df["resolution_days"] = df["resolution_days"].clip(lower=0)

    # Drop rows with no complaint type
    if "complaint_type" in df.columns:
        df = df.dropna(subset=["complaint_type"])

    return df


# ─── FILTER HELPERS ──────────────────────────────────────────────────────────

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply all sidebar filters and return the filtered dataframe."""
    fdf = df.copy()

    # Date range filter
    if filters.get("date_range") and "created_date" in fdf.columns:
        start, end = filters["date_range"]
        fdf = fdf[
            (fdf["created_date"].dt.date >= start) &
            (fdf["created_date"].dt.date <= end)
        ]

    # Borough (category) filter
    if filters.get("boroughs") and "borough" in fdf.columns:
        fdf = fdf[fdf["borough"].isin(filters["boroughs"])]

    # Complaint type multi-select
    if filters.get("complaint_types") and "complaint_type" in fdf.columns:
        fdf = fdf[fdf["complaint_type"].isin(filters["complaint_types"])]

    # Resolution days slider
    if filters.get("res_days_range") and "resolution_days" in fdf.columns:
        lo, hi = filters["res_days_range"]
        fdf = fdf[
            (fdf["resolution_days"] >= lo) &
            (fdf["resolution_days"] <= hi)
        ]

    # Keyword / text search
    if filters.get("keyword") and "descriptor" in fdf.columns:
        kw = filters["keyword"].lower()
        fdf = fdf[fdf["descriptor"].str.lower().str.contains(kw, na=False)]

    return fdf


def get_top_n(df: pd.DataFrame, col: str, n: int = 10) -> pd.Series:
    """Return value counts for the top-N entries in a column."""
    return df[col].value_counts().head(n)
