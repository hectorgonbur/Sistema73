import streamlit as st
import itertools

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistemista Pro", layout="wide")
st.title("📊 Sviluppo 6 Triple con Simulador")

# --- VARIABLES GLOBALES ---
num_p = 6  # Número fijo de partidos
nombres_equipos = [f"Partido {i+1}" for i in range(num_p)] # Nombres genéricos
solo_ganador = False # False = Fútbol (hay empate), True = Tenis/Basket

# --- SIDEBAR ---
st.sidebar.header("1. Configuración")
costo_colonna = st.sidebar.number_input("Costo por columna (€)", min_value=0.1, value=1.0, step=0.1)
max_err = st.sidebar.radio("Errores permitidos", [0, 1, 2], index=1)

# --- SECCIÓN 1: PRONÓSTICOS (BASE) ---
st.subheader("2. Define tu Base y Cuotas")
st.info("Elige tu pronóstico base (lo que crees que pasará) y las cuotas.")

col_base = [] # Aquí guardaremos lo que el usuario elige (1, X, 2)
quote_partite = []

cols = st.columns(num_p)
for i in range(num_p):
    with cols[i]:
        st.markdown(f"**{nombres_equipos[i]}**")
        # Selección del signo base
        b = st.selectbox(f"Base", ["1", "X", "2"], key=f"b{i}")
        col_base.append(b)
        
        # Inputs de cuotas
        q1 = st.number_input(f"Q(1)", value=1.50, format="%.2f", key=f"q1_{i}")
        qx = st.number_input(f"Q(X)", value=3.20, format="%.2f", key=f"qx_{i}")
        q2 = st.number_input(f"Q(2)", value=4.50, format="%.2f", key=f"q2_{i}")
        quote_partite.append({"1": q1, "X": qx, "2": q2})

# --- LÓGICA DEL SISTEMA (Matemática) ---
def genera_sistema(base_user, err_maxima, quotes):
    esiti = ["1", "X", "2"]
    combinazioni = itertools.product(esiti, repeat=num_p)
    sistema = []
    
    for c in combinazioni:
        diff = sum(1 for i in range(num_p) if c[i] != base_user[i])
        if diff <= err_maxima:
            quota_tot = 1.0
            for idx, s in enumerate(c):
                quota_tot *= quotes[idx][s]
            
            sistema.append({
                "Columna": "-".join(c),
                "Fallos": diff,
                "Quota": round(quota_tot, 2),
                "Ganancia": round(quota_tot * costo_colonna, 2)
            })
    return sistema

df_sistema = genera_sistema(col_base, max_err, quote_partite)
spesa = len(df_sistema) * costo_colonna

st.write(f"📊 **Sistema Generado:** {len(df_sistema)} columnas. Costo: **{spesa:.2f}€**")

# --- SECCIÓN 2: TU NUEVA MEJORA (SIMULADOR) ---
st.divider()
st.header("🎰 Simulador por Marcadores (Checkeo Real)")
st.write("Ingresa los goles reales para ver si tu base acierta:")

res_sim = []
cols_sim = st.columns(num_p)

# Usamos 'num_p' y 'nombres_equipos' definidos arriba
for i in range(num_p):
    with cols_sim[i]:
        st.caption(f"🏁 {nombres_equipos[i]}")
        
        # Campos para goles (usamos columnas pequeñas dentro de la columna)
        c_loc, c_vis = st.columns(2)
        g_loc = c_loc.number_input("Loc", min_value=0, step=1, key=f"gl_{i}")
        g_vis = c_vis.number_input("Vis", min_value=0, step=1, key=f"gv_{i}")
        
        # Lógica automática de signo
        if solo_ganador: 
            signo_auto = "1" if g_loc > g_vis else "2"
        else: # Fútbol
            if g_loc > g_vis: signo_auto = "1"
            elif g_loc < g_vis: signo_auto = "2"
            else: signo_auto = "X"
            
        # Mostrar el signo detectado vs Base
        # Comparamos con col_base[i] que viene de arriba
        es_acierto = (signo_auto == col_base[i])
        color_signo = "🟢" if es_acierto else "🔴"
        
        st.markdown(f"Res: **{signo_auto}** {color_signo}")
        res_sim.append(signo_auto)

# --- CONTADOR DINÁMICO ---
aciertos = sum(1 for b, r in zip(col_base, res_sim) if b == r)
fallos = num_p - aciertos
margen = max_err - fallos # Usamos 'max_err' definido en sidebar

st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("✅ Aciertos Base", f"{aciertos}/{num_p}")
c2.metric("❌ Fallos Base", f"{fallos}", delta=f"Margen Restante: {margen}")
c3.progress(aciertos / num_p)

if margen >= 0:
    st.success(f"🎉 ¡Bien! Tu pronóstico base está dentro de los {max_err} errores permitidos.")
    st.balloons()
else:
    st.error(f"💀 Se han superado los errores permitidos. La columna base ha fallado.")

# Botón extra (Decorativo por ahora)
if st.checkbox("💾 ¿Guardar en historial?"):
    if st.button("Confirmar y Registrar"):
        st.toast("Datos guardados (simulado)", icon="💾")
