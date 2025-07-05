from backend.config import supabase
from backend.services.rules_engine import default_rules_engine  

def get_all_rules():
    response = supabase.table("classification_rules").select("*").order("id").execute()
    return response.data

def update_rule_threshold(rule_name, new_value):
    supabase.table("classification_rules") \
        .update({"threshold_value": new_value}) \
        .eq("rule_name", rule_name) \
        .execute()


def reset_all_thresholds():
    default_rules_engine.reset_thresholds()
    defaults = default_rules_engine.get_thresholds()

    # 1 requête par règle, mais pas d’erreur de NOT NULL
    for name, value in defaults.items():
        update_rule_threshold(name, value)

    return defaults

