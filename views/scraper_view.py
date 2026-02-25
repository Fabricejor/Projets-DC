import streamlit as st
from scraper import scrape_all_categories
from utils import load_data

def show_scraper_page():
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
            try:
                total = scrape_all_categories(max_pages_per_category=nb_pages)
                st.success(f"Scraping terminé ! {total} nouvelles annonces ajoutées.")
                st.balloons()
            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")
        
    st.divider()
    st.write("### Aperçu des données actuelles en base")
    
    df = load_data()
    if not df.empty:
        # --- FONCTION DE RECHERCHE ---
        search_term = st.text_input("🔍 Rechercher dans l'aperçu", "")
        
        if search_term:
            # Filtrage simple insensible à la casse
            mask = df.apply(lambda x: x.astype(str).str.lower().str.contains(search_term.lower(), na=False)).any(axis=1)
            df_display = df[mask]
        else:
            df_display = df

        # On affiche les 10 derniers éléments DU FILTRE, ou du total si pas de filtre
        st.dataframe(df_display.tail(10), use_container_width=True)
        st.write(f"Total d'annonces en base : **{len(df)}**")
    else:
        st.info("La base de données est vide pour le moment.")
