import streamlit as st
import itertools
import json
import os
from datetime import datetime

st.set_page_config(page_title="Betsson Pro: Real vs Virtual", layout="wide")

# --- PERSISTENCIA MEJORADA ---
def gestionar_archivos(accion, nombre=None, datos=None):
    arch_sistemas = "mis_sistemas_premium.json"
    arch_stats = "historial_equipos_pro.json"
    
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

# --- INTERFAZ PRINCIPAL ---
st.title("🏆 Betsson System & Analytics")
nombres_s = gestionar_archivos("listar_sistemas")
seleccion = st.sidebar.selectbox("📂 Abrir Jugada:", ["-- Nuevo --"] + nombres_s)
datos_c = gestionar_archivos("cargar_sistema", seleccion) if seleccion != "-- Nuevo --" else None

# (Parámetros de configuración simplificados para este bloque)
st.sidebar.header("⚙️ Configuración")
num_p = st.sidebar.slider("Partidos", 2, 10, datos_c["num_p"] if datos_c else 6)
solo_ganador = st.sidebar.checkbox("Modo 2 Resultados", value=datos_c["solo_ganador"] if datos_c else False)
opciones = ["1", "2"] if solo_ganador else ["1", "X", "2"]
err_max = st.sidebar.select_slider("Errores", options=[1, 2, 3, 4], value=datos_c["err_max"] if datos_c else 2)
apuesta = st.sidebar.number_input("Inversión (€/col)", value=datos_c["apuesta"] if datos_c else 1.0)

# --- ENTRADA DE EQUIPOS Y CUOTAS ---
# [Aquí se mantiene la misma estructura de nombres de equipos y cuotas que definimos antes]
# ...

# --- SECCIÓN DEL SIMULADOR CON INTERRUPTOR ---
st.divider()
st.header("🎰 Simulador y Registro de Resultados")

col_sim1, col_sim2 = st.columns([2, 1])

with col_sim1:
    st.write("Selecciona los resultados de los partidos:")
    res_sim = [st.selectbox(f"Res. {i+1}", opciones, key=f"sim_{i}") for i in range(num_p)]

with col_sim2:
    st.write("🔧 Opciones de Registro")
    es_real = st.checkbox("✅ ¿ES UNA JUGADA REAL?", help="Si marcas esto, los resultados se guardarán en tu biblioteca de estadísticas. Si no, será solo una prueba visual.")
    boton_simular = st.button("🚀 CALCULAR PREMIO")

if boton_simular:
    # Lógica de cálculo de premios (ya definida)
    # ...
    
    if es_real:
        # Solo guardamos en la biblioteca si el interruptor está activo
        nuevos_datos = []
        for i in range(num_p):
            # (Aquí va la lógica de recopilación de datos para cada equipo...)
            pass 
        gestionar_archivos("registrar_stats", datos=nuevos_datos)
        st.success("📊 ¡Datos guardados en tu historial de equipos!")
    else:
        st.info("💡 Prueba virtual finalizada. Los datos no se han guardado en la biblioteca.")

# --- BIBLIOTECA DE ESTADÍSTICAS ---
st.divider()
st.subheader("📚 Biblioteca de Rendimiento Real")
# [Aquí se muestra la tabla de estadísticas con la opción de filtrar solo por 'Reales']
