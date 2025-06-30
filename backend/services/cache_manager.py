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
        # Images qui ont au moins une annotation (jointure interne)
        resp = supabase.table(IMAGE_TABLE).select("*, annotation!inner(*)").execute()
    
    elif filter_type == "unlabeled":
        # Images qui n'ont AUCUNE annotation (LEFT JOIN puis filtrer sur NULL)
        resp = supabase.table(IMAGE_TABLE).select("*, annotation(*)").is_("annotation", "null").execute()
    
    else:  # filter_type == "all" ou autre valeur
        # Toutes les images avec leurs annotations éventuelles (jointure externe complète)
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

def load_cache(dataset_name=None, input_path=CACHE_PATH):
    """
    Charge le JSON existant et retourne la liste des métadonnées.
    - Si `dataset_name` est fourni, on cherchera dans le même dossier que CACHE_PATH
      un fichier nommé `<dataset_name>.json`.
    - Sinon on utilisera `input_path` (par défaut CACHE_PATH).
    """
    if dataset_name:
        cache_dir   = os.path.dirname(input_path)
        custom_path = os.path.join(cache_dir, f"{dataset_name}.json")
        input_path  = custom_path

    with open(input_path, "r", encoding="utf-8") as f:
        return json.load(f)
    

if __name__ == "__main__":
    """
    Si le script est exécuté directement, initialise le cache.
    """
    
    # supprime le cache précédent s'il existe
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)
        print("Cache précédent supprimé.")

    initialize_cache()