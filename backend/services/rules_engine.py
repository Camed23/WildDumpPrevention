# backend/services/rules_engine.py

class Rule:
    def __init__(self, name, condition_fn):
        self.name = name
        self.condition = condition_fn

    def applies(self, features):
        # Renvoie True si la règle correspond à dirty
        return self.condition(features)

# 1) Zone occupée (surface détectée / surface totale)
rule_area_full  = Rule(
    "area_ratio > 0.6 → dirty",
    lambda f: f["area_ratio"] > 0.6
)
rule_area_empty = Rule(
    "area_ratio < 0.2 → clean",
    lambda f: f["area_ratio"] < 0.2
)

# 2) Densité de contours (beaucoup de déchets = plein de formes / arêtes)
rule_edges_full  = Rule(
    "edge_density > 0.20 → dirty",
    lambda f: f["edge_density"] > 0.20
)
rule_edges_empty = Rule(
    "edge_density < 0.05 → clean",
    lambda f: f["edge_density"] < 0.05
)

# 3) Luminosité moyenne (intérieur sombre = plein, clair = vide)
rule_dark_full  = Rule(
    "mean_brightness < 80 → dirty",
    lambda f: f["mean_brightness"] < 80
)
rule_light_empty = Rule(
    "mean_brightness > 160 → clean",
    lambda f: f["mean_brightness"] > 160
)

# 4) Contraste inter-quartile (beaucoup de variation = plein)
rule_contrast_full  = Rule(
    "contrast_iqr > 80 → dirty",
    lambda f: f["contrast_iqr"] > 80
)
rule_contrast_empty = Rule(
    "contrast_iqr < 30 → clean",
    lambda f: f["contrast_iqr"] < 30
)

# 5) Taille de fichier (fichiers plus gros quand ils contiennent plus de détails)
rule_size_full = Rule(
    "file_size_mb > 1.5 → dirty",
    lambda f: f["file_size_mb"] > 1.5
)

# 6) Variabilité de teinte (plus de couleurs / saletés = plein)
rule_hue_full  = Rule(
    "hue_std > 25 → dirty",
    lambda f: f["hue_std"] > 25
)
rule_hue_empty = Rule(
    "hue_std < 10 → clean",
    lambda f: f["hue_std"] < 10
)

# Regrouper toutes les règles
all_rules = [
    rule_area_full,
    rule_area_empty,
    rule_edges_full,
    rule_edges_empty,
    rule_dark_full,
    rule_light_empty,
    rule_contrast_full,
    rule_contrast_empty,
    rule_size_full,
    rule_hue_full,
    rule_hue_empty
]

def apply_rules(features, rules):
    # Parcourt les règles et renvoie le nom de la première qui s’applique
    for rule in rules:
        if rule.applies(features):
            return rule.name
    return "pas_de_conclusion"
