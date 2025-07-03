"""
Classifier - Module de classification des poubelles pleines/vides

LOGIQUE GÉNÉRALE :
- Séparer scoring (rules_engine) et classification (ce module)
- Utiliser des seuils configurables pour transformer les scores en prédictions
- Gérer l'incertitude avec une catégorie "inconnu"
- Fournir des métriques de confiance pour évaluer la qualité des prédictions

ARCHITECTURE :
1. BinClassifier : Classe principale qui utilise RulesEngine + seuils
2. test_classifier() : Fonction pour évaluer les performances sur un dataset
3. Gestion des erreurs et analyse pour amélioration continue
"""

# backend/services/classifier.py

import json
import backend.config as config
from backend.services.feature_extractor import ImageFeatures
from backend.services.rules_engine import RulesEngine
from collections import Counter

# Configuration
CACHE_PATH = "cache/images_metadata_labeled.json"
# CACHE_PATH = config.CACHE_PATH  # Utiliser la configuration une fois le projet terminé


class BinClassifier:
    """
    Classificateur principal pour déterminer si une poubelle est pleine, vide ou incertaine
    
    LOGIQUE DE CONCEPTION :
    1. Utilise un RulesEngine pour obtenir un score [-1, +1]
    2. Applique des seuils pour convertir le score en classe
    3. Calcule une confiance basée sur la distance aux seuils
    4. Permet l'ajustement dynamique des seuils
    
    AVANTAGES :
    - Séparation claire entre scoring et classification
    - Gestion explicite de l'incertitude
    - Métriques de confiance pour filtrer les prédictions douteuses
    - Facilité d'ajustement des seuils selon le contexte d'usage
    """
    def __init__(self, rules_engine=None, thresholds=None):
        """
        Initialise le classificateur
        
        Args:
            rules_engine (RulesEngine): Moteur de règles personnalisé (optionnel)
            thresholds (dict): Seuils de classification personnalisés (optionnel)
            
        LOGIQUE DES SEUILS :
        - full_min : Score minimum pour être sûr que c'est "plein"
        - empty_max : Score maximum pour être sûr que c'est "vide"
        - Zone d'incertitude : entre empty_max et full_min
        - confidence_min : Seuil de confiance en dessous duquel on force "inconnu"
        """
        self.rules_engine = rules_engine or RulesEngine()
        self.thresholds = thresholds or {
            'full_min': 0.2,      # Score minimum pour "plein" (moins strict)
            'empty_max': -0.05,   # Score maximum pour "vide" (moins strict)
            'confidence_min': 0.1  # Confiance minimum (évite les prédictions hasardeuses)
        }
        
    def classify(self, features):
        """
        Classifie une image en fonction de ses features extraites
        
        LOGIQUE DE CLASSIFICATION :
        1. Obtenir un score normalisé [-1, +1] via le RulesEngine
        2. Appliquer les seuils pour déterminer la classe
        3. Calculer une confiance basée sur la distance aux seuils
        4. Appliquer un filtre de confiance minimum
        
        INTERPRÉTATION DES SCORES :
        - score >= full_min (ex: 0.3) → "plein" avec confiance = score
        - score <= empty_max (ex: -0.3) → "vide" avec confiance = |score|
        - entre les deux → "inconnu" (zone d'incertitude)
        - confiance < confidence_min → forcer "inconnu" (prédiction pas fiable)
        
        Args:
            features (dict): Features extraites de l'image (area_ratio, contrast, etc.)
            
        Returns:
            dict: {
                'prediction': str,        # 'plein', 'vide', ou 'inconnu'
                'confidence': float,      # Confiance [0, 1] dans la prédiction
                'score': float,          # Score brut du RulesEngine [-1, +1]
                'details': dict          # Détails de l'évaluation (règles actives, etc.)
            }
        """
        # Étape 1 : Évaluation avec le moteur de règles
        evaluation = self.rules_engine.evaluate(features)
        score = evaluation['score']  # Score normalisé [-1, +1]
        
        # Étape 2 : Classification basée sur les seuils
        if score >= self.thresholds['full_min']:
            # Score élevé = poubelle pleine
            prediction = "plein"
            confidence = min(score, 1.0)  # Confiance = proximité à +1
        elif score <= self.thresholds['empty_max']:
            # Score faible = poubelle vide
            prediction = "vide"
            confidence = min(abs(score), 1.0)  # Confiance = proximité à -1
        else:
            # Score dans la zone d'incertitude
            prediction = "inconnu"
            confidence = 1.0 - abs(score)  # Plus on est proche de 0, moins on est sûr
            
        # Étape 3 : Filtre de confiance minimum
        # Si la confiance est trop faible, forcer "inconnu" pour éviter les erreurs
        if confidence < self.thresholds['confidence_min']:
            prediction = "inconnu"
            
        return {
            'prediction': prediction,
            'confidence': confidence,
            'score': score,
            'details': evaluation
        }
    
    def set_thresholds(self, full_min=None, empty_max=None, confidence_min=None):
        """
        Ajuste les seuils de classification pour optimiser les performances
        
        UTILITÉ :
        - Adapter le comportement selon le contexte (tolérance aux erreurs)
        - Optimiser la précision après analyse des résultats
        - Expérimenter avec différents compromis précision/rappel
        
        Args:
            full_min (float): Seuil minimum pour "plein" (plus haut = plus strict)
            empty_max (float): Seuil maximum pour "vide" (plus bas = plus strict)  
            confidence_min (float): Confiance minimum requise (plus haut = plus d'"inconnu")
        """
        if full_min is not None:
            self.thresholds['full_min'] = full_min
        if empty_max is not None:
            self.thresholds['empty_max'] = empty_max
        if confidence_min is not None:
            self.thresholds['confidence_min'] = confidence_min


