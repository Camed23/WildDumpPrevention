from flask import Blueprint, render_template, flash
from backend.config import supabase
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')



dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    
    try:
        print("Tentative de récupération des données depuis Supabase...")
        # On récupère les annotations et la taille de l'image liée
        response = supabase.table("annotation").select("label, image_id, image(size)").execute()
        # Correction : APIResponse n'a pas d'attribut 'error', il faut vérifier 'status_code' et 'data'
        if hasattr(response, 'status_code') and response.status_code >= 400:
            print(f"Erreur Supabase: status_code={response.status_code}")
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

        data = getattr(response, 'data', None)
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

        # DEBUG : Afficher les données brutes et le DataFrame
        #print('DATA RECUE:', data)
        df = pd.DataFrame(data)
        #print('DATAFRAME:', df.head())

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

        # Nettoyer les valeurs manquantes
        df = df.dropna(subset=['label', 'size'])
        total_images = len(df)
        full_count = df['label'].value_counts().get('plein', 0)
        empty_count = df['label'].value_counts().get('vide', 0)
        full_percentage = round((full_count / total_images) * 100, 2) if total_images > 0 else 0
        empty_percentage = round((empty_count / total_images) * 100, 2) if total_images > 0 else 0
        file_sizes = df['size'].dropna().tolist() if 'size' in df.columns else []

        # Conversion des types de données
        total_images = int(total_images)
        full_count = int(full_count)
        empty_count = int(empty_count)
        file_sizes = [float(x) for x in file_sizes]
        # Calcul de la taille moyenne des fichiers (en Ko)
        if file_sizes:
            moyenne_taille = round(np.mean(file_sizes) / 1024, 2)
        else:
            moyenne_taille = 0.0

        # Générer un graphique matplotlib
        import os
        plot_dir = os.path.join('static', 'plots')
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plot_filename = f'plots/distribution_{timestamp}.png'
        filepath = os.path.join('static', plot_filename)
        radar_filename = f'plots/radar_{timestamp}.png'
        radar_filepath = os.path.join('static', radar_filename)

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

        try:
            # Crée le graphique à barres
            plt.figure(figsize=(10, 6))
            df['label'].value_counts().plot(kind='bar', color=['red', 'green'])
            plt.title("Répartition des annotations")
            plt.xlabel("État")
            plt.ylabel("Nombre d'images")
            plt.xticks(rotation=0)
            plt.tight_layout()
            plt.savefig(filepath)
            plt.close()
        except Exception as plot_err:
            print(f"Erreur lors de la génération des graphiques : {plot_err}")
            flash("Erreur lors de la génération des graphiques.")


        city_stats = get_city_stats()
        return render_template("dashboard.html",
                               total_images=total_images,
                               full_percentage=full_percentage,
                               empty_percentage=empty_percentage,
                               full_count=full_count,
                               empty_count=empty_count,
                               file_sizes=file_sizes,
                               plot_filename=plot_filename,
                               images=data,
                               moyenne_taille=moyenne_taille,
                                radar_filename=radar_filename,
                                city_stats=city_stats)

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
    


def get_city_stats():
    villes_possibles = [
        "Paris", "Lyon", "Marseille", "Toulouse", "Nice",
        "Lille", "Nantes", "Strasbourg", "Bordeaux", "Montpellier",
        "Rennes", "Reims", "Le Havre"
    ]

    stats = []

    for ville in villes_possibles:
        try:
            pleines_resp = supabase.rpc("nb_poubelles_pleines", {"par_ville": ville}).execute()
            vides_resp = supabase.rpc("nb_poubelles_vides", {"par_ville": ville}).execute()
            non_annot_resp = supabase.rpc("nb_poubelles_non_annotées", {"par_ville": ville}).execute()


            pleines = pleines_resp.data if pleines_resp.data is not None else 0
            vides = vides_resp.data if vides_resp.data is not None else 0
            non_annotées = non_annot_resp.data if non_annot_resp.data is not None else 0

            stats.append({
                "ville": ville,
                "pleines": pleines,
                "vides": vides,
                "non_annotées": non_annotées
            })

        except Exception as e:
            print(f"Erreur récupération stats pour {ville} : {e}")
            stats.append({
                "ville": ville,
                "pleines": 0,
                "vides": 0,
                "non_annotées": 0
            })

    return stats

