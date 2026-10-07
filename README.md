# OXMEMBER — Application Django de Chat & Visioconférence Entreprise

OXMEMBER est la plateforme web entreprise de messagerie instantanée, d'appel audio et de visioconférence WebRTC développée sous **Django** et **Django Channels** pour les collaborateurs d'**Oxalix**.

---

## ⚙️ Configuration des Variables d'Environnement (`.env`)

L'application utilise un fichier `.env` à la racine du projet pour gérer l'ensemble des paramètres de configuration.

Un exemple de fichier `.env.example` est fourni dans le dépôt.

### Liste des Variables d'Environnement :

| Variable | Description | Valeur par défaut |
| :--- | :--- | :--- |
| `SECRET_KEY` | Clé de sécurité unique de l'application Django | `django-insecure-oxmember-secret-key-oxalix-2026` |
| `DEBUG` | Mode débogage (`True` ou `False`) | `True` |
| `ALLOWED_HOSTS` | Hôtes/Domaines autorisés (séparés par des virgules) | `*` |
| `MYSQL_HOST` | Hôte du serveur MySQL (ex: `localhost` ou IP) | *(si vide, bascule sur SQLite `oxmember.db`)* |
| `MYSQL_DATABASE` | Nom de la base de données MySQL | `oxmember_db` |
| `MYSQL_USER` | Nom d'utilisateur de la base MySQL | `root` |
| `MYSQL_PASSWORD` | Mot de passe de l'utilisateur MySQL | `""` (vide) |
| `MYSQL_PORT` | Port d'écoute du serveur MySQL | `3306` |

---

## 🚀 Guide d'Installation et Lancement Étape par Étape

### 1. Préparer l'Environnement Virtuel & Dépendances
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirement.txt
```

### 2. Configurer le fichier `.env`
Copiez le fichier exemple `.env.example` vers `.env` et adaptez les valeurs si besoin :
```bash
cp .env.example .env
```

### 3. Exécuter les Migrations et Initialiser les Données
```bash
# 1. Appliquer les migrations de structure Django
python3 manage.py makemigrations
python3 manage.py migrate

# 2. Peupler la base de données avec les utilisateurs et salons de test Oxalix
python3 manage.py init_db
```

### 4. (Optionnel) Créer un Compte Administrateur Django Admin
```bash
python3 manage.py createsuperuser
```

### 5. Lancer le Serveur ASGI (Daphne / Django Channels)
```bash
python3 manage.py runserver 0.0.0.0:8000
```
L'application est immédiatement accessible sur `http://127.0.0.1:8000`.
Interface d'administration Django : `http://127.0.0.1:8000/admin`

---

## 🔑 Jeu de Test & Matrice d'Accès Back-Office

Afin de préserver la confidentialité sur la page d'accueil (login), les identifiants membres ne sont pas affichés à l'écran. Utilisez la matrice de test suivante :

| ID Utilisateur | Nom & Prénom | Fonction | Salles Autorisées |
| :--- | :--- | :--- | :--- |
| **OX-001** | Alice Dupont | Chef de Projet | `101` (Général), `dev` (Développement), `reunion` (Réunion) |
| **OX-002** | Jean Martin | Développeur Senior | `101` (Général), `dev` (Développement) |
| **OX-003** | Sophie Bernard | UI/UX Designer | `101` (Général), `reunion` (Réunion) |
| **OX-004** | Thomas Dubois | Ingénieur DevOps | `101` (Général), `dev` (Développement) |
| **OX-005** | Claire Moreau | Directrice Générale | `101` (Général), `dev`, `reunion`, `directeur` (Direction) |

---

## 📄 Spécifications Techniques

Consultez le fichier [SPEC_TECHNIQUE_FRONTOFFICE.md](SPEC_TECHNIQUE_FRONTOFFICE.md) pour la spécification complète du Front-Office et [AUDIT_ET_PREPARATION_MAJ.md](AUDIT_ET_PREPARATION_MAJ.md) pour le rapport d'audit.
