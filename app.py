import streamlit as st
import pandas as pd
from database import create_tables, get_db_connection
from scraper import scrape_all_categories

# Initialisation de la base de données au démarrage
create_tables()

st.set_page_config(page_title="CoinAfrique Scraper", layout="wide")

st.title("Projet 2 : CoinAfrique Scraper 🛍️")

# Sidebar
st.sidebar.header("Menu")
menu = ["Scraper", "Télécharger Données", "Dashboard", "Évaluation"]
choice = st.sidebar.selectbox("Choisissez une option", menu)

# --- FONCTIONS UTILITAIRES ---
def load_data():
    """Charge les données depuis la base de données"""
    conn = get_db_connection()
    if conn:
        query = "SELECT * FROM coinafrique_items"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return pd.DataFrame()

# --- PAGES ---

if choice == "Scraper":
    st.subheader("Scraper les données en direct")
    st.markdown("""
    Cette section permet de lancer le robot de collecte sur les 4 catégories :
    - Vêtements Homme
    - Chaussures Homme
    - Vêtements Enfants
    - Chaussures Enfants
    """)
    
    nb_pages = st.slider("Nombre de pages à scraper par catégorie", min_value=1, max_value=5, value=1)
    
    if st.button("Lancer le Scraping 🚀"):
        with st.spinner('Le robot est au travail... Veuillez patienter.'):
            # On lance le scraping
            try:
                # On utilise une fonction wrapper pour capturer la sortie ou juste lancer
                # Ici on appelle directement la fonction importée
                scrape_all_categories(max_pages_per_category=nb_pages)
                st.success("Scraping terminé avec succès !")
                st.balloons()
            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")
        
    st.divider()
    st.write("### Aperçu des données actuelles en base")
    df = load_data()
    if not df.empty:
        st.dataframe(df.tail(10)) # Affiche les 10 derniers éléments
        st.write(f"Total d'annonces en base : **{len(df)}**")
    else:
        st.info("La base de données est vide pour le moment.")


elif choice == "Télécharger Données":
    st.subheader("Télécharger des données brutes (Web Scraper)")
    st.info("Fonctionnalité à venir : Upload de fichier CSV issu de l'extension Web Scraper.")
    
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")
    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            st.write("Aperçu du fichier :")
            st.dataframe(df_upload.head())
            # Ici on pourrait ajouter la logique pour nettoyer et insérer en base
        except Exception as e:
            st.error(f"Erreur de lecture du fichier : {e}")

elif choice == "Dashboard":
    st.subheader("Tableau de bord des données 📊")
    
    df = load_data()
    
    if not df.empty:
        # Conversion des prix en numérique si ce n'est pas déjà le cas (pandas le fait souvent auto via read_sql mais on assure)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        # Métriques principales
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Annonces", len(df))
        col2.metric("Prix Moyen", f"{int(df['price'].mean()):,} CFA")
        col3.metric("Catégories", df['category'].nunique())
        
        st.divider()
        
        # Graphiques
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.write("### Répartition par Catégorie")
            st.bar_chart(df['category'].value_counts())
            
        with col_chart2:
            st.write("### Top 10 des Adresses")
            st.bar_chart(df['address'].value_counts().head(10))
            
        st.write("### Données détaillées")
        st.dataframe(df)
        
    else:
        st.warning("Aucune donnée à afficher. Lancez d'abord le scraping !")

elif choice == "Évaluation":
    st.subheader("Évaluation de l'application")
    st.markdown("""
    Merci d'utiliser notre application ! Votre avis compte.
    
    👉 [Cliquez ici pour remplir le formulaire d'évaluation](https://docs.google.com/forms/d/e/1FAIpQLSdtNF46c-avvx4SnWwlrVxYN4z_Gap6Y7PK8hv8MdXM9o-nzA/viewform?usp=publish-editor)
    """)
