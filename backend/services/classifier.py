"""
Classifier - Module de classification binaire des poubelles pleines/vides

LOGIQUE GÉNÉRALE :
- Séparer scoring (rules_engine) et classification (ce module)
- Utiliser des seuils configurables pour transformer les scores en prédictions
- Classification binaire forcée : "plein" ou "vide" uniquement (plus d'"inconnu")
- Fournir des métriques de confiance pour évaluer la qualité des prédictions

ARCHITECTURE :
1. BinClassifier : Classe principale qui utilise RulesEngine + décision binaire
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
#CACHE_PATH = "cache/images_metadata_labeled.json"
CACHE_PATH = config.CACHE_PATH  # Utiliser la configuration une fois le projet terminé


class BinClassifier:
    """
    Classificateur principal pour déterminer si une poubelle est pleine ou vide (classification binaire)
    
    LOGIQUE DE CONCEPTION :
    1. Utilise un RulesEngine pour obtenir un score [-1, +1]
    2. Applique une décision binaire simple : score >= 0 → "plein", score < 0 → "vide"
    3. Calcule une confiance basée sur l'amplitude du score et la cohérence des règles
    4. Permet l'ajustement dynamique des seuils
    5. **NOUVEAU**: Plus de catégorie "inconnu" - toujours une décision ferme
    
    AVANTAGES :
    - Séparation claire entre scoring et classification
    - Décision binaire forcée pour éviter l'indécision
    - Métriques de confiance pour évaluer la fiabilité
    - Facilité d'ajustement des paramètres selon le contexte d'usage
    - Exploitation optimale des règles avancées
    """
    def __init__(self, rules_engine=None, thresholds=None, high_precision=False):
        """
        Initialise le classificateur
        
        Args:
            rules_engine (RulesEngine): Moteur de règles personnalisé (optionnel)
            thresholds (dict): Seuils de classification personnalisés (optionnel)
            high_precision (bool): Active le mode haute précision (plus strict, plus de règles)
            
        LOGIQUE DES SEUILS :
        - full_min : Score minimum pour être sûr que c'est "plein"
        - empty_max : Score maximum pour être sûr que c'est "vide"
        - Zone d'incertitude : entre empty_max et full_min
        - confidence_min : Seuil de confiance en dessous duquel on force "inconnu"
        - rules_count_min : Nombre minimum de règles actives pour une confiance élevée
        - advanced_rules_bonus : Bonus de confiance si des règles avancées sont actives
        """
        self.rules_engine = rules_engine or RulesEngine()
        self.high_precision = high_precision
        
        # Seuils recalibrés pour équilibrer les prédictions entre "plein" et "vide"
        base_thresholds = {
            'full_min': 0.20 if high_precision else 0.15,      # ABAISSÉ pour faciliter la détection "plein"
            'empty_max': -0.2 if high_precision else -0.15,    # RENDU PLUS STRICT pour "vide" 
            'confidence_min': 0.15 if high_precision else 0.12, # ABAISSÉ pour réduire les "inconnu"
            'rules_count_min': 5 if high_precision else 4,      # Légèrement réduit
            'advanced_rules_bonus': 0.1,                        # AUGMENTÉ pour valoriser les règles avancées
            'negative_rules_min': 3 if high_precision else 2    # Inchangé
        }
        
        # Utiliser les seuils fournis ou les valeurs par défaut
        self.thresholds = thresholds or base_thresholds
        
        # Liste des règles avancées pour le bonus de confiance
        self.advanced_rules = [
            'texture_entropy_high', 'texture_entropy_low',
            'color_complexity_high', 'color_complexity_low',
            'brightness_variance_high', 'brightness_variance_low',
            'spatial_frequency_high', 'spatial_frequency_low',
            'fill_ratio_advanced_high', 'fill_ratio_advanced_low',
            'red_blue_ratio_high', 'saturation_high',
            'corner_variance_high', 'vertical_fill_high',
            'irregular_shapes_high', 'symmetry_high',
            'background_uniformity_high', 'center_emptiness_high',
            'vertical_fill_low', 'perspective_lines_visible'
        ]
        
    def classify(self, features):
        """
        Classifie une image en fonction de ses features extraites
        
        LOGIQUE DE CLASSIFICATION AMÉLIORÉE :
        1. Obtenir un score normalisé [-1, +1] via le RulesEngine
        2. Calculer le ratio de règles positives vs négatives
        3. Vérifier si le score et le ratio de règles sont cohérents
        4. Appliquer une logique plus stricte pour la classe "plein"
        5. Calculer une confiance en tenant compte du ratio de règles
        6. Filtrer les prédictions à faible confiance
        
        STRATÉGIE DE DÉCISION BINAIRE (SANS "INCONNU") :
        - "plein" : score >= 0 (positif ou neutre)
        - "vide" : score < 0 (négatif)
        - Confiance calculée selon l'amplitude du score et la cohérence des règles
        
        Args:
            features (dict): Features extraites de l'image (area_ratio, contrast, etc.)
            
        Returns:
            dict: {
                'prediction': str,          # 'plein' ou 'vide' uniquement
                'confidence': float,        # Confiance [0, 1] dans la prédiction
                'score': float,             # Score brut du RulesEngine [-1, +1]
                'details': dict,            # Détails de l'évaluation (règles actives, etc.)
                'advanced_rules': list,     # Liste des règles avancées actives
                'positive_rules_count': int, # Nombre de règles positives activées
                'negative_rules_count': int, # Nombre de règles négatives activées
                'rules_ratio': float        # Ratio règles positives/négatives
            }
        """
        # Étape 1 : Évaluation avec le moteur de règles
        evaluation = self.rules_engine.evaluate(features)
        score = evaluation['score']  # Score normalisé [-1, +1]
        active_rules = evaluation.get('active_rules', [])
        raw_score = evaluation.get('raw_score', 0)
        
        # Étape 2 : Analyse des règles actives par type
        # Liste des règles négatives (vide) connues - rendue plus précise et exhaustive
        negative_rule_prefixes = (
            'area_ratio_low', 'hue_std_low', 'contrast_iqr_low', 'edge_density_high', 
            'mean_brightness_high', 'texture_entropy_low', 'color_complexity_low', 
            'brightness_variance_low', 'spatial_frequency_low', 'fill_ratio_advanced_low', 
            'spatial_frequency_very_low', 'file_size_low', 'edge_coherence_high', 
            'symmetry_high', 'background_uniformity_high', 'center_emptiness_high', 
            'vertical_fill_low', 'perspective_lines_visible', 'edge_density_low', 
            'very_empty_center', 'structural_symmetry_with_edges', 'uniform_brightness',
            'corner_variance_low'
        )
        
        # Compter les règles négatives et positives de manière plus robuste
        negative_rules = [rule for rule in active_rules if any(rule.startswith(prefix) for prefix in negative_rule_prefixes)]
        positive_rules = [rule for rule in active_rules if rule not in negative_rules]
        
        # Calculer le ratio de règles (éviter division par zéro)
        pos_count = len(positive_rules)
        neg_count = len(negative_rules)
        rules_ratio = pos_count / max(1, neg_count)
        
        # Étape 3 : Classification binaire forcée (plus de label "inconnu")
        # Logique simplifiée : décision basée principalement sur le score
        if score >= 0:
            # Score positif ou neutre → tendance "plein"
            prediction = "plein"
            # Confiance basée sur le score et renforcée par le ratio de règles
            base_confidence = min(abs(score) * 1.5 + 0.3, 1.0)  # Score minimum de confiance : 0.3
            rules_bonus = min(rules_ratio / 4.0, 0.3) if rules_ratio >= 1.0 else 0  # Bonus si ratio favorable
            confidence = min(base_confidence + rules_bonus, 1.0)
            
        else:
            # Score négatif → tendance "vide"  
            prediction = "vide"
            # Confiance basée sur l'amplitude du score négatif et le nombre de règles négatives
            base_confidence = min(abs(score) * 1.5 + 0.3, 1.0)  # Score minimum de confiance : 0.3
            neg_bonus = min(neg_count / 5.0, 0.3) if neg_count >= 2 else 0  # Bonus si suffisamment de règles négatives
            confidence = min(base_confidence + neg_bonus, 1.0)
            
        # Étape 4 : Ajustement de confiance basé sur les règles avancées
        # Identifier les règles avancées actives
        advanced_active = [rule for rule in active_rules if rule in self.advanced_rules]
        # Étape 4 : Ajustements basés sur les règles avancées spécifiques
        if len(advanced_active) > 0:
                # Règles spécifiques à la classe pleine
                if prediction == "plein":
                    # Vérifier la présence de règles avancées vraiment discriminantes pour "plein"
                    critical_full_rules = ['fill_ratio_advanced_high', 'vertical_fill_high', 'irregular_shapes_high']
                    critical_count = len([r for r in advanced_active if r in critical_full_rules])
                    
                    if critical_count > 0:
                        # Bonus si des règles critiques sont présentes
                        bonus = min(critical_count / len(critical_full_rules), 1.0) * 0.3
                        confidence = min(confidence + bonus, 1.0)
                    else:
                        # Pénalité si aucune règle critique n'est présente
                        confidence *= 0.7
                        
                    # Vérifier qu'il n'y a pas trop de règles contradictoires
                    contradictory_rules = ['symmetry_high', 'background_uniformity_high', 'center_emptiness_high']
                    contradictory_count = len([r for r in advanced_active if r in contradictory_rules])
                    
                    if contradictory_count > 0:
                        # Forte pénalité si des règles contradictoires sont présentes
                        confidence *= (1.0 - contradictory_count * 0.2)
                
                # Règles spécifiques à la classe vide
                elif prediction == "vide":
                    # Vérifier la présence de règles avancées vraiment discriminantes pour "vide"
                    critical_empty_rules = ['symmetry_high', 'background_uniformity_high', 'center_emptiness_high', 'vertical_fill_low']
                    critical_count = len([r for r in advanced_active if r in critical_empty_rules])
                    
                    if critical_count > 0:
                        # Bonus si des règles critiques sont présentes
                        bonus = min(critical_count / len(critical_empty_rules), 1.0) * 0.3
                        confidence = min(confidence + bonus, 1.0)
                    else:
                        # Pénalité si aucune règle critique n'est présente
                        confidence *= 0.7
        
        # Étape 5 : Malus de confiance si trop peu de règles sont actives au total
        min_total_rules = self.thresholds['rules_count_min']
        if len(active_rules) < min_total_rules:
            confidence *= (len(active_rules) / min_total_rules) * 0.9  # Moins pénalisant qu'avant
        
        # Plus de filtrage par confiance minimum ni de vérifications supplémentaires
        # qui forceraient vers "inconnu" - on garde toujours la prédiction binaire
            
        return {
            'prediction': prediction,
            'confidence': confidence,
            'score': score,
            'details': evaluation,
            'advanced_rules': advanced_active,
            'positive_rules_count': len(positive_rules),
            'negative_rules_count': len(negative_rules)
        }
    
    def set_thresholds(self, full_min=None, empty_max=None, confidence_min=None, 
                      rules_count_min=None, advanced_rules_bonus=None, negative_rules_min=None):
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
            rules_count_min (int): Nombre minimum de règles actives pour confiance élevée
            advanced_rules_bonus (float): Bonus de confiance pour les règles avancées
            negative_rules_min (int): Nombre minimum de règles négatives pour classer "vide"
        """
        if full_min is not None:
            self.thresholds['full_min'] = full_min
        if empty_max is not None:
            self.thresholds['empty_max'] = empty_max
        if confidence_min is not None:
            self.thresholds['confidence_min'] = confidence_min
        if rules_count_min is not None:
            self.thresholds['rules_count_min'] = rules_count_min
        if advanced_rules_bonus is not None:
            self.thresholds['advanced_rules_bonus'] = advanced_rules_bonus
        if negative_rules_min is not None:
            self.thresholds['negative_rules_min'] = negative_rules_min
            
    def set_high_precision(self, enabled=True):
        """
        Active ou désactive le mode haute précision
        
        UTILITÉ :
        - Quand la précision est critique, utiliser enabled=True
        - Pour maximiser les prédictions définitives, utiliser enabled=False
        
        Args:
            enabled (bool): True pour activer le mode haute précision
        """
        self.high_precision = enabled
        
        # Ajuster les seuils selon le mode - nettement recalibrés
        if enabled:
            self.set_thresholds(
                full_min=0.35,              # Beaucoup plus strict pour "plein"
                empty_max=-0.1,             # Plus permissif pour "vide"
                confidence_min=0.2,         # Confiance minimum augmentée
                rules_count_min=6,          # Plus de règles requises
                negative_rules_min=3        # Minimum 3 règles négatives pour "vide"
            )
        else:
            self.set_thresholds(
                full_min=0.3,               # Plus strict qu'avant
                empty_max=-0.08,            # Plus permissif qu'avant
                confidence_min=0.15,        # Plus exigeant en confiance
                rules_count_min=4,          # Plus de règles requises
                negative_rules_min=2        # Minimum 2 règles négatives pour "vide"
            )


