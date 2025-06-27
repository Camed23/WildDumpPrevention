from flask import Blueprint, render_template
from services.supabase_client import supabase

bp = Blueprint('user', __name__)

@bp.route('/users')
def users():
    try:
        result = supabase.table("User").select("*").execute()
        return render_template("users.html", users=result.data)
    except Exception as e:
        return f"Erreur lors de la récupération des utilisateurs : {e}"
