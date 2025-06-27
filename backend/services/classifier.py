# backend/services/classifier.py

from feature_extractor import ImageFeatures
from rules_engine import apply_rules, rule_dark, rule_moyen

if __name__ == "__main__":
    # Exemple de liste d’images (à remplacer par la lecture d'un dossier)
    images = ["Data/train/with_label/clean/img1.jpg",
              "Data/train/with_label/dirty/img2.jpg"]

    for img_path in images:
        # 1. Extraire les features
        ext = ImageFeatures(img_path)
        feats = {
            "mean_brightness": ext.compute_mean_brightness(),
            "edge_density":  ext.compute_edge_density(),
            "area_ratio":    ext.compute_area_ratio()
        }

        # 2. Appliquer les règles
        result = apply_rules(feats, [rule_dark, rule_moyen])

        # 3. Afficher le résultat
        print(f"{img_path} → {result}")
