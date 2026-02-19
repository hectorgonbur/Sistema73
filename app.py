import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Sistema de Apuestas", layout="wide")

# --- INICIALIZACIÓN DE STATE ---
if 'num_eventos' not in st.session_state:
    st.session_state.num_eventos = 1
if 'num_jugadas_sist' not in st.session_state:
    st.session_state.num_jugadas_sist = 1

# --- MENÚ LATERAL (Nivel 1 y 2) ---
with st.sidebar:
    st.header("🏆 Menú")
    menu_principal = st.radio("Navegación:", ["🏠 Inicio", "💰 Apuestas", "📂 Mis Apuestas", "📥 Exportar"])

    sub_seccion = None
    herramienta_sistematica = None

    if menu_principal == "💰 Apuestas":
        st.markdown("---")
        sub_seccion = st.radio("Sección:", ["Jugada", "Cálculo Sistemático"])
        
        if sub_seccion == "Cálculo Sistemático":
            st.markdown("---")
            st.subheader("🛠️ Herramientas")
            herramienta_sistematica = st.radio("Sub-opciones:", ["Jugadas", "Cálculo Columnas", "Ganancias"])

# --- LÓGICA DE SECCIONES ---

# 1. SECCIÓN JUGADA (Antiguo Registro)
if sub_seccion == "Jugada":
    st.title("⚽ Gestión de Jugada")
    
    # Cálculo de Marcador Global (Ganados / Jugados)
    aciertos = 0
    for i in range(st.session_state.num_eventos):
        r1 = st.session_state.get(f"res1_{i}", "0")
        r2 = st.session_state.get(f"res2_{i}", "0")
        base = st.session_state.get(f"base_{i}", "1")
        try:
            ir1, ir2 = int(r1), int(r2)
            real = "1" if ir1 > ir2 else ("2" if ir1 < ir2 else "X")
            if real == base and (ir1 > 0 or ir2 > 0): aciertos += 1
        except: pass

    # Cabecera: Contador y Resultados
    col_c1, col_c2, col_c3, col_txt, col_score = st.columns([1, 1, 1, 2, 2])
    with col_c1:
        if st.button("➖", key="m1") and st.session_state.num_eventos > 1:
            st.session_state.num_eventos -= 1
            st.rerun()
    with col_c2:
        st.markdown(f"### {st.session_state.num_eventos}")
    with col_c3:
        if st.button("➕", key="p1") and st.session_state.num_eventos < 30:
            st.session_state.num_eventos += 1
            st.rerun()
    with col_txt:
        st.markdown("### Resultados:")
    with col_score:
        st.markdown(f"### <span style='color:#2ecc71;'>{aciertos}</span> / {st.session_state.num_eventos}", unsafe_allow_html=True)

    st.markdown("### EVENTOS")
    
    for i in range(st.session_state.num_eventos):
        # Lógica de la Bolita
        r1_val = st.session_state.get(f"res1_{i}", "0")
        r2_val = st.session_state.get(f"res2_{i}", "0")
        base_val = st.session_state.get(f"base_{i}", "1")
        
        bolita = "⚪"
        try:
            ir1, ir2 = int(r1_val), int(r2_val)
            if ir1 == 0 and ir2 == 0: bolita = "⚪"
            else:
                real = "1" if ir1 > ir2 else ("2" if ir1 < ir2 else "X")
                bolita = "🟢" if real == base_val else "🔴"
        except: pass

        # FILA 1: Info General + Bolita
        f1c1, f1c2, f1c3, f1c4, f1c5 = st.columns([1.5, 3, 2, 1.5, 1])
        with f1c1: st.selectbox(f"Deporte", ["⚽", "🏀", "🎾", "🥊"], key=f"dep_{i}")
        with f1c2: st.text_input(f"Evento", placeholder="Liga/Torneo", key=f"tipo_{i}")
        with f1c3: st.date_input(f"Fecha", key=f"fec_{i}")
        with f1c4: st.text_input(f"Hora", value="20:00", key=f"hor_{i}")
        with f1c5: st.markdown(f"## {bolita}")

        # FILA 2: Marcador, Cuotas y Base
        f2c1, f2r1, f2r2, f2c2, f2c3, f2c4, f2c5, f2c6 = st.columns([2, 0.7, 0.7, 2, 0.8, 0.8, 0.8, 1.2])
        with f2c1: st.text_input("Local", key=f"e1_{i}")
        with f2r1: st.text_input("R1", key=f"res1_{i}", value="0")
        with f2r2: st.text_input("R2", key=f"res2_{i}", value="0")
        with f2c2: st.text_input("Visitante", key=f"e2_{i}")
        with f2c3: st.number_input("C1", min_value=1.0, step=0.01, key=f"c1_{i}")
        with f2c4: st.number_input("CX", min_value=1.0, step=0.01, key=f"cx_{i}")
        with f2c5: st.number_input("C2", min_value=1.0, step=0.01, key=f"c2_{i}")
        with f2c6: st.selectbox("Base", ["1", "X", "2"], key=f"base_{i}")
        st.markdown("---")

# 2. SECCIÓN CÁLCULO SISTEMÁTICO (Sub-niveles)
elif sub_seccion == "Cálculo Sistemático":
    if herramienta_sistematica == "Jugadas":
        st.title("📂 Definición de Jugadas")
        
        # Contador específico para Jugadas Sistemáticas
        col_s1, col_s2, col_s3 = st.columns([1, 1, 1])
        with col_s1:
            if st.button("➖", key="sm") and st.session_state.num_jugadas_sist > 1:
                st.session_state.num_jugadas_sist -= 1
                st.rerun()
        with col_s2:
            st.markdown(f"<h2 style='text-align:center;'>{st.session_state.num_jugadas_sist}</h2>", unsafe_allow_html=True)
        with col_s3:
            if st.button("➕", key="sp") and st.session_state.num_jugadas_sist < 30:
                st.session_state.num_jugadas_sist += 1
                st.rerun()

        st.markdown("---")
        for j in range(st.session_state.num_jugadas_sist):
            sc1, sc2, sc3, sc4 = st.columns([0.5, 3, 1, 1])
            with sc1: st.write(f"#{j+1}")
            with sc2: st.text_input("Partido", key=f"sist_ev_{j}")
            with sc3: st.number_input("Cuota", key=f"sist_cuo_{j}", min_value=1.0)
            with sc4: st.selectbox("Pronóstico", ["1", "X", "2"], key=f"sist_base_{j}")

    elif herramienta_sistematica == "Cálculo Columnas":
        st.title("📋 Cálculo de Columnas")
        st.info("Aquí se procesarán las combinaciones de los eventos definidos.")

    elif herramienta_sistematica == "Ganancias":
        st.title("💰 Ganancias")
        st.write("Cálculo del retorno basado en las cuotas seleccionadas.")

# 3. OTROS (Inicio)
elif menu_principal == "🏠 Inicio":
    st.title("Bienvenido a tu App de Apuestas")
    st.write("Selecciona '💰 Apuestas' para empezar.")