def test_classifier(cache_path=CACHE_PATH, show_details=False, high_precision=False):
    """
    Fonction de test et d'évaluation du classifier sur un dataset labellisé
    
    OBJECTIFS :
    1. Mesurer la précision globale du système
    2. Analyser la répartition des prédictions (plein/vide uniquement)
    3. Identifier les erreurs pour améliorer les règles
    4. Calculer des métriques de performance (confiance, scores)
    5. Analyser l'impact des règles avancées et le ratio règles positives/négatives
    
    LOGIQUE D'ANALYSE :
    - Comparer prédictions vs labels réels
    - Tracker les règles impliquées dans les erreurs
    - Calculer précision binaire directe (toutes les prédictions sont définitives)
    - Statistiques des scores pour validation du système
    - Analyse spécifique des règles avancées et des ratios positif/négatif
    
    Args:
        cache_path (str): Chemin vers le fichier JSON des images labellisées
        show_details (bool): Afficher les détails des règles pour debug
        high_precision (bool): Utiliser le mode haute précision
        
    Returns:
        tuple: (classifier, accuracy) pour usage programmatique
    """
    # Initialisation du classifier avec paramètres recalibrés
    classifier = BinClassifier(high_precision=high_precision)
    
    # Chargement du dataset labellisé depuis le cache JSON
    with open(cache_path, "r", encoding="utf-8") as f:
        images = json.load(f)

    # Initialisation des métriques de performance
    total = len(images)                                          # Nombre total d'images
    correct = 0                                                  # Prédictions correctes
    predictions_count = {"plein": 0, "vide": 0}   # Répartition des prédictions (plus d'"inconnu")
    scores = []                                                  # Scores pour analyse statistique
    confidences = []                                             # Niveaux de confiance
    errors_analysis = []                                         # Analyse détaillée des erreurs
    advanced_rules_usage = Counter()                             # Compteur des règles avancées
    advanced_rules_success = Counter()                           # Règles avancées dans les prédictions correctes
    
    # Nouvelles métriques pour analyse des règles positives/négatives
    positive_rules_avg = {"plein": [], "vide": []}  # Règles positives par classe (plus d'"inconnu")
    negative_rules_avg = {"plein": [], "vide": []}  # Règles négatives par classe (plus d'"inconnu")

    precision_mode = "HAUTE PRÉCISION" if high_precision else "STANDARD"
    print(f"=== TEST DU CLASSIFIER RECALIBRÉ (MODE {precision_mode}) ===\n")
    
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
        advanced_rules = result.get('advanced_rules', [])  # Règles avancées utilisées
        
        # Mise à jour des statistiques globales
        predictions_count[predicted] += 1
        scores.append(score)
        confidences.append(confidence)
        
        # Mise à jour du compteur de règles avancées
        for rule in advanced_rules:
            advanced_rules_usage[rule] += 1
            if predicted == true_label:
                advanced_rules_success[rule] += 1
        
        # Collecte des statistiques sur les règles positives/négatives
        pos_count = result.get('positive_rules_count', 0)
        neg_count = result.get('negative_rules_count', 0)
        positive_rules_avg[predicted].append(pos_count)
        negative_rules_avg[predicted].append(neg_count)
        
        # Affichage du résultat pour suivi en temps réel avec ratio positif/négatif
        status = "✓" if predicted == true_label else "✗"  # Symbole visuel pour rapidité
        img_name = img.get('name_image', '')[:25]          # Nom tronqué pour lisibilité
        advanced_count = len(advanced_rules)
        ratio_str = f"{pos_count}+/{neg_count}-"           # Ratio règles positives/négatives
        print(f"{status} {img_name:25} | {true_label:6} → {predicted:6} | Score: {score:+.3f} | Conf: {confidence:.3f} | {ratio_str:7} | {advanced_count} règles avancées")
        
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
                'active_rules': result['details']['active_rules'],  # Règles qui ont influencé l'erreur
                'advanced_rules': advanced_rules                   # Règles avancées impliquées
            })
            
        # Debug détaillé pour les premières images (optionnel)
        if show_details and i < 3:
            print(f"    Rules actives: {result['details']['active_rules']}")
            print(f"    Règles avancées: {advanced_rules}")
            print(f"    Score brut: {result['details']['raw_score']:.2f}")
    
    # === CALCUL ET AFFICHAGE DES MÉTRIQUES FINALES ===
    
    print(f"\n=== RÉSULTATS FINAUX (MODE {precision_mode}) ===")
    print(f"Précision globale: {correct}/{total} = {correct/total:.2%}")
    print(f"Répartition: {predictions_count}")
    
    # Plus besoin de calculer la précision sans les "inconnu" puisqu'il n'y en a plus
    # Toutes les prédictions sont maintenant définitives
    
    # Statistiques des scores pour validation de la distribution
    if scores:
        print(f"\nStatistiques des scores:")
        print(f"  Moyenne: {sum(scores)/len(scores):+.3f}")        # Biais vers plein (+) ou vide (-)
        print(f"  Min: {min(scores):+.3f}, Max: {max(scores):+.3f}")  # Étendue des scores
        print(f"  Confiance moyenne: {sum(confidences)/len(confidences):.3f}")  # Fiabilité générale
        
    # Analyse des ratios de règles positives/négatives
    print(f"\nAnalyse des ratios règles positives/négatives:")
    for class_name in ["plein", "vide"]:  # Plus d'"inconnu"
        if positive_rules_avg[class_name]:
            pos_avg = sum(positive_rules_avg[class_name]) / len(positive_rules_avg[class_name])
            neg_avg = sum(negative_rules_avg[class_name]) / len(negative_rules_avg[class_name])
            print(f"  {class_name}: {pos_avg:.1f}+ / {neg_avg:.1f}- (ratio: {pos_avg/max(1, neg_avg):.2f})")
    
    # Analyse des erreurs pour identifier les améliorations possibles
    if errors_analysis:
        print(f"\nAnalyse des erreurs ({len(errors_analysis)} erreurs):")
        error_rules = []  # Collecte des règles impliquées dans les erreurs
        
        # Affichage des erreurs les plus représentatives avec ratio positif/négatif
        for err in errors_analysis[:5]:  # Limiter à 5 pour lisibilité
            pos_count = sum(1 for rule in err['active_rules'] if not rule.startswith(('area_ratio_low', 'hue_std_low', 
                                                                                     'contrast_iqr_low', 'edge_density_high', 
                                                                                     'mean_brightness_high', 'texture_entropy_low',
                                                                                     'color_complexity_low', 'brightness_variance_low')))
            neg_count = len(err['active_rules']) - pos_count
            print(f"  {err['image']:20} {err['expected']} → {err['predicted']} (score: {err['score']:+.3f}, ratio: {pos_count}+/{neg_count}-)")
            error_rules.extend(err['active_rules'])  # Accumuler les règles problématiques
        
        # Identification des règles les plus souvent impliquées dans les erreurs
        # UTILITÉ : Permet d'identifier les règles à revoir/ajuster
        if error_rules:
            rule_counter = Counter(error_rules)
            print(f"\nRègles les plus impliquées dans les erreurs:")
            for rule, count in rule_counter.most_common(5):
                # Déterminer si c'est une règle positive ou négative
                rule_type = "+" if not rule.startswith(('area_ratio_low', 'hue_std_low', 'contrast_iqr_low', 
                                                       'edge_density_high', 'mean_brightness_high', 'texture_entropy_low',
                                                       'color_complexity_low', 'brightness_variance_low', 'spatial_frequency_low',
                                                       'fill_ratio_advanced_low')) else "-"
                print(f"  {rule} ({rule_type}): {count} fois")
    
    # === ANALYSE DES RÈGLES AVANCÉES ===
    if advanced_rules_usage:
        print(f"\nAnalyse des règles avancées:")
        print(f"  Utilisation totale des règles avancées: {sum(advanced_rules_usage.values())} fois")
        
        # Top 5 des règles avancées les plus utilisées
        print(f"\nTop 5 des règles avancées les plus actives:")
        for rule, count in advanced_rules_usage.most_common(5):
            success_rate = advanced_rules_success.get(rule, 0) / count if count > 0 else 0
            print(f"  {rule}: {count} fois (taux de succès: {success_rate:.1%})")
        
        # Règles avancées avec le meilleur taux de succès
        print(f"\nRègles avancées les plus efficaces (min. 5 utilisations):")
        for rule, count in advanced_rules_usage.items():
            if count >= 5:  # Au moins 5 utilisations pour être significatif
                success_rate = advanced_rules_success.get(rule, 0) / count
                if success_rate > 0.7:  # Afficher seulement les règles à succès élevé
                    print(f"  {rule}: {success_rate:.1%} de succès ({advanced_rules_success.get(rule, 0)}/{count})")
    
    return classifier, correct/total


