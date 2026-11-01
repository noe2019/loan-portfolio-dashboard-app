import pandas as pd
import plotly.express as px
import streamlit as st

from data import PROVINCES, simulate

st.set_page_config(page_title="Bank Loan Portfolio", page_icon="📊", layout="wide")
st.title("📊 Bank Loan Portfolio Dashboard")
st.caption("Summary · Overview · Details — web version of the Power BI report · simulated portfolio")


@st.cache_data
def load():
    df = simulate()
    df["good_loan"] = df.loan_status.isin(["Fully Paid", "Current"])
    df["month"] = df.issue_date.dt.to_period("M").dt.to_timestamp()
    return df


df = load()
with st.sidebar:
    st.header("Filters")
    prov = st.multiselect("Province", list(PROVINCES), default=list(PROVINCES))
    grades = st.multiselect("Grade", list("ABCDEFG"), default=list("ABCDEFG"))
    term = st.multiselect("Term (months)", [36, 60], default=[36, 60])
    d0, d1 = st.date_input("Issue date", (df.issue_date.min().date(), df.issue_date.max().date()))
    st.markdown("[Portfolio](https://noe2019.github.io/DA-Portfolio-Website/)")

f = df[df.province.isin(prov) & df.grade.isin(grades) & df.term_months.isin(term)
       & df.issue_date.between(pd.Timestamp(d0), pd.Timestamp(d1))]
if f.empty:
    st.warning("No loans match the filters.")
    st.stop()

last = f.month.max()
mtd, prev = f[f.month == last], f[f.month == last - pd.DateOffset(months=1)]


def delta(cur, old):
    return f"{(cur / old - 1):+.1%} MoM" if old else None


k = st.columns(5)
k[0].metric("Loan applications", f"{len(f):,}", delta(len(mtd), len(prev)))
k[1].metric("Funded amount", f"${f.funded_amount.sum() / 1e6:,.1f} M", delta(mtd.funded_amount.sum(), prev.funded_amount.sum()))
k[2].metric("Amount received", f"${f.total_received.sum() / 1e6:,.1f} M", delta(mtd.total_received.sum(), prev.total_received.sum()))
k[3].metric("Avg interest rate", f"{f.int_rate.mean():.2f}%")
k[4].metric("Avg DTI", f"{f.dti.mean():.1f}%")

t1, t2, t3 = st.tabs(["Summary", "Overview", "Details"])
with t1:
    g = st.columns(4)
    good = f[f.good_loan]
    g[0].metric("Good loans", f"{f.good_loan.mean():.1%}")
    g[1].metric("Good loan funded", f"${good.funded_amount.sum() / 1e6:,.1f} M")
    g[2].metric("Bad loans", f"{1 - f.good_loan.mean():.1%}")
    g[3].metric("Bad loan funded", f"${f[~f.good_loan].funded_amount.sum() / 1e6:,.1f} M")
    status = f.groupby("loan_status").agg(applications=("loan_id", "size"), funded=("funded_amount", "sum"),
                                          received=("total_received", "sum"), avg_rate=("int_rate", "mean"), avg_dti=("dti", "mean"))
    st.dataframe(status.style.format({"funded": "${:,.0f}", "received": "${:,.0f}", "avg_rate": "{:.2f}%", "avg_dti": "{:.1f}%"}),
                 use_container_width=True)
    l, r = st.columns(2)
    l.plotly_chart(px.pie(f, names="loan_status", hole=.5, title="Loans by status"), use_container_width=True)
    r.plotly_chart(px.bar(f.groupby("grade").good_loan.mean().reset_index(), x="grade", y="good_loan", title="Good-loan rate by grade",
                          labels={"good_loan": "Good-loan rate"}).update_yaxes(tickformat=".0%"), use_container_width=True)
with t2:
    measure = st.radio("Measure", ["Applications", "Funded amount", "Amount received"], horizontal=True)
    col = {"Applications": "loan_id", "Funded amount": "funded_amount", "Amount received": "total_received"}[measure]
    agg = "size" if col == "loan_id" else "sum"
    l, r = st.columns(2)
    l.plotly_chart(px.area(f.groupby("month")[col].agg(agg).reset_index(), x="month", y=col, title=f"Monthly trend – {measure}"), use_container_width=True)
    pv = f.groupby("province")[col].agg(agg).reset_index()
    pv[["lat", "lon"]] = pv.province.map(PROVINCES).tolist()
    r.plotly_chart(px.scatter_geo(pv, lat="lat", lon="lon", size=col, hover_name="province", scope="north america",
                                  title=f"{measure} by province").update_geos(fitbounds="locations"), use_container_width=True)
    a, b, c = st.columns(3)
    a.plotly_chart(px.bar(f.groupby("purpose")[col].agg(agg).sort_values().reset_index(), x=col, y="purpose", orientation="h", title="By purpose"), use_container_width=True)
    b.plotly_chart(px.pie(f.groupby("term_months")[col].agg(agg).reset_index(), names="term_months", values=col, hole=.5, title="By term"), use_container_width=True)
    c.plotly_chart(px.bar(f.groupby("employment_length")[col].agg(agg).reset_index(), x="employment_length", y=col, title="By employment length",
                          category_orders={"employment_length": ["< 1 yr", "1-3 yrs", "4-6 yrs", "7-9 yrs", "10+ yrs"]}), use_container_width=True)
with t3:
    st.dataframe(f.drop(columns=["good_loan", "month"]).sort_values("issue_date", ascending=False), use_container_width=True, height=480, hide_index=True)
    st.download_button("Download filtered loans (CSV)", f.to_csv(index=False), "loans.csv", "text/csv")
