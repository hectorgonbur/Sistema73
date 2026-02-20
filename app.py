import streamlit as st
import itertools
import pandas as pd
import json
import os
from datetime import datetime

# 1. PRIMER COMANDO
st.set_page_config(page_title="App de Apuestas Pro", layout="wide")

# 2. ESTILO VISUAL
st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    .stApp, .stApp p, .stApp span, .stApp h1, .stApp h2, .stApp h3, .stApp label { color: black !important; }
    [data-testid="stSidebar"] { background-color: #f0f2f6 !important; }
    [data-testid="stSidebar"] * { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

DATA_FILE = "datos_apuestas.json"

def cargar_datos():
    if not os.path.exists(DATA_FILE):
        return {"jugadas": {}, "stats": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"jugadas": {}, "stats": []}

def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4)

def registrar_stats_json(local, visitante, base, resultado_real, deporte, liga, fecha, hora):
    datos = cargar_datos()
    stats = datos["stats"]
    
    def buscar_equipo(nombre, dep, lig):
        for s in stats:
            if s["equipo"] == nombre and s["deporte"] == dep and s["liga"] == lig:
                return s
        nuevo = {"equipo": nombre, "deporte": dep, "liga": lig, "apostado": 0, "aciertos": 0, "desaciertos": 0, "ultima_act": ""}
        stats.append(nuevo)
        return nuevo

    eq_l = buscar_equipo(local, deporte, liga)
    eq_v = buscar_equipo(visitante, deporte, liga)
    
    # Actualizar fecha de última actividad del equipo
    timestamp = f"{fecha} {hora}"
    eq_l["ultima_act"] = timestamp
    eq_v["ultima_act"] = timestamp

    eq_l["apostado"] += 1
    eq_v["apostado"] += 1
    
    acerto_base = (base == resultado_real)
    
    if base == "1":
        if acerto_base:
            eq_l["aciertos"] += 1
            eq_v["desaciertos"] += 1
        else:
            eq_l["desaciertos"] += 1
            if resultado_real == "2": eq_v["aciertos"] += 1
    elif base == "2":
        if acerto_base:
            eq_v["aciertos"] += 1
            eq_l["desaciertos"] += 1
        else:
            eq_v["desaciertos"] += 1
            if resultado_real == "1": eq_l["aciertos"] += 1
            
    guardar_datos(datos)

if 'num_eventos_simple' not in st.session_state: 
    st.session_state.num_eventos_simple = 1

with st.sidebar:
    st.title("🏆 Betting Pro v10")
    menu = st.radio("Navegación:", ["🏠 Inicio", "🎯 Jugada Simple", "📊 Estadísticas"])
    
# --- JUGADA SIMPLE ---
if menu == "🎯 Jugada Simple":
    st.title("🎯 Nueva Jugada")
    
    col_btn1, col_btn2 = st.columns([1, 5])
    with col_btn1:
        if st.button("➕"):
            st.session_state.num_eventos_simple += 1
            st.rerun()
    with col_btn2:
        if st.button("➖") and st.session_state.num_eventos_simple > 1:
            st.session_state.num_eventos_simple -= 1
            st.rerun()

    eventos = []
    for i in range(st.session_state.num_eventos_simple):
        with st.expander(f"Evento #{i+1} - Configuración", expanded=True):
            # --- NUEVA SECCIÓN DE FECHA Y HORA ---
            c_fecha, c_hora, c_dep, c_liga = st.columns([2, 2, 2, 3])
            fecha_ev = c_fecha.date_input("Fecha", value=datetime.now(), key=f"date_{i}")
            hora_ev = c_hora.time_input("Hora", value=datetime.now().time(), key=f"time_{i}")
            dep = c_dep.selectbox("Deporte", ["⚽ Fútbol", "🎾 Tenis", "🏀 Basket"], key=f"d_{i}")
            liga = c_liga.text_input("Liga", key=f"lg_{i}", placeholder="Ej: La Liga")

            st.markdown("---")
            fl, fr1, fr2, fv = st.columns([2, 1, 1, 2])
            loc = fl.text_input("Local", key=f"l_{i}")
            r1 = fr1.number_input("Marcador L", 0, key=f"r1_{i}")
            r2 = fr2.number_input("Marcador V", 0, key=f"r2_{i}")
            vis = fv.text_input("Visitante", key=f"v_{i}")
            
            q1, qx, q2, qsel = st.columns(4)
            c1 = q1.number_input("Cuota 1", 1.0, value=2.0, key=f"c1_{i}")
            cx = qx.number_input("Cuota X", 1.0, value=3.0, key=f"cx_{i}") if "Fútbol" in dep else 1.0
            c2 = q2.number_input("Cuota 2", 1.0, value=2.0, key=f"c2_{i}")
            
            opc = ["1", "X", "2"] if "Fútbol" in dep else ["1", "2"]
            base = qsel.selectbox("Tu Apuesta", opc, key=f"b_{i}")
            
            cuota_elec = c1 if base=="1" else (cx if base=="X" else c2)
            eventos.append({
                "l": loc, "v": vis, "cuo": cuota_elec, "base": base, 
                "dep": dep, "liga": liga, "r1": r1, "r2": r2,
                "fecha": str(fecha_ev), "hora": str(hora_ev)
            })

    st.markdown("---")
    inv = st.number_input("Inversión ($)", 1.0, value=10.0)
    cuota_total = 1.0
    for e in eventos: cuota_total *= e["cuo"]
    
    st.metric("Ganancia Bruta", f"${(inv * cuota_total):.2f}", f"Cuota Total: {cuota_total:.2f}")

    if st.button("🔥 FINALIZAR Y REGISTRAR", use_container_width=True):
        for e in eventos:
            if e['l'] and e['v']:
                res_real = "1" if e['r1'] > e['r2'] else ("2" if e['r1'] < e['r2'] else "X")
                registrar_stats_json(e['l'], e['v'], e['base'], res_real, e['dep'], e['liga'], e['fecha'], e['hora'])
        st.success(f"Registrado con éxito el {datetime.now().strftime('%d/%m/%Y %H:%M')}")

elif menu == "📊 Estadísticas":
    st.title("📊 Análisis de Rendimiento")
    datos = cargar_datos()
    if datos["stats"]:
        df = pd.DataFrame(datos["stats"])
        df['% Acierto'] = (df['aciertos'] / df['apostado'] * 100).round(2)
        # Reordenar columnas para que la fecha se vea al final
        columnas = ['equipo', 'deporte', 'liga', 'apostado', 'aciertos', 'desaciertos', '% Acierto', 'ultima_act']
        st.dataframe(df[columnas], use_container_width=True)
    else:
        st.info("Sin estadísticas.")

elif menu == "🏠 Inicio":
    st.title("🚀 Betting Manager v10")
    st.write("Registra tus apuestas con fecha, hora y estadísticas automáticas.")
