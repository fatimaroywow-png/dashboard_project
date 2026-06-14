# NYC 311 Service Requests Dashboard
**EDA Course Project · SAP ID: 70176600**  
**Dataset:** `rows.csv` (Open Data NYC · SAP ID 70176600)  
**Instructor:** Ali Hassan Sherazi · Course: Exploratory Data Analysis

---

## Project Overview
An interactive data-visualization dashboard built on the **NYC 311 Service Requests** open dataset.  
It presents insights through 10 required chart types with fully linked sidebar filters.

---

## Quick Start

### 1. Clone / unzip the project
```bash
unzip dashboard_project.zip
cd dashboard_project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Place the dataset
Put the exact file (`rows.csv`) inside the `data/` folder — **do not rename it**.

### 4. Run the dashboard
```bash
streamlit run app.py
```
The dashboard opens automatically at `http://localhost:8501`

---

## Folder Structure
```
dashboard_project/
├── data/
│   └── rows.csv              ← EXACT file name, do NOT rename
├── notebooks/
│   └── analysis.ipynb        ← EDA notebook
├── app.py                    ← Main Streamlit dashboard
├── charts.py                 ← All 10 chart functions
├── filters.py                ← Data loading, cleaning & filter logic
├── requirements.txt
└── README.md
```

---

## Required Chart Types (all 10 implemented)

| # | Chart | Purpose |
|---|-------|---------|
| 1 | Pie Chart | Complaint share by Borough |
| 2 | Histogram | Resolution-time frequency distribution |
| 3 | Line Chart | Monthly complaint volume trend |
| 4 | Bar Chart | Top-15 complaint types |
| 5 | Scatter Plot | Hour of day vs. resolution time by Borough |
| 6 | Box Plot | Resolution time spread per Borough |
| 7 | Heatmap | Complaints: Day-of-week × Hour-of-day |
| 8 | Area Chart | Cumulative monthly complaints by Borough |
| 9 | Count Plot | Complaint count by Status |
| 10 | Violin Plot | Resolution-time distribution by Borough |

---

## Dashboard Filters (all linked to every chart)

| Filter | Type |
|--------|------|
| Date Range | Date picker |
| Borough | Multi-select |
| Complaint Type (Top 30) | Multi-select |
| Resolution Days | Range slider |
| Keyword Search | Text input |
| Reset All Filters | Button |

---

## Key Insights
- **Noise-related complaints** (Noise – Residential, Noise – Street/Sidewalk) consistently rank as the top complaint categories across all boroughs.
- **Brooklyn** generates the highest absolute volume of 311 requests.
- Complaint filings peak between **8 AM and 8 PM**, with a notable afternoon surge.
- **Weekdays** see higher complaint volumes than weekends overall.
- Median resolution time is notably lower than the mean, indicating a right-skewed distribution driven by a small proportion of very slow cases.
- **Staten Island** shows the longest median resolution time despite having the fewest complaints.

---

## Technical Stack

| Component | Tool |
|-----------|------|
| Language | Python 3.x |
| Data processing | Pandas, NumPy |
| Visualisation | Matplotlib, Seaborn |
| Dashboard | Streamlit |

---

*All code and insights are original work. Dataset file `rows.csv` has not been renamed.*
