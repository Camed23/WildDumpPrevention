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
    dirty_ratios = []  # Pour statistiques

    wrong_prediction_rule = []  # Liste pour collecter les règles erronées
    for img in images:
        # Récupère le label attendu
        annotation = img.get("annotation", [{}])[0]
        true_label = annotation.get("label", "inconnu")

        # Extrait les features
        feats = ImageFeatures(img).extract_all_features()

        # Applique les règles
        dirty_ratio, rule_results = apply_rules(feats, all_rules)
        dirty_ratios.append(dirty_ratio)  # Pour statistiques
        
        # Classification basée sur le dirty_ratio
        if dirty_ratio >= 0.75:
            predicted = "plein"
        else:
            predicted = "vide"

        # Affiche le résultat pour debug
        print(f"{img.get('name_image', img.get('file_path')):30} | Attendu: {true_label:6} | Prédit: {predicted:6} | Dirty ratio: {dirty_ratio:.2f}")

        if predicted == true_label:
            correct += 1
        else:
            # Collecte les règles actives lors d'erreurs de classification
            active_rules = [all_rules[i].name for i, result in enumerate(rule_results) if result]
            wrong_prediction_rule.extend(active_rules)

    print(f"\nPrécision: {correct}/{total} = {correct/total:.2%}")
    
    # Statistiques sur les dirty ratios
    if dirty_ratios:
        avg_ratio = sum(dirty_ratios) / len(dirty_ratios)
        print(f"Dirty ratio moyen: {avg_ratio:.2f}")
        print(f"Dirty ratio min: {min(dirty_ratios):.2f}, max: {max(dirty_ratios):.2f}")

    # Compte et classe les règles actives lors des erreurs par fréquence
    if wrong_prediction_rule:
        rule_counter = Counter(wrong_prediction_rule)
        print("\nRègles les plus souvent impliquées dans les erreurs de classification :")
        for rule, count in rule_counter.most_common():
            print(f"  {rule}: {count} erreurs ({count/len(wrong_prediction_rule):.1%} des erreurs)")
    else:
        print("\nAucune erreur de classification détectée!")
    

if __name__ == "__main__":
    print(f"running classifier tests...\n")
    test_classifier()