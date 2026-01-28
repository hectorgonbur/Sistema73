import streamlit as st
import itertools

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistemista Pro", layout="wide")
st.title("📊 Sviluppo 6 Triple - Sistema Profesional")

# --- VARIABLES GLOBALES ---
num_p = 6
nombres_equipos = [f"Partido {i+1}" for i in range(num_p)] 
opciones = ["1", "X", "2"] # Las opciones para el selector manual

# --- SIDEBAR ---
st.sidebar.header("1. Configuración")
costo_colonna = st.sidebar.number_input("Costo por columna (€)", min_value=0.1, value=1.0, step=0.1)
max_err = st.sidebar.radio("Errores permitidos (Reducción)", [0, 1, 2], index=1)

# --- SECCIÓN 1: PRONÓSTICO BASE ---
st.subheader("2. Define tu Base y Cuotas")
st.info("Elige tu pronóstico lógico y las cuotas de la casa de apuestas.")

col_base = [] 
quote_partite = []

cols = st.columns(num_p)
for i in range(num_p):
    with cols[i]:
        st.markdown(f"**{nombres_equipos[i]}**")
        # Selección del signo base
        b = st.selectbox(f"Base", opciones, key=f"b{i}")
        col_base.append(b)
        
        # Inputs de cuotas
        q1 = st.number_input(f"Q(1)", value=1.50, format="%.2f", key=f"q1_{i}")
        qx = st.number_input(f"Q(X)", value=3.20, format="%.2f", key=f"qx_{i}")
        q2 = st.number_input(f"Q(2)", value=4.50, format="%.2f", key=f"q2_{i}")
        quote_partite.append({"1": q1, "X": qx, "2": q2})

# --- MOTOR LÓGICO ---
def genera_sistema(base_user, err_maxima, quotes):
    combinazioni = itertools.product(opciones, repeat=num_p)
    sistema = []
    
    for c in combinazioni:
        diff = sum(1 for i in range(num_p) if c[i] != base_user[i])
        if diff <= err_maxima:
            quota_tot = 1.0
            for idx, s in enumerate(c):
                quota_tot *= quotes[idx][s]
            
            sistema.append({
                "Columna": "-".join(c), # Formato clave: "1-X-2..."
                "Fallos": diff,
                "Quota": round(quota_tot, 2),
                "Vincita Lorda": round(quota_tot * costo_colonna, 2)
            })
    return sistema

# Generamos el sistema
df_sistema = genera_sistema(col_base, max_err, quote_partite)
spesa = len(df_sistema) * costo_colonna

st.write(f"📊 **Sistema Generado:** {len(df_sistema)} columnas cubiertas. Costo: **{spesa:.2f}€**")

# --- SECCIÓN 2: SIMULADOR MANUAL (TU CÓDIGO CORREGIDO) ---
st.divider()
st.header("🎰 Simulador de Resultados Reales")
st.write("Selecciona lo que ha sucedido realmente en cada partido para verificar premios:")

# 1. Selectores manuales
res_sim = []
cols_sim = st.columns(num_p)

for i in range(num_p):
    with cols_sim[i]:
        # Selector manual directo (1, X, 2)
        st.caption(f"🏁 {nombres_equipos[i]}")
        res_s = st.selectbox("Resultado", opciones, key=f"sim_manual_{i}", label_visibility="collapsed")
        res_sim.append(res_s)

# --- PANEL DE CONTROL DE ACIERTOS ---
# Calculamos aciertos comparando la BASE con el SIMULADOR
aciertos = sum(1 for b, r in zip(col_base, res_sim) if b == r)
fallos = num_p - aciertos
margen = max_err - fallos # Usamos 'max_err' del sidebar
porcentaje = aciertos / num_p

st.markdown("---")
# Barra de progreso visual
bar_color = "green" if margen >= 0 else "red"
st.write(f"*Coincidencia con la Base:* {aciertos} de {num_p}")
st.progress(porcentaje)

# Métricas grandes
c1, c2, c3 = st.columns(3)
c1.metric("✅ Aciertos Base", f"{aciertos}")
# El delta color 'inverse' hace que si el margen es negativo, salga rojo
c2.metric("❌ Fallos Base", f"{fallos}", delta=f"Margen Restante: {margen}", delta_color="normal" if margen >= 0 else "inverse")

estado_texto = "EN CARRERA" if margen >= 0 else "FUERA DE SISTEMA"
c3.metric("🎯 Estado", estado_texto)

# --- BOTÓN DE PROCESAMIENTO ---
st.write("")
col_check, col_btn = st.columns([1, 2])

with col_check:
    es_real = st.checkbox("✅ ¿REGISTRAR JUGADA?", help="Simula guardar en base de datos.")

with col_btn:
    if st.button("🚀 CALCULAR GANANCIAS FINAL", type="primary"):
        
        # 1. Construimos la cadena ganadora (ej: "1-X-1-2-1-1")
        columna_ganadora_str = "-".join(res_sim)
        
        # 2. Buscamos si esa columna existe en nuestro sistema generado
        # (Filtramos la lista de diccionarios 'df_sistema')
        columna_encontrada = next((item for item in df_sistema if item["Columna"] == columna_ganadora_str), None)
        
        st.divider()
        if columna_encontrada:
            dinero = columna_encontrada['Vincita Lorda']
            st.balloons()
            st.success(f"💰 ¡FELICIDADES! Tienes una columna ganadora.")
            st.metric(label="Cobras Exactamente:", value=f"{dinero} €", delta=f"Beneficio Neto: {dinero - spesa:.2f} €")
            
            # Mostramos los detalles técnicos
