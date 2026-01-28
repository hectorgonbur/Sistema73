import streamlit as st
import itertools

# --- SECCIÓN DEL SIMULADOR (VOLVIENDO A SELECTORES MANUALES) ---
st.divider()
st.header("🎰 Simulador de Resultados Reales")
st.write("Selecciona lo que ha sucedido en cada partido:")

# 1. Selectores manuales para cada partido
res_sim = []
cols_sim = st.columns(num_p)
for i in range(num_p):
    with cols_sim[i]:
        # Mostramos el nombre del equipo y el selector
        res_s = st.selectbox(f"{nombres_equipos[i]}", opciones, key=f"sim_manual_{i}")
        res_sim.append(res_s)

# --- PANEL DE CONTROL DE ACIERTOS (VISUAL) ---
# Calculamos aciertos comparando la BASE con lo que el usuario puso en el SIMULADOR
aciertos = sum(1 for b, r in zip(col_base, res_sim) if b == r)
fallos = num_p - aciertos
margen = err_max - fallos
porcentaje = aciertos / num_p

st.markdown("---")
st.write(f"*Progreso de la Jugada:* {aciertos} de {num_p} aciertos")
st.progress(porcentaje)

# Métricas grandes para ver en el celular
c1, c2, c3 = st.columns(3)
c1.metric("✅ Aciertos", f"{aciertos}")
c2.metric("❌ Fallos", f"{fallos}", delta=f"Margen: {margen}", delta_color="normal" if margen >= 0 else "inverse")
c3.metric("🎯 Estado", "PREMIO" if margen >= 0 else "SIN PREMIO")

# --- BOTÓN DE PROCESAMIENTO ---
st.write("")
es_real = st.checkbox("✅ ¿REGISTRAR COMO JUGADA REAL?", help="Marca esto solo si los partidos han terminado y quieres guardar los datos en tu biblioteca.")

if st.button("🚀 CALCULAR GANANCIAS FINAL"):
    # Aquí iría la lógica de buscar la columna ganadora en el sistema y mostrar el dinero
    # Y si 'es_real' es True, guardar en la biblioteca de equipos.
    pass
