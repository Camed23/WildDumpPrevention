from flask import Blueprint, render_template, flash
from backend.config import supabase
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime



dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    
    try:
        print("Tentative de récupération des données depuis Supabase...")
        # On récupère les annotations et la taille de l'image liée
        response = supabase.table("annotation").select("label, image_id, image(size)").execute()

        if response.error:
            print(f"Erreur Supabase: {response.error}")
            flash("Erreur lors de la récupération des données.")
            return render_template("dashboard.html",
                                   error="Erreur de récupération Supabase.",
                                   total_images=0,
                                   full_percentage=0,
                                   empty_percentage=0,
                                   full_count=0,
                                   empty_count=0,
                                   file_sizes=[],
                                   plot_filename=None,
                                   images=[])

        data = response.data
        if not data:
            flash("Aucune annotation trouvée.")
            return render_template("dashboard.html",
                                   error="Aucune donnée disponible.",
                                   total_images=0,
                                   full_percentage=0,
                                   empty_percentage=0,
                                   full_count=0,
                                   empty_count=0,
                                   file_sizes=[],
                                   plot_filename=None,
                                   images=[])

        df = pd.DataFrame(data)
        # Extraire la taille depuis le champ imbriqué 'image'
        if 'image' in df.columns:
            df['size'] = df['image'].apply(lambda x: x['size'] if isinstance(x, dict) and 'size' in x else None)

        # Vérifiez que les colonnes attendues existent
        if 'label' not in df.columns or 'size' not in df.columns:
            flash("Champs manquants dans les données.")
            return render_template("dashboard.html",
                                   error="Champs manquants dans les données.",
                                   total_images=0,
                                   full_percentage=0,
                                   empty_percentage=0,
                                   full_count=0,
                                   empty_count=0,
                                   file_sizes=[],
                                   plot_filename=None,
                                   images=[])

        total_images = len(df)
        full_count = df['label'].value_counts().get('plein', 0)
        empty_count = df['label'].value_counts().get('vide', 0)
        full_percentage = round((full_count / total_images) * 100, 2) if total_images > 0 else 0
        empty_percentage = round((empty_count / total_images) * 100, 2) if total_images > 0 else 0
        file_sizes = df['size'].dropna().tolist() if 'size' in df.columns else []

        # Générer un graphique matplotlib
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plot_filename = f'plots/distribution_{timestamp}.png'
        filepath = f'static/{plot_filename}'

        # Crée le graphique APRES plt.figure
        plt.figure(figsize=(10, 6))
        df['label'].value_counts().plot(kind='bar', color=['red', 'green'])
        plt.title("Répartition des annotations")
        plt.xlabel("État")
        plt.ylabel("Nombre d'images")
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()

        return render_template("dashboard.html",
                               total_images=total_images,
                               full_percentage=full_percentage,
                               empty_percentage=empty_percentage,
                               full_count=full_count,
                               empty_count=empty_count,
                               file_sizes=file_sizes,
                               plot_filename=plot_filename,
                               images=data)

    except Exception as e:
        print(f"Erreur critique : {e}")
        flash("Erreur critique lors du chargement du tableau de bord.")
        return render_template("dashboard.html",
                               error="Erreur critique.",
                               total_images=0,
                               full_percentage=0,
                               empty_percentage=0,
                               full_count=0,
                               empty_count=0,
                               file_sizes=[],
                               plot_filename=None,
                               images=[])