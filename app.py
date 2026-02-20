# app.py
# Aplicación Streamlit para gestión de apuestas deportivas (Parte 1)
# Autor: Desarrollador Senior Python
# Ejecutar: streamlit run app.py

import streamlit as st
import pandas as pd
from datetime import datetime, time, date
from typing import Dict, List, Optional, Any
import json

# -------------------------------------------------------------------
# CONFIGURACIÓN INICIAL DE LA PÁGINA
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Bet Manager - Apuestas Deportivas",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# INYECCIÓN DE CSS PERSONALIZADO (bolitas, texto verde, etc.)
# -------------------------------------------------------------------
def inject_custom_css():
    st.markdown("""
    <style>
    /* Estilo para las bolitas de estado */
    .bolita {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: inline-block;
        margin-top: 8px;
    }
    .bolita.gris { background-color: #9ca3af; }
    .bolita.verde { background-color: #10b981; }
    .bolita.roja { background-color: #ef4444; }
    /* Texto verde para contador cuando todos ganados */
    .texto-verde {
        color: #10b981 !important;
        font-weight: bold;
    }
    /* Botón gigante */
    .stButton > button {
        font-size: 1.5rem;
        padding: 0.75rem 2rem;
        background-color: #3b82f6;
        color: white;
        border-radius: 0.5rem;
        border: none;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #2563eb;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# INICIALIZACIÓN AVANZADA DEL ESTADO DE SESIÓN
# -------------------------------------------------------------------
def init_session_state():
    """Inicializa todas las variables de estado necesarias."""
    # Página actual (controlada por el menú)
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = "Inicio"
    
    # Datos maestros (deportes y ligas)
    if 'deportes' not in st.session_state:
        st.session_state.deportes = [
            {"id": "futbol", "nombre": "Fútbol"},
            {"id": "baloncesto", "nombre": "Baloncesto"},
        ]
    if 'ligas' not in st.session_state:
        st.session_state.ligas = [
            {"id": "liga-espanola", "deporte_id": "futbol", "nombre": "LaLiga"},
            {"id": "premier", "deporte_id": "futbol", "nombre": "Premier League"},
            {"id": "nba", "deporte_id": "baloncesto", "nombre": "NBA"},
        ]
    
    # Estado de la página "Apuesta Simple"
    if 'eventos' not in st.session_state:
        st.session_state.eventos = []  # lista de eventos (diccionarios)
    if 'cantidad_eventos' not in st.session_state:
        st.session_state.cantidad_eventos = 1
    if 'monto_jugado' not in st.session_state:
        st.session_state.monto_jugado = 0.0
    
    # Historial de apuestas registradas (estadísticas)
    if 'estadisticas' not in st.session_state:
        st.session_state.estadisticas = []

# -------------------------------------------------------------------
# FUNCIONES DE AYUDA PARA DEPORTES/LIGAS
# -------------------------------------------------------------------
def obtener_deportes() -> List[Dict]:
    return st.session_state.deportes

def obtener_ligas_por_deporte(deporte_id: str) -> List[Dict]:
    return [liga for liga in st.session_state.ligas if liga['deporte_id'] == deporte_id]

def agregar_deporte(nombre: str):
    nuevo_id = f"dep_{len(st.session_state.deportes)}_{datetime.now().timestamp()}"
    st.session_state.deportes.append({"id": nuevo_id, "nombre": nombre})

def agregar_liga(nombre: str, deporte_id: str):
    nuevo_id = f"lig_{len(st.session_state.ligas)}_{datetime.now().timestamp()}"
    st.session_state.ligas.append({"id": nuevo_id, "deporte_id": deporte_id, "nombre": nombre})

# -------------------------------------------------------------------
# CONSTRUCCIÓN DEL MENÚ LATERAL (ACORDEÓN)
# -------------------------------------------------------------------
def render_sidebar():
    """Renderiza el menú lateral con expanders y botones."""
    with st.sidebar:
        st.title("⚡ Bet Manager")
        st.markdown("---")
        
        # APUESTAS
        with st.expander("📊 APUESTAS", expanded=True):
            if st.button("Apuesta Simple", key="btn_apuesta_simple", use_container_width=True):
                st.session_state.pagina_actual = "Apuesta Simple"
            if st.button("Apuesta Múltiple", key="btn_apuesta_multiple", use_container_width=True):
                st.session_state.pagina_actual = "Apuesta Múltiple"
            if st.button("Sistema", key="btn_sistema", use_container_width=True):
                st.session_state.pagina_actual = "Sistema"
        
        # SISTEMAS
        with st.expander("⚙️ SISTEMAS", expanded=False):
            if st.button("Jugadas", key="btn_jugadas", use_container_width=True):
                st.session_state.pagina_actual = "Jugadas"
            if st.button("Filtros", key="btn_filtros", use_container_width=True):
                st.session_state.pagina_actual = "Filtros"
            if st.button("Columnas", key="btn_columnas", use_container_width=True):
                st.session_state.pagina_actual = "Columnas"
        
        # ESTADÍSTICAS
        with st.expander("📈 ESTADÍSTICAS", expanded=False):
            if st.button("Est. Equipos", key="btn_est_equipos", use_container_width=True):
                st.session_state.pagina_actual = "Est. Equipos"
            if st.button("Est. Jugadas", key="btn_est_jugadas", use_container_width=True):
                st.session_state.pagina_actual = "Est. Jugadas"
        
        # GANANCIAS
        with st.expander("💰 GANANCIAS", expanded=False):
            if st.button("Billetera", key="btn_billetera", use_container_width=True):
                st.session_state.pagina_actual = "Billetera"
        
        # ARCHIVOS
        with st.expander("📁 ARCHIVOS", expanded=False):
            if st.button("Guardar", key="btn_guardar", use_container_width=True):
                st.session_state.pagina_actual = "Guardar"
            if st.button("Exportar", key="btn_exportar", use_container_width=True):
                st.session_state.pagina_actual = "Exportar"
        
        st.markdown("---")
        st.caption(f"Página actual: **{st.session_state.pagina_actual}**")

# -------------------------------------------------------------------
# PÁGINA DE INICIO (POR DEFECTO)
# -------------------------------------------------------------------
def render_inicio():
    st.title("Bienvenido a Bet Manager")
    st.markdown("Seleccione una opción del menú lateral para comenzar.")
    st.image("https://via.placeholder.com/800x200?text=Gestion+Profesional+de+Apuestas", use_column_width=True)

# -------------------------------------------------------------------
# PÁGINA "EN CONSTRUCCIÓN" PARA DEMÁS OPCIONES
# -------------------------------------------------------------------
def render_en_construccion():
    st.title("🚧 Página en construcción")
    st.markdown(f"La sección **{st.session_state.pagina_actual}** estará disponible próximamente.")

# -------------------------------------------------------------------
# PÁGINA "APUESTA SIMPLE" (COMPLETA)
# -------------------------------------------------------------------
def render_apuesta_simple():
    st.title("📋 Apuesta Simple")
    
    # -----------------------------------------------------------------
    # A. Cabecera: control de eventos y marcador
    # -----------------------------------------------------------------
    col1, col2 = st.columns([3, 1])
    with col1:
        # Control de eventos (number_input con botones +/-)
        cantidad = st.number_input(
            "Número de eventos",
            min_value=1,
            max_value=30,
            value=st.session_state.cantidad_eventos,
            step=1,
            key="input_cantidad_eventos"
        )
        # Actualizar la cantidad si cambia
        if cantidad != st.session_state.cantidad_eventos:
            st.session_state.cantidad_eventos = cantidad
            # Ajustar la lista de eventos (añadir o quitar)
            actualizar_lista_eventos()
            st.rerun()
    
    # -----------------------------------------------------------------
    # Función para ajustar la lista de eventos según cantidad
    # -----------------------------------------------------------------
    def actualizar_lista_eventos():
        eventos = st.session_state.eventos
        target = st.session_state.cantidad_eventos
        if len(eventos) < target:
            # Añadir nuevos eventos vacíos
            for i in range(len(eventos), target):
                eventos.append({
                    "id": f"ev_{datetime.now().timestamp()}_{i}",
                    "deporte": None,
                    "liga": None,
                    "fecha": date.today(),
                    "hora": time(12, 0),
                    "equipo_local": "",
                    "resultado_local": None,
                    "resultado_visitante": None,
                    "equipo_visitante": "",
                    "cuota_local": None,
                    "cuota_empate": None,
                    "cuota_visitante": None,
                    "base": None,
                })
        elif len(eventos) > target:
            st.session_state.eventos = eventos[:target]
    
    # Calcular eventos ganados para el marcador
    eventos_ganados = 0
    for ev in st.session_state.eventos:
        if ev["resultado_local"] is not None and ev["resultado_visitante"] is not None and ev["base"]:
            if ev["resultado_local"] > ev["resultado_visitante"]:
                ganador = "1"
            elif ev["resultado_local"] < ev["resultado_visitante"]:
                ganador = "2"
            else:
                ganador = "X"
            if ganador == ev["base"]:
                eventos_ganados += 1
    
    with col2:
        st.markdown("##### Marcador")
        # Clase condicional para texto verde
        clase_texto = "texto-verde" if eventos_ganados == st.session_state.cantidad_eventos else ""
        st.markdown(f"<div class='{clase_texto}' style='font-size: 2rem; font-weight: bold;'>{eventos_ganados}/{st.session_state.cantidad_eventos}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # -----------------------------------------------------------------
    # B. Lista dinámica de eventos (tarjetas)
    # -----------------------------------------------------------------
    # Ordenar eventos por fecha y hora (para mostrarlos ordenados)
    eventos_ordenados = sorted(
        st.session_state.eventos,
        key=lambda e: (e["fecha"] or date.today(), e["hora"] or time(0,0))
    )
    
    # Para facilitar la actualización, usaremos índices basados en el orden
    # Pero necesitamos mantener la referencia al original para modificar.
    # Creamos un mapeo: posición visible -> id del evento
    orden_ids = [ev["id"] for ev in eventos_ordenados]
    
    # Diccionario para acceso rápido por id
    eventos_dict = {ev["id"]: ev for ev in st.session_state.eventos}
    
    for idx, ev_id in enumerate(orden_ids):
        ev = eventos_dict[ev_id]
        with st.container():
            # Usamos un expander o un contenedor con borde (simula tarjeta)
            with st.expander(f"Evento #{idx+1} - {ev['equipo_local'] or 'Local'} vs {ev['equipo_visitante'] or 'Visitante'}", expanded=True):
                cols = st.columns([1, 1, 1, 1])
                
                # Fila 1: Deporte, Liga, Fecha, Hora
                with cols[0]:
                    # Selector de deporte con opción "Agregar nuevo"
                    deportes = obtener_deportes()
                    deporte_options = [d["nombre"] for d in deportes] + ["➕ Agregar nuevo..."]
                    # Índice actual
                    deporte_actual = ev["deporte"]
                    deporte_nombre_actual = next((d["nombre"] for d in deportes if d["id"] == deporte_actual), None)
                    try:
                        default_idx = deporte_options.index(deporte_nombre_actual) if deporte_nombre_actual else 0
                    except ValueError:
                        default_idx = 0
                    
                    seleccion = st.selectbox(
                        "Deporte",
                        options=deporte_options,
                        index=default_idx,
                        key=f"deporte_{ev_id}"
                    )
                    if seleccion == "➕ Agregar nuevo...":
                        nuevo_nombre = st.text_input("Nombre del nuevo deporte:", key=f"nuevo_deporte_{ev_id}")
                        if nuevo_nombre and st.button("Guardar deporte", key=f"btn_guardar_deporte_{ev_id}"):
                            agregar_deporte(nuevo_nombre)
                            st.rerun()
                    else:
                        # Buscar id del deporte seleccionado
                        deporte_obj = next((d for d in deportes if d["nombre"] == seleccion), None)
                        if deporte_obj:
                            ev["deporte"] = deporte_obj["id"]
                        else:
                            ev["deporte"] = None
                
                with cols[1]:
                    # Selector de liga (dependiente del deporte)
                    ligas_disponibles = obtener_ligas_por_deporte(ev["deporte"]) if ev["deporte"] else []
                    liga_options = [l["nombre"] for l in ligas_disponibles] + (["➕ Agregar nueva..."] if ev["deporte"] else [])
                    liga_actual = ev["liga"]
                    liga_nombre_actual = next((l["nombre"] for l in ligas_disponibles if l["id"] == liga_actual), None)
                    try:
                        default_liga_idx = liga_options.index(liga_nombre_actual) if liga_nombre_actual else 0
                    except ValueError:
                        default_liga_idx = 0
                    
                    seleccion_liga = st.selectbox(
                        "Liga",
                        options=liga_options,
                        index=default_liga_idx,
                        key=f"liga_{ev_id}",
                        disabled=not ev["deporte"]
                    )
                    if seleccion_liga == "➕ Agregar nueva...":
                        nuevo_nombre_liga = st.text_input("Nombre de la nueva liga:", key=f"nueva_liga_{ev_id}")
                        if nuevo_nombre_liga and st.button("Guardar liga", key=f"btn_guardar_liga_{ev_id}"):
                            agregar_liga(nuevo_nombre_liga, ev["deporte"])
                            st.rerun()
                    else:
                        liga_obj = next((l for l in ligas_disponibles if l["nombre"] == seleccion_liga), None)
                        if liga_obj:
                            ev["liga"] = liga_obj["id"]
                        else:
                            ev["liga"] = None
                
                with cols[2]:
                    # Fecha
                    fecha_val = ev.get("fecha", date.today())
                    if not fecha_val:
                        fecha_val = date.today()
                    ev["fecha"] = st.date_input("Fecha", value=fecha_val, key=f"fecha_{ev_id}")
                
                with cols[3]:
                    # Hora
                    hora_val = ev.get("hora", time(12,0))
                    if not hora_val:
                        hora_val = time(12,0)
                    ev["hora"] = st.time_input("Hora", value=hora_val, key=f"hora_{ev_id}")
                
                # Fila 2: Equipos y resultados
                cols2 = st.columns(4)
                with cols2[0]:
                    ev["equipo_local"] = st.text_input("Equipo Local", value=ev.get("equipo_local", ""), key=f"el_{ev_id}")
                with cols2[1]:
                    ev["resultado_local"] = st.number_input("Resultado Local", value=ev.get("resultado_local") if ev.get("resultado_local") is not None else 0, step=1, key=f"rl_{ev_id}")
                with cols2[2]:
                    ev["resultado_visitante"] = st.number_input("Resultado Visitante", value=ev.get("resultado_visitante") if ev.get("resultado_visitante") is not None else 0, step=1, key=f"rv_{ev_id}")
                with cols2[3]:
                    ev["equipo_visitante"] = st.text_input("Equipo Visitante", value=ev.get("equipo_visitante", ""), key=f"ev_{ev_id}")
                
                # Fila 3: Cuotas, Base y Bolita
                cols3 = st.columns([1,1,1,1,0.5])
                with cols3[0]:
                    ev["cuota_local"] = st.number_input("Cuota 1", value=ev.get("cuota_local") if ev.get("cuota_local") is not None else 0.0, step=0.01, format="%.2f", key=f"c1_{ev_id}")
                with cols3[1]:
                    ev["cuota_empate"] = st.number_input("Cuota X", value=ev.get("cuota_empate") if ev.get("cuota_empate") is not None else 0.0, step=0.01, format="%.2f", key=f"cx_{ev_id}")
                with cols3[2]:
                    ev["cuota_visitante"] = st.number_input("Cuota 2", value=ev.get("cuota_visitante") if ev.get("cuota_visitante") is not None else 0.0, step=0.01, format="%.2f", key=f"c2_{ev_id}")
                with cols3[3]:
                    base_options = ["", "1", "X", "2"]
                    try:
                        default_base_idx = base_options.index(ev.get("base")) if ev.get("base") else 0
                    except ValueError:
                        default_base_idx = 0
                    ev["base"] = st.selectbox("Base", options=base_options, index=default_base_idx, key=f"base_{ev_id}")
                
                with cols3[4]:
                    # Lógica de la bolita
                    bolita_clase = "gris"
                    if ev["resultado_local"] is not None and ev["resultado_visitante"] is not None and ev["base"]:
                        if ev["resultado_local"] > ev["resultado_visitante"]:
                            ganador = "1"
                        elif ev["resultado_local"] < ev["resultado_visitante"]:
                            ganador = "2"
                        else:
                            ganador = "X"
                        if ganador == ev["base"]:
                            bolita_clase = "verde"
                        else:
                            bolita_clase = "roja"
                    st.markdown(f"<div class='bolita {bolita_clase}'></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # -----------------------------------------------------------------
    # C. Pie de página: cálculos y botón registrar
    # -----------------------------------------------------------------
    # Calcular cuota combinada (producto de las cuotas de la base de cada evento)
    cuota_combinada = 1.0
    for ev in st.session_state.eventos:
        if ev["base"] and ev["base"] != "":
            if ev["base"] == "1" and ev["cuota_local"] and ev["cuota_local"] > 0:
                cuota_combinada *= ev["cuota_local"]
            elif ev["base"] == "X" and ev["cuota_empate"] and ev["cuota_empate"] > 0:
                cuota_combinada *= ev["cuota_empate"]
            elif ev["base"] == "2" and ev["cuota_visitante"] and ev["cuota_visitante"] > 0:
                cuota_combinada *= ev["cuota_visitante"]
            else:
                cuota_combinada *= 1.0  # si no hay cuota, se multiplica por 1 (no afecta)
    
    # Monto jugado
    monto = st.number_input(
        "Monto Jugado (Stake)",
        min_value=0.0,
        value=st.session_state.monto_jugado,
        step=0.5,
        format="%.2f",
        key="monto_jugado_input"
    )
    st.session_state.monto_jugado = monto
    
    # Ganancias
    ganancia_bruta = monto * cuota_combinada
    ganancia_neta = ganancia_bruta - monto
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.metric("Ganancia Bruta", f"{ganancia_bruta:.2f}")
    with col_f2:
        st.metric("Ganancia Neta", f"{ganancia_neta:.2f}")
    with col_f3:
        # Botón gigante de registrar
        if st.button("📝 REGISTRAR", key="btn_registrar"):
            # Validar que todos los eventos tengan base y cuota correspondiente
            error = False
            for ev in st.session_state.eventos:
                if not ev["base"] or ev["base"] == "":
                    st.error("Todos los eventos deben tener una base seleccionada.")
                    error = True
                    break
                if ev["base"] == "1" and (not ev["cuota_local"] or ev["cuota_local"] <= 0):
                    st.error(f"Evento {ev['equipo_local']} vs {ev['equipo_visitante']}: Cuota Local inválida.")
                    error = True
                    break
                if ev["base"] == "X" and (not ev["cuota_empate"] or ev["cuota_empate"] <= 0):
                    st.error(f"Evento {ev['equipo_local']} vs {ev['equipo_visitante']}: Cuota Empate inválida.")
                    error = True
                    break
                if ev["base"] == "2" and (not ev["cuota_visitante"] or ev["cuota_visitante"] <= 0):
                    st.error(f"Evento {ev['equipo_local']} vs {ev['equipo_visitante']}: Cuota Visitante inválida.")
                    error = True
                    break
            if monto <= 0:
                st.error("El monto jugado debe ser mayor a cero.")
                error = True
            
            if not error:
                # Crear diccionario de la apuesta
                apuesta = {
                    "id": f"apuesta_{datetime.now().timestamp()}",
                    "fecha": datetime.now().isoformat(),
                    "eventos": st.session_state.eventos.copy(),
                    "monto_jugado": monto,
                    "ganancia_bruta": ganancia_bruta,
                    "ganancia_neta": ganancia_neta,
                }
                st.session_state.estadisticas.append(apuesta)
                st.success("✅ Apuesta registrada correctamente en estadísticas.")
                # Opcional: mostrar un resumen
                with st.expander("Ver detalle de la apuesta registrada"):
                    st.json(apuesta)

# -------------------------------------------------------------------
# CONTROLADOR PRINCIPAL DE PÁGINAS
# -------------------------------------------------------------------
def main():
    init_session_state()
    inject_custom_css()
    render_sidebar()
    
    # Renderizar la página según el estado
    if st.session_state.pagina_actual == "Inicio":
        render_inicio()
    elif st.session_state.pagina_actual == "Apuesta Simple":
        render_apuesta_simple()
    else:
        render_en_construccion()

if __name__ == "__main__":
    main()
