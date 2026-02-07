import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard sprzedaży",
    page_icon="📊",
    layout="wide"
)

st.title("Dashboard Sprzedaży")
st.caption("Dashboard  KPI z filtrem dat, produktów i płci")

#WCZYTANIE DANYCH
df = pd.read_csv("sales.csv", parse_dates=["data"])
df["przychod"]=df["ilosc"]*df["cena"]

#FILTR DATY
with st.sidebar:
    st.header("Filtry")

    min_date = df["data"].min().date()
    max_date = df["data"].max().date()

    st.subheader("Czas")

    sidebar_start, sidebar_end = st.date_input(
        "Zakres dat",
        value=(min_date, max_date),
        min_value = min_date,
        max_value = max_date
    )

df_filtered = df[(df["data"].dt.date>=sidebar_start)&(df["data"].dt.date<=sidebar_end)]

if df_filtered.empty:
    st.warning("Brak danych dla wybranych filtrów")
    st.stop()

#FILTR PŁCI
with st.sidebar:

    st.subheader("Segment")

    plec_options = sorted(df["plec"].dropna().unique())
    selected_plec = st.multiselect(
        "Płeć",
        options = plec_options,
        default = plec_options
    )

df_filtered = df_filtered[df_filtered["plec"].isin(selected_plec)]
if df_filtered.empty:
    st.warning("Brak danych dla wybranych filtrów")
    st.stop()

#FILTR PRODUKTÓW
with st.sidebar:

    st.subheader("Asortyment")

    produkt_options = sorted(df_filtered["produkt"].unique())
    selected_produkty = st.multiselect(
        'Produkty',
        options=produkt_options,
        default=produkt_options
    )
df_filtered = df_filtered[df_filtered["produkt"].isin(selected_produkty)]
if df_filtered.empty:
    st.warning("Brak danych dla wybranych filtrów")
    st.stop()

with st.sidebar:
    st.caption("Dane demonstracyjne")

#KPI
kpi = (
    df_filtered
    .groupby("produkt")
    .agg(
        total_ilosc = ("ilosc", "sum"),
        total_przychod = ("przychod", "sum")
    )
    .reset_index()
)

#METRYKI
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Łączny przychód", f"{kpi['total_przychod'].sum():,.0f} zł")

with col2:
    st.metric("Łączna sprzedaż (szt.)", kpi["total_ilosc"].sum())

with col3:
    st.metric("Liczba produktów", kpi["produkt"].nunique())

#TABELA
st.subheader("KPI każdego produktu")
st.dataframe(kpi)

#PRZYCHOD W CZASIE
przychod_czas = (
    df_filtered
    .groupby(df_filtered["data"].dt.to_period("M"))
    .agg(przychod=("przychod", "sum"))
    .reset_index()
    .rename(columns={"data": "okres"})
)
przychod_czas["okres"] = przychod_czas["okres"].astype(str)

st.subheader("Przychód każdego miesiąca")

st.line_chart(przychod_czas, x="okres", y="przychod")

#TOP PRODUKTÓW
st.subheader("Najlepsze produkty")

metric = st.radio(
    "Metryka rankingu",
    options = ["Przychód","Ilość"],
    horizontal = True
)

top_n = st.slider("Top N", min_value = 1, max_value = int(kpi.shape[0]), value = min(5, int(kpi.shape[0])))

if metric == "Przychód":
    ranking = kpi.sort_values("total_przychod", ascending = False).head(top_n)
    y_col = "total_przychod"
else:
    ranking = kpi.sort_values("total_ilosc", ascending = False).head(top_n)
    y_col = "total_ilosc"

st.bar_chart(ranking, x="produkt", y = y_col)

#UDZIAŁ TOP PRODUKTU
st.subheader("Udział najlepszego produktu")

total_przychod = kpi["total_przychod"].sum()

top_produkt_przychod = (
    kpi
    .sort_values("total_przychod", ascending = False)
    .iloc[0]["total_przychod"]
)

udzial = (top_produkt_przychod/total_przychod)*100

st.metric(
    "Udział najlepszego produktu w przychodzie",
    f"{udzial:.1f}%"
)