# === POINT D'ENTRÉE PRINCIPAL ===
if __name__ == "__main__":
    """
    Exécution directe du module pour test rapide
    
    UTILISATION :
    - python backend/services/classifier.py
    - Ou depuis la racine : python -c "from backend.services.classifier import test_classifier; test_classifier()"
    
    OPTIONS:
    - show_details=True: Afficher le détail des règles
    - high_precision=True: Utiliser le mode haute précision (plus strict)
    """
    print("Test du classifier\n")
    
    # Test en mode standard
    print("\n\n=== MODE STANDARD ===")
    classifier_std, accuracy_std = test_classifier(show_details=True, high_precision=True)
    print(f"\n🎯 Précision mode standard: {accuracy_std:.2%}..")
    
    # Test en mode haute précision
    #print("\n\n=== MODE HAUTE PRÉCISION ===")
    #classifier_hp, accuracy_hp = test_classifier(show_details=True, high_precision=True)
    
    # Comparaison des résultats
    #print("\n\n=== COMPARAISON DES MODES ===")
    #print(f"🎯 Mode standard:        {accuracy_std:.2%}")
    #print(f"🎯 Mode haute précision: {accuracy_hp:.2%}")
    
    # PROCHAINES ÉTAPES suggérées selon l'accuracy du meilleur mode:
    #best_accuracy = max(accuracy_std, accuracy_hp)
    #print(best_accuracy)