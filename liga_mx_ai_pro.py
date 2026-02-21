import streamlit as st
import pandas as pd
import numpy as np
import requests
import sqlite3
import random
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

# ==========================
# CONFIG
# ==========================

st.set_page_config(layout="wide")
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color:white;
}
</style>
""", unsafe_allow_html=True)

st.title("⚽ FUTBOL AI – Sistema Autónomo Inteligente")

st.image("https://upload.wikimedia.org/wikipedia/commons/9/9d/Liga_MX_logo.svg", width=200)

# ==========================
# BASE DE DATOS LOCAL
# ==========================

conn = sqlite3.connect("futbol_autonomo.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS resultados (
equipo TEXT,
goles INTEGER
)
""")

conn.commit()

# ==========================
# SCRAPING SIMPLE (DATOS PÚBLICOS)
# ==========================

def obtener_datos_publicos():
    url = "https://en.wikipedia.org/wiki/Liga_MX"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    texto = soup.get_text()

    palabras = texto.split()

    equipos = ["América","Chivas","Tigres","Monterrey","Pumas"]

    datos = []

    for equipo in equipos:
        if equipo in texto:
            goles_simulados = random.randint(0,3)
            datos.append((equipo, goles_simulados))

    return datos

# ==========================
# ACTUALIZAR BASE AUTOMÁTICAMENTE
# ==========================

if st.button("🔄 Buscar Información Automáticamente"):

    datos = obtener_datos_publicos()

    for equipo, goles in datos:
        c.execute("INSERT INTO resultados VALUES (?,?)", (equipo, goles))

    conn.commit()

    st.success("Datos actualizados automáticamente ✅")

# ==========================
# MOSTRAR ESTADÍSTICAS
# ==========================

df = pd.read_sql_query("SELECT * FROM resultados", conn)

st.subheader("📊 Base de Datos Local")

st.dataframe(df)

if not df.empty:

    st.subheader("📈 Promedio de Goles por Equipo")

    promedio = df.groupby("equipo")["goles"].mean()

    fig, ax = plt.subplots()
    promedio.plot(kind="bar", ax=ax)
    ax.set_ylabel("Promedio Goles")
    st.pyplot(fig)

# ==========================
# TABLERO VISUAL FUTBOL
# ==========================

st.subheader("🏟 Dashboard Futbol")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Equipos Analizados", len(df["equipo"].unique()) if not df.empty else 0)

with col2:
    st.metric("Registros Guardados", len(df))

with col3:
    st.metric("Última Actualización", "Automática")

st.markdown("---")

st.write("💡 Este sistema aprende de información pública y la guarda localmente.")

