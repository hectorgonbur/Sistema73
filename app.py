import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(
    page_title="App de Apuestas",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos personalizados
st.markdown("""
<style>
    .main-header {
        background-color: #2c3e50;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        text-align: center;
    }
    .evento-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    .contador {
        font-size: 1.5rem;
        font-weight: bold;
        padding: 1rem;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .contador-verde {
        color: #28a745;
    }
    .contador-normal {
        color: #6c757d;
    }
    .bolita {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: inline-block;
        margin-left: 10px;
    }
    .bolita-gris {
        background-color: #6c757d;
    }
    .bolita-verde {
        background-color: #28a745;
    }
    .bolita-roja {
        background-color: #dc3545;
    }
    .base-btn {
        padding: 5px 15px;
        margin: 0 2px;
        border: 1px solid #dee2e6;
        background-color: white;
        border-radius: 5px;
        cursor: pointer;
    }
    .base-btn-selected {
        background-color: #007bff;
        color: white;
        border-color: #0056b3;
    }
    .ganancia-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    .ganancia-valor {
        font-size: 1.8rem;
        font-weight: bold;
        color: #28a745;
    }
    .stButton > button {
        width: 100%;
        background-color: #28a745;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #218838;
    }
    .menu-item {
        padding: 10px;
        margin: 5px 0;
        background-color: #f8f9fa;
        border-radius: 5px;
        cursor: pointer;
    }
    .menu-item:hover {
        background-color: #e9ecef;
    }
    .submenu {
        margin-left: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Inicialización de variables de sesión
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 'Apuesta Simple'
if 'eventos_count' not in st.session_state:
    st.session_state.eventos_count = 1
if 'deportes' not in st.session_state:
    st.session_state.deportes = ['Fútbol', 'Baloncesto', 'Tenis', 'Béisbol', 'Fútbol Americano']
if 'ligas_por_deporte' not in st.session_state:
    st.session_state.ligas_por_deporte = {
        'Fútbol': ['La Liga', 'Premier League', 'Serie A', 'Bundesliga', 'Ligue 1'],
        'Baloncesto': ['NBA', 'EuroLeague', 'ACB', 'Liga Endesa'],
        'Tenis': ['ATP', 'WTA', 'Grand Slam'],
        'Béisbol': ['MLB', 'Liga Mexicana', 'Serie Nacional'],
        'Fútbol Americano': ['NFL', 'NCAA']
    }
if 'apuestas' not in st.session_state:
    # Cargar apuestas guardadas si existen
    if os.path.exists('apuestas.json'):
        with open('apuestas.json', 'r', encoding='utf-8') as f:
            st.session_state.apuestas = json.load(f)
    else:
        st.session_state.apuestas = []

# Función para guardar apuestas
def guardar_apuestas():
    with open('apuestas.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state.apuestas, f, ensure_ascii=False, indent=2)

# Menú lateral
with st.sidebar:
    st.markdown("## 📊 Menú Principal")
    
    # APUESTAS
    with st.expander("🎲 APUESTAS", expanded=False):
        if st.button("Apuesta Simple", use_container_width=True):
            st.session_state.pagina_actual = "Apuesta Simple"
        if st.button("Apuesta Múltiple", use_container_width=True):
            st.session_state.pagina_actual = "Apuesta Múltiple"
        if st.button("Sistema", use_container_width=True):
            st.session_state.pagina_actual = "Sistema"
    
    # SISTEMAS
    with st.expander("⚙️ SISTEMAS", expanded=False):
        if st.button("Jugadas", use_container_width=True):
            st.session_state.pagina_actual = "Jugadas"
        if st.button("Filtros", use_container_width=True):
            st.session_state.pagina_actual = "Filtros"
        if st.button("Columnas", use_container_width=True):
            st.session_state.pagina_actual = "Columnas"
    
    # ESTADÍSTICAS
    with st.expander("📈 ESTADÍSTICAS", expanded=False):
        if st.button("Est. Equipos", use_container_width=True):
            st.session_state.pagina_actual = "Est. Equipos"
        if st.button("Est. Jugadas", use_container_width=True):
            st.session_state.pagina_actual = "Est. Jugadas"
    
    # GANANCIAS
    with st.expander("💰 GANANCIAS", expanded=False):
        if st.button("Billetera", use_container_width=True):
            st.session_state.pagina_actual = "Billetera"
    
    # ARCHIVOS
    with st.expander("📁 ARCHIVOS", expanded=False):
        if st.button("Guardar", use_container_width=True):
            st.session_state.pagina_actual = "Guardar"
        if st.button("Exportar", use_container_width=True):
            st.session_state.pagina_actual = "Exportar"

# Cabecera principal
st.markdown(f"""
<div class="main-header">
    <h1>🎲 {st.session_state.pagina_actual}</h1>
</div>
""", unsafe_allow_html=True)

# Página de Apuesta Simple
if st.session_state.pagina_actual == "Apuesta Simple":
    # Control de eventos
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.markdown("### 📅 Eventos")
        eventos_col1, eventos_col2, eventos_col3 = st.columns([1, 2, 1])
        with eventos_col1:
            if st.button("➖", key="minus_eventos"):
                if st.session_state.eventos_count > 1:
                    st.session_state.eventos_count -= 1
                    st.rerun()
        with eventos_col2:
            st.markdown(f"<h2 style='text-align: center;'>{st.session_state.eventos_count}</h2>", unsafe_allow_html=True)
        with eventos_col3:
            if st.button("➕", key="plus_eventos"):
                if st.session_state.eventos_count < 30:
                    st.session_state.eventos_count += 1
                    st.rerun()
    
    with col2:
        st.markdown("### 📊 Progreso")
        # Calcular eventos ganados
        eventos_ganados = 0
        for i in range(st.session_state.eventos_count):
            if f'bolita_{i}' in st.session_state and st.session_state[f'bolita_{i}'] == 'verde':
                eventos_ganados += 1
        
        color_class = "contador-verde" if eventos_ganados == st.session_state.eventos_count else "contador-normal"
        st.markdown(f"""
        <div class="contador {color_class}">
            {eventos_ganados}/{st.session_state.eventos_count}
        </div>
        """, unsafe_allow_html=True)
    
    # Eventos
    st.markdown("### 🎯 Eventos")
    
    cuota_total = 1
    
    for i in range(st.session_state.eventos_count):
        with st.container():
            st.markdown(f'<div class="evento-card">', unsafe_allow_html=True)
            st.markdown(f"**Evento {i+1}**")
            
            # Primera fila - Deporte, Liga, Fecha, Hora
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                deporte = st.selectbox(
                    "Deporte",
                    options=st.session_state.deportes + ["Otro..."],
                    key=f'deporte_{i}'
                )
                if deporte == "Otro...":
                    nuevo_deporte = st.text_input("Nuevo deporte", key=f'nuevo_deporte_{i}')
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
                    key=f'liga_{i}'
                )
                if liga == "Otra...":
                    nueva_liga = st.text_input("Nueva liga", key=f'nueva_liga_{i}')
                    if nueva_liga and nueva_liga not in ligas_disponibles:
                        st.session_state.ligas_por_deporte[deporte].append(nueva_liga)
                        st.rerun()
            
            with col3:
                fecha = st.date_input("Fecha", key=f'fecha_{i}')
            
            with col4:
                hora = st.time_input("Hora", key=f'hora_{i}')
            
            # Segunda fila - Equipos y resultados
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                equipo_local = st.text_input("Equipo Local", key=f'local_{i}')
            
            with col2:
                resultado_local = st.number_input("Resultado Local", min_value=0, step=1, key=f'res_local_{i}')
            
            with col3:
                resultado_visitante = st.number_input("Resultado Visitante", min_value=0, step=1, key=f'res_vis_{i}')
            
            with col4:
                equipo_visitante = st.text_input("Equipo Visitante", key=f'vis_{i}')
            
            # Tercera fila - Cuotas y base
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                cuota_local = st.number_input("Cuota Local", min_value=1.0, value=1.0, step=0.1, key=f'cuota_local_{i}')
            
            with col2:
                cuota_empate = st.number_input("Cuota Empate", min_value=1.0, value=1.0, step=0.1, key=f'cuota_empate_{i}')
            
            with col3:
                cuota_visitante = st.number_input("Cuota Visitante", min_value=1.0, value=1.0, step=0.1, key=f'cuota_vis_{i}')
            
            with col4:
                st.markdown("**Base**")
                base_col1, base_col2, base_col3 = st.columns(3)
                
                # Inicializar base si no existe
                if f'base_{i}' not in st.session_state:
                    st.session_state[f'base_{i}'] = '1'
                
                with base_col1:
                    if st.button("1", key=f'base1_{i}'):
                        st.session_state[f'base_{i}'] = '1'
                        st.rerun()
                with base_col2:
                    if st.button("X", key=f'basex_{i}'):
                        st.session_state[f'base_{i}'] = 'x'
                        st.rerun()
                with base_col3:
                    if st.button("2", key=f'base2_{i}'):
                        st.session_state[f'base_{i}'] = '2'
                        st.rerun()
            
            with col5:
                st.markdown("**Estado**")
                # Determinar color de la bolita
                if resultado_local == 0 and resultado_visitante == 0:
                    color_bolita = "gris"
                    st.session_state[f'bolita_{i}'] = "gris"
                else:
                    base = st.session_state.get(f'base_{i}', '1')
                    if (base == '1' and resultado_local > resultado_visitante) or \
                       (base == 'x' and resultado_local == resultado_visitante) or \
                       (base == '2' and resultado_local < resultado_visitante):
                        color_bolita = "verde"
                        st.session_state[f'bolita_{i}'] = "verde"
                    else:
                        color_bolita = "roja"
                        st.session_state[f'bolita_{i}'] = "roja"
                
                st.markdown(f'<div class="bolita bolita-{color_bolita}"></div>', unsafe_allow_html=True)
            
            # Calcular cuota para ganancias
            base = st.session_state.get(f'base_{i}', '1')
            if base == '1':
                cuota_total *= cuota_local
            elif base == 'x':
                cuota_total *= cuota_empate
            else:
                cuota_total *= cuota_visitante
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Resumen de apuesta
    st.markdown("### 💰 Resumen de Apuesta")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monto_jugado = st.number_input("Monto Jugado (€)", min_value=0.0, value=0.0, step=10.0, key="monto_jugado")
    
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
    
    # Botón registrar
    if st.button("📝 REGISTRAR APUESTA", use_container_width=True):
        # Crear registro de apuesta
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
        
        # Agregar detalles de cada evento
        for i in range(st.session_state.eventos_count):
            detalle = {
                "deporte": st.session_state.get(f'deporte_{i}', ''),
                "liga": st.session_state.get(f'liga_{i}', ''),
                "fecha": str(st.session_state.get(f'fecha_{i}', '')),
                "hora": str(st.session_state.get(f'hora_{i}', '')),
                "equipo_local": st.session_state.get(f'local_{i}', ''),
                "equipo_visitante": st.session_state.get(f'vis_{i}', ''),
                "resultado_local": st.session_state.get(f'res_local_{i}', 0),
                "resultado_visitante": st.session_state.get(f'res_vis_{i}', 0),
                "base": st.session_state.get(f'base_{i}', '1'),
                "estado": st.session_state.get(f'bolita_{i}', 'gris')
            }
            apuesta["detalles"].append(detalle)
        
        # Guardar apuesta
        st.session_state.apuestas.append(apuesta)
        guardar_apuestas()
        
        st.success("✅ Apuesta registrada correctamente!")

# Página de Apuesta Múltiple (placeholder)
elif st.session_state.pagina_actual == "Apuesta Múltiple":
    st.info("🚧 Página en desarrollo - Próximamente disponible")

# Página de Sistema (placeholder)
elif st.session_state.pagina_actual == "Sistema":
    st.info("🚧 Página en desarrollo - Próximamente disponible")

# Página de Jugadas (placeholder)
elif st.session_state.pagina_actual == "Jugadas":
    st.info("🚧 Página en desarrollo - Próximamente disponible")

# Página de Filtros (placeholder)
elif st.session_state.pagina_actual == "Filtros":
    st.info("🚧 Página en desarrollo - Próximamente disponible")

# Página de Columnas (placeholder)
elif st.session_state.pagina_actual == "Columnas":
    st.info("🚧 Página en desarrollo - Próximamente disponible")

# Página de Estadísticas de Equipos
elif st.session_state.pagina_actual == "Est. Equipos":
    st.markdown("### 📊 Estadísticas de Equipos")
    
    if st.session_state.apuestas:
        # Procesar datos para estadísticas de equipos
        equipos_data = []
        for apuesta in st.session_state.apuestas:
            for detalle in apuesta["detalles"]:
                if detalle["equipo_local"]:
                    equipos_data.append({
                        "equipo": detalle["equipo_local"],
                        "resultado": "Ganado" if detalle["estado"] == "verde" else "Perdido" if detalle["estado"] == "roja" else "Pendiente",
                        "tipo": "Local"
                    })
                if detalle["equipo_visitante"]:
                    equipos_data.append({
                        "equipo": detalle["equipo_visitante"],
                        "resultado": "Ganado" if detalle["estado"] == "verde" else "Perdido" if detalle["estado"] == "roja" else "Pendiente",
                        "tipo": "Visitante"
                    })
        
        if equipos_data:
            df_equipos = pd.DataFrame(equipos_data)
            
            # Estadísticas por equipo
            stats_equipos = df_equipos.groupby('equipo').agg({
                'resultado': lambda x: list(x)
            }).reset_index()
            
            stats_equipos['total'] = stats_equipos['resultado'].apply(len)
            stats_equipos['ganados'] = stats_equipos['resultado'].apply(lambda x: x.count('Ganado'))
            stats_equipos['perdidos'] = stats_equipos['resultado'].apply(lambda x: x.count('Perdido'))
            stats_equipos['% victorias'] = (stats_equipos['ganados'] / stats_equipos['total'] * 100).round(1)
            
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
        else:
            st.info("No hay datos de equipos disponibles")
    else:
        st.info("No hay apuestas registradas para mostrar estadísticas")

# Página de Estadísticas de Jugadas
elif st.session_state.pagina_actual == "Est. Jugadas":
    st.markdown("### 📈 Estadísticas de Jugadas")
    
    if st.session_state.apuestas:
        # Resumen general
        total_apuestas = len(st.session_state.apuestas)
        total_jugado = sum(a["monto_jugado"] for a in st.session_state.apuestas)
        total_ganado = sum(a["ganancia_bruta"] for a in st.session_state.apuestas)
        beneficio_total = total_ganado - total_jugado
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Apuestas", total_apuestas)
        with col2:
            st.metric("Total Jugado", f"€ {total_jugado:.2f}")
        with col3:
            st.metric("Total Ganado", f"€ {total_ganado:.2f}")
        with col4:
            st.metric("Beneficio", f"€ {beneficio_total:.2f}", 
                     delta_color="normal" if beneficio_total >= 0 else "inverse")
        
        # Tabla de apuestas
        df_apuestas = pd.DataFrame(st.session_state.apuestas)
        df_apuestas['fecha'] = pd.to_datetime(df_apuestas['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        
        st.dataframe(
            df_apuestas[['fecha', 'tipo', 'eventos_totales', 'eventos_ganados', 'monto_jugado', 'ganancia_neta']],
            use_container_width=True,
            hide_index=True,
            column_config={
                'fecha': 'Fecha',
                'tipo': 'Tipo',
                'eventos_totales': 'Eventos',
                'eventos_ganados': 'Ganados',
                'monto_jugado': 'Jugado (€)',
                'ganancia_neta': 'Neto (€)'
            }
        )
    else:
        st.info("No hay apuestas registradas para mostrar estadísticas")

# Página de Billetera
elif st.session_state.pagina_actual == "Billetera":
    st.markdown("### 💰 Billetera")
    
    # Inicializar saldo si no existe
    if 'saldo' not in st.session_state:
        st.session_state.saldo = 1000.0
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="ganancia-card">
            <h3>Saldo Actual</h3>
            <div class="ganancia-valor">€ {st.session_state.saldo:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Agregar Fondos")
        cantidad_agregar = st.number_input("Cantidad (€)", min_value=0.0, value=100.0, step=10.0)
        if st.button("Agregar a Billetera"):
            st.session_state.saldo += cantidad_agregar
            st.success(f"✅ Se agregaron € {cantidad_agregar:.2f} a tu billetera")
            st.rerun()
    
    # Historial de movimientos
    st.markdown("### 📋 Últimos Movimientos")
    if st.session_state.apuestas:
        movimientos = []
        for apuesta in st.session_state.apuestas[-10:]:  # Últimas 10 apuestas
            movimientos.append({
                "fecha": datetime.fromisoformat(apuesta["fecha"]).strftime("%d/%m/%Y"),
                "concepto": f"Apuesta - {apuesta['tipo']}",
                "cantidad": f"-€ {apuesta['monto_jugado']:.2f}",
                "resultado": apuesta['ganancia_neta']
            })
        
        df_movimientos = pd.DataFrame(movimientos)
        st.dataframe(df_movimientos, use_container_width=True, hide_index=True)
    else:
        st.info("No hay movimientos recientes")

# Página de Guardar
elif st.session_state.pagina_actual == "Guardar":
    st.markdown("### 💾 Guardar Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Guardar Apuestas")
        if st.button("💾 Guardar en archivo", use_container_width=True):
            guardar_apuestas()
            st.success("✅ Datos guardados correctamente en 'apuestas.json'")
    
    with col2:
        st.markdown("#### Cargar Apuestas")
        uploaded_file = st.file_uploader("Seleccionar archivo JSON", type=['json'])
        if uploaded_file is not None:
            try:
                datos_cargados = json.load(uploaded_file)
                st.session_state.apuestas = datos_cargados
                guardar_apuestas()
                st.success(f"✅ Se cargaron {len(datos_cargados)} apuestas correctamente")
            except Exception as e:
                st.error(f"Error al cargar el archivo: {e}")

# Página de Exportar
elif st.session_state.pagina_actual == "Exportar":
    st.markdown("### 📤 Exportar Datos")
    
    if st.session_state.apuestas:
        formato = st.radio("Seleccionar formato:", ["JSON", "CSV", "Excel"])
        
        if formato == "JSON":
            json_str = json.dumps(st.session_state.apuestas, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Descargar JSON",
                data=json_str,
                file_name=f"apuestas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        elif formato == "CSV":
            df = pd.DataFrame(st.session_state.apuestas)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"apuestas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        else:  # Excel
            df = pd.DataFrame(st.session_state.apuestas)
            # Para Excel necesitamos un archivo temporal
            excel_file = f"apuestas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(excel_file, index=False)
            with open(excel_file, 'rb') as f:
                st.download_button(
                    label="📥 Descargar Excel",
                    data=f,
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.info("No hay datos para exportar")

# Pie de página
st.markdown("---")
st.markdown("© 2024 App de Apuestas - Todos los derechos reservados")
