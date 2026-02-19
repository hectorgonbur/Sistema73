import streamlit as st
import itertools
import pandas as pd
import json
from datetime import datetime

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="Betsson Pro: Master Suite", layout="wide")

# CSS Custom per migliorare l'estetica
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    div[data-testid="stExpander"] {
        border: 1px solid #31333F;
        border-radius: 10px;
        background-color: #161b22;
    }
    .stMetric {
        background-color: #1e2227;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #31333F;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE STATO ---
if "biblioteca" not in st.session_state:
    st.session_state["biblioteca"] = {}
if "ultimo_sistema" not in st.session_state:
    st.session_state["ultimo_sistema"] = None

# --- FUNZIONI CORE ---
def genera_sistema(base_user, err_maxima, quotes, costo, ops):
    combinazioni = itertools.product(ops, repeat=len(base_user))
    sistema = []
    for c in combinazioni:
        diff = sum(1 for i in range(len(base_user)) if c[i] != base_user[i])
        if diff <= err_maxima:
            quota_tot = 1.0
            for idx, s in enumerate(c):
                quota_tot *= quotes[idx][s]
            sistema.append({
                "Colonna": "-".join(c),
                "Fallos": diff,
                "Ganancia Bruta (€)": round(quota_tot * costo, 2)
            })
    return pd.DataFrame(sistema)

# --- SIDEBAR: NAVIGAZIONE E CONFIGURAZIONE ---
st.sidebar.title("🎮 Menu Principale")
menu = st.sidebar.radio(
    "Vai a:", 
    ["1. Configura Partite", "2. Tabella Combinazioni", "3. Simulatore Risultati"]
)

st.sidebar.divider()
st.sidebar.header("⚙️ Parametri Globali")
num_p = st.sidebar.slider("Numero Partite", 2, 10, value=6)
solo_ganador = st.sidebar.checkbox("Modo 2 Risultati (1-2)", value=False)
err_max = st.sidebar.select_slider("Errori Permessi", options=list(range(num_p)), value=2)
apuesta_col = st.sidebar.number_input("Investimento per colonna (€)", min_value=0.1, value=1.0)

opciones = ["1", "2"] if solo_ganador else ["1", "X", "2"]

# --- RACCOLTA DATI (Sempre attiva in background) ---
matriz_cuotas, col_base, equipos_local, equipos_visit = [], [], [], []

# --- LOGICA DELLE PAGINE ---

# ---------------------------------------------------------
# PAGINA 1: CONFIGURAZIONE
# ---------------------------------------------------------
if menu == "1. Configura Partite":
    st.title("⚽ Configurazione Partite e Quote")
    st.info("Inserisci i nomi delle squadre, le quote e scegli la tua base.")
    
    for i in range(num_p):
        with st.expander(f"🏟️ PARTITA {i+1}", expanded=True):
            # Riga 1: Squadre
            c_loc, c_vs, c_vis = st.columns([10, 1, 10])
            loc = c_loc.text_input("Local", key=f"l_{i}", value=f"Local {i+1}", label_visibility="collapsed")
            c_vs.markdown("<p style='text-align:center; padding-top:5px;'>vs</p>", unsafe_allow_html=True)
            vis = c_vis.text_input("Visitante", key=f"v_{i}", value=f"Visitante {i+1}", label_visibility="collapsed")
            
            equipos_local.append(loc); equipos_visit.append(vis)

            # Riga 2: Quote e Base
            if not solo_ganador:
                q1, qx, q2, space, base_col = st.columns([1, 1, 1, 0.5, 2])
                dq = {
                    "1": q1.number_input("Q1", min_value=1.01, key=f"q1_{i}", value=2.0, label_visibility="collapsed"),
                    "X": qx.number_input("QX", min_value=1.01, key=f"qx_{i}", value=3.0, label_visibility="collapsed"),
                    "2": q2.number_input("Q2", min_value=1.01, key=f"q2_{i}", value=2.5, label_visibility="collapsed")
                }
                q1.caption("Q1"); qx.caption("QX"); q2.caption("Q2")
            else:
                q1, q2, space, base_col = st.columns([1, 1, 1.5, 2])
                dq = {
                    "1": q1.number_input("Q1", min_value=1.01, key=f"q1_{i}", value=2.0, label_visibility="collapsed"),
                    "2": q2.number_input("Q2", min_value=1.01, key=f"q2_{i}", value=2.5, label_visibility="collapsed")
                }
                q1.caption("Q1"); q2.caption("Q2")
            
            b = base_col.selectbox("Base", opciones, key=f"b_{i}")
            col_base.append(b)
            matriz_cuotas.append(dq)

    st.success("Configurazione completata. Vai alla sezione 'Tabella Combinazioni' per calcolare.")

# ---------------------------------------------------------
# PAGINA 2: TABELLA COMBINAZIONI
# ---------------------------------------------------------
elif menu == "2. Tabella Combinazioni":
    st.title("📊 Analisi e Redditività del Sistema")
    
    # Dobbiamo rigenerare le liste per il calcolo se siamo in questa pagina
    for i in range(num_p):
        equipos_local.append(st.session_state.get(f"l_{i}"))
        col_base.append(st.session_state.get(f"b_{i}"))
        dq = {"1": st.session_state.get(f"q1_{i}"), "2": st.session_state.get(f"q2_{i}")}
        if not solo_ganador: dq["X"] = st.session_state.get(f"qx_{i}")
        matriz_cuotas.append(dq)

    if st.button("🚀 Calcola Sistema", type="primary", use_container_width=True):
        df = genera_sistema(col_base, err_max, matriz_cuotas, apuesta_col, opciones)
        st.session_state["ultimo_sistema"] = df
        st.session_state["costo_tot"] = len(df) * apuesta_col

    if st.session_state["ultimo_sistema"] is not None:
        df = st.session_state["ultimo_sistema"].copy()
        costo = st.session_state["costo_tot"]
        df["Ganancia Neta (€)"] = df["Ganancia Bruta (€)"] - costo
        
        c1, c2, c3 = st.columns(3)
        c1.metric("N. Colonne", len(df))
        c2.metric("Costo Totale", f"{costo:.2f} €")
        c3.metric("Max Vincita Neta", f"{df['Ganancia Neta (€)'].max():.2f} €")

        st.dataframe(df.style.format({
            "Ganancia Bruta (€)": "{:.2f} €",
            "Ganancia Neta (€)": "{:.2f} €"
        }), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# PAGINA 3: SIMULATORE
# ---------------------------------------------------------
elif menu == "3. Simulatore Risultati":
    st.title("🎯 Verifica Risultati Reali")
    
    res_sim = []
    for i in range(num_p):
        loc = st.session_state.get(f"l_{i}", f"Squadra A{i}")
        vis = st.session_state.get(f"v_{i}", f"Squadra B{i}")
        base_scelta = st.session_state.get(f"b_{i}", "1")

        c1, c2, c3, c4, c5, c6 = st.columns([3, 1, 0.5, 1, 3, 1.5])
        
        c1.markdown(f"<p style='text-align: right; padding-top: 25px;'><b>{loc}</b></p>", unsafe_allow_html=True)
        gl = c2.number_input("L", min_value=0, step=1, key=f"sim_gl_{i}", label_visibility="collapsed")
        c3.markdown("<p style='text-align: center; padding-top: 25px;'>-</p>", unsafe_allow_html=True)
        gv = c4.number_input("V", min_value=0, step=1, key=f"sim_gv_{i}", label_visibility="collapsed")
        c5.markdown(f"<p style='text-align: left; padding-top: 25px;'><b>{vis}</b></p>", unsafe_allow_html=True)
        
        if solo_ganador: s_auto = "1" if gl > gv else "2"
        else: s_auto = "1" if gl > gv else ("2" if gv > gl else "X")
        res_sim.append(s_auto)
        
        color = "🟢" if s_auto == base_scelta else "🔴"
        c6.markdown(f"<div style='padding-top: 25px;'><b>{s_auto}</b> {color}</div>", unsafe_allow_html=True)

    # Verifica finale
    if st.button("💰 Verifica Vincita Totale"):
        colonna_risultato = "-".join(res_sim)
        df_inv = st.session_state.get("ultimo_sistema")
        if df_inv is not None:
            vincita = df_inv[df_inv["Colonna"] == colonna_risultato]
            if not vincita.empty:
                val = vincita.iloc[0]["Ganancia Bruta (€)"]
                st.balloons()
                st.success(f"HAI VINTO! Incasso: {val:.2f} €")
            else:
                st.error("Colonna non presente nel sistema (troppi errori).")
