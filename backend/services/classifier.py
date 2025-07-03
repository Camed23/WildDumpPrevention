# backend/services/classifier.py - Version ultra simple pour tests

import json
import backend.config as config
from backend.services.feature_extractor import ImageFeatures
from backend.services.rules_engine import all_rules, apply_rules
from collections import Counter

#  À MODIFIER POUR TES TESTS
CACHE_PATH = "cache/images_metadata_labeled.json"  # dataset à tester via le cache; mettre en place plus tard la récupération depuis la base de données si le cache n'existe pas
# CACHE_PATH = config.CACHE_PATH  # Chemin du cache des données extraites défini dans la configuration (.env)

def test_classifier(cache_path=CACHE_PATH):
    # Charge le cache
    with open(cache_path, "r", encoding="utf-8") as f:
        images = json.load(f)

    total = len(images)  # Nombre total d'images
    correct = 0

    wrong_prediction_rule = []  # Liste pour collecter les règles erronées
    for img in images:
        # Récupère le label attendu
        annotation = img.get("annotation", [{}])[0]
        true_label = annotation.get("label", "inconnu")

        # Extrait les features
        feats = ImageFeatures(img).extract_all_features()

        # Applique les règles
        rule = apply_rules(feats, all_rules)
        if "dirty" in rule:
            predicted = "plein"
        elif "clean" in rule:
            predicted = "vide"
        else:
            predicted = "inconnu"

        # Affiche le résultat pour debug
        print(f"{img.get('name_image', img.get('file_path')):30} | Attendu: {true_label:6} | Prédit: {predicted:6} | Règle: {rule}")


        

        if predicted == true_label:
            correct += 1
        else:
            # Collecte les features qui ont conduit à une mauvaise prédiction
            wrong_prediction_rule.append(rule)

    print(f"\nPrécision: {correct}/{total} = {correct/total:.2%}")

    # Compte et classe les règles erronées par fréquence
    rule_counter = Counter(wrong_prediction_rule)
    print("\nRègles erronées les plus fréquentes :")
    print(rule_counter)
    

if __name__ == "__main__":
    print(f"running classifier tests...\n")
    test_classifier()