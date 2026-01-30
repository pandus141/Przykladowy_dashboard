import streamlit as st
import pandas as pd

st.title ("Sales dashboard")
st.caption("Dashboard KPI z filtrem produktu")

#WCZYTANIE DANYCH
df = pd.read_csv("data/sales.csv", parse_dates=["date"])
df["revenue"] = df["price"]*df["qty"]

#FILTR DAT
min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.date_input(
    "Zakres dat",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
start_date, end_date = date_range

df_filtered = df[(df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)]

#FILTR PRODUKTOW
products = df["product"].unique()
selected_products = st.multiselect(
    "Wybierz produkty",
    options = products,
    default = products
)
df_filtered = df_filtered[df_filtered["product"].isin(selected_products)]

#KPI
kpi = (
    df_filtered
    .groupby("product")
    .agg(
        total_qty = ("qty", "sum"),
        total_revenue = ("revenue", "sum")
    )
    .reset_index()
)

#METRYKI
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Łączna sprzedaż (szt.)", kpi["total_qty"].sum())

with col2:
    st.metric("Łączny przychód", kpi["total_revenue"].sum())

with col3:
    st.metric("Liczba produktów", kpi["product"].nunique())

#TABELA
st.subheader("KPI per product")
st.dataframe(kpi)

#PRZYCHOD W CZASIE
st.subheader("Przychód w czasie")

granularity = st.radio(
    "Agregacja czasu",
    options = ["Dziennie", "Miesięcznie"],
    horizontal = True
)

if granularity == "Dziennie":
    series = (
        df_filtered
        .groupby(df_filtered["date"].dt.date)
        .agg(revenue=("revenue", "sum"))
        .reset_index()
        .rename(columns={"date": "period"})
    )
else:
    series = (
        df_filtered
        .groupby(df_filtered["date"].dt.to_period("M"))
        .agg(revenue=("revenue", "sum"))
        .reset_index()
        .rename(columns={"date": "period"})
    )
    series["period"] = series["period"].astype(str)

st.line_chart(series, x="period", y="revenue")

#TOP
st.subheader("Top produkty")

metric = st.radio(
    "Metryka rankingu",
    options = ["Przychód", "Ilość"],
    horizontal=True
)

top_n =st.slider("Top N", min_value=1, max_value=int(kpi.shape[0]), value=min(5, int(kpi.shape[0])))

if metric == "Przychód":
    ranking = kpi.sort_values("total_revenue", ascending=False).head(top_n)
    y_col = "total_revenue"
else:
    ranking = kpi.sort_values("total_qty", ascending = False).head(top_n)
    y_col = "total_qty"

st.bar_chart(ranking, x="product", y=y_col)


st.subheader("Udział top produktu")

total_revenue = kpi["total_revenue"].sum()

top_product_revenue = (
    kpi
    .sort_values("total_revenue", ascending = False)
    .iloc[0]["total_revenue"]
)

share = (top_product_revenue / total_revenue) * 100

st.metric(
    "Top produkt - udział w przychodzie",
    f"{share:.1f}%"
)
