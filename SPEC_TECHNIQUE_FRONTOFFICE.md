# OXMEMBER — Spécification Technique Front-Office

Ce document détaille l'architecture logicielle, la description détaillée des **modules**, la cartographie des **bibliothèques** utilisées ainsi que les spécifications fonctionnelles du Front-Office de la plateforme **OXMEMBER**, l'application interne de messagerie instantanée et de visioconférence dédiée aux collaborateurs de l'entreprise **Oxalix**.

---

## 1. Description Détaillée des Modules de l'Application

Le projet est structuré autour de modules modulaires assurant la séparation des responsabilités entre le serveur d'application, la persistance des données et les vues utilisateur.

| Fichier / Module | Type | Description & Rôle Fonctionnel |
| :--- | :--- | :--- |
| **`app.py`** | **Serveur Backend (Flask / Socket.IO)** | **Module Serveur Principal :**<br/>• Configuration de l'application Flask et initialisation des extensions (`SQLAlchemy`, `SocketIO`).<br/>• Définition des modèles ORM (`User`, `Message`).<br/>• Routage HTTP REST (`/`, `/chat`, `/upload`, `/api/user/<id>`, `/api/history/<room>`).<br/>• Gestionnaire d'événements Socket.IO temps réel (messages instantanés, création et suivi des appels WebRTC, signalisation P2P).<br/>• Commande CLI (`flask init-db`) pour l'initialisation et le peuplement des données Back-Office. |
| **`templates/index.html`** | **Vue Frontend (Page d'Authentification)** | **Module d'Acheminement & Identification :**<br/>• Interface de connexion stylisée intégrant le thème pastel **OXMEMBER**.<br/>• Formulaire d'identification par **ID Utilisateur Back-Office** (ex: `OX-001`) et choix du salon.<br/>• Script JavaScript de prévisualisation dynamique interrogeant l'API `/api/user/<id>` pour afficher le nom complet et la fonction de l'employé avant connexion. |
| **`templates/chat.html`** | **Vue Frontend (Espace de Discussion & Visioconférence)** | **Module Application Principal Front-Office :**<br/>• Disposition 3 colonnes responsive (Navigation, Discussion, Profil & Appels).<br/>• Connexion temps réel Socket.IO (`recu_msg`, `announcement_join_room`).<br/>• Module Visioconférence & Telephonie WebRTC avec file d'attente d'appels (`APPELS EN COURS`) et grille vidéo multi-participants.<br/>• Module Sélecteur d'émojis (Popover interactif).<br/>• Module Téléversement de médias avec galeries partagées (`SHARED FILES`, `SHARED PHOTOS`). |
| **`requirement.txt`** | **Configuration Dépendances** | **Module de Gestion des Packages Python :** Spécifie l'ensemble des bibliothèques nécessaires à l'exécution du serveur backend en environnement virtuel. |
| **`README.md`** | **Documentation Technique** | **Guide d'Installation & Déploiement :** Fournit les instructions étape par étape pour l'installation, la configuration des bases de données (MySQL / SQLite) et l'exécution des tests. |

---

## 2. Cartographie des Bibliothèques & Leurs Fonctions

### A. Bibliothèques Backend (Python / Flask)

| Bibliothèque | Catégorie | Fonction & Rôle dans l'Application |
| :--- | :--- | :--- |
| **`Flask`** | Framework Web | Fournit le noyau d'application Web WSGI, le moteur de rendu de templates Jinja2, la gestion des requêtes HTTP et le routage des endpoints. |
| **`Flask-SocketIO`** | Websockets / Realtime | Permet la communication bidirectionnelle en temps réel à faible latence entre le serveur et les clients pour la messagerie instantanée et la signalisation d'appels WebRTC. |
| **`eventlet`** | Serveur Asynchrone / WSGI | Moteur d'E/S asynchrones basé sur les greenlets permettant de gérer simultanément un grand nombre de connexions Websockets actives sous Flask-SocketIO. |
| **`Flask-SQLAlchemy`** | ORM (Object-Relational Mapping) | Abstraction de la base de données permettant de manipuler les objets `User` et `Message` en Python sans écrire de requêtes SQL brutes. |
| **`PyMySQL`** | Pilote BDD MySQL | Connecteur SQL purement Python permettant à SQLAlchemy d'interagir directement avec un serveur de base de données MySQL ou MariaDB. |
| **`Werkzeug`** | Utilitaires Web | Fournit des fonctions de sécurité essentielles comme `secure_filename()` pour nettoyer les noms de fichiers téléversés et prévenir les failles de traversée de répertoire. |

### B. Bibliothèques & API Frontend (Client JS / CSS)

| Bibliothèque / API | Type | Fonction & Rôle dans l'Application |
| :--- | :--- | :--- |
| **`Socket.IO Client`** (`/socket.io.js`) | Client Websocket JS | Maintient la connexion temps réel avec le serveur Flask, écoute et émet les événements de chat (`envoie_message`, `recu_msg`) et de signalisation d'appels. |
| **`WebRTC API`** (`RTCPeerConnection`, `getUserMedia`) | API Navigateur Native | Assure la capture audio/vidéo matérielle du microphone/caméra de l'utilisateur et établit les connexions peer-to-peer chiffrées pour les flux vidéo/audio en direct. |
| **`Font Awesome`** (`font-awesome/6.4.0`) | CDN Icônes Vectorielles | Fournit l'ensemble des icônes graphiques de l'interface (caméra, téléphone, trombone, image, recherche, smileys, bouton de déconnexion). |
| **`Google Fonts Inter`** | Typographie Web | Police de caractères moderne et lisible optimisée pour les interfaces utilisateur d'entreprise SaaS. |

---

## 3. Authentification & Données Back-Office

L'accès au Front-Office s'effectue via l'identifiant unique attribué par le Back-Office (ex: `OX-001`, `OX-002`, `OX-003`).

### Fonctionnement :
1. **Saisie de l'ID :** Sur la page d'accueil (`index.html`), l'utilisateur renseigne son **ID Utilisateur** et le **Salon de discussion** souhaité.
2. **Prévisualisation dynamique :** Le Front-Office interroge l'API du serveur (`/api/user/<user_id>`) pour afficher en temps réel le nom, le prénom et la fonction de l'employé avant validation.
3. **Récupération des attributs :** À la validation, les informations officielles transmises au chat sont :
   - **ID Utilisateur** (ex: `OX-001`)
   - **Nom complet** (ex: `Alice Dupont`)
   - **Fonction officielle** (ex: `Chef de Projet`)

### Base d'exemples d'employés Back-Office :
| ID Utilisateur | Nom & Prénom | Fonction Officielle |
| :--- | :--- | :--- |
| **OX-001** | Alice Dupont | Chef de Projet |
| **OX-002** | Jean Martin | Développeur Senior |
| **OX-003** | Sophie Bernard | UI/UX Designer |
| **OX-004** | Thomas Dubois | Ingénieur DevOps |
| **OX-005** | Claire Moreau | Responsable Produit |

---

## 4. Ergonomie & Interface Graphique (Layout 3 Colonnes)

L'interface du Front-Office (`chat.html`) utilise une structure responsive **100% Fullscreen (100vw x 100vh)** aux tons pastel clairs (dégradé violet/bleu `#E0C3FC` vers `#8EC5FC`).

### Structure des Colonnes :

```
+------------------+----------------------------------+------------------+
|                  |                                  |                  |
|  PANNEAU GAUCHE  |         PANNEAU CENTRAL          |   PANNEAU DROIT  |
|     (280px)      |             (Flex 1)             |     (320px)      |
|                  |                                  |                  |
| - Titre OXMEMBER | - En-tête du salon               | - Profil membre  |
| - Onglets Nav    | - Flux des messages (Sable/Bleu) | - Ecran vidéo    |
| - Barre recherche| - Sélecteur d'émojis (Popover)   | - Appels en cours|
| - Liste salons   | - Zone de saisie & Téléversement | - Fichiers/Photos|
|                  |                                  |                  |
+------------------+----------------------------------+------------------+
```

1. **Panneau Gauche (Sidebar Contacts - 280px) :**
   - Marque **OXMEMBER** en typographie bold.
   - Navigation par onglets (`CHATS`, `CONTACTS`, `FAVORIS`).
   - Champ de recherche d'utilisateurs et statut en ligne (pastille verte).

2. **Panneau Central (Flux de Chat - Flex 1) :**
   - En-tête indiquant le nom du salon et contrôles d'appel rapide.
   - Bulles de messages personnalisées :
     - **Sable doux (`#FFF8E7`)** pour les messages reçus.
     - **Bleu doux (`#E3F2FD`)** pour les messages envoyés.
   - Zone de saisie avec bouton **REPLY**, popover émojis et icônes d'import de fichiers.

3. **Panneau Droit (Profil & Appels - 320px) :**
   - Carte profil affichant le nom complet et la fonction de l'utilisateur connecté.
   - Fenêtre d'appel vidéo/audio active avec grilles vidéo.
   - File d'attente des appels en cours (**APPELS EN COURS**).
   - Galeries **SHARED FILES** et **SHARED PHOTOS**.

---

## 5. Spécifications des Appels Audio & Vidéo WebRTC

L'application intègre une visioconférence et téléphonie IP basées sur les standards **WebRTC** et **Socket.IO**.

### Fonctionnalités :

1. **Aucune Pop-up Intrusive :**
   - Lorsqu'un utilisateur démarre un appel vidéo ou audio via les icônes d'en-tête, l'appel est directement publié dans la liste **APPELS EN COURS** du panneau droit de tous les membres du salon.

2. **File d'Attente des Appels (Calls Queue) :**
   - Chaque carte d'appel indique le créateur de l'appel (ex: *Appel Vidéo de Alice*), le type (*Vidéo* ou *Audio*), et la liste des participants connectés avec leur nombre exact.
   - Les autres membres du salon peuvent cliquer sur **Rejoindre** à tout moment.

3. **Affichage Multi-Participants (Grid System 3+ Participants) :**
   - Pour les appels vidéo comprenant 3 participants ou plus, le composant vidéo ajuste dynamiquement sa grille (`grid-template-columns: repeat(auto-fit, minmax(110px, 1fr))`) pour afficher simultanément les caméras de tous les membres en direct.

4. **Contrôles d'Appel :**
   - Bouton Mute / Unmute du microphone.
   - Bouton Activation / Désactivation de la caméra vidéo.
   - Bouton de fin d'appel (Téléphone rouge).

5. **Règles de Fermeture d'Appel :**
   - Si un participant secondaire quitte l'appel, son flux est retiré de la grille sans affecter les autres participants.
   - **Si l'organisateur/créateur de l'appel quitte, l'appel est automatiquement terminé pour l'ensemble des participants.**

---

## 6. Sélecteur d'Emojis & Gestion des Médias Partagés

### Popover d'Emojis :
- Un panneau rétractable s'ouvre au clic sur le bouton Smile et propose une sélection rapide des émojis les plus courants (`😃`, `😂`, `😊`, `😍`, `👍`, `👏`, `🔥`, `✨`, `🎉`, `❤️`, `🙌`, `💡`, `😎`, `🚀`, `🙏`).
- Le clic sur un émoji l'insère à la position actuelle du champ de saisie.

### Téléversement de Fichiers & Images :
- **Images (PNG, JPG, GIF, WebP) :** Affichées sous forme de miniature intégrée dans la bulle de chat (agrandissable au clic) et automatiquement ajoutées en haut de la galerie **SHARED PHOTOS**.
- **Documents (PDF, XLSX, DOCX...) :** Affichés sous forme de lien de téléchargement direct dans la bulle et ajoutés à la liste **SHARED FILES**.
- **Comportement au Démarrage :** Les listes **SHARED FILES** et **SHARED PHOTOS** du panneau droit sont **initialement vides** à l'entrée dans un salon et se complètent dynamiquement au cours des échanges.

---

## 7. Historique & Persistance des Données

- Les messages, fichiers joints et horodatages sont enregistrés de manière permanente en BDD via **Flask-SQLAlchemy**.
- Support natif de **MySQL** avec bascule automatique sur une base **SQLite** locale (`oxmember.db`) en l'absence de variable d'environnement MySQL.
- Lors de l'entrée dans un salon, l'historique complet est automatiquement rechargé via l'API REST `/api/history/<room>`.
