# Bank Loan Portfolio Dashboard

End-to-end analysis and reporting of a bank loan portfolio (web version of the Power BI report).

**Live app:** https://noe-loan-portfolio-8d5a1d8de0d8.herokuapp.com/
**Portfolio:** https://noe2019.github.io/DA-Portfolio-Website/

## Features
- KPIs: applications, funded and received amounts, average rate and DTI
- Good vs. bad loans
- Monthly trends, purpose, term, grade and province breakdowns
- Interactive filters and detail table

## Tech stack
Python, Pandas, Streamlit, Plotly

## Data
All data in this app is **simulated** (generated in `data.py` with a fixed random seed) to reproduce the structure of the original project without exposing real or confidential records.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment
Deployed on Heroku (stack `heroku-24`, Python 3.12) using the `Procfile` in this repository.

---
Author: Noé Carème Fouotsa Manfouo
