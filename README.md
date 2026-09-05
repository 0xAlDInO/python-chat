# OXMEMBER — Application de Chat & Visioconférence Entreprise

OXMEMBER est une plateforme web moderne de messagerie instantanée, d'appel audio et de visioconférence WebRTC développée pour les collaborateurs d'Oxalix.

---

## 🚀 Fonctionnalités Principales

- **Authentification par ID Back-Office :** Identification par ID utilisateur (ex: `OX-001`, `OX-002`) avec contrôle strict des autorisations d'accès aux salles.
- **Interface Pastel Modern 3 Colonnes :** Layout responsive Fullscreen (100vw x 100vh) aux tons pastel clairs avec bulles de messages personnalisées.
- **Visioconférence & Telephonie WebRTC :**
  - File d'attente d'appels en direct dans le panneau droit (**APPELS EN COURS**) sans pop-up directe.
  - Support des appels **Audio** et **Vidéo**.
  - Grille dynamique vidéo multi-participants (3+ caméras en direct).
  - Fin d'appel globale contrôlée par l'organisateur/hôte.
- **Sélecteur d'Émojis :** Popover d'émojis interactif.
- **Partage de Fichiers & Images :** Téléversement d'images et documents avec galeries partagées dans le panneau droit (initialement vides à la connexion).
- **Persistance des Données :** Intégration Flask-SQLAlchemy avec support **MySQL** et bascule automatique sur **SQLite**.

---

## 🛠️ Installation et Démarrage

### 1. Cloner et préparer l'environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirement.txt
```

### 2. Initialiser la Base de Données
```bash
flask init-db
```

### 3. Lancer l'Application
```bash
python3 app.py
```
L'application sera accessible sur `http://127.0.0.1:5000`.

---

## 🔑 Identifiants de Test & Matrice d'Accès

| ID Utilisateur | Nom & Prénom | Fonction | Salles Autorisées |
| :--- | :--- | :--- | :--- |
| **OX-001** | Alice Dupont | Chef de Projet | `101`, `dev`, `reunion` |
| **OX-002** | Jean Martin | Développeur Senior | `101`, `dev` |
| **OX-003** | Sophie Bernard | UI/UX Designer | `101`, `reunion` |
| **OX-004** | Thomas Dubois | Ingénieur DevOps | `101`, `dev` |
| **OX-005** | Claire Moreau | Directrice Générale | `101`, `dev`, `reunion`, `directeur` |

---

## 📄 Spécification Technique
Consultez le fichier [SPEC_TECHNIQUE_FRONTOFFICE.md](SPEC_TECHNIQUE_FRONTOFFICE.md) pour la spécification technique complète du Front-Office.
