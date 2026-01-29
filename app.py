import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Betsson Pro: Gestor Portátil", layout="wide")

st.title("⚽ Betsson Pro: Sistema de Gestión de Apuestas")

# --- FUNCIÓN PARA CARGAR DATOS EN SESSION STATE ---
# Esta función es mágica: toma el archivo subido y rellena los huecos automáticamente
def cargar_datos_en_session_state(datos):
    # 1. Ajustar número de partidos y configuraciones generales
    st.session_state["num_p_slider"] = datos.get("num_p", 6)
    st.session_state["solo_ganador_check"] = datos.get("solo_ganador", False)
    st.session_state["err_max_slider"] = datos.get("err_max", 2)
    st.session_state["apuesta_input"] = datos.get("apuesta_col", 1.0)
    
    # 2. Rellenar los campos de cada partido
    num = datos.get("num_p", 6)
    for i in range(num):
        try:
            # Recuperamos claves (keys) dinámicas
            st.session_state[f"c_{i}"] = datos["competiciones"][i]
            st.session_state[f"l_{i}"] = datos["local"][i]
            st.session_state[f"v_{i}"] = datos["visit"][i]
            st.session_state[f"b_{i}"] = datos["base"][i]
            
            # Recuperamos cuotas
            opciones_carga = ["1", "2"] if datos.get("solo_ganador") else ["1", "X", "2"]
            for op in opciones_carga:
                st.session_state[f"q_{op}_{i}"] = datos["cuotas"][i].get(op, 1.0)
        except IndexError:
            pass # Si el archivo tiene menos datos de los esperados

# --- BARRA LATERAL: IMPORTAR/EXPORTAR ---
st.sidebar.header("📂 Archivo de Jugada")
st.sidebar.info("Sube tu archivo .json para restaurar una jugada anterior.")

# 1. WIDGET DE SUBIDA (UPLOAD)
archivo_subido = st.sidebar.file_uploader("Cargar Jugada Guardada", type=["json"])

if archivo_subido is not None:
    try:
        datos_cargados = json.load(archivo_subido)
        # Botón para confirmar la carga (evita recargas accidentales)
        if st.sidebar.button("🔄 Restaurar Datos del Archivo"):
            cargar_datos_en_session_state(datos_cargados)
            st.toast("¡Datos restaurados con éxito!", icon="✅")
            st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error al leer el archivo: {e}")

st.sidebar.divider()

# --- CONFIGURACIÓN GENERAL ---
st.sidebar.header("⚙️ Parámetros")

# Usamos claves (keys) para poder modificarlas desde la carga del archivo
num_p = st.sidebar.slider("Partidos", 2, 10, key="num_p_slider", value=6)
solo_ganador = st.sidebar.checkbox("Modo 2 Resultados (Tenis/Basket)", key="solo_ganador_check", value=False)
err_max = st.sidebar.select_slider("Errores a corregir", options=[1,2,3,4], key="err_max_slider", value=2)
apuesta_col = st.sidebar.number_input("Inversión por columna (€)", min_value=0.1, key="apuesta_input", value=1.0)

opciones = ["1", "2"] if solo_ganador else ["1", "X", "2"]

# --- ENTRADA DE DATOS (GRID) ---
st.subheader("📝 Configuración de Encuentros")
matriz_cuotas, col_base, equipos_local, equipos_visit, competiciones = [], [], [], [], []

grid = st.columns(2)
for i in range(num_p):
    with grid[i % 2]:
        with st.expander(f"PARTIDO {i+1}", expanded=True):
            # Usamos st.session_state.get para valores por defecto seguros
            comp = st.text_input("Competición", key=f"c_{i}", value="Liga")
            competiciones.append(comp)
            
            c_l, c_v = st.columns(2)
            loc = c_l.text_input("🏠 Local", key=f"l_{i}", value=f"Local {i+1}")
            vis = c_v.text_input("🚀 Visitante", key=f"v_{i}", value=f"Visitante {i+1}")
            equipos_local.append(loc); equipos_visit.append(vis)

            c_b, c_qs = st.columns([1, 3])
            b = c_b.selectbox("Base", opciones, key=f"b_{i}")
            col_base.append(b)
            
            q_cols = c_qs.columns(len(opciones))
            d_q = {}
            for j, op in enumerate(opciones):
                val_q = q_cols[j].number_input(f"Q{op}", min_value=1.01, key=f"q_{op}_{i}", value=2.0)
                d_q[op] = val_q
            matriz_cuotas.append(d_q)

# --- LÓGICA DE EXPORTACIÓN (DESCARGA) ---
st.divider()
st.subheader("💾 Guardar y Descargar")

col_d1, col_d2 = st.columns([3, 1])
with col_d1:
    nombre_archivo = st.text_input("Nombre del archivo:", value="mi_jugada_semanal")

# Preparamos el diccionario de datos ACTUALES en pantalla
datos_para_exportar = {
    "num_p": num_p,
    "solo_ganador": solo_ganador,
    "err_max": err_max,
    "apuesta_col": apuesta_col,
    "local": equipos_local,
    "visit": equipos_visit,
    "competiciones": competiciones,
    "base": col_base,
    "cuotas": matriz_cuotas,
    "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

# Convertimos a JSON texto
json_string = json.dumps(datos_para_exportar, indent=4)

with col_d2:
    st.write("##") # Espaciado
    st.download_button(
        label="⬇️ Descargar Archivo .JSON",
        data=json_string,
        file_name=f"{nombre_archivo}.json",
        mime="application/json",
        help="Descarga este archivo y súbelo la próxima vez para recuperar todo."
    )

# --- SIMULADOR POR MARCADORES ---
st.divider()
st.header("🎰 Simulador por Marcadores Reales")
res_sim, goles_l, goles_v = [], [], []
cols_sim = st.columns(num_p)

# Importante: No usamos claves fijas aquí para permitir reseteo fácil
for i in range(num_p):
    with cols_sim[i]:
        st.caption(f"{equipos_local[i]} vs {equipos_visit[i]}")
        c_gl, c_gv = st.columns(2)
        gl = c_gl.number_input("L", min_value=0, step=1, key=f"sim_gl_{i}")
        gv = c_gv.number_input("V", min_value=0, step=1, key=f"sim_gv_{i}")
        goles_l.append(gl); goles_v.append(gv)
        
        if solo_ganador: s_auto = "1" if gl > gv else "2"
        else: s_auto = "1" if gl > gv else ("2" if gv > gl else "X")
        res_sim.append(s_auto)
        
        color = "🟢" if s_auto == col_base[i] else "🔴"
        st.markdown(f"**{s_auto}** {color}")

# --- MÉTRICAS ---
aciertos = sum(1 for b, r in zip(col_base, res_sim) if b == r)
fallos = num_p - aciertos
margen = err_max - fallos
st.progress(aciertos / num_p)

m1, m2, m3 = st.columns(3)
m1.metric("Aciertos Base", f"{aciertos}/{num_p}")
m2.metric("Margen Restante", f"{margen}", delta_color="normal" if margen >= 0 else "inverse")

if margen >= 0:
    st.success("🎉 ¡EN PREMIO! El sistema cubre los fallos actuales.")
else:
    st.error("💀 FUERA DE PREMIO. Demasiados errores para la reducción elegida.")
