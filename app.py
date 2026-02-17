.import streamlit as st

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Betsson Pro: Dashboard", layout="wide")

# --- SIDEBAR: CONFIGURAZIONE E SIMULATORE ---
with st.sidebar:
    st.title("⚙️ Pannello di Controllo")
    
    # 1. Configurazione Numero Partite
    num_partite = st.number_input("Numero di eventi", min_value=2, max_value=13, value=3)
    st.divider()

    # 2. Simulatore (dentro la Sidebar)
    st.subheader("🎯 Simulatore Real-time")
    
    punti_indovinati = 0
    icone_risultati = []

    for i in range(num_partite):
        # Usiamo un layout più compatto per la sidebar
        st.markdown(f"**Evento {i+1}**")
        c1, c2 = st.columns(2)
        with c1:
            gl = st.number_input(f"L", min_value=0, step=1, key=f"side_gl_{i}")
        with c2:
            gv = st.number_input(f"V", min_value=0, step=1, key=f"side_gv_{i}")
        
        base_giocata = st.selectbox("Base", ["1", "X", "2"], key=f"side_base_{i}")
        
        # Logica di calcolo
        esito_reale = "1" if gl > gv else "2" if gl < gv else "X"
        
        if esito_reale == base_giocata:
            st.caption("✅ Preso")
            punti_indovinati += 1
            icone_risultati.append("🟢")
        else:
            st.caption("❌ Mancato")
            icone_risultati.append("🔴")
        st.divider()

# --- CORPO CENTRALE: RISULTATI E GRAFICI ---
st.title("📊 Analisi e Risultati del Sistema")

# Riga superiore con le statistiche principali (KPI)
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Eventi Totali", num_partite)
kpi2.metric("Basi Indovinate", f"{punti_indovinati} / {num_partite}")
kpi3.metric("Percentuale Successo", f"{(punti_indovinati/num_partite)*100:.1f}%")

st.markdown("---")

# Visualizzazione grafica del progresso
st.subheader("Progresso Serie")
st.title(" ".join(icone_risultati))

# Qui sotto lasceremo lo spazio per la "Tabla de Combinaciones"
st.subheader("📈 2. Tabla de Combinaciones y Ganancias")
st.info("Qui verranno visualizzati i calcoli di itertools basati sulle tue quote.")
