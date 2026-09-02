# OXMEMBER - Guide d'Utilisation Base de Données & Téléversement de Fichiers

**OXMEMBER** est la plateforme d'échange, de visioconférence et de partage de fichiers développée pour les collaborateurs d'**Oxalix**.

---

## 🗄️ Guide d'Utilisation de la Base de Données (MySQL & SQLite)

L'application intègre **Flask-SQLAlchemy** pour la persistance complète des messages, des fichiers et des salons.

### 1. Structure de la Base de Données

La table `messages` est automatiquement créée au démarrage de l'application :

```sql
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL,
    room VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    file_url VARCHAR(255) NULL,
    file_type VARCHAR(20) NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Utilisation avec MySQL

Pour connecter l'application à votre serveur **MySQL** (local ou serveur distant) :

1. Créez la base de données dans votre serveur MySQL :
   ```sql
   CREATE DATABASE oxmember_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. Exportez les variables d'environnement dans votre terminal avant de lancer l'application :
   ```bash
   # Sous Linux / macOS :
   export MYSQL_USER="votre_utilisateur"
   export MYSQL_PASSWORD="votre_mot_de_passe"
   export MYSQL_HOST="localhost"
   export MYSQL_DATABASE="oxmember_db"

   # Sous Windows (PowerShell) :
   $env:MYSQL_USER="votre_utilisateur"
   $env:MYSQL_PASSWORD="votre_mot_de_passe"
   $env:MYSQL_HOST="localhost"
   $env:MYSQL_DATABASE="oxmember_db"
   ```

3. Ou fournissez une URL de connexion SQL directe :
   ```bash
   export DATABASE_URL="mysql+pymysql://utilisateur:motdepasse@localhost:3306/oxmember_db"
   ```

### 3. Mode de Repli SQLite Automatique (Sans Configuration)

Si vous ne définissez aucune variable MySQL (`MYSQL_HOST`), l'application bascule automatiquement sur une base de données **SQLite** locale stockée dans le fichier `instance/oxmember.db`. **Aucune installation ou configuration préalable de MySQL n'est requise pour tester l'application.**

---

## 📁 Guide d'Utilisation du Téléversement d'Images et de Fichiers (File/Image Upload)

L'application prend en charge l'envoi d'images (PNG, JPG, GIF, WebP) et de documents (PDF, XLSX, DOCX, TXT, etc.).

### 1. Fonctionnement du Téléversement

1. Dans la zone de saisie du chat, cliquez sur l'icône **Image** 🖼️ ou **Fichier/Trombone** 📎.
2. Sélectionnez votre fichier sur votre appareil.
3. Le fichier est automatiquement envoyé vers le serveur via la route HTTP POST `/upload` (limite max 16 Mo).
4. Le fichier est stocké dans le répertoire `static/uploads/`.
5. Un message WebSocket est diffusé instantanément à tous les participants du salon avec le lien du fichier ou la prévisualisation de l'image.

### 2. Galerie Automatique du Panneau Latéral
- Les images téléchargées s'affichent directement dans les bulles du chat et s'ajoutent à la galerie **SHARED PHOTOS** dans le panneau latéral droit.
- Les documents téléchargés s'affichent sous forme de bouton de téléchargement direct et s'ajoutent à la liste **SHARED FILES**.

---

## ⚙️ Procédure Rapide de Démarrage

### 1. Installer les dépendances

```bash
pip install -r requirement.txt
```

### 2. Démarrer l'application

```bash
python app.py
```

Accédez à l'application dans votre navigateur : `http://127.0.0.1:5000`.

---

## 🧪 Scénarios de Test et d'Assistance

### Scénario 1 : Test du Téléversement d'Image et de Document
1. Connectez-vous sur `http://127.0.0.1:5000` avec le nom **John Mayers** dans le salon **101**.
2. Cliquez sur l'icône Image 🖼️ en bas à gauche de la zone d'écriture.
3. Choisissez une photo. L'image apparaît directement dans la discussion et s'ajoute à la section **SHARED PHOTOS** à droite.
4. Cliquez sur l'icône Trombone 📎 pour envoyer un document PDF. Le fichier apparaît sous forme de lien de téléchargement.

### Scénario 2 : Test de l'Historique de Base de Données
1. Après avoir envoyé quelques messages et fichiers, rafraîchissez votre navigateur (F5).
2. L'ensemble des messages et des fichiers envoyés est réaffiché automatiquement grâce à l'API de rechargement d'historique `/api/history/101`.
