# OXMEMBER - Plateforme d'Échange, Historique MySQL & Visioconférence

**OXMEMBER** est la plateforme d'échange et de visioconférence sécurisée développée pour les collaborateurs d'**Oxalix**.

---

## 🎨 Fonctionnalités Principales & Nouveau Design

- **Interface Modèle 3 Colonnes :**
  - **Colonne de Gauche :** Titre **OXMEMBER** épuré (sans logo et sans le texte "Chat"), barre de recherche d'utilisateurs et salons avec statut en ligne.
  - **Colonne Centrale :** En-tête de conversation avec l'interlocuteur/salon (`To: Salon #...`), historique des messages persistant, bulles de messages stylisées (jaune sable `#FFF8E7` pour les destinataires, bleu clair `#E3F2FD` pour l'utilisateur), et zone de saisie avec bouton **REPLY**.
  - **Colonne de Droite :** Fiche profil de l'utilisateur connectée, panneau d'appel vidéo WebRTC rétractable et prévisualisation des fichiers et images partagés.

- **Persistance des Messages & Base de Données MySQL / SQLite :**
  - Sauvegarde automatique en base de données SQL (table `messages`).
  - Restitution immédiate de l'historique des conversations lors de la connexion à un salon via une API REST `/api/history/<room>`.
  - Support natif de **MySQL** avec bascule automatique vers SQLite pour un démarrage rapide sans configuration externe.

- **Visioconférence HD WebRTC P2P :**
  - Appels vidéo et audio en direct sans plugin externe.
  - Panneau d'incrustation vidéo (Picture-in-Picture) et boutons de contrôle (coupure micro, coupure caméra, raccrocher).

- **Sélecteur d'Emojis (Emoji Picker) :**
  - Insertion rapide d'emojis dans le champ de texte via une fenêtre popover.

---

## 🛠️ Configuration de la Base de Données MySQL

L'application supporte nativement un serveur MySQL distant ou local via **Flask-SQLAlchemy** et **PyMySQL**.

### Variables d'environnement pour MySQL :

Pour vous connecter à votre propre instance MySQL, définissez les variables d'environnement suivantes avant de lancer l'application :

```bash
export MYSQL_USER="votre_utilisateur"
export MYSQL_PASSWORD="votre_mot_de_passe"
export MYSQL_HOST="localhost"
export MYSQL_DATABASE="oxmember_db"
```

*Note : Si aucune variable MySQL n'est configurée, l'application crée et utilise automatiquement une base de données SQLite locale `instance/oxmember.db` sans aucune erreur.*

---

## ⚙️ Guide d'Installation & Démarrage Rapide

### 1. Activer l'environnement virtuel

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirement.txt
```

### 3. Lancer le serveur d'application

```bash
python app.py
```

L'application est disponible sur `http://127.0.0.1:5000`.

---

## 🧪 Le Meilleur Assistant de Test & Validation (Guide Complétif)

Ce guide permet de tester l'intégralité du système rapidement :

### Scénario 1 : Validation de l'historique et de la persistance des messages (MySQL / SQLite)
1. Ouvrez un navigateur et rendez-vous sur `http://127.0.0.1:5000`.
2. Connectez-vous sous le nom **"John Mayers"** dans le salon **101**.
3. Tapez le message : `"Bonjour l'équipe Oxalix, voici le premier message !"`. Cliquez sur **REPLY**.
4. Fermez l'onglet ou rafraîchissez la page.
5. Reconnectez-vous au salon **101** : le message précédent s'affiche immédiatement grâce au rechargement de l'historique depuis la base de données.

### Scénario 2 : Test d'échange en temps réel multi-utilisateurs
1. Ouvrez deux fenêtres de navigateur côte à côte.
2. Window 1 : Nom **"John Mayers"**, Salon **101**.
3. Window 2 : Nom **"Mike Stuart"**, Salon **101**.
4. Transmettez des messages de part et d'autre et vérifiez :
   - L'affichage instantané côté destinataire (bulle couleur sable `#FFF8E7`).
   - L'affichage côté expéditeur (bulle couleur bleu clair `#E3F2FD`).
   - L'horodatage en bas à droite de chaque message.

### Scénario 3 : Test de l'Emoji Picker
1. Cliquez sur l'icône Smile 😃 dans la barre d'outils inférieure.
2. Cliquez sur l'emoji 👍 ou 🚀.
3. Vérifiez que l'emoji s'insère dans le champ de saisie, puis envoyez-le.

### Scénario 4 : Test de l'Appel Vidéo WebRTC
1. Dans l'en-tête de discussion, cliquez sur l'icône caméra 📹.
2. Le panneau d'appel vidéo s'ouvre sur la colonne de droite.
3. Autorisez l'accès au micro/caméra. La vidéo locale s'incruste dans le coin inférieur droit.
4. Testez la coupure micro, caméra et le bouton rouge pour raccrocher.
