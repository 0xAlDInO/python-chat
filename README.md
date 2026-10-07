# OXMEMBER — Application Django de Chat & Visioconférence Entreprise

OXMEMBER est la plateforme web entreprise de messagerie instantanée, d'appel audio et de visioconférence WebRTC développée sous **Django** et **Django Channels** pour les collaborateurs d'**Oxalix**.

---

## 🚀 Fonctionnalités Principales

- **Architecture Django & Channels (ASGI) :** Migré à 100% sous le framework Web Django avec gestion asynchrone des WebSockets via Daphne/Channels.
- **Support Base de Données MySQL (avec fallback SQLite) :** Utilise PyMySQL pour la connexion directe à un serveur MySQL entreprise, ou SQLite localement.
- **Nouvelle Identité Visuelle Oxalix :** Intégration du logo officiel Trèfle Vert Oxalix (`static/logo.png`) avec sélecteur de **Mode Clair / Mode Sombre**.
- **Authentification par ID Back-Office :** Identification par ID utilisateur (ex: `OX-001`, `OX-002`) avec contrôle strict des autorisations d'accès aux salles.
- **Interface Administration Django Admin (`/admin`) :** Gestion visuelle des salons, des utilisateurs et de leurs habilitations.
- **Visioconférence & Téléphonie WebRTC Multi-participants :**
  - File d'attente d'appels en direct (**APPELS EN COURS**).
  - Support des appels **Audio** et **Vidéo** avec grille vidéo dynamique (3+ caméras).
  - Contrôle d'appel global par l'organisateur.
- **Sélecteur d'Émojis & Partage de Fichiers :** Galerie partagée et téléversement sécurisé de pièces jointes.

---

## 🛠️ Guide d'Installation et Lancement Étape par Étape

### 1. Préparer l'Environnement Virtuel
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirement.txt
```

### 2. Configuration Base de Données (MySQL ou SQLite)

#### Options A : Utilisation de SQLite (Par défaut)
Aucune variable d'environnement supplémentaire requise. SQLite sera utilisé automatiquement.

#### Option B : Utilisation de MySQL
Définissez les variables d'environnement de votre base de données MySQL :
```bash
export MYSQL_HOST="localhost"
export MYSQL_DATABASE="oxmember_db"
export MYSQL_USER="root"
export MYSQL_PASSWORD="votre_mot_de_passe"
export MYSQL_PORT="3306"
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
Interface d'administration : `http://127.0.0.1:8000/admin`

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

### Scénarios de Test Vérifiés :
1. **Accès Autorisé :**
   - Saisir `OX-002` et choisir `Salon Général (101)` ou `Salle Développement (dev)` -> Connexion réussie à l'espace de chat.
2. **Accès Refusé (Salle Non Autorisée) :**
   - Saisir `OX-002` et choisir `Salle Réunion (reunion)` -> Redirection vers la page d'accueil avec message d'alerte rouge : *"Accès refusé : L'identifiant OX-002 n'a pas l'autorisation pour la Salle Réunion (reunion)"*.
3. **Identifiant Invalide :**
   - Saisir `OX-999` -> Redirection avec message d'erreur : *"Identifiant Back-Office invalide"*.

---

## 📄 Spécifications Techniques

Consultez le fichier [SPEC_TECHNIQUE_FRONTOFFICE.md](SPEC_TECHNIQUE_FRONTOFFICE.md) pour la spécification complète de l'application et [AUDIT_ET_PREPARATION_MAJ.md](AUDIT_ET_PREPARATION_MAJ.md) pour le rapport d'audit d'architecture.
