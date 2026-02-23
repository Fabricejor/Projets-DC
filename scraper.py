import requests
from bs4 import BeautifulSoup
import time
from database import get_db_connection
import sys

def scrape_coinafrique(category_url, category_name, max_pages=1):
    """
    Scrape les données d'une catégorie spécifique sur CoinAfrique.
    """
    print(f"Début du scraping pour la catégorie : {category_name}")
    sys.stdout.flush()
    
    conn = get_db_connection()
    if not conn:
        print("Impossible de se connecter à la base de données. Abandon.")
        return

    cur = conn.cursor()
    
    total_added = 0
    
    for page in range(1, max_pages + 1):
        url = f"{category_url}?page={page}"
        print(f"Scraping page {page} : {url}")
        sys.stdout.flush()
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print(f"Erreur lors de la requête : {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            ads = soup.find_all('div', class_='col s6 m4 l3')
            if not ads:
                 ads = soup.find_all('div', class_='card-ad')

            if not ads:
                print("Aucune annonce trouvée sur cette page.")
                break
            
            page_added_count = 0
            for ad in ads:
                try:
                    # Extraction des données
                    title_elem = ad.find('p', class_='ad__card-description')
                    item_type = title_elem.text.strip() if title_elem else "N/A"
                    
                    price_elem = ad.find('p', class_='ad__card-price')
                    price_text = price_elem.text.strip().replace('CFA', '').replace(' ', '') if price_elem else "0"
                    price_clean = ''.join(filter(str.isdigit, price_text))
                    price = int(price_clean) if price_clean else 0
                        
                    address_elem = ad.find('p', class_='ad__card-location')
                    address = address_elem.text.strip().replace('location_on', '') if address_elem else "N/A"
                    
                    img_elem = ad.find('img', class_='ad__card-img')
                    image_link = img_elem['src'] if img_elem and 'src' in img_elem.attrs else "N/A"
                    
                    # --- VÉRIFICATION DES DOUBLONS ---
                    # On vérifie si ce lien d'image existe déjà dans la base
                    cur.execute("SELECT id FROM coinafrique_items WHERE image_link = %s", (image_link,))
                    if cur.fetchone():
                        # L'annonce existe déjà, on passe à la suivante
                        continue

                    # Insertion si pas de doublon
                    cur.execute(
                        """
                        INSERT INTO coinafrique_items (category, item_type, price, address, image_link)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (category_name, item_type, str(price), address, image_link)
                    )
                    page_added_count += 1
                    total_added += 1
                    
                except Exception as e:
                    print(f"Erreur lors du traitement d'une annonce : {e}")
                    continue
            
            conn.commit()
            print(f"{page_added_count} nouvelles annonces ajoutées pour la page {page}.")
            
            time.sleep(1) # Pause courte
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête sur la page {page} : {e}")
        except Exception as e:
            print(f"Erreur générale sur la page {page} : {e}")

    cur.close()
    conn.close()
    print(f"Fin du scraping pour {category_name}. Total ajouté : {total_added}")
    return total_added

def scrape_all_categories(max_pages_per_category=2):
    """
    Lance le scraping pour toutes les catégories demandées dans le projet.
    """
    categories = [
        ("https://sn.coinafrique.com/categorie/vetements-homme", "Vêtements Homme"),
        ("https://sn.coinafrique.com/categorie/chaussures-homme", "Chaussures Homme"),
        ("https://sn.coinafrique.com/categorie/vetements-enfants", "Vêtements Enfants"),
        ("https://sn.coinafrique.com/categorie/chaussures-enfants", "Chaussures Enfants")
    ]
    
    total_global = 0
    for url, name in categories:
        total_global += scrape_coinafrique(url, name, max_pages=max_pages_per_category)
        
    return total_global

if __name__ == "__main__":
    # Test local
    scrape_all_categories(max_pages_per_category=1)
