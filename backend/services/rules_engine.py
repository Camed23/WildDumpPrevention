"""
Rules Engine - Moteur de règles pour la classification des poubelles

LOGIQUE GÉNÉRALE :
- Séparer la responsabilité : ce module calcule uniquement des SCORES, pas de classification
- Utiliser un système de règles pondérées pour capturer différents aspects visuels
- Permettre facilement l'ajout/suppression de règles sans casser le système
- Retourner un score normalisé entre -1 (vide) et +1 (plein) pour simplifier la classification

ARCHITECTURE :
1. Rule : Classe pour une règle individuelle (condition + poids)
2. RulesEngine : Moteur qui évalue toutes les règles et calcule un score global
3. Scoring bipolaire : règles positives (plein) vs négatives (vide)
"""

class Rule:
    """
    Une règle individuelle pour évaluer un aspect spécifique d'une image
    
    LOGIQUE :
    - Chaque règle teste une condition sur les features d'image (ex: contraste > seuil)
    - Le poids détermine l'importance de cette règle dans la décision finale
    - Les poids positifs indiquent "plein", les poids négatifs indiquent "vide"
    """
    def __init__(self, name, condition_fn, weight=1.0):
        """
        Args:
            name (str): Nom descriptif de la règle pour debug
            condition_fn (function): Fonction lambda qui teste les features
            weight (float): Poids de la règle (positif=plein, négatif=vide)
        """
        self.name = name
        self.condition = condition_fn
        self.weight = weight

    def applies(self, features):
        """
        Vérifie si la règle s'applique aux features
        
        Returns:
            bool: True si la condition est remplie
        """
        return self.condition(features)

    def score(self, features):
        """
        Retourne le score pondéré de cette règle
        
        LOGIQUE : Seulement si la règle s'applique, on compte son poids
        Sinon score = 0 (règle neutre)
        
        Returns:
            float: Poids de la règle si elle s'applique, 0 sinon
        """
        return self.weight if self.applies(features) else 0.0


