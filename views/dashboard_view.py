import streamlit as st
import pandas as pd
from utils import load_data

def show_dashboard_page():
    st.subheader("Tableau de bord des données 📊")
    
    df = load_data()
    
    if not df.empty:
        # Conversion des prix en numérique
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
        
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
        
        # --- FONCTION DE RECHERCHE ---
        search_term = st.text_input("🔍 Rechercher dans le tableau (Titre, Adresse, Catégorie...)", "")
        
        # Filtrage du DataFrame
        if search_term:
            # On convertit tout en string et en minuscule pour une recherche insensible à la casse
            mask = df.apply(lambda x: x.astype(str).str.lower().str.contains(search_term.lower(), na=False)).any(axis=1)
            df_display = df[mask]
            st.caption(f"{len(df_display)} résultats trouvés pour '{search_term}'")
        else:
            df_display = df

        # Affichage du tableau (avec use_container_width pour prendre toute la largeur)
        st.dataframe(df_display, use_container_width=True)
        
    else:
        st.warning("Aucune donnée à afficher. Lancez d'abord le scraping !")
