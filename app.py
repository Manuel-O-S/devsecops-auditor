import os
import sqlite3
from contextlib import closing

import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = "seguridad.db"

PESOS = {"Critica": 50, "Alta": 30, "Media": 15, "Baja": 5}
COLORES = {"Critica": "#b91c1c", "Alta": "#ea580c",
           "Media": "#ca8a04", "Baja": "#16a34a"}
ORDEN = ["Critica", "Alta", "Media", "Baja"]

st.set_page_config(page_title="Dashboard DevSecOps", layout="wide")


@st.cache_data(ttl=30)
def cargar_datos():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        return pd.read_sql_query(
            "SELECT * FROM hallazgos ORDER BY fecha DESC", conn)


def estado_actual(df):
    return df.sort_values("fecha").groupby("codigo").tail(1)


def puntaje_riesgo(df):
    return int(min(100, df["severidad"].map(PESOS).fillna(0).sum()))


def nivel_riesgo(puntaje):
    if puntaje >= 75:
        return "Crítico"
    if puntaje >= 50:
        return "Alto"
    if puntaje >= 25:
        return "Medio"
    return "Bajo"


st.title("Dashboard de Auditoría de Seguridad")
st.caption("Hallazgos generados por auditor.py e ingestados en seguridad.db")

if not os.path.exists(DB_PATH):
    st.error("No existe seguridad.db. Ejecuta `python3 ingesta.py` antes de abrir el dashboard.")
    st.stop()

df = cargar_datos()
if df.empty:
    st.success("No hay hallazgos registrados: el sistema no presenta riesgos detectados.")
    st.stop()

with st.sidebar:
    st.header("Filtros")
    severidades = [s for s in ORDEN if s in df["severidad"].unique()]
    categorias = sorted(df["categoria"].unique())
    sev_sel = st.multiselect("Severidad", severidades, default=severidades)
    cat_sel = st.multiselect("Categoría", categorias, default=categorias)
    if st.button("Recargar datos"):
        st.cache_data.clear()
        st.rerun()

filtrado = df[df["severidad"].isin(sev_sel) & df["categoria"].isin(cat_sel)]

puntaje = puntaje_riesgo(estado_actual(df))
c1, c2, c3, c4 = st.columns(4)
c1.metric("Puntaje global de riesgo", f"{puntaje}/100",
          nivel_riesgo(puntaje), delta_color="off")
c2.metric("Hallazgos en el historial", len(filtrado))
c3.metric("Críticos", int((filtrado["severidad"] == "Critica").sum()))
c4.metric("Altos", int((filtrado["severidad"] == "Alta").sum()))
st.progress(puntaje / 100)

if filtrado.empty:
    st.info("Ningún hallazgo coincide con los filtros seleccionados.")
    st.stop()

g1, g2 = st.columns(2)

por_sev = filtrado.groupby("severidad").size().reset_index(name="cantidad")
fig_pie = px.pie(por_sev, names="severidad", values="cantidad",
                 color="severidad", color_discrete_map=COLORES,
                 category_orders={"severidad": ORDEN},
                 hole=0.4, title="Hallazgos por severidad")
g1.plotly_chart(fig_pie)

por_cat = (filtrado.groupby(["categoria", "severidad"])
           .size().reset_index(name="cantidad"))
fig_bar = px.bar(por_cat, x="categoria", y="cantidad", color="severidad",
                 color_discrete_map=COLORES,
                 category_orders={"severidad": ORDEN},
                 labels={"categoria": "Categoría", "cantidad": "Cantidad"},
                 title="Hallazgos por categoría")
g2.plotly_chart(fig_bar)

st.subheader("Detalle de hallazgos")
st.dataframe(
    filtrado[["fecha", "codigo", "categoria", "severidad",
              "descripcion", "recomendacion"]],
    hide_index=True,
)
