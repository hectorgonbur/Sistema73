import streamlit as st
import itertools
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Betsson Pro: Gestor de Marcadores", layout="wide")

def gestionar_archivos(accion, nombre=None, datos=None):
    arch_sistemas = "sistemas.json"
    arch_stats = "biblioteca_goles.json"
    for arc in [arch_sistemas, arch_stats]:
        if not os.path.exists(arc):
            with open(arc, "w") as f: json.dump({}, f)

    if accion == "guardar_sistema":
        with open(arch_sistemas, "r") as f: bd = json.load(f)
        bd[nombre] = datos
        with open(arch_sistemas, "w") as f: json.dump(bd, f)
    elif accion == "listar_sistemas":
        with open(arch_sistemas, "r") as f: return list(json.load(f).keys())
    elif accion == "cargar_sistema":
        with open(arch_sistemas, "r") as f: return json.load(f).get(nombre)
    elif accion == "registrar_stats":
        with open(arch_stats, "r") as f: stats = json.load(f)
        for entry in datos:
            eq = entry['equipo']
            if eq not in stats: stats[eq] = []
            stats[eq].append(entry)
        with open(arch_stats, "w") as f: json.dump(stats, f)
    elif accion == "obtener_stats":
        with open(arch_stats, "r") as f: return json.load(f)

st.title("⚽ Betsson Pro: Marcadores y Estadísticas")

# --- BARRA LATERAL ---
st.sidebar.header("📂 Gestión")
nombres_s = gestionar_archivos("listar_sistemas")
seleccion = st.sidebar.selectbox("Abrir Jugada:", ["-- Nuevo --"] + nombres_s)
datos_c = gestionar_archivos("cargar_sistema", seleccion) if seleccion != "-- Nuevo --" else None

num_p = st.sidebar.slider("Partidos", 2, 10, datos_c["num_p"] if datos_c else 6)
solo_ganador = st.sidebar.checkbox("Modo 2 Resultados (Tenis/Basket)", value=datos_c["solo_ganador"] if datos_c else False)
opciones = ["1", "2"] if solo_ganador else ["1", "X", "2"]
err_max = st.sidebar.select_slider("Errores a corregir", options=[1,2,3,4], value=datos_c["err_max"] if datos_c else 2)
apuesta_col = st.sidebar.number_input("Inversión por columna (€)", min_value=0.1, value=datos_c["apuesta_col"] if datos_c else 1.0)

# --- ENTRADA DE DATOS ---
st.subheader("📝 Configuración de Encuentros")
matriz_cuotas, col_base, equipos_local, equipos_visit, competiciones = [], [], [], [], []

grid = st.columns(2)
for i in range(num_p):
    with grid[i % 2]:
        with st.expander(f"PARTIDO {i+1}", expanded=True):
            comp = st.text_input("Competición", value=datos_c["competiciones"][i] if datos_c else "Liga", key=f"c_{i}")
            competiciones.append(comp)
            
            c_l, c_v = st.columns(2)
            loc = c_l.text_input("🏠 Local", value=datos_c["local"][i] if datos_c else f"Local {i+1}", key=f"l_{i}")
            vis = c_v.text_input("🚀 Visitante", value=datos_c["visit"][i] if datos_c else f"Visitante {i+1}", key=f"v_{i}")
            equipos_local.append(loc); equipos_visit.append(vis)

            c_b, c_qs = st.columns([1, 3])
            b = c_b.selectbox("Base", opciones, key=f"b_{i}", index=opciones.index(datos_c["base"][i]) if datos_c else 0)
            col_base.append(b)
            
            q_cols = c_qs.columns(len(opciones))
            d_q = {op: q_cols[j].number_input(f"Q{op}", value=datos_c["cuotas"][i][op] if datos_c else 2.0, key=f"q_{op}_{i}") for j, op in enumerate(opciones)}
            matriz_cuotas.append(d_q)

# --- BOTÓN GUARDAR ---
nombre_sis = st.text_input("Nombre para esta jugada:", value=seleccion if seleccion != "-- Nuevo --" else "Sistema 1")
if st.button("💾 GUARDAR CONFIGURACIÓN"):
    ds = {"num_p":num_p, "solo_ganador":solo_ganador, "err_max":err_max, "apuesta_col":apuesta_col, "local":equipos_local, "visit":equipos_visit, "competiciones":competiciones, "base":col_base, "cuotas":matriz_cuotas}
    gestionar_archivos("guardar_sistema", nombre_sis, ds)
    st.rerun()

# --- SIMULADOR POR MARCADORES ---
st.divider()
st.header("🎰 Simulador por Marcadores Reales")
res_sim, goles_l, goles_v = [], [], []
cols_sim = st.columns(num_p)

for i in range(num_p):
    with cols_sim[i]:
        st.write(f"*{equipos_local[i]}*")
        gl = st.number_input("L", min_value=0, step=1, key=f"gl_{i}")
        gv = st.number_input("V", min_value=0, step=1, key=f"gv_{i}")
        goles_l.append(gl); goles_v.append(gv)
        
        if solo_ganador: s_auto = "1" if gl > gv else "2"
        else: s_auto = "1" if gl > gv else ("2" if gv > gl else "X")
        res_sim.append(s_auto)
        st.code(f"Signo: {s_auto}")

# --- MÉTRICAS DE ACIERTO ---
aciertos = sum(1 for b, r in zip(col_base, res_sim) if b == r)
fallos = num_p - aciertos
margen = err_max - fallos
st.progress(aciertos / num_p)

m1, m2, m3 = st.columns(3)
m1.metric("Aciertos", f"{aciertos}/{num_p}")
m2.metric("Margen de Error", f"{margen}", delta_color="normal" if margen >= 0 else "inverse")
m3.metric("Estado", "PREMIO" if margen >= 0 else "SIN PREMIO")

# --- BIBLIOTECA DE ESTADÍSTICAS ---
st.divider()
st.header("📊 Biblioteca y Promedio de Goles")
stats_bd = gestionar_archivos("obtener_stats")

if stats_bd:
    eq_sel = st.selectbox("Consultar Equipo:", list(stats_bd.keys()))
    h = stats_bd[eq_sel]
    g_m = sum(x['goles_f'] for x in h) / len(h)
    g_r = sum(x['goles_c'] for x in h) / len(h)
    
    c_a, c_b = st.columns(2)
    c_a.info(f"⚽ Promedio Goles Marcados: *{g_m:.2f}*")
    c_b.warning(f"🛡️ Promedio Goles Recibidos: *{g_r:.2f}*")
    st.dataframe(h)

if st.checkbox("✅ ¿REGISTRAR COMO JUGADA REAL?"):
    if st.button("🚀 Procesar y Guardar en Historial"):
        datos_hist = []
        for i in range(num_p):
            # Guardar para el Local
            datos_hist.append({"fecha": datetime.now().strftime("%d/%m/%Y"), "equipo": equipos_local[i], "goles_f": goles_l[i], "goles_c": goles_v[i], "resultado": res_sim[i], "acertado": res_sim[i] == col_base[i]})
            # Guardar para el Visitante
            datos_hist.append({"fecha": datetime.now().strftime("%d/%m/%Y"), "equipo": equipos_visit[i], "goles_f": goles_v[i], "goles_c": goles_l[i], "resultado": res_sim[i], "acertado": res_sim[i] == col_base[i]})
        gestionar_archivos("registrar_stats", datos=datos_hist)
        st.success("¡Historial actualizado con marcadores exactos!")
