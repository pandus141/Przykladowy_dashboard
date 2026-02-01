import streamlit as st
import pandas as pd

streamlit.set_page_config(
    page_title="Dashboard sprzedaży",
    page_icon="📊",
    layout="wide"
)

st.title("Dashboard Sprzedaży")
st.caption("Dashboard  KPI z filtrem dat, produktów i płci")

#WCZYTANIE DANYCH
df = pd.read_csv("sales.csv", parse_dates=["data"])
df["przychod"]=df["ilosc"]*df["cena"]

#FILTR DAT
min_data=df["data"].min().date()
max_data=df["data"].max().date()

zakres_dat = st.date_input(
    "Zakres dat",
    value=(min_data, max_data),
    min_value=min_data,
    max_value=max_data
)
start_data, end_data = zakres_dat

df_filtered = df[(df["data"].dt.date>=start_data)&(df["data"].dt.date<=end_data)]

#FILTR PRODUKTÓW
produkty = df_filtered["produkt"].unique()
wybrane_produkty = st.multiselect(
    "Wybierz produkty",
    options = produkty,
    default = produkty
)
df_filtered = df_filtered[df_filtered["produkt"].isin(wybrane_produkty)]

#FILTR PŁCI
sex = df_filtered["plec"].unique()
wybrana_plec = st.multiselect(
    "Wybierz płeć",
    options = sex,
    default = sex
)
df_filtered = df_filtered[df_filtered["plec"].isin(wybrana_plec)]

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
    st.metric("Łączna sprzedaż (szt.)", kpi["total_ilosc"].sum())

with col2:
    st.metric("Łączny przychód", f"{kpi['total_przychod'].sum():,.0f} zł")

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


