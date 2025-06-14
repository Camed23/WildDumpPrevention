# WildDumpPrevention
Plateforme web intelligente de suivi des poubelles à partir d’images – Mastercamp Efrei 2025

## 🔧 Architecture du Projet

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
