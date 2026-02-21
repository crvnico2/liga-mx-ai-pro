import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import poisson
import matplotlib.pyplot as plt

st.set_page_config(page_title="Liga MX AI PRO", layout="wide")

st.title("⚽ Liga MX AI PRO - Predictor Profesional")

st.sidebar.header("Datos del Partido")

local = st.sidebar.text_input("Equipo Local")
visitante = st.sidebar.text_input("Equipo Visitante")

xg_local = st.sidebar.number_input("xG Local", 0.0, 5.0, 1.6)
xg_visit = st.sidebar.number_input("xG Visitante", 0.0, 5.0, 1.2)

cuota_local = st.sidebar.number_input("Cuota Local", 1.01, 10.0, 1.80)

if st.sidebar.button("Calcular Pronóstico"):

    sims = 20000
    
    goles_local = np.random.poisson(xg_local, sims)
    goles_visit = np.random.poisson(xg_visit, sims)

    prob_local = np.mean(goles_local > goles_visit)
    prob_empate = np.mean(goles_local == goles_visit)
    prob_visit = np.mean(goles_local < goles_visit)

    over25 = np.mean((goles_local + goles_visit) > 2)

    tiros = np.random.poisson((xg_local + xg_visit)*10, sims)
    corners = np.random.poisson((xg_local + xg_visit)*3, sims)
    tarjetas = np.random.poisson(4.5, sims)
    atajadas = np.random.poisson(6, sims)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Probabilidades 1X2")
        st.write("Local:", round(prob_local*100,2), "%")
        st.write("Empate:", round(prob_empate*100,2), "%")
        st.write("Visitante:", round(prob_visit*100,2), "%")

        st.subheader("Over 2.5 goles")
        st.write(round(over25*100,2), "%")

    with col2:
        st.subheader("Estadísticas Esperadas")
        st.write("Tiros promedio:", int(np.mean(tiros)))
        st.write("Corners promedio:", int(np.mean(corners)))
        st.write("Tarjetas promedio:", int(np.mean(tarjetas)))
        st.write("Atajadas promedio:", int(np.mean(atajadas)))

    prob_implicita = 1 / cuota_local
    value = prob_local - prob_implicita

    st.subheader("Detector de Value Bet")

    if value > 0.05:
        st.success(f"🔥 Hay VALOR de {round(value*100,2)}%")
    else:
        st.warning("No hay valor suficiente")

    # Generador Parlay
    st.subheader("Parlay Automático")

    picks = []

    if prob_local > 0.60:
        picks.append(prob_local)

    if over25 > 0.60:
        picks.append(over25)

    if np.mean(corners) > 8:
        picks.append(0.60)

    if len(picks) >= 2:
        prob_parlay = np.prod(picks)
        st.write("Probabilidad combinada:", round(prob_parlay*100,2), "%")
    else:
        st.write("No hay suficientes picks seguros para parlay.")

    # Gráfico distribución goles
    st.subheader("Distribución de Goles Simulados")
    fig, ax = plt.subplots()
    ax.hist(goles_local + goles_visit, bins=10)
    st.pyplot(fig)