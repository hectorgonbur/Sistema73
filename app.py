import streamlit as st
import pandas as pd
import sqlite3
import itertools
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y BASE DE DATOS
# ==========================================
st.set_page_config(page_title="Betting Pro v10 - Cuotas 1X2", layout="wide")

def init_db():
    conn = sqlite3.connect('apuestas_master.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS historial (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, tipo TEXT, inversion REAL, neto REAL)')
    c.execute('''CREATE TABLE IF NOT EXISTS stats_equipos 
                 (equipo TEXT, deporte TEXT, liga TEXT, apostado INTEGER, aciertos INTEGER, desaciertos INTEGER,
                  PRIMARY KEY (equipo, deporte, liga))''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. COMPONENTE: EVENTO CON CUOTAS 1, X, 2
# ==========================================
def renderizar_evento(id_evento, prefijo=""):
    with st.expander(f"📌 Evento {prefijo} #{id_evento + 1}", expanded=True):
        # Fila 1: Jerarquía
        c1, c2 = st.columns([2, 2])
        dep = c1.selectbox("Deporte", ["⚽ Fútbol", "🏀 Basket", "🎾 Tenis"], key=f"{prefijo}_dep_{id_evento}")
        liga = c2.text_input("Liga", key=f"{prefijo}_liga_{id_evento}", placeholder="Ej: Premier League")
        
        # Fila 2: Equipos
        l = st.columns(2)[0].text_input("Local", key=f"{prefijo}_l_{id_evento}")
        v = st.columns(2)[1].text_input("Visitante", key=f"{prefijo}_v_{id_evento}")
        
        # Fila 3: LAS 3 CUOTAS DE RESULTADO (1, X, 2)
        st.write("**💰 Cuotas del Mercado**")
        q1, qx, q2 = st.columns(3)
        cuo1 = q1.number_input("Cuota Local (1)", 1.0, value=2.0, step=0.01, key=f"{prefijo}_q1_{id_evento}")
        
        # La cuota X solo se muestra si es Fútbol
        if dep == "⚽ Fútbol":
            cuox = qx.number_input("Cuota Empate (X)", 1.0, value=3.2, step=0.01, key=f"{prefijo}_qx_{id_evento}")
        else:
            cuox = 1.0 # Valor nulo para otros deportes
            qx.write("N/A")
            
        cuo2 = q2.number_input("Cuota Visitante (2)", 1.0, value=2.5, step=0.01, key=f"{prefijo}_q2_{id_evento}")
        
        # Fila 4: Pronóstico y Marcador
        st.write("---")
        p1, p2, p3 = st.columns([2, 1, 1])
        opciones = ["1", "X", "2"] if dep == "⚽ Fútbol" else ["1", "2"]
        base = p1.selectbox("Tu Apuesta (Base)", opciones, key=f"{prefijo}_base_{id_evento}")
        
        # Selección automática de la cuota según la base elegida
        if base == "1": cuota_elegida = cuo1
        elif base == "X": cuota_elegida = cuox
        else: cuota_elegida = cuo2
        
        st.info(f"Seleccionada Cuota **{base}**: {cuota_elegida}")
        
        r1 = p2.number_input("Goles L", 0, key=f"{prefijo}_r1_{id_evento}")
        r2 = p3.number_input("Goles V", 0, key=f"{prefijo}_r2_{id_evento}")
        
        return {"l": l, "v": v, "cuo": cuota_elegida, "base": base, "dep": dep, "liga": liga, "r1": r1, "r2": r2}

# ==========================================
# 3. NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.title("🏆 Betting Pro v10")
    menu = st.radio("Secciones", ["🏠 Inicio", "🎯 Jugada Simple", "⚙️ Sistemas Combinados", "📊 Estadísticas"])

# ==========================================
# 4. SECCIÓN: JUGADA SIMPLE
# ==========================================
if menu == "🎯 Jugada Simple":
    st.header("🎯 Registro de Jugada Simple")
    datos = renderizar_evento(0, "simple")
    
    st.markdown("---")
    inv = st.number_input("Inversión ($)", 1.0, value=10.0)
    retorno = inv * datos["cuo"]
    st.metric("Retorno Potencial", f"${retorno:.2f}", f"Cuota: {datos['cuo']}")
    
    if st.button("🔥 REGISTRAR APUESTA"):
        st.balloons()
        st.success(f"Apuesta al '{datos['base']}' registrada con éxito.")

# ==========================================
# 5. SECCIÓN: SISTEMAS (K de N)
# ==========================================
elif menu == "⚙️ Sistemas Combinados":
    st.header("⚙️ Gestión de Sistemas")
    if 'n_sis' not in st.session_state: st.session_state.n_sis = 2
    
    c_add, c_rem, _ = st.columns([0.5, 0.5, 5])
    if c_add.button("➕"): st.session_state.n_sis += 1; st.rerun()
    if c_rem.button("➖") and st.session_state.n_sis > 1: st.session_state.n_sis -= 1; st.rerun()

    eventos = []
    for i in range(st.session_state.n_sis):
        eventos.append(renderizar_evento(i, "sis"))

    st.markdown("---")
    k = st.number_input("Sistema (K de N)", 1, st.session_state.n_sis, st.session_state.n_sis)
    inv_total = st.number_input("Inversión Total ($)", 1.0, value=20.0)
    
    combis = list(itertools.combinations(eventos, k))
    inv_col = inv_total / len(combis)
    
    with st.expander("📋 Desglose de Columnas del Sistema"):
        res = []
        for idx, combo in enumerate(combis):
            c_tot = 1.0
            for e in combo: c_tot *= e['cuo']
            res.append({"Columna": f"#{idx+1}", "Cuota": round(c_tot, 2), "Paga ($)": round(c_tot * inv_col, 2)})
        st.table(pd.DataFrame(res))

elif menu == "📊 Estadísticas":
    st.header("📊 Análisis de Rendimiento")
    st.write("Filtra por Deporte, Liga y Equipo para ver tu efectividad.")

elif menu == "🏠 Inicio":
    st.title("Betting Manager Pro v10")
    st.write("Registra eventos usando las cuotas de Local, Empate o Visitante.")
