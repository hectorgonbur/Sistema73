import streamlit as st

st.header("🎰 Simulador por Marcadores (Goles/Puntos)")
st.write("Ingresa los goles o puntos de cada equipo para calcular el resultado:")

res_sim = []
cols_sim = st.columns(num_p)

for i in range(num_p):
    with cols_sim[i]:
        st.markdown(f"*{nombres_equipos[i]}*")
        # Campos para goles
        g_loc = st.number_input("Local", min_value=0, step=1, key=f"gl_{i}")
        g_vis = st.number_input("Visit.", min_value=0, step=1, key=f"gv_{i}")
        
        # Lógica automática de signo
        if solo_ganador: # Si es Tenis/Basket (No hay empate)
            signo_auto = "1" if g_loc > g_vis else "2"
        else: # Fútbol (Con empate)
            if g_loc > g_vis: signo_auto = "1"
            elif g_loc < g_vis: signo_auto = "2"
            else: signo_auto = "X"
            
        # Mostrar el signo detectado
        color_signo = "🟢" if signo_auto == col_base[i] else "🔴"
        st.code(f"Resultado: {signo_auto} {color_signo}")
        
        res_sim.append(signo_auto)

# --- CONTADOR DINÁMICO ---
aciertos = sum(1 for b, r in zip(col_base, res_sim) if b == r)
fallos = num_p - aciertos
margen = err_max - fallos

st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("✅ Aciertos", f"{aciertos}")
c2.metric("❌ Fallos", f"{fallos}", delta=f"Margen: {margen}")
c3.progress(aciertos / num_p)

if margen >= 0:
    st.success(f"¡Vas por buen camino! Estás dentro de los {err_max} errores permitidos.")
else:
    st.error(f"Se han superado los errores. Sistema sin premio.")

# Botón para registrar en biblioteca
if st.checkbox("💾 ¿Guardar marcadores finales en la Biblioteca?"):
    if st.button("Confirmar y Registrar"):
        # Aquí se guarda en el historial de equipos con los marcadores incluidos
        pass
