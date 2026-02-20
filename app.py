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
st.set_page_config(page_title="Betting Manager Pro v6.0", layout="wide")

def init_db():
    conn = sqlite3.connect('apuestas_master.db')
    c = conn.cursor()
    # Tabla para guardar sesiones completas
    c.execute('CREATE TABLE IF NOT EXISTS jugadas (nombre TEXT PRIMARY KEY, datos TEXT)')
    # Tabla de historial financiero
    c.execute('''CREATE TABLE IF NOT EXISTS historial 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, deporte TEXT, 
                  inversion REAL, neto REAL, resultado TEXT)''')
    # Tabla de equipos con jerarquía: Deporte -> Liga -> Equipo
    c.execute('''CREATE TABLE IF NOT EXISTS stats_equipos 
                 (equipo TEXT, deporte TEXT, liga TEXT, apostado INTEGER, aciertos INTEGER, desaciertos INTEGER,
                  PRIMARY KEY (equipo, deporte, liga))''')
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. FUNCIONES DE LÓGICA (ESPEJO Y CRONOLOGÍA)
# ==========================================

def obtener_fecha_hora_obj(fecha_str, hora_str):
    try:
        if not isinstance(fecha_str, str): fecha_str = fecha_str.strftime("%Y-%m-%d")
        return datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
    except: return datetime.max

