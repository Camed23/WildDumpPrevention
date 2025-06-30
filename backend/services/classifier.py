# backend/services/classifier.py

from cache_manager import load_cache, initialize_cache
from feature_extractor import ImageFeatures
from rules_engine import apply_rules, all_rules

if __name__ == "__main__":
    # Exemple de liste d’images (à remplacer par la lecture d'un dossier)
    if load_cache() == None:
        initialize_cache()
    images = load_cache()


    for img_path in images:
        # 1. Extraire les features
        ext = ImageFeatures(img_path)
        feats = {
            "mean_brightness": ext.compute_mean_brightness(),
            "edge_density":  ext.compute_edge_density(),
            "area_ratio":    ext.compute_area_ratio()
        }

        # 2. Appliquer les règles
        result = apply_rules(feats, all_rules)

        # 3. Afficher le résultat
        print(f"{img_path} → {result}")
