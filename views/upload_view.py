import streamlit as st
import pandas as pd
from utils import clean_dataframe
from database import get_db_connection

def show_upload_page():
    st.subheader("Télécharger des données brutes (Web Scraper)")
    st.markdown("""
    Ici, vous pouvez uploader un fichier CSV généré par l'extension **Web Scraper**.
    L'application va nettoyer les données (supprimer 'CFA', 'location_on', etc.) et vous montrer le résultat.
    """)
    
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type="csv")
    
    if uploaded_file is not None:
        try:
            # Lecture du fichier
            df_upload = pd.read_csv(uploaded_file)
            
            st.write("### 1. Données Brutes (Avant nettoyage)")
            st.dataframe(df_upload.head())
            
            # Bouton pour nettoyer
            if st.button("Nettoyer et Analyser 🧹"):
                df_clean = clean_dataframe(df_upload)
                # On stocke le résultat dans la session pour qu'il ne disparaisse pas au prochain clic
                st.session_state['df_clean'] = df_clean
                st.success("Nettoyage effectué ! Vous pouvez maintenant sauvegarder.")

            # Si on a des données nettoyées en mémoire, on affiche la suite
            if 'df_clean' in st.session_state:
                df_clean = st.session_state['df_clean']
                
                st.write("### 2. Données Nettoyées")
                st.dataframe(df_clean.head())
                
                st.write("### 3. Statistiques Rapides du Fichier")
                col1, col2 = st.columns(2)
                if 'price_cleaned' in df_clean.columns:
                    avg_price = df_clean['price_cleaned'].mean()
                    col1.metric("Prix Moyen (Fichier)", f"{int(avg_price):,} CFA")
                
                col2.metric("Nombre d'annonces", len(df_clean))
                
                # Optionnel : Sauvegarder en base
                st.write("### 4. Sauvegarde")
                
                # On utilise un formulaire pour éviter le rechargement intempestif
                # Le formulaire permet de grouper l'action et d'éviter que le bouton ne reset l'état trop vite
                with st.form("save_form"):
                    st.write("Confirmez-vous l'ajout de ces données à la base ?")
                    submit_save = st.form_submit_button("Ajouter ces données à la Base de Données 💾")
                    
                    if submit_save:
                        conn = get_db_connection()
                        if conn:
                            cur = conn.cursor()
                            count = 0
                            duplicates = 0
                            
                            # On ne peut pas facilement mettre une progress bar DANS un form submit sans ruser,
                            # mais on peut afficher un spinner
                            with st.spinner("Sauvegarde en cours..."):
                                for index, row in df_clean.iterrows():
                                    # Mapping des colonnes
                                    price_val = str(row.get('price_cleaned', 0))
                                    address_val = row.get('address_cleaned', row.get('address', 'Inconnu'))
                                    image_link_val = row.get('image_link', '')
                                    item_type_val = row.get('item_type', 'Inconnu')
                                    
                                    category_val = "Import CSV"
                                    if 'web_scraper_start_url' in row:
                                        url_str = str(row['web_scraper_start_url'])
                                        if 'chaussures-homme' in url_str:
                                            category_val = "Chaussures Homme"
                                        elif 'vetements-homme' in url_str:
                                            category_val = "Vêtements Homme"
                                        elif 'chaussures-enfants' in url_str:
                                            category_val = "Chaussures Enfants"
                                        elif 'vetements-enfants' in url_str:
                                            category_val = "Vêtements Enfants"

                                    try:
                                        # Vérification doublon image
                                        cur.execute("SELECT id FROM coinafrique_items WHERE image_link = %s", (image_link_val,))
                                        if cur.fetchone():
                                            duplicates += 1
                                            continue

                                        cur.execute(
                                            """
                                            INSERT INTO coinafrique_items (category, item_type, price, address, image_link)
                                            VALUES (%s, %s, %s, %s, %s)
                                            """,
                                            (category_val, item_type_val, price_val, address_val, image_link_val)
                                        )
                                        count += 1
                                    except Exception as e:
                                        st.error(f"Erreur insertion ligne {index}: {e}")
                                        continue
                                
                                conn.commit()
                                cur.close()
                                conn.close()
                            
                            st.success(f"Opération terminée ! {count} annonces ajoutées. {duplicates} doublons ignorés.")
                            # On garde le df_clean en session pour voir le résultat, ou on l'enlève si on veut forcer un reload
                            # del st.session_state['df_clean'] 

        except Exception as e:
            st.error(f"Erreur de lecture du fichier : {e}")
