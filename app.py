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
        font-size: 2rem;
        font-weight: bold;
    }
    .contador-verde {
        color: #4ade80;
    }
    .contador-normal {
        color: #000000;
    }
    .contador-blanco {
        color: white;
    }
    .bolita {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-block;
        margin: 0 auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: transform 0.3s;
    }
    .bolita:hover {
        transform: scale(1.1);
    }
    .bolita-verde {
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 100%);
    }
    .bolita-roja {
        background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
    }
    .base-btn {
        padding: 5px 10px;
        margin: 0 2px;
        border: 1px solid #dee2e6;
        background-color: white;
        border-radius: 5px;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s;
    }
    .base-btn:hover {
        background-color: #e9ecef;
    }
    .base-btn-selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
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
    .evento-titulo {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
    }
    .resultado-input {
        max-width: 60px;
    }
    .eventos-control {
        display: flex;
        align-items: center;
        gap: 10px;
        background-color: white;
        padding: 5px 10px;
        border-radius: 5px;
        border: 1px solid #dee2e6;
    }
    .eventos-control button {
        width: 30px;
        height: 30px;
        padding: 0;
        font-size: 1.2rem;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        cursor: pointer;
    }
    .eventos-control button:hover {
        background-color: #e9ecef;
    }
    .eventos-control span {
        font-size: 1.2rem;
        font-weight: bold;
        min-width: 30px;
        text-align: center;
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
    if 'jugada_actual' not in st.session_state:
        st.session_state.jugada_actual = {}

init_session_state()

# Función para guardar apuestas
def guardar_apuestas():
    with open('apuestas.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.apuestas, f, ensure_ascii=False, indent=2)

# Función para guardar jugada actual en archivo
def guardar_jugada(nombre_archivo):
    jugada = {
        "tipo": st.session_state.pagina_actual,
        "eventos_count": st.session_state.eventos_count,
        "datos": {}
    }
    
    # Guardar datos específicos según la página
    if st.session_state.pagina_actual == "Apuesta Simple":
        for i in range(st.session_state.eventos_count):
            jugada["datos"][f"evento_{i}"] = {
                "deporte": st.session_state.get(f'deporte_simple_{i}', ''),
                "liga": st.session_state.get(f'liga_simple_{i}', ''),
                "fecha": str(st.session_state.get(f'fecha_simple_{i}', '')),
                "hora": str(st.session_state.get(f'hora_simple_{i}', '')),
                "local": st.session_state.get(f'local_simple_{i}', ''),
                "visitante": st.session_state.get(f'vis_simple_{i}', ''),
                "resultado_local": st.session_state.get(f'res_local_simple_{i}', 0),
                "resultado_visitante": st.session_state.get(f'res_vis_simple_{i}', 0),
                "cuota_local": st.session_state.get(f'cuota_local_simple_{i}', 1.0),
                "cuota_empate": st.session_state.get(f'cuota_empate_simple_{i}', 1.0),
                "cuota_visitante": st.session_state.get(f'cuota_vis_simple_{i}', 1.0),
                "base": st.session_state.get(f'base_simple_{i}', '1')
            }
    
    with open(f"{nombre_archivo}.json", 'w', encoding='utf-8') as f:
        json.dump(jugada, f, ensure_ascii=False, indent=2)

# Función para cargar jugada desde archivo
def cargar_jugada(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            jugada = json.load(f)
        
        st.session_state.eventos_count = jugada["eventos_count"]
        
        # Cargar datos específicos según la página
        if jugada["tipo"] == "Apuesta Simple":
            for i in range(jugada["eventos_count"]):
                evento = jugada["datos"][f"evento_{i}"]
                st.session_state[f'deporte_simple_{i}'] = evento["deporte"]
                st.session_state[f'liga_simple_{i}'] = evento["liga"]
                if evento["fecha"]:
                    st.session_state[f'fecha_simple_{i}'] = datetime.fromisoformat(evento["fecha"]).date()
                if evento["hora"]:
                    st.session_state[f'hora_simple_{i}'] = datetime.fromisoformat(evento["hora"]).time()
                st.session_state[f'local_simple_{i}'] = evento["local"]
                st.session_state[f'vis_simple_{i}'] = evento["visitante"]
                st.session_state[f'res_local_simple_{i}'] = evento["resultado_local"]
                st.session_state[f'res_vis_simple_{i}'] = evento["resultado_visitante"]
                st.session_state[f'cuota_local_simple_{i}'] = evento["cuota_local"]
                st.session_state[f'cuota_empate_simple_{i}'] = evento["cuota_empate"]
                st.session_state[f'cuota_vis_simple_{i}'] = evento["cuota_visitante"]
                st.session_state[f'base_simple_{i}'] = evento["base"]
        
        return True
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return False

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
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📅 Eventos")
        eventos_col1, eventos_col2, eventos_col3 = st.columns([1, 1, 1])
        with eventos_col1:
            if st.button("➖", key="minus_eventos_simple"):
                if st.session_state.eventos_count > 1:
                    st.session_state.eventos_count -= 1
                    st.rerun()
        with eventos_col2:
            st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: bold;'>{st.session_state.eventos_count:02d}</div>", unsafe_allow_html=True)
        with eventos_col3:
            if st.button("➕", key="plus_eventos_simple"):
                if st.session_state.eventos_count < 30:
                    st.session_state.eventos_count += 1
                    st.rerun()
    
    with col2:
        st.markdown("### 🎯 Aciertos")
        # Calcular eventos ganados (bolitas verdes)
        eventos_ganados = 0
        for i in range(st.session_state.eventos_count):
            if f'bolita_simple_{i}' in st.session_state and st.session_state[f'bolita_simple_{i}'] == 'verde':
                eventos_ganados += 1
        
        color_class = "contador-verde" if eventos_ganados == st.session_state.eventos_count else "contador-normal"
        st.markdown(f'<div style="text-align: center; font-size: 1.5rem; font-weight: bold;" class="{color_class}">{eventos_ganados:02d}/{st.session_state.eventos_count:02d}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Eventos
    cuota_total = 1
    
    for i in range(st.session_state.eventos_count):
        with st.container():
            st.markdown(f'<div class="evento-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="evento-titulo">Evento {i+1}</div>', unsafe_allow_html=True)
            
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
                resultado_local = st.number_input("Resultado Local", min_value=0, step=1, key=f'res_local_simple_{i}', format="%d")
            
            with col3:
                resultado_visitante = st.number_input("Resultado Visitante", min_value=0, step=1, key=f'res_vis_simple_{i}', format="%d")
            
            with col4:
                equipo_visitante = st.text_input("Equipo Visitante", key=f'vis_simple_{i}')
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                cuota_local = st.number_input("Cuota Local", min_value=1.0, value=1.0, step=0.1, key=f'cuota_local_simple_{i}', format="%.2f")
            
            with col2:
                cuota_empate = st.number_input("Cuota Empate", min_value=1.0, value=1.0, step=0.1, key=f'cuota_empate_simple_{i}', format="%.2f")
            
            with col3:
                cuota_visitante = st.number_input("Cuota Visitante", min_value=1.0, value=1.0, step=0.1, key=f'cuota_vis_simple_{i}', format="%.2f")
            
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
                base = st.session_state.get(f'base_simple_{i}', '1')
                
                # Determinar color de la bolita
                if (base == '1' and resultado_local > resultado_visitante) or \
                   (base == 'x' and resultado_local == resultado_visitante) or \
                   (base == '2' and resultado_local < resultado_visitante):
                    color_bolita = "verde"
                    st.session_state[f'bolita_simple_{i}'] = "verde"
                else:
                    color_bolita = "roja"
                    st.session_state[f'bolita_simple_{i}'] = "roja"
                
                st.markdown(f'<div style="display: flex; justify-content: center;"><div class="bolita bolita-{color_bolita}"></div></div>', unsafe_allow_html=True)
            
            # Calcular cuota para ganancia total
            if base == '1':
                cuota_total *= cuota_local
            elif base == 'x':
                cuota_total *= cuota_empate
            else:
                cuota_total *= cuota_visitante
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 💰 Apuesta Total")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monto_jugado = st.number_input("Monto Jugado (€)", min_value=0.0, value=0.0, step=10.0, key="monto_simple", format="%.2f")
    
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
    
    # Billetera
    st.markdown("### 👛 Billetera")
    st.markdown(f"""
    <div class="ganancia-card">
        <h4>Saldo Actual</h4>
        <div class="ganancia-valor">€ {st.session_state.saldo:.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📝 REGISTRAR", use_container_width=True):
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
                "estado": st.session_state.get(f'bolita_simple_{i}', 'roja')
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
        st.markdown("### 📅 Eventos")
        eventos_col1, eventos_col2, eventos_col3 = st.columns([1, 1, 1])
        with eventos_col1:
            if st.button("➖", key="minus_eventos_multiple"):
                if st.session_state.eventos_count > 1:
                    st.session_state.eventos_count -= 1
                    st.rerun()
        with eventos_col2:
            st.markdown(f"<div style='text-align: center; font-size: 1.5rem; font-weight: bold;'>{st.session_state.eventos_count:02d}</div>", unsafe_allow_html=True)
        with eventos_col3:
            if st.button("➕", key="plus_eventos_multiple"):
                if st.session_state.eventos_count < 30:
                    st.session_state.eventos_count += 1
                    st.rerun()
    
    with col2:
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
            st.markdown(f'<div style="text-align: center; font-size: 1.5rem; font-weight: bold;" class="{color_class}">{max_aciertos:02d}/{st.session_state.eventos_count:02d}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="text-align: center; font-size: 1.5rem; font-weight: bold;" class="contador-normal">00/{st.session_state.eventos_count:02d}</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("### 🎯 Aciertos Base")
