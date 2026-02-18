# --- NAVBAR NELLA SIDEBAR ---
st.sidebar.header("🧭 Navigazione")
menu = st.sidebar.radio(
    "Seleziona Visualizzazione:",
    ["1. Configura Partite", "2. Tabella Combinazioni", "3. Simulatore Risultati"]
)

st.sidebar.divider()

# --- RE-ORGANIZZAZIONE DELLE SEZIONI ---

# --- SEZIONE 1: CONFIGURAZIONE (PAGINA PRINCIPALE) ---
if menu == "1. Configura Partite":
    st.subheader("1. Definizione Partite e Quote")
    # ... Qui inseriamo il loop dei match che abbiamo creato prima ...
    for i in range(num_p):
        with st.expander(f"🏟️ MATCH {i+1}", expanded=True):
            # Riga 1: Team
            c_loc, c_vs, c_vis = st.columns([10, 1, 10])
            loc = c_loc.text_input("Local", key=f"l_{i}", value=f"Local {i+1}", label_visibility="collapsed")
            c_vs.markdown("<div style='text-align: center; padding-top: 5px;'>vs</div>", unsafe_allow_html=True)
            vis = c_vis.text_input("Visitante", key=f"v_{i}", value=f"Visitante {i+1}", label_visibility="collapsed")
            
            # Riga 2: Quote e Base
            q1_c, qx_c, q2_c, space, base_c = st.columns([1, 1, 1, 0.5, 2])
            # (Codice delle quote come visto prima...)
            # ... (Logica d_q e col_base.append)
            
# --- SEZIONE 2: TABELLA (PAGINA PRINCIPALE) ---
elif menu == "2. Tabella Combinaciones":
    st.subheader("2. Analisi del Sistema")
    
    if st.button("🚀 Calcola / Aggiorna Sistema", type="primary"):
        # Logica genera_sistema...
        df_sistema = genera_sistema(col_base, err_max, matriz_cuotas, apuesta_col, opciones)
        st.session_state["ultimo_sistema"] = df_sistema
        # ... calcolo spesa_totale ...

    if "ultimo_sistema" in st.session_state:
        # Visualizzazione tabella a tutta pagina
        st.dataframe(st.session_state["ultimo_sistema"], use_container_width=True)

# --- SEZIONE 3: SIMULATORE (PAGINA PRINCIPALE) ---
elif menu == "3. Simulatore Risultati":
    st.subheader("3. Simulatore Risultati Reali")
    # Inseriamo il layout orizzontale che ti ho dato nell'ultimo passaggio
    for i in range(num_p):
        c1, c2, c3, c4, c5, c6 = st.columns([3, 1, 0.5, 1, 3, 1.5])
        # (Codice del simulatore con nomi squadre e input gol...)
