from flask import Blueprint, render_template
from backend.config import supabase

user_bp = Blueprint("user", __name__)

@user_bp.route('/')
def users():
    try:
        result = supabase.table("User").select("*").execute()
        return render_template("users.html", users=result.data)
    except Exception as e:
        return f"Erreur lors de la récupération des utilisateurs : {e}"
