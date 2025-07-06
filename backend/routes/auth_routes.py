from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.config import supabase

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        result = supabase.table("User").select("*").eq("email", email).execute()
        if not result.data:
            flash("Utilisateur non trouvé", "error")
            return redirect(url_for("auth.login"))

        user = result.data[0]
        # Vérification du mot de passe chiffré
        verify = supabase.rpc("verify_password", {
            "p_email": email,
            "p_password": password
        }).execute()

        if not verify.data:
            flash("Mot de passe incorrect", "error")
            return redirect(url_for("auth.login"))

        # Stocker l’utilisateur en session
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['role'] = user['role']

        flash(f"Bienvenue, {user['username']}", "success")
        return redirect(url_for('home'))

    return render_template("login.html")


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Déconnexion réussie", "success")
    return redirect(url_for('auth.login'))
