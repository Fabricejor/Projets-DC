import os
import psycopg2
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

def get_db_connection():
    """
    Établit une connexion à la base de données PostgreSQL en utilisant
    la variable d'environnement DATABASE_URL définie dans le fichier .env.
    """
    try:
        # Utilisation de la chaîne de connexion complète (DSN)
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("La variable d'environnement DATABASE_URL n'est pas définie.")
            
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return None

def create_tables():
    """
    Crée les tables nécessaires si elles n'existent pas déjà.
    Nous utilisons une seule table 'coinafrique_items' avec une colonne 'category'
    pour distinguer les types d'articles (vêtements homme, chaussures, etc.).
    """
    commands = (
        """
        CREATE TABLE IF NOT EXISTS coinafrique_items (
            id SERIAL PRIMARY KEY,
            category VARCHAR(100) NOT NULL,
            item_type VARCHAR(255),
            price VARCHAR(100),
            address VARCHAR(255),
            image_link TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
    )
    
    conn = get_db_connection()
    if conn is not None:
        try:
            cur = conn.cursor()
            # Exécuter chaque commande de création de table
            for command in commands:
                cur.execute(command)
            
            # Valider les changements
            conn.commit()
            cur.close()
            print("Vérification de la base de données terminée. Les tables sont prêtes.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Erreur lors de la création des tables : {error}")
        finally:
            if conn is not None:
                conn.close()