def registrar_stats_bilateral(local, visitante, base, resultado_real, deporte, liga):
    conn = sqlite3.connect('apuestas_master.db')
    c = conn.cursor()
    # Inicializar ambos equipos en esa liga/deporte
    for eq in [local, visitante]:
        c.execute('INSERT OR IGNORE INTO stats_equipos VALUES (?, ?, ?, 0, 0, 0)', (eq, deporte, liga))
        c.execute('UPDATE stats_equipos SET apostado = apostado + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (eq, deporte, liga))
    
    # Lógica Espejo: El acierto de uno es el desacierto del otro
    acerto_base = (base == resultado_real)
    
    if base == "1": # Apostaste al Local
        if acerto_base:
            c.execute('UPDATE stats_equipos SET aciertos = aciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (local, deporte, liga))
            c.execute('UPDATE stats_equipos SET desaciertos = desaciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (visitante, deporte, liga))
        else:
            c.execute('UPDATE stats_equipos SET desaciertos = desaciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (local, deporte, liga))
            if resultado_real == "2": 
                c.execute('UPDATE stats_equipos SET aciertos = aciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (visitante, deporte, liga))
    
    elif base == "2": # Apostaste al Visitante
        if acerto_base:
            c.execute('UPDATE stats_equipos SET aciertos = aciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (visitante, deporte, liga))
            c.execute('UPDATE stats_equipos SET desaciertos = desaciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (local, deporte, liga))
        else:
            c.execute('UPDATE stats_equipos SET desaciertos = desaciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (visitante, deporte, liga))
            if resultado_real == "1": 
                c.execute('UPDATE stats_equipos SET aciertos = aciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (local, deporte, liga))
    
    elif base == "X": # Apostaste al Empate
        if acerto_base:
            for eq in [local, visitante]: c.execute('UPDATE stats_equipos SET aciertos = aciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (eq, deporte, liga))
        else:
            for eq in [local, visitante]: c.execute('UPDATE stats_equipos SET desaciertos = desaciertos + 1 WHERE equipo = ? AND deporte = ? AND liga = ?', (eq, deporte, liga))
    
    conn.commit()
    conn.close()

# ==========================================
# 3. INTERFAZ Y NAVEGACIÓN
# ==========================================
with st.sidebar:
    st.title("🏆 BettingManager Pro")
    menu = st.radio("Secciones", [
        "🏠 Inicio", 
        "💰 Gestión de Apuestas", 
        "🧮 Calculadora de Arbitraje", 
        "📊 Estadísticas"
    ])
    st.markdown("---")
    nombre_sesion = st.text_input("Sesión", placeholder="Ej: Finde Champions")
    if st.button("💾 Guardar Sesión"):
        st.success("Configuración guardada.")

# ==========================================
# 4. SECCIÓN: GESTIÓN DE APUESTAS (SIMPLES Y SISTEMAS)
# ==========================================
if menu == "💰 Gestión de Apuestas":
    st.header("📝 Registro de Jugadas")
    
    if 'n_eventos' not in st.session_state: st.session_state.n_eventos = 1
    
    c_btn1, c_btn2, _ = st.columns([0.5, 0.5, 5])
    if c_btn1.button("➕"): st.session_state.n_eventos += 1; st.rerun()
    if c_btn2.button("➖") and st.session_state.n_eventos > 1: st.session_state.n_eventos -= 1; st.rerun()

    eventos_lista = []
    # Ordenar por fecha y hora automáticamente
    indices = list(range(st.session_state.n_eventos))
    indices.sort(key=lambda i: obtener_fecha_hora_obj(st.session_state.get(f"s_fec_{i}", datetime.now().date()), st.session_state.get(f"s_hor_{i}", "23:59")))

    for i in indices:
        with st.expander(f"Evento #{i+1}", expanded=True):
            f1, f2, f3, f4 = st.columns([1.5, 2, 2, 1.5])
            dep = f1.selectbox("Deporte", ["⚽ Fútbol", "🏀 Basket", "🎾 Tenis"], key=f"s_dep_{i}")
            liga = f2.text_input("Liga", key=f"s_liga_{i}", placeholder="Ej: NBA")
            f3.date_input("Fecha", key=f"s_fec_{i}")
            f4.text_input("Hora", key=f"s_hor_{i}", value="20:00")
            
            fl, fv, fc, fb = st.columns([2.5, 2.5, 1, 1.5])
            l = fl.text_input("Local", key=f"s_l_{i}")
            v = fv.text_input("Visitante", key=f"s_v_{i}")
            cuota = fc.number_input("Cuota", 1.0, key=f"s_cuo_{i}", step=0.01)
            base = fb.selectbox("Base", ["1", "X", "2"] if dep == "⚽ Fútbol" else ["1", "2"], key=f"s_base_{i}")
            
            r1, r2 = st.columns(2)[0].number_input("R1", 0, key=f"s_r1_{i}"), st.columns(2)[1].number_input("R2", 0, key=f"s_r2_{i}")
            
            res_r = "1" if r1 > r2 else ("2" if r1 < r2 else "X")
            if r1 == 0 and r2 == 0: st.info("⌛ Pendiente")
            elif res_r == base: st.success("🟢 ACERTADO")
            else: st.error("🔴 FALLADO")
            
            eventos_lista.append({"l": l, "v": v, "cuo": cuota, "base": base, "dep": dep, "liga": liga, "r1": r1, "r2": r2})

    st.markdown("---")
    st.subheader("⚙️ Configuración Final")
    c_s1, c_s2, c_s3 = st.columns(3)
    k_sis = c_s1.number_input("Sistema (K de N)", 1, st.session_state.n_eventos, st.session_state.n_eventos, help="Pon el total para apuesta simple.")
    inv_total = c_s2.number_input("Inversión Total ($)", 1.0, value=10.0)
    neto_final = c_s3.number_input("Neto Real ($)", value=0.0)

    # Lógica de Columnas
    combis = list(itertools.combinations(eventos_lista, k_sis))
    inv_col = inv_total / len(combis)
    
    with st.expander("📋 Desglose de Ganancias por Columna"):
        filas_c = []
        for idx, combo in enumerate(combis):
            c_cuota = 1.0
            for e in combo: c_cuota *= e['cuo']
            filas_c.append({"Columna": f"#{idx+1}", "Cuota": round(c_cuota, 2), "Paga ($)": round(c_cuota * inv_col, 2)})
        st.table(pd.DataFrame(filas_c))

    if st.button("🔥 REGISTRAR JUGADA Y ESTADÍSTICAS", use_container_width=True):
        conn = sqlite3.connect('apuestas_master.db')
        conn.execute("INSERT INTO historial (fecha, deporte, inversion, neto, resultado) VALUES (?,?,?,?,?)",
                  (datetime.now().strftime("%Y-%m-%d %H:%M"), "Múltiple", inv_total, neto_final, "Cerrado"))
        conn.commit(); conn.close()
        for e in eventos_lista:
            res_real = "1" if e['r1'] > e['r2'] else ("2" if e['r1'] < e['r2'] else "X")
            registrar_stats_bilateral(e['l'], e['v'], e['base'], res_real, e['dep'], e['liga'])
        st.balloons(); st.success("¡Datos guardados!")

# ==========================================
# 5. SECCIÓN: CALCULADORA DE ARBITRAJE
# ==========================================
elif menu == "🧮 Calculadora de Arbitraje":
    st.header("🧮 Calculadora de Surebet (Arbitraje)")
    st.write("Calcula cómo cubrir todos los resultados para ganar siempre.")
    
    col_a, col_b = st.columns(2)
    c1 = col_a.number_input("Cuota Local (Casa 1)", 1.01, value=2.10, step=0.01)
    c2 = col_b.number_input("Cuota Visitante (Casa 2)", 1.01, value=2.10, step=0.01)
    inversion_arb = st.number_input("Inversión Total ($)", 1.0, value=100.0)
    
    prob_total = (1/c1) + (1/c2)
    beneficio_pct = (1 - prob_total) * 100
    
    st.markdown("---")
    if prob_total < 1:
        st.success(f"✅ ¡Arbitraje! Rentabilidad: {beneficio_pct:.2f}%")
        s1, s2 = inversion_arb / (prob_total * c1), inversion_arb / (prob_total * c2)
        r1, r2, r3 = st.columns(3)
        r1.metric("Apostar al Local", f"${s1:.2f}")
        r2.metric("Apostar al Visitante", f"${s2:.2f}")
        r3.metric("Ganancia Neta", f"${(s1*c1 - inversion_arb):.2f}")
    else:
        st.error(f"❌ No hay arbitraje. Margen: {beneficio_pct:.2f}%")

# ==========================================
# 6. SECCIÓN: ESTADÍSTICAS (FILTROS CASCADA Y BARRA PRO)
# ==========================================
elif menu == "📊 Estadísticas":
    tab_gan, tab_eq = st.tabs(["📈 Análisis de Ganancias", "⚽ Rendimiento Equipos"])

    with tab_gan:
        st.header("💰 Balance de Caja")
        conn = sqlite3.connect('apuestas_master.db')
        df_h = pd.read_sql_query("SELECT * FROM historial", conn); conn.close()
        if not df_h.empty:
            df_h['fecha_dt'] = pd.to_datetime(df_h['fecha'])
            f_ini, f_fin = st.columns(2)[0].date_input("Desde", df_h['fecha_dt'].min()), st.columns(2)[1].date_input("Hasta", datetime.now())
            df_f = df_h[(df_h['fecha_dt'].dt.date >= f_ini) & (df_h['fecha_dt'].dt.date <= f_fin)]
            
            st.metric("Balance Neto Total", f"${df_f['neto'].sum():.2f}")
            st.line_chart(df_f.sort_values('fecha_dt').set_index('fecha')['neto'].cumsum())
        else: st.info("No hay registros financieros.")

    with tab_eq:
        conn = sqlite3.connect('apuestas_master.db')
        df_full = pd.read_sql_query("SELECT * FROM stats_equipos", conn); conn.close()
        
        if not df_full.empty:
            # BARRA DE HERRAMIENTAS ESPACIAL
            c_act, c_res, c_exp, c_dep, c_lig, c_bus = st.columns([0.6, 0.6, 1, 1.5, 1.5, 2])
            with c_act: 
                if st.button("🔄"): st.rerun()
            with c_res:
                if st.button("🗑️"):
                    c = sqlite3.connect('apuestas_master.db'); c.execute("DELETE FROM stats_equipos"); c.commit(); c.close(); st.rerun()
            with c_exp:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='xlsxwriter') as wr: df_full.to_excel(wr, index=False)
                st.download_button("📥 Excel", buf.getvalue(), "stats_equipos.xlsx")

            # Filtros en Cascada
            sel_d = c_dep.selectbox("Deporte", ["Todos"] + df_full['deporte'].unique().tolist(), label_visibility="collapsed")
            lig_opts = df_full[df_full['deporte'] == sel_d]['liga'].unique().tolist() if sel_d != "Todos" else df_full['liga'].unique().tolist()
            sel_l = c_lig.selectbox("Liga", ["Todas"] + lig_opts, label_visibility="collapsed")
            sel_b = c_bus.text_input("Buscar equipo...", label_visibility="collapsed")

            # Aplicación de filtros
            df_v = df_full.copy()
            if sel_d != "Todos": df_v = df_v[df_v['deporte'] == sel_d]
            if sel_l != "Todas": df_v = df_v[df_v['liga'] == sel_l]
            if sel_b: df_v = df_v[df_v['equipo'].str.contains(sel_b, case=False)]
            
            df_v['% Efic.'] = (df_v['aciertos'] / df_v['apostado'] * 100).round(1).astype(str) + '%'
            st.dataframe(df_v.sort_values('apostado', ascending=False), use_container_width=True, hide_index=True)
        else: st.info("No hay estadísticas de equipos.")

elif menu == "🏠 Inicio":
    st.title("Betting Manager Pro v6.0")
    st.write("Bienvenido al sistema integral de gestión de apuestas.")