def test_classifier(cache_path=CACHE_PATH, show_details=False):
    """
    Fonction de test et d'évaluation du classifier sur un dataset labellisé
    
    OBJECTIFS :
    1. Mesurer la précision globale du système
    2. Analyser la répartition des prédictions (plein/vide/inconnu)
    3. Identifier les erreurs pour améliorer les règles
    4. Calculer des métriques de performance (confiance, scores)
    
    LOGIQUE D'ANALYSE :
    - Comparer prédictions vs labels réels
    - Tracker les règles impliquées dans les erreurs
    - Calculer précision avec et sans les "inconnu"
    - Statistiques des scores pour validation du système
    
    Args:
        cache_path (str): Chemin vers le fichier JSON des images labellisées
        show_details (bool): Afficher les détails des règles pour debug
        
    Returns:
        tuple: (classifier, accuracy) pour usage programmatique
    """
    # Initialisation du classifier avec paramètres par défaut
    classifier = BinClassifier()
    
    # Chargement du dataset labellisé depuis le cache JSON
    with open(cache_path, "r", encoding="utf-8") as f:
        images = json.load(f)

    # Initialisation des métriques de performance
    total = len(images)                                          # Nombre total d'images
    correct = 0                                                  # Prédictions correctes
    predictions_count = {"plein": 0, "vide": 0, "inconnu": 0}  # Répartition des prédictions
    scores = []                                                  # Scores pour analyse statistique
    confidences = []                                             # Niveaux de confiance
    errors_analysis = []                                         # Analyse détaillée des erreurs

    print("=== TEST DU CLASSIFIER MODERNE ===\n")
    
    # Boucle principale : tester chaque image du dataset
    for i, img in enumerate(images):
        # Récupération du label attendu (vérité terrain)
        annotation = img.get("annotation", [{}])[0]
        true_label = annotation.get("label", "inconnu")

        # Extraction des features visuelles de l'image
        feats = ImageFeatures(img).extract_all_features()
        
        # Classification avec notre système
        result = classifier.classify(feats)
        predicted = result['prediction']    # Classe prédite
        confidence = result['confidence']   # Confiance [0, 1]
        score = result['score']            # Score brut [-1, +1]
        
        # Mise à jour des statistiques globales
        predictions_count[predicted] += 1
        scores.append(score)
        confidences.append(confidence)
        
        # Affichage du résultat pour suivi en temps réel
        status = "✓" if predicted == true_label else "✗"  # Symbole visuel pour rapidité
        img_name = img.get('name_image', '')[:25]          # Nom tronqué pour lisibilité
        print(f"{status} {img_name:25} | {true_label:6} → {predicted:6} | Score: {score:+.3f} | Conf: {confidence:.3f}")
        
        # Évaluation de la prédiction et collecte des erreurs
        if predicted == true_label:
            correct += 1  # Compteur des prédictions correctes
        else:
            # Analyse détaillée des erreurs pour amélioration future
            errors_analysis.append({
                'image': img_name,
                'expected': true_label,
                'predicted': predicted,
                'score': score,
                'confidence': confidence,
                'active_rules': result['details']['active_rules']  # Règles qui ont influencé l'erreur
            })
            
        # Debug détaillé pour les premières images (optionnel)
        if show_details and i < 3:
            print(f"    Rules actives: {result['details']['active_rules']}")
            print(f"    Score brut: {result['details']['raw_score']:.2f}")
    
    # === CALCUL ET AFFICHAGE DES MÉTRIQUES FINALES ===
    
    print(f"\n=== RÉSULTATS FINAUX ===")
    print(f"Précision globale: {correct}/{total} = {correct/total:.2%}")
    print(f"Répartition: {predictions_count}")
    
    # Calcul de la précision en excluant les prédictions "inconnu"
    # LOGIQUE : Les "inconnu" ne sont ni vrais ni faux, on s'intéresse aux prédictions fermes
    definitive = total - predictions_count["inconnu"]
    if definitive > 0:
        # Compter les prédictions correctes parmi les prédictions définitives
        definitive_correct = sum(1 for err in errors_analysis if err['predicted'] != 'inconnu')
        definitive_correct = correct - (len(errors_analysis) - definitive_correct)
        definitive_accuracy = definitive_correct / definitive
        print(f"Précision sur prédictions définitives: {definitive_correct}/{definitive} = {definitive_accuracy:.2%}")
    
    # Statistiques des scores pour validation de la distribution
    if scores:
        print(f"\nStatistiques des scores:")
        print(f"  Moyenne: {sum(scores)/len(scores):+.3f}")        # Biais vers plein (+) ou vide (-)
        print(f"  Min: {min(scores):+.3f}, Max: {max(scores):+.3f}")  # Étendue des scores
        print(f"  Confiance moyenne: {sum(confidences)/len(confidences):.3f}")  # Fiabilité générale
    
    # Analyse des erreurs pour identifier les améliorations possibles
    if errors_analysis:
        print(f"\nAnalyse des erreurs ({len(errors_analysis)} erreurs):")
        error_rules = []  # Collecte des règles impliquées dans les erreurs
        
        # Affichage des erreurs les plus représentatives
        for err in errors_analysis[:5]:  # Limiter à 5 pour lisibilité
            print(f"  {err['image']:20} {err['expected']} → {err['predicted']} (score: {err['score']:+.3f})")
            error_rules.extend(err['active_rules'])  # Accumuler les règles problématiques
        
        # Identification des règles les plus souvent impliquées dans les erreurs
        # UTILITÉ : Permet d'identifier les règles à revoir/ajuster
        if error_rules:
            rule_counter = Counter(error_rules)
            print(f"\nRègles les plus impliquées dans les erreurs:")
            for rule, count in rule_counter.most_common(3):
                print(f"  {rule}: {count} fois")
                # CONSEIL : Examiner ces règles pour ajuster seuils ou poids
    
    return classifier, correct/total


# === POINT D'ENTRÉE PRINCIPAL ===
if __name__ == "__main__":
    """
    Exécution directe du module pour test rapide
    
    UTILISATION :
    - python backend/services/classifier.py
    - Ou depuis la racine : python -c "from backend.services.classifier import test_classifier; test_classifier()"
    
    CONSEIL : Utiliser show_details=True pour debug approfondi des règles
    """
    print("🚀 Test du classifier moderne...\n")
    classifier, accuracy = test_classifier(show_details=True)
    print(f"\n🎯 Accuracy finale: {accuracy:.2%}")
    
    # PROCHAINES ÉTAPES suggérées selon l'accuracy :
    if accuracy > 0.8:
        print("✅ Bonnes performances ! Considérer l'ajout de features avancées.")
    elif accuracy > 0.6:
        print("⚠️  Performances moyennes. Revoir les seuils et règles problématiques.")
    else:
        print("❌ Performances faibles. Revoir la logique des règles et les features.")