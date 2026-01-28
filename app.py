import streamlit as st
import itertools

st.set_page_config(page_title="Simulador de Sistemas Betsson", layout="wide")

st.title("🚀 Simulador de Sistemas Pro: Multi-Error y Multi-Partido")

# --- CONFIGURACIÓN EN LA BARRA LATERAL ---
st.sidebar.header("⚙️ Parámetros del Sistema")
num_partidos = st.sidebar.slider("Número de partidos", 2, 10, 6)
solo_ganador = st.sidebar.checkbox("Modo 2 resultados (Sin X)", value=False)
opciones = ["1", "2"] if solo_ganador else ["1", "X", "2"]
max_errores = st.sidebar.select_slider("Errores a corregir", options=list(range(1, 5)), value=2)
apuesta_col = st.sidebar.number_input("Inversión por columna (€)", min_value=0.1, value=1.0)

# --- ENTRADA DE CUOTAS ---
st.sidebar.header("📈 Cuotas Reales")
matriz_cuotas = []
for i in range(num_partidos):
    st.sidebar.subheader(f"Partido {i+1}")
    cols_q = st.sidebar.columns(len(opciones))
    dict_q = {}
    for j, op in enumerate(opciones):
        dict_q[op] = cols_q[j].number_input(f"Cuota {op}", min_value=1.01, value=2.0, key=f"q_{op}_{i}")
    matriz_cuotas.append(dict_q)

# --- COLUMNA BASE Y SIMULACIÓN ---
st.subheader("1. Configuración de Base y Resultados Reales")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 Tu Columna Base")
    base = [st.selectbox(f"Base Part. {i+1}", opciones, key=f"b_{i}") for i in range(num_partidos)]

with col2:
    st.markdown("### 🏟️ Resultados Reales (Simulación)")
    reales = [st.selectbox(f"Resultado Real {i+1}", opciones, key=f"r_{i}") for i in range(num_partidos)]

# --- LÓGICA DE GENERACIÓN ---
def generar_sistema():
    combs_posibles = itertools.product(opciones, repeat=num_partidos)
    sistema = []
    for c in combs_posibles:
        diff_base = sum(1 for i in range(num_partidos) if c[i] != base[i])
        if diff_base <= max_errores:
            cuota_t = 1.0
            for p, signo in enumerate(c):
                cuota_t *= matriz_cuotas[p][signo]
            sistema.append({"comb": c, "bruta": cuota_t * apuesta_col})
    return sistema

sistema_final = generar_sistema()
inversion_total = len(sistema_final) * apuesta_col

# --- BOTÓN DE SIMULACIÓN Y CÁLCULO DE PREMIO ---
st.divider()
if st.button("🎰 EJECUTAR SIMULACIÓN DE PREMIOS"):
    ganancia_total_bruta = 0
    columnas_ganadoras = 0
    
    for col in sistema_final:
        if list(col["comb"]) == reales:
            ganancia_total_bruta += col["bruta"]
            columnas_ganadoras += 1
    
    ganancia_neta = ganancia_total_bruta - inversion_total
    
    # Mostrar resultados de la simulación
    s1, s2, s3 = st.columns(3)
    s1.metric("Columnas Ganadoras", columnas_ganadoras)
    s2.metric("Total Cobrado (Bruto)", f"{ganancia_total_bruta:.2f} €")
    s3.metric("Balance Final (Neto)", f"{ganancia_neta:.2f} €", delta=round(ganancia_neta, 2))
    
    if ganancia_neta > 0:
        st.balloons()
        st.success(f"¡Felicidades! Has ganado {ganancia_neta:.2f} € netos.")
    else:
        st.error(f"Pérdida neta de {abs(ganancia_neta):.2f} €. Inténtalo de nuevo.")

# --- TABLA DE TODAS LAS COLUMNAS ---
st.subheader(f"📋 Desglose del Sistema ({len(sistema_final)} columnas)")
tabla_detallada = []
for i, d in enumerate(sistema_final, 1):
    tabla_detallada.append({
        "Nº": i,
        "Combinación": " - ".join(d["comb"]),
        "Ganancia Bruta": f"{d['bruta']:.2f} €",
        "Ganancia Neta": f"{(d['bruta'] - inversion_total):.2f} €"
    })

st.dataframe(tabla_detallada, use_container_width=True)
