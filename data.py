"""Simulated bank loan portfolio (2025 – 2026)."""
import numpy as np
import pandas as pd

PROVINCES = {"QC": (46.8, -71.2), "ON": (43.7, -79.4), "BC": (49.3, -123.1), "AB": (51.0, -114.1), "MB": (49.9, -97.1),
             "SK": (52.1, -106.7), "NS": (44.6, -63.6), "NB": (45.9, -66.6), "NL": (47.6, -52.7), "PE": (46.2, -63.1)}
PURPOSES = ["Debt consolidation", "Credit card", "Home improvement", "Car", "Small business", "Medical", "Education", "Other"]


def simulate(n=12000, seed=13):
    r = np.random.default_rng(seed)
    issue = pd.to_datetime("2025-01-01") + pd.to_timedelta(r.integers(0, 638, n), unit="D")
    grade = r.choice(list("ABCDEFG"), n, p=[.2, .3, .22, .14, .08, .04, .02])
    rate = np.array([7, 10.5, 13.5, 16.5, 19.5, 23, 26])[pd.Series(grade).map(dict(zip("ABCDEFG", range(7)))).to_numpy()] + r.normal(0, .8, n)
    amount = (r.lognormal(9.3, 0.55, n).clip(1000, 40000) / 25).round() * 25
    term = r.choice([36, 60], n, p=[.73, .27])
    bad_p = np.array([.03, .06, .1, .15, .2, .26, .32])[pd.Series(grade).map(dict(zip("ABCDEFG", range(7)))).to_numpy()]
    u = r.random(n)
    months = ((pd.Timestamp("2026-10-31") - issue).days / 30.4).to_numpy()
    status = np.where(u < bad_p, "Charged Off", np.where(u < bad_p + .03, "Late", np.where(r.random(n) < months / term * 1.6, "Fully Paid", "Current")))
    paid_frac = np.where(status == "Fully Paid", 1 + rate / 100 * term / 24,
                         np.where(status == "Charged Off", r.uniform(.1, .6, n), (months / term).clip(0, 1) * (1 + rate / 100 * term / 24)))
    return pd.DataFrame({
        "loan_id": np.arange(100001, 100001 + n), "issue_date": issue, "province": r.choice(list(PROVINCES), n, p=[.25, .35, .13, .1, .04, .03, .03, .03, .02, .02]),
        "purpose": r.choice(PURPOSES, n, p=[.45, .15, .1, .08, .06, .05, .04, .07]), "grade": grade, "term_months": term,
        "employment_length": r.choice(["< 1 yr", "1-3 yrs", "4-6 yrs", "7-9 yrs", "10+ yrs"], n, p=[.1, .25, .22, .15, .28]),
        "home_ownership": r.choice(["Rent", "Mortgage", "Own"], n, p=[.45, .45, .1]),
        "annual_income": r.lognormal(11.1, .45, n).round(-2), "dti": (r.beta(2, 5, n) * 40).round(2),
        "int_rate": rate.round(2), "funded_amount": amount, "total_received": (amount * paid_frac).round(2), "loan_status": status,
    })
