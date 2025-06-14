# WildDumpPrevention
Plateforme web intelligente de suivi des poubelles à partir d’images – Mastercamp Efrei 2025



## Arborescence des fichiers
WildDumpPrevention/
│
├── backend/                # Flask (ou Django si maîtrise rapide)
│   ├── app.py              # Point d’entrée principal
│   ├── routes/             # Routes API REST (upload, annotation, stats, etc.)
│   ├── services/           # Logique métier : extraction de features, règles, etc.
│   ├── models/             # ORM ou requêtes SQL
│   ├── utils/              # Fonctions d’analyse d’images
│   └── static/             # Stockage images uploadées
│
├── frontend/               # HTML, CSS, JS (vanilla ou Bootstrap/Chart.js)
│   ├── index.html
│   ├── upload.html
│   ├── dashboard.html
│   └── js/                 # Scripts (ex : chart.js)
│
├── database/
│   ├── schema.sql          # Schéma de la BDD (ou migration ORM)
│   └── dump.sqlite         # Base SQLite initiale (ou PostgreSQL)
│
├── docs/                   # Rapport technique, écoconception, etc.
│
├── tests/                  # Unitaires, règles, performances
│
├── .gitignore
├── README.md
└── requirements.txt
