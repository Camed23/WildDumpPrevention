# backend/services/cache_manager.py

import os
import json
import backend.config as config
from Data.init_db import supabase            

IMAGE_TABLE = config.IMAGE_TABLE
CACHE_PATH  = config.CACHE_PATH

def initialize_cache(output_path=CACHE_PATH):
    """
    Appelle un SELECT * sur la table image et dump le résultat dans un JSON.
    À lancer UNE SEULE FOIS pour créer ou recréer le cache.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    resp = supabase.table(IMAGE_TABLE).select("*").execute()
    data = resp.data
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Cache généré ({len(data)} entrées) dans : {output_path}")

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
    initialize_cache(CACHE_PATH)
    print("Cache initialisé avec succès.")
