import streamlit as st
import itertools

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Betsson Pro - Jugada Simple", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN LÓGICA: MOTOR DE DESARROLLO ---
def desarrollasistema(partidos, min_x, max_x, max_err, max_consec, q_min, q_max, f_n, f_min):
    # Generamos todas las combinaciones posibles de los signos elegidos para cada partido
    # partidos = [{'base': '1', 'opciones': ['1', 'X'], 'cuotas': {'1': 1.5, 'X': 3.2, '2': 4.0}}, ...]
    
    opciones_por_partido = []
    for p in partidos:
        # Simplificación: permitimos que el sistema juegue la Base y el Empate como variante si no es la base
        posibles = {p['base'], 'X'} 
        opciones_por_partido.append(list(posibles))

    todas_las_columnas = list(itertools.product(*opciones_por_partido))
    filtradas = []

    for col in todas_las_columnas:
        # 1. Filtro X
        num_x = col.count('X')
        if not (min_x <= num_x <= max_x): continue
        
        # 2. Filtro Errores sobre Base
        errores = sum(1 for i, signo in enumerate(col) if signo != partidos[i]['base'])
        if errores > max_err: continue
        
        # 3. Filtro Consecutividad
        max_c = 1
        current_c = 1
        for i in range(len(col)-1):
            if col[i] == col[i+1]:
                current_c += 1
                max_c = max(max_c, current_c)
            else:
                current_c = 1
        if max_c > max_consec: continue
        
        # 4. Filtro Franja (Fascia Alta)
        err_franja = sum(1 for i in range(f_n) if col[i] != partidos[i]['base'])
        if (f_n - err_franja) < f_min: continue
        
        # 5. Filtro Cuotas
        cuota_total = 1.0
        for i, signo in enumerate(col):
            cuota_total *= partidos[i]['cuotas'][signo]
        
        if q_min <= cuota_total <= q_max:
            filtradas.append((col, cuota_total))
            
    return filtradas

# --- SIDEBAR: PANEL DE CONTROL ---
with st.sidebar:
    st.title("⚙️ Configuración")
    num_partite = st.number_input("Número de eventos", 2, 13, 3)
    
    st.divider()
    st.subheader("🎯 Filtros de Empates (X)")
    c_min, c_max = st.columns(2)
    min_x = c_min.number_input("Min X", 0, num_partite, 0, key="minx")
    max_x = c_max.number_input("Max X", 0, num_partite, num_partite, key="maxx")
    
    st.subheader("🛠️ Filtros Expertos")
    max_errori = st.number_input("Max Errores vs Base", 0, num_partite, 1)
    max_consec = st.slider("Max Consecutivos", 2, 6, 3)
    
    q_range = st.select_slider("Rango Cuota Total", 
                               options=[1.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0, 500.0, 1000.0],
                               value=(10.0, 100.0))

    st.subheader("📏 Filtro Franja Alta")
    f_n = st.number_input("N° primeros partidos", 1, num_partite, 2)
    f_min = st.number_input("Mín. aciertos en franja", 0, f_n, 1)
    
    st.divider()
    btn_genera = st.button("🚀 GENERA SISTEMA", use_container_width=True, type="primary")

# --- CUERPO CENTRAL ---
st.title("🏆 Jugada Simple - Dashboard")

# 1. ENTRADA DE DATOS Y SIMULADOR
with st.expander("📝 1. Datos de Partidos y Simulador Real", expanded=True):
    h1, h2, h3, h4, h5, h6, h7 = st.columns([2, 2, 0.7, 0.7, 0.7, 1, 0.5])
    h1.caption("LOCAL")
    h2.caption("VISITANTE")
    h3.caption("Q1")
    h4.caption("QX")
    h5.caption("Q2")
    h6.caption("BASE")
    h7.caption("GOL")

    lista_partidos = []
    punti_presi = 0
    iconos = []

    for i in range(num_partite):
        c1, c2, c3, c4, c5, c6, c7 = st.columns([2, 2, 0.7, 0.7, 0.7, 1, 0.8])
        with c1: loc = st.text_input(f"L{i}", key=f"l_{i}", label_visibility="collapsed", placeholder="Local")
        with c2: vis = st.text_input(f"V{i}", key=f"v_{i}", label_visibility="collapsed", placeholder="Visita")
        with c3: q1 = st.number_input("Q1", 1.0, 50.0, 1.5, key=f"q1_{i}", label_visibility="collapsed")
        with c4: qx = st.number_input("QX", 1.0, 50.0, 3.0, key=f"qx_{i}", label_visibility="collapsed")
        with c5: q2 = st.number_input("Q2", 1.0, 50.0, 4.0, key=f"q2_{i}", label_visibility="collapsed")
        with c6: base = st.selectbox("B", ["1", "X", "2"], key=f"b_{i}", label_visibility="collapsed")
        with c7: 
            gl = st.number_input("L", 0, 20, 0, key=f"gl_{i}", label_visibility="collapsed")
            gv = st.number_input("V", 0, 20, 0, key=f"gv_{i}", label_visibility="collapsed")
        
        # Lógica de aciertos automática
        res_real = "1" if gl > gv else "2" if gv > gl else "X"
        if res_real == base:
            punti_presi += 1
            iconos.append("🟢")
        else:
            iconos.append("🔴")
            
        lista_partidos.append({'base': base, 'cuotas': {'1': q1, 'X': qx, '2': q2}})

# 2. INDICADORES (KPI)
st.divider()
k1, k2, k3 = st.columns(3)
k1.metric("Aciertos Base", f"{punti_presi} / {num_partite}")
k2.metric("Progreso", " ".join(iconos))
k3.metric("Estado", "En juego" if punti_presi < num_partite else "🏆 Ganador")

# 3. SCROLLVIEW DE RESULTADOS
st.subheader("📋 Columnas Generadas")
if 'cols' not in st.session_state: st.session_state.cols = []

if btn_genera:
    st.session_state.cols = desarrollasistema(lista_partidos, min_x, max_x, max_errori, max_consec, q_range[0], q_range[1], f_n, f_min)

with st.container(height=400, border=True):
    if st.session_state.cols:
        for idx, (colonna, cuota) in enumerate(st.session_state.cols):
            r1, r2 = st.columns([1, 4])
            r1.markdown(f"**#{idx+1}** |  📈 `{cuota:.2f}`")
            r2.markdown(f"` {'  '.join(colonna)} `")
            st.divider()
    else:
        st.info("Configura los filtros y pulsa 'Genera Sistema'")
