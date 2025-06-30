# backend/services/cache_manager.py

import os
import json
from backend.config import IMAGE_TABLE, CACHE_PATH, supabase

IMAGE_TABLE = IMAGE_TABLE    
CACHE_PATH  = CACHE_PATH
supabase = supabase

def initialize_cache(output_path=CACHE_PATH, filter_type="all"):
    """
    Appelle un SELECT sur la table image et dump le résultat dans un JSON.
    À lancer UNE SEULE FOIS pour créer ou recréer le cache.
    
    Args:
        output_path (str): Chemin de sortie du fichier cache JSON
        filter_type (str): Type de filtrage des images:
            - "all": Toutes les images (par défaut)
            - "labeled": Uniquement les images avec un label ('plein' ou 'vide')
            - "unlabeled": Uniquement les images sans label
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if filter_type == "labeled":
        # Images qui ont au moins une annotation avec un label défini
        resp = supabase.table(IMAGE_TABLE).select("*, annotation(*)").not_.is_("annotation.label", "null").execute()
    elif filter_type == "unlabeled":
        # Images qui n'ont aucune annotation avec label OU qui ont des annotations sans label
        resp = supabase.table(IMAGE_TABLE).select("*, annotation(*)").is_("annotation.label", "null").execute()
    else:  # filter_type == "all" ou autre valeur
        # Toutes les images avec leurs annotations éventuelles
        resp = supabase.table(IMAGE_TABLE).select("*, annotation(*)").execute()
    
    data = resp.data
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    filter_msg = {
        "labeled": "images labélisées (avec annotation 'plein'/'vide')",
        "unlabeled": "images non labélisées (sans annotation de label)", 
        "all": "toutes les images"
    }.get(filter_type, "toutes les images")
    
    print(f"✅ Cache généré ({len(data)} entrées - {filter_msg}) dans : {output_path}")

def load_cache(input_path=CACHE_PATH):
    """
    Charge le JSON existant et retourne la liste des métadonnées.
    Ne touche pas à la base, ne fait qu’un simple open().
    """
    with open(input_path, "r") as f:
        return json.load(f)
    

if __name__ == "__main__":
    """
    Si le script est exécuté directement, initialise le cache.
    """
    
    # supprime le cache précédent s'il existe
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)
        print("Cache précédent supprimé.")

    initialize_cache(CACHE_PATH,"labeled")
    print("Cache initialisé avec succès.")
