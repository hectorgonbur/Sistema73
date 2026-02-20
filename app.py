import streamlit as st
import itertools
import pandas as pd
import sqlite3
import json
import io
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="App de Apuestas Pro - v10 Master", layout="wide")

# --- LÓGICA DE BASE DE DATOS (ACTUALIZADA CON STATS) ---
def init_db():
    conn = sqlite3.connect('apuestas_master.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS jugadas (nombre TEXT PRIMARY KEY, datos TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS historial 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, deporte TEXT, 
                  inversion REAL, neto REAL, resultado TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS stats_equipos 
                 (equipo TEXT, deporte TEXT, liga TEXT, apostado INTEGER, aciertos INTEGER, desaciertos INTEGER,
                  PRIMARY KEY (equipo, deporte, liga))''')
    conn.commit()
    conn.close()

def registrar_stats_bilateral(local, visitante, base, resultado_real, deporte, liga):
    conn = sqlite3.connect('apuestas_master.db')
    c = conn.cursor()
    for eq in [local, visitante]:
        c.execute('INSERT OR IGNORE INTO stats_equipos VALUES (?, ?, ?, 0, 0, 0)', (eq, deporte, liga))
        c.execute('UPDATE stats_equipos SET apostado = apostado + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (eq, deporte, liga))
    
    acerto_base = (base == resultado_real)
    if base == "1":
        if acerto_base:
            c.execute('UPDATE stats_equipos SET aciertos = aciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (local, deporte, liga))
            c.execute('UPDATE stats_equipos SET desaciertos = desaciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (visitante, deporte, liga))
        else:
            c.execute('UPDATE stats_equipos SET desaciertos = desaciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (local, deporte, liga))
            if resultado_real == "2": c.execute('UPDATE stats_equipos SET aciertos = aciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (visitante, deporte, liga))
    elif base == "2":
        if acerto_base:
            c.execute('UPDATE stats_equipos SET aciertos = aciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (visitante, deporte, liga))
            c.execute('UPDATE stats_equipos SET desaciertos = desaciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (local, deporte, liga))
        else:
            c.execute('UPDATE stats_equipos SET desaciertos = desaciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (visitante, deporte, liga))
            if resultado_real == "1": c.execute('UPDATE stats_equipos SET aciertos = aciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (local, deporte, liga))
    conn.commit(); conn.close()

init_db()

# --- INICIALIZACIÓN DE VARIABLES ---
if 'num_eventos_simple' not in st.session_state: st.session_state.num_eventos_simple = 1

# --- MENÚ LATERAL (REDISEÑADO V10) ---
with st.sidebar:
    st.title("🏆 Betting Pro v10")
    menu = st.radio("Navegación:", ["🏠 Inicio", "🎯 Jugada Simple", "⚙️ Sistemas", "🧮 Arbitraje", "📊 Estadísticas"])
    
    st.markdown("---")
    st.header("💾 Gestión de Sesiones")
    nombre_arch = st.text_input("Nombre de jugada", placeholder="Ej: Finde Premier")
    if st.button("📁 Guardar Todo"):
        if nombre_arch:
            datos_serializables = {k: v for k, v in st.session_state.items() if not k.startswith('_')}
            conn = sqlite3.connect('apuestas_master.db')
            conn.execute("INSERT OR REPLACE INTO jugadas VALUES (?, ?)", (nombre_arch, json.dumps(datos_serializables, default=str)))
            conn.commit(); conn.close()
            st.success("Guardado.")

# --- CONTENIDO: JUGADA SIMPLE (CON CUOTAS 1X2) ---
if menu == "🎯 Jugada Simple":
    st.title("🎯 Jugada Simple con Cuotas 1X2")
    
    c1, c2, c3 = st.columns([1, 1, 3])
    with c1: 
        if st.button("➖") and st.session_state.num_eventos_simple > 1:
            st.session_state.num_eventos_simple -= 1; st.rerun()
    with c3:
        if st.button("➕"):
            st.session_state.num_eventos_simple += 1; st.rerun()

    eventos_simples = []
    for i in range(st.session_state.num_eventos_simple):
        with st.expander(f"Evento #{i+1}", expanded=True):
            f1, f2, f3 = st.columns([1.5, 2, 2])
            dep = f1.selectbox("Deporte", ["⚽ Fútbol", "🎾 Tenis", "🏀 Basket"], key=f"sim_dep_{i}")
            liga = f2.text_input("Liga", key=f"sim_liga_{i}")
            
            # Equipos y Marcador
            fl, fr1, fr2, fv = st.columns([2, 0.7, 0.7, 2])
            local = fl.text_input("Local", key=f"sim_l_{i}")
            r1 = fr1.number_input("R1", 0, key=f"sim_r1_{i}")
            r2 = fr2.number_input("R2", 0, key=f"sim_r2_{i}")
            visitante = fv.text_input("Visitante", key=f"sim_v_{i}")
            
            # Cuotas 1 X 2 (Lo que pediste)
            st.markdown("**💰 Cuotas de Resultado**")
            q1, qx, q2, qsel = st.columns([1, 1, 1, 1.5])
            cuo1 = q1.number_input("Cuota 1", 1.0, value=2.0, key=f"sim_c1_{i}")
            cuox = qx.number_input("Cuota X", 1.0, value=3.0, key=f"sim_cx_{i}") if dep == "⚽ Fútbol" else 1.0
            cuo2 = q2.number_input("Cuota 2", 1.0, value=2.0, key=f"sim_c2_{i}")
            
            base = qsel.selectbox("Tu Apuesta", ["1", "X", "2"] if dep == "⚽ Fútbol" else ["1", "2"], key=f"sim_base_{i}")
            
            c_escogida = cuo1 if base=="1" else (cuox if base=="X" else cuo2)
            st.caption(f"Cuota seleccionada: {c_escogida}")
            eventos_simples.append({"l": local, "v": visitante, "cuo": c_escogida, "base": base, "dep": dep, "liga": liga, "r1": r1, "r2": r2})

    st.markdown("---")
    st.subheader("💰 Resumen de Jugada Simple")
    inv = st.number_input("Inversión Total ($)", 1.0, value=10.0)
    
    cuota_final = 1.0
    for ev in eventos_simples: cuota_final *= ev["cuo"]
    
    st.metric("Retorno Bruto", f"${(inv * cuota_final):.2f}", f"Cuota Total: {cuota_final:.2f}")

    if st.button("🔥 REGISTRAR TODO", use_container_width=True):
        for e in eventos_simples:
            res_r = "1" if e['r1'] > e['r2'] else ("2" if e['r1'] < e['r2'] else "X")
            registrar_stats_bilateral(e['l'], e['v'], e['base'], res_r, e['dep'], e['liga'])
        st.success("Estadísticas y jugadas registradas.")

# --- CONTENIDO: ARBITRAJE (NUEVA SECCIÓN) ---
elif menu == "🧮 Arbitraje":
    st.title("🧮 Calculadora de Arbitraje (Surebet)")
    st.info("Calcula el beneficio asegurado comparando dos resultados opuestos.")
    ca, cb = st.columns(2)
    c_a = ca.number_input("Cuota Resultado A", 1.01, value=2.10)
    c_b = cb.number_input("Cuota Resultado B", 1.01, value=2.10)
    inv_arb = st.number_input("Inversión a repartir ($)", 1.0, value=100.0)
    
    prob = (1/c_a) + (1/c_b)
    if prob < 1:
        st.success(f"✅ Arbitraje: {((1-prob)*100):.2f}% de ganancia.")
        st.write(f"Apostar A: **${(inv_arb/(prob*c_a)):.2f}** | Apostar B: **${(inv_arb/(prob*c_b)):.2f}**")
    else: st.error("No hay arbitraje en estas cuotas.")

# --- CONTENIDO: ESTADÍSTICAS ---
elif menu == "📊 Estadísticas":
    st.title("📊 Rendimiento por Ligas y Equipos")
    conn = sqlite3.connect('apuestas_master.db')
    df = pd.read_sql_query("SELECT * FROM stats_equipos", conn); conn.close()
    
    if not df.empty:
        c_dep, c_lig, c_bus = st.columns([1, 1, 2])
        sel_d = c_dep.selectbox("Deporte", ["Todos"] + df['deporte'].unique().tolist())
        df_f = df[df['deporte'] == sel_d] if sel_d != "Todos" else df
        
        sel_l = c_lig.selectbox("Liga", ["Todas"] + df_f['liga'].unique().tolist())
        df_f = df_f[df_f['liga'] == sel_l] if sel_l != "Todas" else df_f
        
        bus = c_bus.text_input("Buscar Equipo...")
        if bus: df_f = df_f[df_f['equipo'].str.contains(bus, case=False)]
        
        st.dataframe(df_f, use_container_width=True, hide_index=True)
    else: st.info("Sin datos registrados.")

# --- INICIO ---
elif menu == "🏠 Inicio":
    st.title("🚀 Betting Manager v10")
    st.write("Bienvenido al sistema profesional. Usa el menú lateral para navegar.")
