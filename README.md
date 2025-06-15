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
```
---

### 💡 Fonctionnalités principales

- Upload d’image par utilisateur
- Annotation manuelle de l’état (pleine/vide)
- Extraction automatique de caractéristiques visuelles :
- Taille du fichier, dimensions, couleur moyenne, histogrammes, contraste, contours
- Classification automatique par règles conditionnelles (sans ML)
- Tableau de bord interactif avec indicateurs et filtres
- Export des données et visualisation des zones à risque

---

### 👥 Équipe projet & responsabilités

| Nom           | Rôle                   | Missions                                   |
| ------------- | ---------------------- | ------------------------------------------ |
| **Farid**     | Backend & Coordination | API Flask, base de données, intégration    |
| **Alexandre** | Feature Engineering    | Extraction d’images, moteur de règles      |
| **Lisa**      | Frontend & UX/UI       | Interfaces web, responsive design          |
| **Loéiz**     | Base de données        | Schéma SQL, ORM, intégration Flask         |
| **Duval**     | QA & Documentation     | Tests, manuel utilisateur, support         |
| **Athalie**   | Dashboard & Green IT   | Visualisation, indicateurs, éco-conception |

---

### ⚙️ Technologies utilisées
| Côté               | Technologies                            |
| ------------------ | --------------------------------------- |
| **Backend**        | Python 3, Flask, OpenCV, Pillow         |
| **Frontend**       | HTML5, CSS3, Bootstrap, JS              |
| **BDD**            | SQLite (dev), PostgreSQL (prod)         |
| **Visualisation**  | Matplotlib (serveur), Chart.js (client) |
| **Collaboration**  | GitHub, Git, Discord                    |
| **Éco-conception** | Green IT Framework (ADEME)              |

---

### 🚀 Lancer le projet en local

#### 🔧 Pré-requis
- Python 3.9+
- `pip`, `virtualenv`
- Git installé

### ▶️ Installation

```bash
# 1. Cloner le projet
git clone https://github.com/farid-dev/wild-dump-prevention.git
cd WildDumpPrevention

# 2. Créer un environnement virtuel
python -m venv venv

# 4. Activer l’environnement
source venv/bin/activate  # sous Linux/macOS
venv\Scripts\activate     # sous Windows

# 5. Installer les dépendances
pip install -r requirements.txt

# 6. Lancer le serveur Flask
cd backend
python app.py
```

### 🤝 Contribuer

- Cloner le projet
- Créer une branche : feature/ma-fonctionnalite
- Faire un pull request avec une bonne description !


