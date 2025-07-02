# backend/services/classifi    # Charger les données
import os
import sys
import json

# Ajouter le répertoire racine du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.services.cache_manager import load_cache, initialize_cache
from backend.services.feature_extractor import ImageFeatures
from backend.services.rules_engine import all_rules, apply_rules


def classify_dataset(dataset_name="all", save_results=True):
    """
    Classifie un dataset d'images en utilisant le rules engine.
    
    Args:
        dataset_name (str, optional): Nom du dataset à charger ("labeled", "unlabeled", "all")
        save_results (bool): Si True, sauvegarde les résultats dans un fichier JSON
    
    Returns:
        list: Liste des résultats de classification
    """
    print(f"🔄 Chargement du dataset: {dataset_name}")
    
    # Charger les données
    try:
        images_data = load_cache("images_metadata_"+dataset_name)
    except FileNotFoundError:
        print("❌ Cache non trouvé. Initialisation en cours...")
        initialize_cache()
        images_data = load_cache("images_metadata_"+dataset_name)
    
    print(f"📊 {len(images_data)} images à classifier")
    
    results = []
    successful_classifications = 0
    errors = 0
    
    for i, image_data in enumerate(images_data):
        try:
            # 1. Extraire les features avec ImageFeatures
            extractor = ImageFeatures(image_data)
            features = extractor.extract_all_features()
            
            # 2. Appliquer les règles
            rule_result = apply_rules(features, all_rules)
            
            # 3. Interpréter le résultat pour classifier
            if "dirty" in rule_result:
                classification = "plein"
            elif "clean" in rule_result:
                classification = "vide"
            else:
                classification = "inconnu"
            
            # 4. Créer le résultat complet
            result = {
                "image_id": image_data.get('image_id'),
                "file_path": image_data.get('file_path'),
                "classification": classification,
                "rule_applied": rule_result,
                "features": features,
                "annotation": image_data.get('annotation')  # Garder l'annotation originale pour comparaison
            }
            
            results.append(result)
            successful_classifications += 1
            
            # Afficher le progrès
            if (i + 1) % 10 == 0:
                print(f"📈 Progression: {i + 1}/{len(images_data)} images traitées")
                
        except Exception as e:
            print(f"⚠️  Erreur lors de la classification de {image_data.get('file_path', 'image inconnue')}: {e}")
            errors += 1
            continue
    
    # Statistiques finales
    print(f"\n✅ Classification terminée:")
    print(f"   - {successful_classifications} images classifiées avec succès")
    print(f"   - {errors} erreurs")
    
    # Compter les résultats par catégorie
    classification_counts = {}
    for result in results:
        classification = result['classification']
        classification_counts[classification] = classification_counts.get(classification, 0) + 1
    
    print(f"📊 Répartition des classifications:")
    for classification, count in classification_counts.items():
        percentage = (count / len(results)) * 100 if results else 0
        print(f"   - {classification}: {count} images ({percentage:.1f}%)")
    
    # Sauvegarder les résultats
    if save_results and results:
        output_file = f"cache/classification_results_{dataset_name or 'default'}.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Résultats sauvegardés dans: {output_file}")
    
    return results


def evaluate_classification_accuracy(results):
    """
    Évalue la précision de la classification en comparant avec les annotations existantes.
    
    Args:
        results (list): Résultats de classification avec annotations
    
    Returns:
        dict: Métriques d'évaluation
    """
    if not results:
        return {"error": "Aucun résultat à évaluer"}
    
    correct_predictions = 0
    total_predictions = 0
    confusion_matrix = {}
    
    for result in results:
        # Récupérer l'annotation de référence du cache original
        annotations = result.get('annotation', [])
        if not annotations or annotations == [None]:
            continue
            
        # Prendre la première annotation comme référence
        if isinstance(annotations, list) and len(annotations) > 0 and annotations[0] is not None:
            ground_truth = annotations[0].get('label')
        else:
            continue
            
        if not ground_truth:
            continue
            
        predicted = result['classification']
        total_predictions += 1
        
        if predicted == ground_truth:
            correct_predictions += 1
        
        # Matrice de confusion
        key = f"{ground_truth}_predicted_{predicted}"
        confusion_matrix[key] = confusion_matrix.get(key, 0) + 1
    
    accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
    
    return {
        "accuracy": accuracy,
        "correct_predictions": correct_predictions,
        "total_predictions": total_predictions,
        "confusion_matrix": confusion_matrix
    }


if __name__ == "__main__":
    """
    Script principal pour classifier les images.
    """
    print("🚀 Démarrage de la classification des images")
    
    # Classifier les images labélisées pour évaluation
    print("\n1️⃣ Classification des images labélisées (pour évaluation):")
    labeled_results = classify_dataset("labeled")
    
    # Évaluer la précision sur les images labélisées
    if labeled_results:
        print("\n📏 Évaluation de la précision:")
        evaluation = evaluate_classification_accuracy(labeled_results)
        if "error" not in evaluation:
            print(f"   - Précision globale: {evaluation['accuracy']:.2%}")
            print(f"   - Prédictions correctes: {evaluation['correct_predictions']}/{evaluation['total_predictions']}")
            
            if evaluation.get('confusion_matrix'):
                print("   - Matrice de confusion:")
                for key, count in evaluation['confusion_matrix'].items():
                    print(f"     {key}: {count}")
        else:
            print(f"   - {evaluation['error']}")
    
    # Classifier les images non labélisées
    print("\n2️⃣ Classification des images non labélisées:")
    unlabeled_results = classify_dataset("unlabeled")
    
    print("\n🎉 Classification terminée !")
