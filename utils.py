import pandas as pd
from database import get_db_connection
import streamlit as st

def load_data():
    """Charge les données depuis la base de données"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM coinafrique_items")
            rows = cur.fetchall()
            # Récupération des noms de colonnes
            colnames = [desc[0] for desc in cur.description]
            cur.close()
            conn.close()
            return pd.DataFrame(rows, columns=colnames)
        except Exception as e:
            st.error(f"Erreur de chargement : {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def clean_dataframe(df):
    """
    Nettoie un DataFrame brut (issu d'un CSV Web Scraper) pour le rendre compatible
    avec notre Dashboard.
    """
    # Mapping des colonnes (basé sur le fichier CSV fourni)
    # CSV: Price, item_type, adress, image_link
    # DB: price, item_type, address, image_link
    
    # Renommage pour standardiser
    rename_map = {
        'Price': 'price',
        'adress': 'address',
        # item_type et image_link sont déjà bons
    }
    df = df.rename(columns=rename_map)
    
    # 1. Nettoyage du PRIX
    if 'price' in df.columns:
        # On convertit en string, on enlève 'CFA', 'FCFA', les espaces, etc.
        df['price_cleaned'] = df['price'].astype(str).str.replace('CFA', '', regex=False)
        df['price_cleaned'] = df['price_cleaned'].str.replace('FCFA', '', regex=False)
        df['price_cleaned'] = df['price_cleaned'].str.replace(' ', '', regex=False)
        # On ne garde que les chiffres (utilisation de raw string r'' pour la regex)
        df['price_cleaned'] = df['price_cleaned'].str.extract(r'(\d+)', expand=False)
        # On convertit en numérique, les erreurs (NaN) deviennent 0
        df['price_cleaned'] = pd.to_numeric(df['price_cleaned'], errors='coerce').fillna(0).astype(int)
    
    # 2. Nettoyage de l'ADRESSE
    if 'address' in df.columns:
        # Suppression de "location_on" et espaces
        df['address_cleaned'] = df['address'].astype(str).str.replace('location_on', '', regex=False).str.strip()
    
    return df
