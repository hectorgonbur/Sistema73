import streamlit as st
import pandas as pd
import json
from datetime import datetime, time
import os
import itertools
from collections import Counter

# Configuración de la página
st.set_page_config(
    page_title="App de Apuestas Profesional",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: white;
        margin: 0;
        text-align: center;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .evento-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .evento-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .contador-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .contador {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .contador-verde {
        color: #4ade80;
    }
    .contador-normal {
        color: white;
    }
    .bolita {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: inline-block;
        margin: 0 auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: transform 0.3s;
    }
    .bolita:hover {
        transform: scale(1.1);
    }
    .bolita-gris {
        background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
    }
    .bolita-verde {
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
    }
    .bolita-roja {
        background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
    }
    .base-btn {
        padding: 10px 20px;
        margin: 0 5px;
        border: none;
        border-radius: 10px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .base-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .base-btn-selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .ganancia-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .ganancia-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .ganancia-valor {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .columna-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        border-left: 5px solid #667eea;
        transition: transform 0.3s;
    }
    .columna-card:hover {
        transform: translateX(5px);
    }
    .filtro-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #764ba2;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .menu-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #667eea;
        padding: 10px;
        border-bottom: 2px solid #667eea;
        margin-bottom: 10px;
    }
    .success-message {
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .info-message {
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Inicialización de variables de sesión
def init_session_state():
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = 'Apuesta Simple'
    if 'eventos_count' not in st.session_state:
        st.session_state.eventos_count = 1
    if 'deportes' not in st.session_state:
        st.session_state.deportes = ['Fútbol', 'Baloncesto', 'Tenis', 'Béisbol', 'Fútbol Americano', 'Hockey', 'Voleibol', 'Handball']
    if 'ligas_por_deporte' not in st.session_state:
        st.session_state.ligas_por_deporte = {
            'Fútbol': ['La Liga', 'Premier League', 'Serie A', 'Bundesliga', 'Ligue 1', 'Eredivisie', 'Primeira Liga'],
            'Baloncesto': ['NBA', 'EuroLeague', 'ACB', 'Liga Endesa', 'Euroliga', 'NCAA'],
            'Tenis': ['ATP', 'WTA', 'Grand Slam', 'Masters 1000', 'ATP 500'],
            'Béisbol': ['MLB', 'Liga Mexicana', 'Serie Nacional', 'NPB', 'KBO'],
            'Fútbol Americano': ['NFL', 'NCAA', 'CFL', 'XFL'],
            'Hockey': ['NHL', 'KHL', 'Liiga', 'SHL'],
            'Voleibol': ['Serie A1', 'Superliga', 'Bundesliga', 'Liga Francesa'],
            'Handball': ['Liga Asobal', 'Bundesliga', 'Liga Francesa', 'Liga Danesa']
        }
    if 'apuestas' not in st.session_state:
        if os.path.exists('apuestas.json'):
            with open('apuestas.json', 'r', encoding='utf-8') as f:
                st.session_state.apuestas = json.load(f)
        else:
            st.session_state.apuestas = []
    if 'jugadas_sistema' not in st.session_state:
        st.session_state.jugadas_sistema = []
    if 'filtros_sistema' not in st.session_state:
        st.session_state.filtros_sistema = {
            'base_min': 0,
            'base_max': 0,
            'signos_1': (0, 0),
            'signos_x': (0, 0),
            'signos_2': (0, 0),
            'consecutivos_1': (0, 0),
            'consecutivos_x': (0, 0),
            'consecutivos_2': (0, 0),
            'interrupciones': (0, 0)
        }
    if 'columnas_generadas' not in st.session_state:
        st.session_state.columnas_generadas = []
    if 'columnas_generadas_multiple' not in st.session_state:
        st.session_state.columnas_generadas_multiple = []
    if 'saldo' not in st.session_state:
        st.session_state.saldo = 1000.0
    if 'aciertos_min' not in st.session_state:
        st.session_state.aciertos_min = 0
    if 'aciertos_max' not in st.session_state:
        st.session_state.aciertos_max = 0

init_session_state()

# Función para guardar apuestas
def guardar_apuestas():
    with open('apuestas.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.apuestas, f, ensure_ascii=False, indent=2)

# Función para generar combinaciones de columnas
def generar_columnas(jugadas, filtros):
    if not jugadas:
        return []
    
    # Generar todas las combinaciones posibles
    signos_posibles = []
    for jugada in jugadas:
        signos = []
        if '1' in jugada['jugada']:
            signos.append('1')
        if 'x' in jugada['jugada']:
            signos.append('x')
        if '2' in jugada['jugada']:
            signos.append('2')
        signos_posibles.append(signos)
    
    todas_columnas = list(itertools.product(*signos_posibles))
    
    # Aplicar filtros
    columnas_filtradas = []
    for columna in todas_columnas:
        cumple_filtros = True
        
        # Filtro BASE
        if filtros['base_min'] > 0 or filtros['base_max'] > 0:
            aciertos_base = sum(1 for i, signo in enumerate(columna) 
                              if i < len(jugadas) and signo == jugadas[i].get('base', ''))
            if aciertos_base < filtros['base_min'] or (filtros['base_max'] > 0 and aciertos_base > filtros['base_max']):
                cumple_filtros = False
        
        # Filtro SIGNOS
        if cumple_filtros:
            conteo = Counter(columna)
            if len(columna) > 0:
                if filtros['signos_1'][1] > 0:
                    if conteo['1'] < filtros['signos_1'][0] or conteo['1'] > filtros['signos_1'][1]:
                        cumple_filtros = False
                if cumple_filtros and filtros['signos_x'][1] > 0:
                    if conteo['x'] < filtros['signos_x'][0] or conteo['x'] > filtros['signos_x'][1]:
                        cumple_filtros = False
                if cumple_filtros and filtros['signos_2'][1] > 0:
                    if conteo['2'] < filtros['signos_2'][0] or conteo['2'] > filtros['signos_2'][1]:
                        cumple_filtros = False
        
        # Filtro CONSECUTIVOS
        if cumple_filtros:
            for signo in ['1', 'x', '2']:
                max_consecutivos = 0
                consecutivos_actual = 0
                for s in columna:
                    if s == signo:
                        consecutivos_actual += 1
                        max_consecutivos = max(max_consecutivos, consecutivos_actual)
                    else:
                        consecutivos_actual = 0
                
                rango = filtros.get(f'consecutivos_{signo}', (0, 0))
                if rango[1] > 0:
                    if max_consecutivos < rango[0] or max_consecutivos > rango[1]:
                        cumple_filtros = False
                        break
        
        # Filtro INTERRUPCIONES
        if cumple_filtros and filtros['interrupciones'][1] > 0:
            interrupciones = 0
            for i in range(1, len(columna)):
                if columna[i] != columna[i-1]:
                    interrupciones += 1
            
            if interrupciones < filtros['interrupciones'][0] or interrupciones > filtros['interrupciones'][1]:
                cumple_filtros = False
        
        if cumple_filtros:
            columnas_filtradas.append(columna)
    
    return columnas_filtradas

# Menú lateral
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='color: #667eea;'>🎲 MENÚ</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # APUESTAS
    with st.expander("🎯 APUESTAS", expanded=True):
        if st.button("📝 Apuesta Simple", use_container_width=True):
            st.session_state.pagina_actual = "Apuesta Simple"
        if st.button("🔄 Apuesta Múltiple", use_container_width=True):
            st.session_state.pagina_actual = "Apuesta Múltiple"
    
    # SISTEMAS
    with st.expander("⚙️ SISTEMAS", expanded=False):
        if st.button("🎮 Jugadas", use_container_width=True):
            st.session_state.pagina_actual = "Jugadas"
        if st.button("🔍 Filtros", use_container_width=True):
            st.session_state.pagina_actual = "Filtros"
        if st.button("📊 Columnas", use_container_width=True):
            st.session_state.pagina_actual = "Columnas"
    
    # ESTADÍSTICAS
    with st.expander("📈 ESTADÍSTICAS", expanded=False):
        if st.button("⚽ Est. Equipos", use_container_width=True):
            st.session_state.pagina_actual = "Est. Equipos"
        if st.button("📊 Est. Jugadas", use_container_width=True):
            st.session_state.pagina_actual = "Est. Jugadas"
    
    # GANANCIAS
    with st.expander("💰 GANANCIAS", expanded=False):
        if st.button("👛 Billetera", use_container_width=True):
            st.session_state.pagina_actual = "Billetera"
    
    # ARCHIVOS
    with st.expander("📁 ARCHIVOS", expanded=False):
        if st.button("💾 Guardar", use_container_width=True):
            st.session_state.pagina_actual = "Guardar"
        if st.button("📤 Exportar", use_container_width=True):
            st.session_state.pagina_actual = "Exportar"

# Cabecera principal
st.markdown(f"""
<div class="main-header">
    <h1>🎲 {st.session_state.pagina_actual}</h1>
</div>
""", unsafe_allow_html=True)

# Página de Apuesta Simple
if st.session_state.pagina_actual == "Apuesta Simple":
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.markdown('<div class="contador-card">', unsafe_allow_html=True)
        st.markdown("### 📅 Eventos")
        eventos_col1, eventos_col2, eventos_col3 = st.columns([1, 2, 1])
        with eventos_col1:
            if st.button("➖", key="minus_eventos_simple"):
                if st.session_state.eventos_count > 1:
                    st.session_state.eventos_count -= 1
                    st.rerun()
        with eventos_col2:
            st.markdown(f"<h2 style='text-align: center;'>{st.session_state.eventos_count}</h2>", unsafe_allow_html=True)
        with eventos_col3:
            if st.button("➕", key="plus_eventos_simple"):
                if st.session_state.eventos_count < 30:
                    st.session_state.eventos_count += 1
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="contador-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Progreso")
        eventos_ganados = 0
        for i in range(st.session_state.eventos_count):
            if f'bolita_simple_{i}' in st.session_state and st.session_state[f'bolita_simple_{i}'] == 'verde':
                eventos_ganados += 1
        
        color_class = "contador-verde" if eventos_ganados == st.session_state.eventos_count else "contador-normal"
        st.markdown(f'<div class="contador {color_class}">{eventos_ganados}/{st.session_state.eventos_count}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="contador-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Billetera")
        st.markdown(f'<div class="contador">€ {st.session_state.saldo:.2f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🎯 Eventos")
    cuota_total = 1
    
    for i in range(st.session_state.eventos_count):
        with st.container():
            st.markdown(f'<div class="evento-card">', unsafe_allow_html=True)
            st.markdown(f"**Evento {i+1}**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                deporte = st.selectbox(
                    "Deporte",
                    options=st.session_state.deportes + ["Otro..."],
                    key=f'deporte_simple_{i}'
                )
                if deporte == "Otro...":
                    nuevo_deporte = st.text_input("Nuevo deporte", key=f'nuevo_deporte_simple_{i}')
                    if nuevo_deporte and nuevo_deporte not in st.session_state.deportes:
                        st.session_state.deportes.append(nuevo_deporte)
                        st.session_state.ligas_por_deporte[nuevo_deporte] = []
                        st.rerun()
            
            with col2:
                ligas_disponibles = st.session_state.ligas_por_deporte.get(
                    deporte if deporte != "Otro..." else st.session_state.deportes[-1],
                    []
                )
                liga = st.selectbox(
                    "Liga",
                    options=ligas_disponibles + ["Otra..."],
                    key=f'liga_simple_{i}'
                )
                if liga == "Otra...":
                    nueva_liga = st.text_input("Nueva liga", key=f'nueva_liga_simple_{i}')
                    if nueva_liga and nueva_liga not in ligas_disponibles:
                        st.session_state.ligas_por_deporte[deporte].append(nueva_liga)
                        st.rerun()
            
            with col3:
                fecha = st.date_input("Fecha", key=f'fecha_simple_{i}')
            
            with col4:
                hora = st.time_input("Hora", value=time(12, 0), key=f'hora_simple_{i}')
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                equipo_local = st.text_input("Equipo Local", key=f'local_simple_{i}')
            
            with col2:
                resultado_local = st.number_input("Resultado Local", min_value=0, step=1, key=f'res_local_simple_{i}')
            
            with col3:
                resultado_visitante = st.number_input("Resultado Visitante", min_value=0, step=1, key=f'res_vis_simple_{i}')
            
            with col4:
                equipo_visitante = st.text_input("Equipo Visitante", key=f'vis_simple_{i}')
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                cuota_local = st.number_input("Cuota Local", min_value=1.0, value=1.0, step=0.1, key=f'cuota_local_simple_{i}')
            
            with col2:
                cuota_empate = st.number_input("Cuota Empate", min_value=1.0, value=1.0, step=0.1, key=f'cuota_empate_simple_{i}')
            
            with col3:
                cuota_visitante = st.number_input("Cuota Visitante", min_value=1.0, value=1.0, step=0.1, key=f'cuota_vis_simple_{i}')
            
            with col4:
                st.markdown("**Base**")
                base_col1, base_col2, base_col3 = st.columns(3)
                
                if f'base_simple_{i}' not in st.session_state:
                    st.session_state[f'base_simple_{i}'] = '1'
                
                with base_col1:
                    if st.button("1", key=f'base1_simple_{i}'):
                        st.session_state[f'base_simple_{i}'] = '1'
                        st.rerun()
                with base_col2:
                    if st.button("X", key=f'basex_simple_{i}'):
                        st.session_state[f'base_simple_{i}'] = 'x'
                        st.rerun()
                with base_col3:
                    if st.button("2", key=f'base2_simple_{i}'):
                        st.session_state[f'base_simple_{i}'] = '2'
                        st.rerun()
            
            with col5:
                st.markdown("**Estado**")
                if resultado_local == 0 and resultado_visitante == 0:
                    color_bolita = "gris"
                    st.session_state[f'bolita_simple_{i}'] = "gris"
                else:
                    base = st.session_state.get(f'base_simple_{i}', '1')
                    if (base == '1' and resultado_local > resultado_visitante) or \
                       (base == 'x' and resultado_local == resultado_visitante) or \
                       (base == '2' and resultado_local < resultado_visitante):
                        color_bolita = "verde"
                        st.session_state[f'bolita_simple_{i}'] = "verde"
                    else:
                        color_bolita = "roja"
                        st.session_state[f'bolita_simple_{i}'] = "roja"
                
                st.markdown(f'<div style="display: flex; justify-content: center;"><div class="bolita bolita-{color_bolita}"></div></div>', unsafe_allow_html=True)
            
            base = st.session_state.get(f'base_simple_{i}', '1')
            if base == '1':
                cuota_total *= cuota_local
            elif base == 'x':
                cuota_total *= cuota_empate
            else:
                cuota_total *= cuota_visitante
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 💰 Resumen de Apuesta")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monto_jugado = st.number_input("Monto Jugado (€)", min_value=0.0, value=0.0, step=10.0, key="monto_simple")
    
    with col2:
        ganancia_bruta = monto_jugado * cuota_total
        st.markdown(f"""
        <div class="ganancia-card">
            <h4>Ganancia Bruta</h4>
            <div class="ganancia-valor">€ {ganancia_bruta:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ganancia_neta = ganancia_bruta - monto_jugado
        st.markdown(f"""
        <div class="ganancia-card">
            <h4>Ganancia Neta</h4>
            <div class="ganancia-valor">€ {ganancia_neta:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("📝 REGISTRAR APUESTA SIMPLE", use_container_width=True):
        apuesta = {
            "fecha": datetime.now().isoformat(),
            "tipo": "Apuesta Simple",
            "eventos_totales": st.session_state.eventos_count,
            "eventos_ganados": eventos_ganados,
            "monto_jugado": monto_jugado,
            "ganancia_bruta": ganancia_bruta,
            "ganancia_neta": ganancia_neta,
            "detalles": []
        }
        
        for i in range(st.session_state.eventos_count):
            detalle = {
                "deporte": st.session_state.get(f'deporte_simple_{i}', ''),
                "liga": st.session_state.get(f'liga_simple_{i}', ''),
                "fecha": str(st.session_state.get(f'fecha_simple_{i}', '')),
                "hora": str(st.session_state.get(f'hora_simple_{i}', '')),
                "equipo_local": st.session_state.get(f'local_simple_{i}', ''),
                "equipo_visitante": st.session_state.get(f'vis_simple_{i}', ''),
                "resultado_local": st.session_state.get(f'res_local_simple_{i}', 0),
                "resultado_visitante": st.session_state.get(f'res_vis_simple_{i}', 0),
                "base": st.session_state.get(f'base_simple_{i}', '1'),
                "estado": st.session_state.get(f'bolita_simple_{i}', 'gris')
            }
            apuesta["detalles"].append(detalle)
        
        st.session_state.apuestas.append(apuesta)
        st.session_state.saldo -= monto_jugado
        st.session_state.saldo += ganancia_bruta
        guardar_apuestas()
        
        st.markdown('<div class="success-message">✅ Apuesta registrada correctamente!</div>', unsafe_allow_html=True)

# Página de Apuesta Múltiple
elif st.session_state.pagina_actual == "Apuesta Múltiple":
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.markdown('<div class="contador-card">', unsafe_allow_html=True)
        st.markdown("### 📅 Eventos")
        eventos_col1, eventos_col2, eventos_col3 = st.columns([1, 2, 1])
        with eventos_col1:
            if st.button("➖", key="minus_eventos_multiple"):
                if st.session_state.eventos_count > 1:
                    st.session_state.eventos_count -= 1
                    st.rerun()
        with eventos_col2:
            st.markdown(f"<h2 style='text-align: center;'>{st.session_state.eventos_count}</h2>", unsafe_allow_html=True)
        with eventos_col3:
            if st.button("➕", key="plus_eventos_multiple"):
                if st.session_state.eventos_count < 30:
                    st.session_state.eventos_count += 1
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="contador-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Máx Aciertos")
        
        # Calcular máximos aciertos posibles de las columnas
        if 'columnas_generadas_multiple' in st.session_state and st.session_state.columnas_generadas_multiple:
            max_aciertos = 0
            for columna in st.session_state.columnas_generadas_multiple:
                aciertos = 0
                for i, signo in enumerate(columna):
                    if i < st.session_state.eventos_count:
                        res_local = st.session_state.get(f'res_local_multiple_{i}', 0)
                        res_vis = st.session_state.get(f'res_vis_multiple_{i}', 0)
                        base = st.session_state.get(f'base_multiple_{i}', '1')
                        
                        if (base == '1' and res_local > res_vis) or \
                           (base == 'x' and res_local == res_vis) or \
                           (base == '2' and res_local < res_vis):
                            if signo == base:
                                aciertos += 1
                max_aciertos = max(max_aciertos, aciertos)
            
            color_class = "contador-verde" if max_aciertos >= st.session_state.get('aciertos_min', 0) else "contador-normal"
            st.markdown(f'<div class="contador {color_class}">{max_aciertos}/{st.session_state.eventos_count}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="contador contador-normal">0/{st.session_state.eventos_count}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="contador-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Aciertos Base")
        
        col_min, col_medio, col_max = st.columns([2, 1, 2])
        with col_min:
            if st.button("➖", key="minus_aciertos_min"):
                if st.session_state.aciertos_min > 0:
                    st.session_state.aciertos_min -= 1
                    st.rerun()
        with col_medio:
            aciertos_min = st.number_input("Mín", min_value=0, max_value=st.session_state.eventos_count, 
                                          value=st.session_state.aciertos_min, key="aciertos_min_input")
            st.session_state.aciertos_min = aciertos_min
        with col_max:
            if st.button("➕", key="plus_aciertos_min"):
                if st.session_state.aciertos_min < st.session_state.eventos_count:
                    st.session_state.aciertos_min += 1
                    st.rerun()
        
        st.markdown("<h3 style='text-align: center;'>A</h3>", unsafe_allow_html=True)
        
        col_min2, col_medio2, col_max2 = st.columns([2, 1, 2])
        with col_min2:
            if st.button("➖", key="minus_aciertos_max"):
                if st.session_state.aciertos_max > 0:
                    st.session_state.aciertos_max -= 1
                    st.rerun()
        with col_medio2:
            aciertos_max = st.number_input("Máx", min_value=0, max_value=st.session_state.eventos_count,
                                          value=st.session_state.aciertos_max, key="aciertos_max_input")
            st.session_state.aciertos_max = aciertos_max
        with col_max2:
            if st.button("➕", key="plus_aciertos_max"):
                if st.session_state.aciertos_max < st.session_state.eventos_count:
                    st.session_state.aciertos_max += 1
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🎯 Eventos")
    
    # Recopilar jugadas para generar columnas
    jugadas_multiple = []
    
    for i in range(st.session_state.eventos_count):
        with st.container():
            st.markdown(f'<div class="evento-card">', unsafe_allow_html=True)
            st.markdown(f"**Evento {i+1}**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                deporte = st.selectbox(
                    "Deporte",
                    options=st.session_state.deportes + ["Otro..."],
                    key=f'deporte_multiple_{i}'
                )
                if deporte == "Otro...":
                    nuevo_deporte = st.text_input("Nuevo deporte", key=f'nuevo_deporte_multiple_{i}')
                    if nuevo_deporte and nuevo_deporte not in st.session_state.deportes:
                        st.session_state.deportes.append(nuevo_deporte)
                        st.session_state.ligas_por_deporte[nuevo_deporte] = []
                        st.rerun()
            
            with col2:
                ligas_disponibles = st.session_state.ligas_por_deporte.get(
                    deporte if deporte != "Otro..." else st.session_state.deportes[-1],
                    []
                )
                liga = st.selectbox(
                    "Liga",
                    options=ligas_disponibles + ["Otra..."],
                    key=f'liga_multiple_{i}'
                )
                if liga == "Otra...":
                    nueva_liga = st.text_input("Nueva liga", key=f'nueva_liga_multiple_{i}')
                    if nueva_liga and nueva_liga not in ligas_disponibles:
                        st.session_state.ligas_por_deporte[deporte].append(nueva_liga)
                        st.rerun()
            
            with col3:
                fecha = st.date_input("Fecha", key=f'fecha_multiple_{i}')
            
            with col4:
                hora = st.time_input("Hora", value=time(12, 0), key=f'hora_multiple_{i}')
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                equipo_local = st.text_input("Equipo Local", key=f'local_multiple_{i}')
            
            with col2:
                resultado_local = st.number_input("Resultado Local", min_value=0, step=1, key=f'res_local_multiple_{i}')
            
            with col3:
                resultado_visitante = st.number_input("Resultado Visitante", min_value=0, step=1, key=f'res_vis_multiple_{i}')
            
            with col4:
                equipo_visitante = st.text_input("Equipo Visitante", key=f'vis_multiple_{i}')
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                cuota_local = st.number_input("Cuota Local", min_value=1.0, value=1.0, step=0.1, key=f'cuota_local_multiple_{i}')
            
            with col2:
                cuota_empate = st.number_input("Cuota Empate", min_value=1.0, value=1.0, step=0.1, key=f'cuota_empate_multiple_{i}')
            
            with col3:
                cuota_visitante = st.number_input("Cuota Visitante", min_value=1.0, value=1.0, step=0.1, key=f'cuota_vis_multiple_{i}')
            
            with col4:
                st.markdown("**Jugada**")
                opciones_jugada = []
                col_j1, col_j2, col_j3 = st.columns(3)
                with col_j1:
                    if st.checkbox("1", key=f'jugada_1_{i}'):
                        opciones_jugada.append('1')
                with col_j2:
                    if st.checkbox("X", key=f'jugada_x_{i}'):
                        opciones_jugada.append('x')
                with col_j3:
                    if st.checkbox("2", key=f'jugada_2_{i}'):
                        opciones_jugada.append('2')
                
                jugada_str = ''.join(opciones_jugada) if opciones_jugada else '1'
                st.session_state[f'jugada_multiple_{i}'] = jugada_str
            
            with col5:
                st.markdown("**Base**")
                base_col1, base_col2, base_col3 = st.columns(3)
                
                if f'base_multiple_{i}' not in st.session_state:
                    st.session_state[f'base_multiple_{i}'] = '1'
                
                with base_col1:
                    if st.button("1", key=f'base1_multiple_{i}'):
                        st.session_state[f'base_multiple_{i}'] = '1'
                        st.rerun()
                with base_col2:
                    if st.button("X", key=f'basex_multiple_{i}'):
                        st.session_state[f'base_multiple_{i}'] = 'x'
                        st.rerun()
                with base_col3:
                    if st.button("2", key=f'base2_multiple_{i}'):
                        st.session_state[f'base_multiple_{i}'] = '2'
                        st.rerun()
            
            # Guardar datos para generación de columnas
            jugadas_multiple.append({
                'jugada': st.session_state.get(f'jugada_multiple_{i}', '1'),
                'base': st.session_state.get(f'base_multiple_{i}', '1'),
                'cuota_local': cuota_local,
                'cuota_empate': cuota_empate,
                'cuota_visitante': cuota_visitante
            })
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 💰 Monto Total")
    monto_total = st.number_input("Monto Total (€)", min_value=0.0, value=0.0, step=10.0, key="monto_multiple")
    
    # Generar columnas
    if st.button("🔄 GENERAR COLUMNAS", use_container_width=True):
        # Crear filtros para la generación
        filtros_temp = {
            'base_min': st.session_state.aciertos_min,
            'base_max': st.session_state.aciertos_max,
            'signos_1': (0, 0),
            'signos_x': (0, 0),
            'signos_2': (0, 0),
            'consecutivos_1': (0, 0),
            'consecutivos_x': (0, 0),
            'consecutivos_2': (0, 0),
            'interrupciones': (0, 0)
        }
        
        columnas = generar_columnas(jugadas_multiple, filtros_temp)
        st.session_state.columnas_generadas_multiple = columnas
        
        st.markdown(f'<div class="info-message">📊 Se generaron {len(columnas)} columnas</div>', unsafe_allow_html=True)
    
    # Mostrar columnas generadas
    if 'columnas_generadas_multiple' in st.session_state and st.session_state.columnas_generadas_multiple:
        st.markdown("### 📊 COLUMNAS GENERADAS")
        
        monto_por_columna = monto_total / len(st.session_state.columnas_generadas_multiple) if len(st.session_state.columnas_generadas_multiple) > 0 else 0
        
        for idx, columna in enumerate(st.session_state.columnas_generadas_multiple):
            with st.container():
                st.markdown(f'<div class="columna-card">', unsafe_allow_html=True)
                
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**Columna {idx+1}:** {' - '.join(columna)}")
                
                with col2:
                    # Calcular cuota total
                    cuota_columna = 1
                    for i, signo in enumerate(columna):
                        if i < len(jugadas_multiple):
                            if signo == '1':
                                cuota_columna *= jugadas_multiple[i]['cuota_local']
                            elif signo == 'x':
                                cuota_columna *= jugadas_multiple[i]['cuota_empate']
                            else:
                                cuota_columna *= jugadas_multiple[i]['cuota_visitante']
                    
                    ganancia_bruta = monto_por_columna * cuota_columna
                    st.markdown(f"💰 **Bruta:** € {ganancia_bruta:.2f}")
                
                with col3:
                    ganancia_neta = ganancia_bruta - monto_por_columna
                    st.markdown(f"💵 **Neta:** € {ganancia_neta:.2f}")
                
                with col4:
                    st.markdown(f"📊 **Cuota:** {cuota_columna:.2f}")
                
                with col5:
                    # Determinar si la columna cumple con los aciertos base
                    if all(st.session_state.get(f'res_local_multiple_{i}', 0) == 0 and 
                          st.session_state.get(f'res_vis_multiple_{i}', 0) == 0 for i in range(len(columna))):
                        color_bolita = "gris"
                    else:
                        aciertos = 0
                        for i, signo in enumerate(columna):
                            if i < st.session_state.eventos_count:
                                res_local = st.session_state.get(f'res_local_multiple_{i}', 0)
                                res_vis = st.session_state.get(f'res_vis_multiple_{i}', 0)
                                base = st.session_state.get(f'base_multiple_{i}', '1')
                                
                                if (base == '1' and res_local > res_vis) or \
                                   (base == 'x' and res_local == res_vis) or \
                                   (base == '2' and res_local < res_vis):
                                    if signo == base:
                                        aciertos += 1
                        
                        if aciertos >= st.session_state.aciertos_min and \
                           aciertos <= st.session_state.aciertos_max:
                            color_bolita = "verde"
                        else:
                            color_bolita = "roja"
                    
                    st.markdown(f'<div class="bolita bolita-{color_bolita}"></div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("📝 REGISTRAR APUESTA MÚLTIPLE", use_container_width=True):
        apuesta = {
            "fecha": datetime.now().isoformat(),
            "tipo": "Apuesta Múltiple",
            "eventos_totales": st.session_state.eventos_count,
            "aciertos_min": st.session_state.aciertos_min,
            "aciertos_max": st.session_state.aciertos_max,
            "monto_total": monto_total,
            "num_columnas": len(st.session_state.columnas_generadas_multiple),
            "monto_por_columna": monto_por_columna if 'columnas_generadas_multiple' in st.session_state else 0,
            "detalles": []
        }
        
        for i in range(st.session_state.eventos_count):
            detalle = {
                "deporte": st.session_state.get(f'deporte_multiple_{i}', ''),
                "liga": st.session_state.get(f'liga_multiple_{i}', ''),
                "fecha": str(st.session_state.get(f'fecha_multiple_{i}', '')),
                "hora": str(st.session_state.get(f'hora_multiple_{i}', '')),
                "equipo_local": st.session_state.get(f'local_multiple_{i}', ''),
                "equipo_visitante": st.session_state.get(f'vis_multiple_{i}', ''),
                "resultado_local": st.session_state.get(f'res_local_multiple_{i}', 0),
                "resultado_visitante": st.session_state.get(f'res_vis_multiple_{i}', 0),
                "jugada": st.session_state.get(f'jugada_multiple_{i}', '1'),
                "base": st.session_state.get(f'base_multiple_{i}', '1')
            }
            apuesta["detalles"].append(detalle)
        
        st.session_state.apuestas.append(apuesta)
        st.session_state.saldo -= monto_total
        guardar_apuestas()
        
        st.markdown('<div class="success-message">✅ Apuesta múltiple registrada correctamente!</div>', unsafe_allow_html=True)

# Página de Jugadas (Sistema)
elif st.session_state.pagina_actual == "Jugadas":
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="contador-card">', unsafe_allow_html=True)
        st.markdown("### 📅 Eventos")
        eventos_col1, eventos_col2, eventos_col3 = st.columns([1, 2, 1])
        with eventos_col1:
            if st.button("➖", key="minus_eventos_jugadas"):
                if st.session_state.eventos_count > 1:
                    st.session_state.eventos_count -= 1
                    st.rerun()
        with eventos_col2:
            st.markdown(f"<h2 style='text-align: center;'>{st.session_state.eventos_count}</h2>", unsafe_allow_html=True)
        with eventos_col3:
            if st.button("➕", key="plus_eventos_jugadas"):
                if st.session_state.eventos_count < 30:
                    st.session_state.eventos_count += 1
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="contador-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Progreso")
        if st.session_state.columnas_generadas:
            # Calcular máximo de aciertos entre columnas
            max_aciertos = 0
            for columna in st.session_state.columnas_generadas:
                aciertos = 0
                for i, signo in enumerate(columna):
                    if i < st.session_state.eventos_count:
                        res_local = st.session_state.get(f'res_local_jugada_{i}', 0)
                        res_vis = st.session_state.get(f'res_vis_jugada_{i}', 0)
                        
                        if (signo == '1' and res_local > res_vis) or \
                           (signo == 'x' and res_local == res_vis) or \
                           (signo == '2' and res_local < res_vis):
                            aciertos += 1
                max_aciertos = max(max_aciertos, aciertos)
            
            color_class = "contador-verde" if max_aciertos == st.session_state.eventos_count else "contador-normal"
            st.markdown(f'<div class="contador {color_class}">{max_aciertos}/{st.session_state.eventos_count}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="contador contador-normal">0/{st.session_state.eventos_count}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🎯 Eventos - Sistema de Jugadas")
    st.markdown('<div class="info-message">📝 Complete los datos de cada evento para el sistema</div>', unsafe_allow_html=True)
    
    jugadas_sistema = []
    
    for i in range(st.session_state.eventos_count):
        with st.container():
            st.markdown(f'<div class="evento-card">', unsafe_allow_html=True)
            st.markdown(f"**Evento {i+1}**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                deporte = st.selectbox(
                    "Deporte",
                    options=st.session_state.deportes + ["Otro..."],
                    key=f'deporte_jugada_{i}'
                )
                if deporte == "Otro...":
                    nuevo_deporte = st.text_input("Nuevo deporte", key=f'nuevo_deporte_jugada_{i}')
                    if nuevo_deporte and nuevo_deporte not in st.session_state.deportes:
                        st.session_state.deportes.append(nuevo_deporte)
                        st.session_state.ligas_por_deporte[nuevo_deporte] = []
                        st.rerun()
            
            with col2:
                ligas_disponibles = st.session_state.ligas_por_deporte.get(
                    deporte if deporte != "Otro..." else st.session_state.deportes[-1],
                    []
                )
                liga = st.selectbox(
                    "Liga",
                    options=ligas_disponibles + ["Otra..."],
                    key=f'liga_jugada_{i}'
                )
                if liga == "Otra...":
                    nueva_liga = st.text_input("Nueva liga", key=f'nueva_liga_jugada_{i}')
                    if nueva_liga and nueva_liga not in ligas_disponibles:
                        st.session_state.ligas_por_deporte[deporte].append(nueva_liga)
                        st.rerun()
            
            with col3:
                fecha = st.date_input("Fecha", key=f'fecha_jugada_{i}')
            
            with col4:
                hora = st.time_input("Hora", value=time(12, 0), key=f'hora_jugada_{i}')
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                equipo_local = st.text_input("Equipo Local", key=f'local_jugada_{i}')
            
            with col2:
                resultado_local = st.number_input("Resultado Local", min_value=0, step=1, key=f'res_local_jugada_{i}')
            
            with col3:
                resultado_visitante = st.number_input("Resultado Visitante", min_value=0, step=1, key=f'res_vis_jugada_{i}')
            
            with col4:
                equipo_visitante = st.text_input("Equipo Visitante", key=f'vis_jugada_{i}')
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                cuota_local = st.number_input("Cuota Local", min_value=1.0, value=1.0, step=0.1, key=f'cuota_local_jugada_{i}')
            
            with col2:
                cuota_empate = st.number_input("Cuota Empate", min_value=1.0, value=1.0, step=0.1, key=f'cuota_empate_jugada_{i}')
            
            with col3:
                cuota_visitante = st.number_input("Cuota Visitante", min_value=1.0, value=1.0, step=0.1, key=f'cuota_vis_jugada_{i}')
            
            with col4:
                st.markdown("**Jugada**")
                opciones_jugada = []
                col_j1, col_j2, col_j3 = st.columns(3)
                with col_j1:
                    if st.checkbox("1", key=f'jugada_sis_1_{i}'):
                        opciones_jugada.append('1')
                with col_j2:
                    if st.checkbox("X", key=f'jugada_sis_x_{i}'):
                        opciones_jugada.append('x')
                with col_j3:
                    if st.checkbox("2", key=f'jugada_sis_2_{i}'):
                        opciones_jugada.append('2')
                
                jugada_str = ''.join(opciones_jugada) if opciones_jugada else '1'
                st.session_state[f'jugada_sistema_{i}'] = jugada_str
            
            # Guardar datos para filtros
            jugadas_sistema.append({
                'equipo_local': equipo_local,
                'equipo_visitante': equipo_visitante,
                'jugada': st.session_state.get(f'jugada_sistema_{i}', '1'),
                'base': '1',  # Base por defecto, se modificará en filtros
                'cuota_local': cuota_local,
                'cuota_empate': cuota_empate,
                'cuota_visitante': cuota_visitante
            })
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 💰 Monto Total del Sistema")
    monto_sistema = st.number_input("Monto Total (€)", min_value=0.0, value=0.0, step=10.0, key="monto_sistema")
    
    if st.button("💾 GUARDAR JUGADAS", use_container_width=True):
        st.session_state.jugadas_sistema = jugadas_sistema
        st.markdown('<div class="success-message">✅ Jugadas guardadas correctamente</div>', unsafe_allow_html=True)

# Página de Filtros
elif st.session_state.pagina_actual == "Filtros":
    st.markdown("### 🔍 FILTROS DEL SISTEMA")
    
    if not st.session_state.jugadas_sistema:
        st.markdown('<div class="info-message">⚠️ Primero debe crear las jugadas en la página "Jugadas"</div>', unsafe_allow_html=True)
    else:
        st.markdown("#### 📋 SISTEMA JUGADO")
        
        # Mostrar lista de partidos
        for i, jugada in enumerate(st.session_state.jugadas_sistema):
            with st.container():
                st.markdown(f'<div class="evento-card">', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"**Local:** {jugada['equipo_local']}")
                
                with col2:
                    st.markdown(f"**Visitante:** {jugada['equipo_visitante']}")
                
                with col3:
                    st.markdown(f"**Signos:** {jugada['jugada']}")
                
                with col4:
                    # Selector de base para cada partido
                    base_options = list(jugada['jugada'])
                    if base_options:
                        base = st.selectbox(
                            f"Base {i+1}",
                            options=base_options,
                            key=f'base_filtro_{i}'
                        )
                        st.session_state.jugadas_sistema[i]['base'] = base
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("#### 🎯 FILTROS SISTEMA")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="filtro-card">', unsafe_allow_html=True)
            st.markdown("**📊 Filtro BASE**")
            
            base_min_col, base_max_col = st.columns(2)
            with base_min_col:
                base_min = st.number_input("Mínimo puntos BASE", min_value=0, 
                                          max_value=len(st.session_state.jugadas_sistema),
                                          value=st.session_state.filtros_sistema['base_min'],
                                          key="base_min_input")
            with base_max_col:
                base_max = st.number_input("Máximo puntos BASE", min_value=0,
                                          max_value=len(st.session_state.jugadas_sistema),
                                          value=st.session_state.filtros_sistema['base_max'] if st.session_state.filtros_sistema['base_max'] > 0 else len(st.session_state.jugadas_sistema),
                                          key="base_max_input")
            
            st.session_state.filtros_sistema['base_min'] = base_min
            st.session_state.filtros_sistema['base_max'] = base_max
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="filtro-card">', unsafe_allow_html=True)
            st.markdown("**🔢 Filtro SIGNOS**")
            
            for signo in ['1', 'x', '2']:
                st.markdown(f"**Signo {signo}**")
                col_min, col_max = st.columns(2)
                with col_min:
                    min_val = st.number_input(f"Mínimo {signo}", min_value=0,
                                             max_value=len(st.session_state.jugadas_sistema),
                                             value=st.session_state.filtros_sistema[f'signos_{signo}'][0],
                                             key=f'signos_{signo}_min')
                with col_max:
                    max_val = st.number_input(f"Máximo {signo}", min_value=0,
                                             max_value=len(st.session_state.jugadas_sistema),
                                             value=st.session_state.filtros_sistema[f'signos_{signo}'][1],
                                             key=f'signos_{signo}_max')
                st.session_state.filtros_sistema[f'signos_{signo}'] = (min_val, max_val)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="filtro-card">', unsafe_allow_html=True)
            st.markdown("**📈 Filtro CONSECUTIVOS**")
            
            for signo in ['1', 'x', '2']:
                st.markdown(f"**Consecutivos {signo}**")
                col_min, col_max = st.columns(2)
                with col_min:
                    min_val = st.number_input(f"Mínimo consec {signo}", min_value=0,
                                             max_value=len(st.session_state.jugadas_sistema),
                                             value=st.session_state.filtros_sistema[f'consecutivos_{signo}'][0],
                                             key=f'consec_{signo}_min')
                with col_max:
                    max_val = st.number_input(f"Máximo consec {signo}", min_value=0,
                                             max_value=len(st.session_state.jugadas_sistema),
                                             value=st.session_state.filtros_sistema[f'consecutivos_{signo}'][1],
                                             key=f'consec_{signo}_max')
                st.session_state.filtros_sistema[f'consecutivos_{signo}'] = (min_val, max_val)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="filtro-card">', unsafe_allow_html=True)
            st.markdown("**🔄 Filtro INTERRUPCIONES**")
            
            col_min, col_max = st.columns(2)
            with col_min:
                interrupciones_min = st.number_input("Mínimo interrupciones", min_value=0,
                                                     max_value=len(st.session_state.jugadas_sistema),
                                                     value=st.session_state.filtros_sistema['interrupciones'][0],
                                                     key="interrupciones_min")
            with col_max:
                interrupciones_max = st.number_input("Máximo interrupciones", min_value=0,
                                                     max_value=len(st.session_state.jugadas_sistema),
                                                     value=st.session_state.filtros_sistema['interrupciones'][1],
                                                     key="interrupciones_max")
            st.session_state.filtros_sistema['interrupciones'] = (interrupciones_min, interrupciones_max)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("💾 GUARDAR FILTROS", use_container_width=True):
            st.markdown('<div class="success-message">✅ Filtros guardados correctamente</div>', unsafe_allow_html=True)

# Página de Columnas
elif st.session_state.pagina_actual == "Columnas":
    st.markdown("### 📊 COLUMNAS GENERADAS")
    
    if not st.session_state.jugadas_sistema:
        st.markdown('<div class="info-message">⚠️ Primero debe crear las jugadas en la página "Jugadas"</div>', unsafe_allow_html=True)
    else:
        if st.button("🔄 GENERAR COLUMNAS", use_container_width=True):
            columnas = generar_columnas(st.session_state.jugadas_sistema, st.session_state.filtros_sistema)
            st.session_state.columnas_generadas = columnas
            st.markdown(f'<div class="info-message">📊 Se generaron {len(columnas)} columnas</div>', unsafe_allow_html=True)
        
        if st.session_state.columnas_generadas:
            monto_total = st.session_state.get('monto_sistema', 0)
            monto_por_columna = monto_total / len(st.session_state.columnas_generadas) if len(st.session_state.columnas_generadas) > 0 else 0
            
            st.markdown(f"**💰 Monto por columna: € {monto_por_columna:.2f}**")
            
            for idx, columna in enumerate(st.session_state.columnas_generadas):
                with st.container():
                    st.markdown(f'<div class="columna-card">', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**Columna {idx+1}:** {' - '.join(columna)}")
                    
                    with col2:
                        # Calcular cuota total
                        cuota_columna = 1
                        for i, signo in enumerate(columna):
                            if i < len(st.session_state.jugadas_sistema):
                                if signo == '1':
                                    cuota_columna *= st.session_state.jugadas_sistema[i]['cuota_local']
                                elif signo == 'x':
                                    cuota_columna *= st.session_state.jugadas_sistema[i]['cuota_empate']
                                else:
                                    cuota_columna *= st.session_state.jugadas_sistema[i]['cuota_visitante']
                        
                        ganancia_bruta = monto_por_columna * cuota_columna
                        st.markdown(f"💰 **Bruta:** € {ganancia_bruta:.2f}")
                    
                    with col3:
                        ganancia_neta = ganancia_bruta - monto_por_columna
                        st.markdown(f"💵 **Neta:** € {ganancia_neta:.2f}")
                    
                    with col4:
                        st.markdown(f"📊 **Cuota:** {cuota_columna:.2f}")
                    
                    with col5:
                        # Determinar estado de la columna
                        if all(st.session_state.get(f'res_local_jugada_{i}', 0) == 0 and 
                              st.session_state.get(f'res_vis_jugada_{i}', 0) == 0 for i in range(len(columna))):
                            color_bolita = "gris"
                        else:
                            aciertos = 0
                            for i, signo in enumerate(columna):
                                if i < st.session_state.eventos_count:
                                    res_local = st.session_state.get(f'res_local_jugada_{i}', 0)
                                    res_vis = st.session_state.get(f'res_vis_jugada_{i}', 0)
                                    
                                    if (signo == '1' and res_local > res_vis) or \
                                       (signo == 'x' and res_local == res_vis) or \
                                       (signo == '2' and res_local < res_vis):
                                        aciertos += 1
                            
                            if aciertos == len(columna):
                                color_bolita = "verde"
                            else:
                                color_bolita = "roja"
                        
                        st.markdown(f'<div class="bolita bolita-{color_bolita}"></div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("📝 REGISTRAR SISTEMA", use_container_width=True):
                apuesta = {
                    "fecha": datetime.now().isoformat(),
                    "tipo": "Sistema",
                    "eventos_totales": len(st.session_state.jugadas_sistema),
                    "num_columnas": len(st.session_state.columnas_generadas),
                    "monto_total": monto_total,
                    "monto_por_columna": monto_por_columna,
                    "filtros": st.session_state.filtros_sistema,
                    "detalles": st.session_state.jugadas_sistema
                }
                
                st.session_state.apuestas.append(apuesta)
                st.session_state.saldo -= monto_total
                guardar_apuestas()
                
                st.markdown('<div class="success-message">✅ Sistema registrado correctamente!</div>', unsafe_allow_html=True)

# Página de Estadísticas de Equipos
elif st.session_state.pagina_actual == "Est. Equipos":
    st.markdown("### ⚽ Estadísticas de Equipos")
    
    if st.session_state.apuestas:
        equipos_data = []
        for apuesta in st.session_state.apuestas:
            if 'detalles' in apuesta:
                for detalle in apuesta["detalles"]:
                    if isinstance(detalle, dict):
                        if detalle.get("equipo_local"):
                            equipos_data.append({
                                "equipo": detalle["equipo_local"],
                                "resultado": "Ganado" if detalle.get("estado") == "verde" else "Perdido" if detalle.get("estado") == "roja" else "Pendiente",
                                "tipo": "Local"
                            })
                        if detalle.get("equipo_visitante"):
                            equipos_data.append({
                                "equipo": detalle["equipo_visitante"],
                                "resultado": "Ganado" if detalle.get("estado") == "verde" else "Perdido" if detalle.get("estado") == "roja" else "Pendiente",
                                "tipo": "Visitante"
                            })
        
        if equipos_data:
            df_equipos = pd.DataFrame(equipos_data)
            
            stats_equipos = df_equipos.groupby('equipo').agg({
                'resultado': lambda x: list(x)
            }).reset_index()
            
            stats_equipos['total'] = stats_equipos['resultado'].apply(len)
            stats_equipos['ganados'] = stats_equipos['resultado'].apply(lambda x: x.count('Ganado'))
            stats_equipos['perdidos'] = stats_equipos['resultado'].apply(lambda x: x.count('Perdido'))
            stats_equipos['% victorias'] = (stats_equipos['ganados'] / stats_equipos['total'] * 100).round(1)
            
            # Ordenar por % de victorias
            stats_equipos = stats_equipos.sort_values('% victorias', ascending=False)
            
            st.dataframe(
                stats_equipos[['equipo', 'total', 'ganados', 'perdidos', '% victorias']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    'equipo': 'Equipo',
                    'total': 'Total Partidos',
                    'ganados': 'Victorias',
                    'perdidos': 'Derrotas',
                    '% victorias': '% Victorias'
                }
            )
            
            # Gráfico de top equipos
            top_equipos = stats_equipos.head(10)
            st.bar_chart(top_equipos.set_index('equipo')['% victorias'])
        else:
            st.info("No hay datos de equipos disponibles")
    else:
        st.info("No hay apuestas registradas para mostrar estadísticas")

# Página de Estadísticas de Jugadas
elif st.session_state.pagina_actual == "Est. Jugadas":
    st.markdown("### 📈 Estadísticas de Jugadas")
    
    if st.session_state.apuestas:
        total_apuestas = len(st.session_state.apuestas)
        total_jugado = 0
        total_ganado = 0
        
        for apuesta in st.session_state.apuestas:
            if "monto_jugado" in apuesta:
                total_jugado += apuesta["monto_jugado"]
                total_ganado += apuesta.get("ganancia_bruta", 0)
            elif "monto_total" in apuesta:
                total_jugado += apuesta["monto_total"]
                # Para sistemas, la ganancia se calcula después
            elif "detalles" in apuesta and isinstance(apuesta["detalles"], list):
                # Intentar calcular de otra manera
                pass
        
        beneficio_total = total_ganado - total_jugado
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Apuestas", total_apuestas)
        with col2:
            st.metric("Total Jugado", f"€ {total_jugado:.2f}")
        with col3:
            st.metric("Total Ganado", f"€ {total_ganado:.2f}")
        with col4:
            delta_color = "normal" if beneficio_total >= 0 else "inverse"
            st.metric("Beneficio", f"€ {beneficio_total:.2f}", delta=beneficio_total, delta_color=delta_color)
        
        # Tabla de apuestas
        if st.session_state.apuestas:
            datos_resumen = []
            for apuesta in st.session_state.apuestas:
                fecha = datetime.fromisoformat(apuesta["fecha"]).strftime("%d/%m/%Y %H:%M") if "fecha" in apuesta else "N/A"
                tipo = apuesta.get("tipo", "N/A")
                eventos = apuesta.get("eventos_totales", 0)
                monto = apuesta.get("monto_jugado", apuesta.get("monto_total", 0))
                ganancia = apuesta.get("ganancia_neta", 0)
                
                datos_resumen.append({
                    "Fecha": fecha,
                    "Tipo": tipo,
                    "Eventos": eventos,
                    "Monto (€)": monto,
                    "Neto (€)": ganancia
                })
            
            df_resumen = pd.DataFrame(datos_resumen)
            st.dataframe(df_resumen, use_container_width=True, hide_index=True)
    else:
        st.info("No hay apuestas registradas para mostrar estadísticas")

# Página de Billetera
elif st.session_state.pagina_actual == "Billetera":
    st.markdown("### 💰 Billetera")
    
    col1, col2 = st.columns(2)
