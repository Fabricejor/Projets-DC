import streamlit as st
from database import create_tables

# Importation des vues
from views.scraper_view import show_scraper_page
from views.upload_view import show_upload_page
from views.dashboard_view import show_dashboard_page
from views.evaluation_view import show_evaluation_page

# --- CONFIGURATION PAGE ---
# set_page_config doit être la PREMIÈRE commande Streamlit
st.set_page_config(
    page_title="CoinAfrique Scraper",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CHARGEMENT DU CSS ---
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Fichier CSS non trouvé. Le style par défaut sera utilisé.")

local_css("assets/style.css")

# --- INITIALISATION ---
@st.cache_resource
def init_db():
    create_tables()

init_db()

# --- HEADER (En-tête principal) ---
# On utilise du HTML brut pour un design plus poussé
st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #007bff 0%, #00d2ff 100%); border-radius: 15px; margin-bottom: 2rem; color: white; box-shadow: 0 4px 15px rgba(0,123,255,0.3);">
        <h1 style="color: white; margin: 0; font-size: 3rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">🛍️ CoinAfrique Scraper</h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-top: 10px;">Analysez le marché de l'occasion au Sénégal en un clic</p>
    </div>
""", unsafe_allow_html=True)

# --- NAVIGATION (SIDEBAR) ---
with st.sidebar:
    # Logo ou Image
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png", width=60)
    
    st.markdown("### 🧭 Navigation")
    
    # Menu principal (Radio buttons stylisés par CSS)
    choice = st.radio(
        "Menu",
        ["Scraper", "Télécharger Données", "Dashboard", "Évaluation"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Section Info
    st.info("💡 **Astuce :** Utilisez le menu pour naviguer entre les fonctionnalités.")
    
    # Pied de page sidebar
    st.markdown("""
        <div style="position: fixed; bottom: 0; padding: 10px; font-size: 0.8rem; color: #6c757d;">
            Projet Data Collection 2026<br>
            Master DIT - IA
        </div>
    """, unsafe_allow_html=True)

# --- ROUTAGE ---
# On enveloppe le contenu dans un conteneur pour le centrer ou l'espacer si besoin
with st.container():
    if choice == "Scraper":
        show_scraper_page()

    elif choice == "Télécharger Données":
        show_upload_page()

    elif choice == "Dashboard":
        show_dashboard_page()

    elif choice == "Évaluation":
        show_evaluation_page()
