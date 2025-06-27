# backend/services/rules_engine.py

class Rule:
    def __init__(self, name, condition_fn):
        self.name = name
        self.condition = condition_fn

    def applies(self, features):
        # Renvoie True si la règle correspond à dirty
        return self.condition(features)

# Exemples de règles
rule_dark = Rule(
    "luminosité_trop_basse",                # nom de la règle
    lambda f: f["mean_brightness"] < 80     # condition de la règle (à ajuster selon nos besoins)
)
rule_moyen = Rule(
    "zone_occupée_moyenne",
    lambda f: f["area_ratio"] > 0.6
)

def apply_rules(features, rules):
    # Parcourt les règles et renvoie le nom de la première qui s’applique
    for rule in rules:
        if rule.applies(features):
            return rule.name
    return "pas_de_conclusion"
