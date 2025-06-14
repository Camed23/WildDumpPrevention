## 🗑️ Wild Dump Prevention – Mastercamp Efrei 2025

**Plateforme web intelligente de suivi des poubelles à partir d’images – Projet Data / AI for Good**

---

## 🚀 Objectif du projet

Développer une plateforme web capable de détecter automatiquement l’état des poubelles (pleines ou vides) à partir d’images uploadées par des citoyens ou des agents municipaux, pour prévenir les dépôts sauvages et améliorer la gestion urbaine des déchets.

---

### 🔧 Architecture du Projet

```bash
WildDumpPrevention/
├── backend/                         # Application Flask (API REST)
│   ├── app.py                       # Point d'entrée principal (lancement serveur)
│   ├── config.py                    # Configuration Flask (dev/prod, chemins, clés)
│   ├── __init__.py                  # Création de l'application Flask (factory)
│   ├── routes/                      # Routes/Blueprints de l'API
│   │   ├── upload_routes.py         # Route : upload d’image
│   │   ├── annotation_routes.py     # Route : annotation manuelle
│   │   ├── dashboard_routes.py      # Route : statistiques, visualisations
│   │   └── classification_routes.py # Route : règles conditionnelles, auto-classement
│   ├── services/                    # Logique métier
│   │   ├── feature_extractor.py     # Extraction de caractéristiques (image)
│   │   ├── rules_engine.py          # Moteur de règles (classification non-ML)
│   │   └── image_handler.py         # Stockage, renommage, compression image
│   ├── models/                      # Modèles de données (ORM ou SQL brut)
│   │   └── image_model.py           # Définition table images + fonctions accès BDD
│   ├── utils/                       # Fonctions indépendantes / outils généraux
│   │   ├── helpers.py               # Horodatage, vérification, conversion, etc.
│   │   └── validators.py            # Validation d’images, formats, extensions
│   ├── static/uploads/             # Dossier où sont stockées les images uploadées
│   └── templates/                  # (optionnel) si front géré avec Flask
│
├── frontend/                        # Front-end HTML/CSS/JS
│   ├── index.html                   # Accueil / vue globale
│   ├── upload.html                  # Formulaire d’upload
│   ├── annotate.html                # Annotation manuelle
│   ├── dashboard.html               # Visualisation des données
│   ├── css/                         # Feuilles de style
│   │   └── style.css
│   └── js/                          # Scripts JS (Chart.js, interactions)
│       └── charts.js
│
├── database/                        # Fichiers liés à la base de données
│   ├── schema.sql                   # Schéma de création initial
│   ├── init_db.py                   # Script Python pour initialisation automatique
│   └── dump.sqlite                  # Base SQLite locale (à versionner au besoin)
│
├── tests/                           # Tests unitaires et fonctionnels
│   ├── test_upload.py
│   ├── test_rules.py
│   └── test_dashboard.py
│
├── docs/                            # Documentation et livrables
│   ├── rapport_technique.md
│   ├── eco_conception.md
│   └── diagrammes/                 # UML, architecture, base, etc.
│
├── .gitignore
├── README.md
├── requirements.txt
└── run.sh                          # (optionnel) script shell pour lancer tout d’un coup


---

## 👥 Équipe projet & responsabilités

| Nom        | Rôle principal        | Missions clés |
|------------|-----------------------|----------------|
| Farid      | Backend & coordination | API Flask, intégration BDD, routes, structuration Git |
| Alexandre  | Feature engineering    | Extraction caractéristiques (taille, couleurs, contours…), classification par règles |
| Lisa       | Front-end & UX/UI     | Interfaces HTML/CSS, interactions JS, responsive design |
| Loéiz      | Base de données       | Schéma SQL, ORM, intégration avec Flask |
| Duval      | QA & documentation    | Tests fonctionnels, manuel utilisateur, support technique |
| Athalie    | Visualisation & Green IT | Dashboard Chart.js, éco-conception, indicateurs dynamiques |

---

## 💡 Fonctionnalités principales

- Upload d’image par utilisateur
- Annotation manuelle de l’état (pleine/vide)
- Extraction automatique de caractéristiques visuelles :
  - Taille du fichier, dimensions, couleur moyenne, histogrammes, contraste, contours
- Classification automatique par règles conditionnelles (sans ML)
- Tableau de bord interactif avec indicateurs et filtres
- Export des données et visualisation des zones à risque

---

## ⚙️ Technologies utilisées

| Côté | Outils |
|------|--------|
| Backend | Python 3, Flask, Pillow, OpenCV, SQLite |
| Frontend | HTML5, CSS3, Bootstrap, Chart.js |
| BDD | SQLite (ou PostgreSQL en prod) |
| Visualisation | Matplotlib (serveur) + Chart.js (client) |
| Autres | GitHub, Discord, Git, Green IT Framework (ADEME) |

---

## 🧪 Lancer le projet localement

### 1. Cloner le dépôt
```bash
git clone https://github.com/<ton-compte>/wild-dump-prevention.git
cd wild-dump-prevention

