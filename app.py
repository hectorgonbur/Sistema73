import streamlit as st
import pandas as pd
import sqlite3
import json
import io
import itertools
from datetime import datetime, timedelta

# ==========================================
# 1. CONFIGURACIÓN Y BASE DE DATOS
# ==========================================
st.set_page_config(page_title="Master Betting Analytics Pro", layout="wide")

def init_db():
    conn = sqlite3.connect('apuestas_master.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS jugadas (nombre TEXT PRIMARY KEY, datos TEXT)')
    c.execute('''CREATE TABLE IF NOT EXISTS historial 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, deporte TEXT, 
                  inversion REAL, neto REAL, resultado TEXT)''')
    # Tabla con jerarquía: Deporte -> Liga -> Equipo
    c.execute('''CREATE TABLE IF NOT EXISTS stats_equipos 
                 (equipo TEXT, deporte TEXT, liga TEXT, apostado INTEGER, aciertos INTEGER, desaciertos INTEGER,
                  PRIMARY KEY (equipo, deporte, liga))''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. FUNCIONES DE LÓGICA (ESPEJO Y CRONO)
# ==========================================

def obtener_fecha_hora_obj(fecha_str, hora_str):
    try:
        if not isinstance(fecha_str, str): fecha_str = fecha_str.strftime("%Y-%m-%d")
        return datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
    except: return datetime.max

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
    elif base == "X":
        if acerto_base:
            for eq in [local, visitante]: c.execute('UPDATE stats_equipos SET aciertos = aciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (eq, deporte, liga))
        else:
            for eq in [local, visitante]: c.execute('UPDATE stats_equipos SET desaciertos = desaciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (eq, deporte, liga))
    conn.commit()
    conn.close()

# ==========================================
# 3. INTERFAZ (SIDEBAR)
# ==========================================
with st.sidebar:
    st.title("🏆 BettingManager v4")
    menu = st.radio("Navegación", ["🏠 Inicio", "💰 Gestión de Apuestas", "📊 Estadísticas"])
    st.markdown("---")
    nombre_ses = st.text_input("Sesión", placeholder="Ej: NBA Night")
    if st.button("💾 Guardar Sesión"):
        conn = sqlite3.connect('apuestas_master.db')
        datos = {k: v for k, v in st.session_state.items() if not k.startswith('_')}
        conn.execute("INSERT OR REPLACE INTO jugadas VALUES (?, ?)", (nombre_ses, json.dumps(datos, default=str)))
        conn.commit(); conn.close()
        st.success("Guardado.")

# ==========================================
# 4. SECCIÓN APUESTAS (SIMPLES Y SISTEMAS)
# ==========================================
if menu == "💰 Gestión de Apuestas":
    st.header("💰 Registro y Calculadora de Columnas")
    if 'n_eventos' not in st.session_state: st.session_state.n_eventos = 1
    
    col_c1, col_c2, _ = st.columns([1,1,5])
    if col_c1.button("➕"): st.session_state.n_eventos += 1; st.rerun()
    if col_c2.button("➖") and st.session_state.n_eventos > 1: st.session_state.n_eventos -= 1; st.rerun()

    eventos_lista = []
    indices = list(range(st.session_state.n_eventos))
    indices.sort(key=lambda i: obtener_fecha_hora_obj(st.session_state.get(f"s_fec_{i}", datetime.now().date()), st.session_state.get(f"s_hor_{i}", "23:59")))

    for i in indices:
        with st.expander(f"Evento #{i+1}", expanded=True):
            f1, f2, f3, f4 = st.columns([1.5, 2, 2, 1.5])
            dep = f1.selectbox("Deporte", ["⚽ Fútbol", "🏀 Basket", "🎾 Tenis"], key=f"s_dep_{i}")
            liga = f2.text_input("Liga / Torneo", key=f"s_liga_{i}", placeholder="Ej: NBA")
            f3.date_input("Fecha", key=f"s_fec_{i}")
            f4.text_input("Hora", key=f"s_hor_{i}", value="21:00")
            
            fl, fv, fc, fb = st.columns([2, 2, 1, 1.5])
            l = fl.text_input("Local", key=f"s_l_{i}")
            v = fv.text_input("Visitante", key=f"s_v_{i}")
            cuota = fc.number_input("Cuota", 1.0, key=f"s_cuo_{i}", step=0.01)
            base = fb.selectbox("Base", ["1", "X", "2"] if dep == "⚽ Fútbol" else ["1", "2"], key=f"s_base_{i}")
            
            r1, r2 = st.columns(2)[0].number_input("R1", 0, key=f"s_r1_{i}"), st.columns(2)[1].number_input("R2", 0, key=f"s_r2_{i}")
            eventos_lista.append({"nom": f"{l} vs {v}", "cuo": cuota, "base": base, "dep": dep, "liga": liga, "l": l, "v": v, "r1": r1, "r2": r2})

    st.markdown("---")
    st.subheader("⚙️ Análisis de Columnas y Finanzas")
    c_s1, c_s2, c_s3 = st.columns(3)
    k_sis = c_s1.number_input("Sistema (Ej: 2 de X)", 1, st.session_state.n_eventos, st.session_state.n_eventos)
    inv_total = c_s2.number_input("Inversión Total ($)", 1.0, value=10.0)
    neto_final = c_s3.number_input("Balance Neto Real ($)", value=0.0, help="Lo que realmente ganaste/perdiste")

    # Lógica de Combinatorias (Pago por columna)
    combis = list(itertools.combinations(eventos_lista, k_sis))
    inv_col = inv_total / len(combis)
    
    with st.expander("📋 Desglose de Ganancias por Columna"):
        filas = []
        for idx, c in enumerate(combis):
            c_cuota = 1.0
            for e in c: c_cuota *= e['cuo']
            filas.append({"Columna": f"#{idx+1}", "Cuota": round(c_cuota, 2), "Paga ($)": round(c_cuota * inv_col, 2)})
        st.table(pd.DataFrame(filas))

    if st.button("🔥 REGISTRAR TODO", use_container_width=True):
        conn = sqlite3.connect('apuestas_master.db')
        conn.execute("INSERT INTO historial (fecha, deporte, inversion, neto, resultado) VALUES (?,?,?,?,?)",
                  (datetime.now().strftime("%Y-%m-%d %H:%M"), "Sistema", inv_total, neto_final, "Cerrado"))
        conn.commit(); conn.close()
        for e in eventos_lista:
            res_r = "1" if e['r1'] > e['r2'] else ("2" if e['r1'] < e['r2'] else "X")
            registrar_stats_bilateral(e['l'], e['v'], e['base'], res_r, e['dep'], e['liga'])
        st.balloons(); st.success("Datos guardados en Historial y Estadísticas.")

# ==========================================
# 5. SECCIÓN ESTADÍSTICAS (FILTROS CASCADA)
# ==========================================
elif menu == "📊 Estadísticas":
    t_gan, t_eq = st.tabs(["📈 Ganancias", "⚽ Equipos & Ligas"])

    with t_gan:
        conn = sqlite3.connect('apuestas_master.db')
        df_h = pd.read_sql_query("SELECT * FROM historial", conn)
        conn.close()
        if not df_h.empty:
            df_h['fecha_dt'] = pd.to_datetime(df_h['fecha'])
            c1, c2 = st.columns(2)
            f_ini = c1.date_input("Desde", df_h['fecha_dt'].min())
            f_fin = c2.date_input("Hasta", datetime.now())
            df_f = df_h[(df_h['fecha_dt'].dt.date >= f_ini) & (df_h['fecha_dt'].dt.date <= f_fin)]
            
            st.metric("Balance Neto", f"${df_f['neto'].sum():.2f}", delta=f"{df_f['neto'].sum():.2f}")
            st.line_chart(df_f.sort_values('fecha_dt').set_index('fecha')['neto'].cumsum())
        else: st.info("Sin datos financieros.")

    with t_eq:
        conn = sqlite3.connect('apuestas_master.db')
        df_full = pd.read_sql_query("SELECT * FROM stats_equipos", conn)
        conn.close()

        if not df_full.empty:
            # BARRA PROFESIONAL
            c_act, c_res, c_exp, c_dep, c_lig, c_bus = st.columns([0.6, 0.6, 1, 1.5, 1.5, 2])
            with c_act: 
                if st.button("🔄"): st.rerun()
            with c_res:
                if st.button("🗑️"): 
                    c = sqlite3.connect('apuestas_master.db'); c.execute("DELETE FROM stats_equipos"); c.commit(); c.close(); st.rerun()
            with c_exp:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df_full.to_excel(wr, index=False)
                st.download_button("📥 Excel", buf.getvalue(), "stats.xlsx")

            # Filtros Cascada
            sel_d = c_dep.selectbox("Deporte", ["Todos"] + df_full['deporte'].unique().tolist())
            ligas_opt = df_full[df_full['deporte'] == sel_d]['liga'].unique().tolist() if sel_d != "Todos" else df_full['liga'].unique().tolist()
            sel_l = c_lig.selectbox("Liga", ["Todas"] + ligas_opt)
            sel_b = c_bus.text_input("Buscar", placeholder="🔍 Equipo...")

            # Aplicar Filtros
            df_v = df_full.copy()
            if sel_d != "Todos": df_v = df_v[df_v['deporte'] == sel_d]
            if sel_l != "Todas": df_v = df_v[df_v['liga'] == sel_l]
            if sel_b: df_v = df_v[df_v['equipo'].str.contains(sel_b, case=False)]
            
            df_v['% Efic.'] = (df_v['aciertos'] / df_v['apostado'] * 100).round(1).astype(str) + '%'
            st.dataframe(df_v.sort_values('apostado', ascending=False), use_container_width=True, hide_index=True)
        else: st.info("Sin datos de equipos.")

elif menu == "🏠 Inicio":
    st.title("Betting Manager Pro v4.0")
    st.write("Bienvenido al sistema de gestión jerárquica por Deporte, Liga y Equipo.")