class RulesEngine:
    """
    Moteur de règles principal qui évalue toutes les règles et calcule un score global
    
    LOGIQUE DE CONCEPTION :
    1. Utilise un système bipolaire : règles "plein" (poids +) vs "vide" (poids -)
    2. Normalise le score final entre -1 et +1 pour simplifier la classification
    3. Garde trace des règles actives pour debug et analyse d'erreurs
    4. Permet l'ajout dynamique de règles pour expérimentation
    5. **NOUVEAU** : Seuils configurables pour ajustement facile
    
    AVANTAGES :
    - Séparation claire entre scoring et classification
    - Facilité d'ajout/modification de règles
    - Transparence : on sait quelles règles ont contribué au score
    - Robustesse : si aucune règle ne s'applique, score neutre (0)
    - **Configurabilité** : L'utilisateur peut ajuster les seuils sans modifier le code
    """
    def __init__(self, rules=None, thresholds=None):
        """
        Args:
            rules (list): Liste de règles personnalisées, sinon utilise les règles par défaut
            thresholds (dict): Seuils configurables pour les règles
        """
        # Seuils par défaut recalibrés avec une séparation plus nette
        self.thresholds = thresholds or {
            # Seuils pour règles "plein" (positives) - PLUS STRICTS
            'area_ratio_high': 0.60,     # Plus strict: seules les images vraiment remplies
            'hue_std_high': 60,          # Plus strict: vraie diversité de couleurs
            'contrast_iqr_high': 85,     # Plus strict: contraste vraiment élevé
            'edge_density_low': 0.07,    # Plus strict: vraiment peu de contours
            'mean_brightness_low': 115,  # Plus strict: vraiment sombre
            
            # Seuils pour règles "vide" (négatives) - PLUS PERMISSIFS
            'area_ratio_low': 0.50,      # Plus permissif: plus d'images peuvent être vides
            'hue_std_low': 55,           # Plus permissif: couleurs plus uniformes
            'contrast_iqr_low': 75,      # Plus permissif: contraste plus faible
            'edge_density_high': 0.09,   # Plus permissif: plus de contours visibles
            'mean_brightness_high': 125, # Plus permissif: plus clair
            
            # NOUVEAUX SEUILS pour features avancées
            'texture_entropy_high': 6.5,     # Entropie élevée = chaos (plein)
            'texture_entropy_low': 5.0,      # Entropie faible = uniforme (vide)
            'color_complexity_high': 0.15,   # Beaucoup de couleurs = plein
            'color_complexity_low': 0.08,    # Peu de couleurs = vide
            'brightness_variance_high': 800, # Forte variance = ombres/objets
            'brightness_variance_low': 400,  # Faible variance = uniforme
            'spatial_frequency_high': 15,    # Haute fréquence = textures/objets
            'spatial_frequency_low': 8,      # Basse fréquence = surfaces lisses
            'fill_ratio_advanced_high': 0.45, # Zone remplie avancée
            'fill_ratio_advanced_low': 0.25,  # Zone vide avancée
        }
        
        self.rules = rules or self._create_default_rules()

    def _create_default_rules(self):
        """
        Crée les règles par défaut avec seuils configurables
        
        LOGIQUE DES RÈGLES :
        - Règles POSITIVES (poids +) : indicateurs de poubelle PLEINE
        - Règles NÉGATIVES (poids -) : indicateurs de poubelle VIDE
        
        CHOIX DES SEUILS :
        - Utilisent self.thresholds pour être configurables
        - L'utilisateur peut les modifier via set_thresholds()
        - Seuils ajustés pour éviter les faux positifs/négatifs
        """
        return [
            # === RÈGLES POUR POUBELLE PLEINE (scores positifs) ===
            # Zone occupée élevée = beaucoup de déchets visibles
            Rule("area_ratio_high", 
                lambda f: f.get('area_ratio', 0) > self.thresholds['area_ratio_high'], 
                weight=3.0),
            
            # Variabilité de couleurs élevée = déchets divers
            Rule("hue_std_high", 
                 lambda f: f.get('hue_std', 0) > self.thresholds['hue_std_high'], 
                 weight=2.0),
            
            # Contraste élevé = formes et objets distincts  
            Rule("contrast_iqr_high", 
                 lambda f: f.get('contrast_iqr', 0) > self.thresholds['contrast_iqr_high'], 
                 weight=2.0),
            
            # Peu de contours nets = déchets qui masquent le fond
            Rule("edge_density_low", 
                 lambda f: f.get('edge_density', 1) < self.thresholds['edge_density_low'], 
                 weight=1.0),
            
            # Luminosité faible = ombres créées par les déchets
            Rule("mean_brightness_low",
                 lambda f: f.get('mean_brightness', 128) < self.thresholds['mean_brightness_low'], 
                 weight=1.5),
            
            # === NOUVELLES RÈGLES AVANCÉES POUR PLEIN ===
            # Haute entropie = chaos, désordre des déchets
            Rule("texture_entropy_high",
                 lambda f: f.get('texture_entropy', 5) > self.thresholds['texture_entropy_high'],
                 weight=2.5),
            
            # Complexité des couleurs = déchets variés
            Rule("color_complexity_high",
                 lambda f: f.get('color_complexity', 0.1) > self.thresholds['color_complexity_high'],
                 weight=2.0),
            
            # Forte variance de luminosité = ombres, reliefs
            Rule("brightness_variance_high",
                 lambda f: f.get('brightness_variance', 500) > self.thresholds['brightness_variance_high'],
                 weight=1.5),
            
            # Zone remplie avancée (segmentation sophistiquée)
            Rule("fill_ratio_advanced_high",
                 lambda f: f.get('fill_ratio_advanced', 0.3) > self.thresholds['fill_ratio_advanced_high'],
                 weight=3.5),  # Poids élevé car c'est une feature sophistiquée
            
            
            # === RÈGLES POUR POUBELLE VIDE (scores négatifs) ===
            # Zone occupée faible = peu/pas de déchets
            Rule("area_ratio_low", 
                 lambda f: f.get('area_ratio', 0) < self.thresholds['area_ratio_low'],
                 weight=-2.5),
            
            # Peu de variabilité = couleurs uniformes du fond
            Rule("hue_std_low", 
                 lambda f: f.get('hue_std', 0) < self.thresholds['hue_std_low'], 
                 weight=-1.5),
            
            # Contraste faible = surface lisse et uniforme
            Rule("contrast_iqr_low", 
                 lambda f: f.get('contrast_iqr', 0) < self.thresholds['contrast_iqr_low'], 
                 weight=-1.5),
            
            # Beaucoup de contours = structure de la poubelle visible
            Rule("edge_density_high", 
                 lambda f: f.get('edge_density', 0) > self.thresholds['edge_density_high'], 
                 weight=-1.0),
            
            # Luminosité élevée = pas d'ombres, fond visible
            Rule("mean_brightness_high", 
                 lambda f: f.get('mean_brightness', 128) > self.thresholds['mean_brightness_high'], 
                 weight=-1.0),
            
            # === NOUVELLES RÈGLES AVANCÉES POUR VIDE ===
            # Faible entropie = uniformité, ordre
            Rule("texture_entropy_low",
                 lambda f: f.get('texture_entropy', 5) < self.thresholds['texture_entropy_low'],
                 weight=-2.0),
            
            # Peu de couleurs = fond uniforme
            Rule("color_complexity_low",
                 lambda f: f.get('color_complexity', 0.1) < self.thresholds['color_complexity_low'],
                 weight=-1.5),
            
            # Faible variance = pas d'ombres, surface plate
            Rule("brightness_variance_low",
                 lambda f: f.get('brightness_variance', 500) < self.thresholds['brightness_variance_low'],
                 weight=-1.5),
            
            # Basse fréquence spatiale = pas de textures
            Rule("spatial_frequency_low",
                 lambda f: f.get('spatial_frequency', 10) < self.thresholds['spatial_frequency_low'],
                 weight=-1.0),
            
            # Zone peu remplie (segmentation avancée)
            Rule("fill_ratio_advanced_low",
                 lambda f: f.get('fill_ratio_advanced', 0.3) < self.thresholds['fill_ratio_advanced_low'],
                 weight=-3.0),  # Poids élevé car c'est une feature sophistiquée
        ]

    def evaluate(self, features):
        """
        Évalue toutes les règles et calcule un score global normalisé
        
        LOGIQUE DE CALCUL :
        1. Pour chaque règle, vérifier si elle s'applique
        2. Si oui, ajouter son score (poids) au total
        3. Normaliser le score par le poids total pour avoir [-1, +1]
        4. Garder trace des règles actives pour debug
        
        INTERPRÉTATION DU SCORE :
        - Score > 0 : tend vers "plein" (plus c'est proche de +1, plus c'est sûr)
        - Score < 0 : tend vers "vide" (plus c'est proche de -1, plus c'est sûr)  
        - Score ~ 0 : incertain (règles contradictoires ou peu de règles actives)
        
        Args:
            features (dict): Features extraites de l'image
            
        Returns:
            dict: {
                'score': float,           # Score normalisé [-1, +1]
                'raw_score': float,       # Score brut (somme des poids)
                'total_weight': float,    # Somme des poids absolus des règles actives
                'active_rules': list,     # Noms des règles qui se sont appliquées
                'rules_count': int        # Nombre de règles actives
            }
        """
        total_score = 0.0        # Somme des scores (peut être négative)
        total_weight = 0.0       # Somme des poids absolus (toujours positive)
        active_rules = []        # Liste des règles qui se sont appliquées

        # Évaluer chaque règle individuellement
        for rule in self.rules:
            if rule.applies(features):  # La condition de la règle est-elle remplie ?
                score = rule.score(features)    # Récupérer le poids de la règle
                total_score += score            # Ajouter au score total (+ ou -)
                total_weight += abs(rule.weight)  # Ajouter le poids absolu pour normalisation
                active_rules.append(rule.name)   # Garder trace pour debug

        # Normalisation du score entre -1 et 1
        # Évite les scores disproportionnés quand peu de règles s'appliquent
        if total_weight > 0:
            normalized_score = total_score / total_weight
        else:
            # Aucune règle ne s'applique = score neutre
            normalized_score = 0.0

        return {
            'score': normalized_score,
            'raw_score': total_score,
            'total_weight': total_weight,
            'active_rules': active_rules,
            'rules_count': len(active_rules)
        }

    def set_thresholds(self, **thresholds):
        """
        Permet à l'utilisateur de modifier les seuils des règles
        
        UTILITÉ :
        - Ajuster les seuils selon le dataset ou le contexte
        - Optimiser les performances après analyse des erreurs
        - Expérimenter avec différents paramètres
        
        Args:
            **thresholds: Seuils à modifier (nom_règle=nouvelle_valeur)
            
        Exemples:
            engine.set_thresholds(area_ratio_high=0.5, hue_std_low=10)
            engine.set_thresholds(mean_brightness_low=90)
        """
        # Mettre à jour seulement les seuils fournis
        for threshold_name, value in thresholds.items():
            if threshold_name in self.thresholds:
                old_value = self.thresholds[threshold_name]
                self.thresholds[threshold_name] = value
                print(f"Seuil '{threshold_name}' modifié: {old_value} → {value}")
            else:
                print(f"⚠️  Seuil '{threshold_name}' introuvable. Seuils disponibles: {list(self.thresholds.keys())}")
        
        # Recréer les règles avec les nouveaux seuils
        self.rules = self._create_default_rules()
        print("✅ Règles mises à jour avec les nouveaux seuils")

    def get_thresholds(self):
        """
        Retourne tous les seuils actuels pour consultation
        
        Returns:
            dict: Dictionnaire des seuils actuels
        """
        return self.thresholds.copy()

    def reset_thresholds(self):
        """
        Remet les seuils aux valeurs par défaut
        
        UTILITÉ : Revenir aux paramètres originaux après expérimentation
        """
        default_thresholds = {
            # Seuils pour règles "plein" (positives) - RECALIBRÉS PLUS STRICTS
            'area_ratio_high': 0.60,
            'hue_std_high': 60,
            'contrast_iqr_high': 85,
            'edge_density_low': 0.07,
            'mean_brightness_low': 115,
            
            # Seuils pour règles "vide" (négatives) - RECALIBRÉS PLUS PERMISSIFS
            'area_ratio_low': 0.50,
            'hue_std_low': 55,
            'contrast_iqr_low': 75,
            'edge_density_high': 0.09,
            'mean_brightness_high': 125,
            
            # NOUVEAUX SEUILS pour features avancées
            'texture_entropy_high': 6.5,
            'texture_entropy_low': 5.0,
            'color_complexity_high': 0.15,
            'color_complexity_low': 0.08,
            'brightness_variance_high': 800,
            'brightness_variance_low': 400,
            'spatial_frequency_high': 15,
            'spatial_frequency_low': 8,
            'fill_ratio_advanced_high': 0.45,
            'fill_ratio_advanced_low': 0.25,
        }
        
        self.thresholds = default_thresholds
        self.rules = self._create_default_rules()
        print("✅ Seuils remis aux valeurs par défaut")
        
    def add_rule(self, name, condition_fn, weight=1.0):
        """
        Ajoute une nouvelle règle au moteur
        
        UTILITÉ : Permet d'expérimenter avec de nouvelles règles sans modifier le code
        
        Args:
            name (str): Nom de la règle pour identification
            condition_fn (function): Fonction qui teste les features
            weight (float): Poids (+ pour plein, - pour vide)
        """
        self.rules.append(Rule(name, condition_fn, weight))

    def remove_rule(self, name):
        """
        Supprime une règle par son nom
        
        UTILITÉ : Permet de désactiver temporairement des règles problématiques
        
        Args:
            name (str): Nom de la règle à supprimer
        """
        self.rules = [rule for rule in self.rules if rule.name != name]

    def get_rule_details(self, features):
        """
        Retourne le détail de chaque règle pour debug et analyse
        
        UTILITÉ : 
        - Comprendre pourquoi une image est mal classée
        - Identifier les règles les plus/moins efficaces
        - Ajuster les seuils et poids
        
        Args:
            features (dict): Features d'une image
            
        Returns:
            list: Liste de dicts avec détails par règle
        """
        details = []
        for rule in self.rules:
            applies = rule.applies(features)
            score = rule.score(features)
            details.append({
                'name': rule.name,
                'applies': applies,      # La règle s'applique-t-elle ?
                'weight': rule.weight,   # Poids de la règle
                'score': score          # Score effectif (0 si pas appliquée)
            })
        return details


# Instance globale pour compatibilité avec l'ancien code
# LOGIQUE : Permet d'utiliser un moteur par défaut sans avoir à l'instancier
default_rules_engine = RulesEngine()
