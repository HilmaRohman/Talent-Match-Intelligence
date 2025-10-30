# 🎯 AI Talent Matching Dashboard

A parameterized, AI-powered interface that transforms SQL talent matching results into actionable insights through dynamic visualizations and AI-generated profiles.

## 🚀 Features

- **Runtime Parameterized Inputs**: Role name, job level, purpose, benchmark selection
- **AI-Generated Job Profiles**: Automated requirements, descriptions, and competencies
- **ML-Driven Matching**: Weights derived from 93% accuracy ML analysis
- **Interactive Dashboard**: Match distributions, strengths analysis, candidate comparisons
- **Dynamic SQL Execution**: Recompute baselines and rerun queries without code changes

## 📋 Step 3 Requirements Met

### ✅ Inputs (Runtime, User-Provided)
- Role name, Job level, Role purpose, Selected benchmark employee IDs

### ✅ Dynamic Logic
1. Records new job_vacancy_id automatically
2. Recomputed baselines from selected benchmarks
3. Parameterized SQL query execution
4. Regenerates profiles, rankings, visuals without code editing

### ✅ Outputs
1. AI-Generated Job Profile (requirements, description, competencies)
2. Ranked Talent List with match rates and supporting fields
3. Interactive Dashboard Visualizations

## 🛠 Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
Configure database in .streamlit/secrets.toml

Run the application:
streamlit run app.py
```
