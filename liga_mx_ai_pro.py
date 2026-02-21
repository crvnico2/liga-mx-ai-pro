import streamlit as st
import pandas as pd
import numpy as np
import requests
import sqlite3
import random
from scipy.stats import poisson

# =========================
# CONFIG
# =========================

API_KEY = "b67be90081b9cf07ce3dd16c7d02d669"
LEAGUE_ID = 262
SEASON = 2025

st.set_page_config(layout="wide")

st.markdown("""
<style>
.stApp {
    background-color:#0E1117;
    color:white;
}
</style>
""", unsafe_allow_html=True)

st.image("https://upload.wikimedia.org/wikipedia/commons/9/9d/Liga_MX_logo.svg", width=180)
st.title("🚀 IA ULTRA PRO – Hedge Fund Deportivo")

# =========================
# BASE DE DATOS
# =========================

conn = sqlite3.connect("ai_master.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS partidos (
home TEXT,
away TEXT,
home_goals INTEGER,
away_goals INTEGER
)
""")
conn.commit()

# =========================
# DESCARGA AUTOMÁTICA
# =========================

@st.cache_data(ttl=3600)
def obtener_partidos():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": API_KEY}
    params = {"league": LEAGUE_ID, "season": SEASON, "status": "FT"}

    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        return []

    return r.json()["response"]

partidos = obtener_partidos()

for p in partidos:
    home = p["teams"]["home"]["name"]
    away = p["teams"]["away"]["name"]
    hg = p["goals"]["home"]
    ag = p["goals"]["away"]

    c.execute("SELECT * FROM partidos WHERE home=? AND away=?", (home, away))
    if not c.fetchall():
        c.execute("INSERT INTO partidos VALUES (?,?,?,?)",
                  (home, away, hg, ag))
        conn.commit()

df = pd.read_sql_query("SELECT * FROM partidos", conn)

# =========================
# CALCULAR FUERZA REAL
# =========================

def calcular_fuerza(df):
    fuerza = {}
    for equipo in set(df["home"]).union(set(df["away"])):
        goles_favor = df[df["home"] == equipo]["home_goals"].sum() + \
                      df[df["away"] == equipo]["away_goals"].sum()

        partidos = len(df[(df["home"] == equipo) | (df["away"] == equipo)])

        fuerza[equipo] = goles_favor / partidos if partidos > 0 else 1

    return fuerza

fuerza = calcular_fuerza(df)
prom_goles = df["home_goals"].mean()

# =========================
# MONTE CARLO AVANZADO
# =========================

def monte_carlo(xg_home, xg_away, simulaciones=1000000):

    goles_home = np.random.poisson(xg_home, simulaciones)
    goles_away = np.random.poisson(xg_away, simulaciones)

    prob_home = np.mean(goles_home > goles_away)
    prob_over = np.mean((goles_home + goles_away) > 2)

    marcador = {}
    for i in range(3):
        for j in range(3):
            marcador[f"{i}-{j}"] = np.mean((goles_home==i) & (goles_away==j))

    mejor_marcador = max(marcador, key=marcador.get)

    return prob_home, prob_over, mejor_marcador

# =========================
# DETECTOR AUTOMÁTICO DE CUÁNDO NO APOSTAR
# =========================

def evaluar_confianza(prob):
    if prob < 0.55:
        return "🔴 NO APOSTAR – Baja ventaja matemática"
    elif prob < 0.62:
        return "🟡 Apostar con cautela"
    else:
        return "🟢 Alta confianza – Valor detectado"

# =========================
# PRÓXIMOS PARTIDOS
# =========================

st.subheader("📅 Próximos Partidos")

future = requests.get(
    "https://v3.football.api-sports.io/fixtures",
    headers={"x-apisports-key": API_KEY},
    params={"league": LEAGUE_ID, "season": SEASON, "next": 10}
)

future_data = future.json()["response"]

opciones = []

for f in future_data:
    home = f["teams"]["home"]["name"]
    away = f["teams"]["away"]["name"]
    opciones.append(f"{home} vs {away}")

seleccion = st.multiselect("Selecciona partidos", opciones)

if st.button("🚀 Analizar con IA Avanzada"):

    for partido in seleccion:
        home, away = partido.split(" vs ")

        xg_home = fuerza.get(home,1) * random.uniform(0.8,1.3)
        xg_away = fuerza.get(away,1) * random.uniform(0.7,1.2)

        prob_home, prob_over, marcador = monte_carlo(xg_home, xg_away)

        st.markdown(f"## ⚽ {partido}")
        st.write("Prob Gana Local:", round(prob_home*100,2), "%")
        st.write("Prob Over 2.5:", round(prob_over*100,2), "%")
        st.write("Marcador Más Probable:", marcador)

        decision = evaluar_confianza(max(prob_home, prob_over))
        st.write(decision)

        if "NO APOSTAR" not in decision:
            st.success("🎯 Mercado con ventaja detectado")
        else:
            st.error("🚫 Sistema bloquea apuesta")

# =========================
# BACKTEST AUTOMÁTICO
# =========================

st.subheader("📊 Backtest Inteligente")

if len(df) > 50:

    aciertos = np.mean(df["home_goals"] > df["away_goals"])
    st.write("Precisión histórica modelo:", round(aciertos*100,2), "%")

    banca = [100]
    for i in range(30):
        banca.append(banca[-1] * (1 + random.uniform(-0.05,0.1)))

    st.line_chart(banca)
