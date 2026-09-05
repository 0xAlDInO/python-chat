# OXMEMBER — Spécification Technique Front-Office

Ce document détaille l'architecture logicielle, la description détaillée des **modules**, la cartographie des **bibliothèques** utilisées, les règles d'**autorisation par salle** ainsi que le **jeu de tests** du Front-Office de la plateforme **OXMEMBER**, l'application interne de messagerie instantanée et de visioconférence dédiée aux collaborateurs de l'entreprise **Oxalix**.

---

## 1. Description Détaillée des Modules de l'Application

Le projet est structuré autour de modules modulaires assurant la séparation des responsabilités entre le serveur d'application, la persistance des données et les vues utilisateur.

| Fichier / Module | Type | Description & Rôle Fonctionnel |
| :--- | :--- | :--- |
| **`app.py`** | **Serveur Backend (Flask / Socket.IO)** | **Module Serveur Principal :**<br/>• Configuration de l'application Flask et initialisation des extensions (`SQLAlchemy`, `SocketIO`).<br/>• Définition des modèles ORM (`User`, `Room`, `Message` et table d'association `user_rooms`).<br/>• Routage HTTP REST (`/`, `/chat`, `/upload`, `/api/user/rooms/<id>`, `/api/history/<room>`).<br/>• Contrôle strict des autorisations d'accès aux salles lors de l'authentification.<br/>• Gestionnaire d'événements Socket.IO temps réel (messages instantanés, création et suivi des appels WebRTC, signalisation P2P).<br/>• Commande CLI (`flask init-db`) pour l'initialisation et le peuplement des données Back-Office. |
| **`templates/index.html`** | **Vue Frontend (Page d'Authentification)** | **Module d'Acheminement & Contrôle d'Accès :**<br/>• Interface de connexion stylisée intégrant le thème pastel **OXMEMBER**.<br/>• Formulaire d'identification par **ID Utilisateur Back-Office** (ex: `OX-001`) et sélection de la salle.<br/>• Gestion de l'affichage des bannières d'erreur dynamiques en cas d'accès refusé ou d'identifiant inexistant. |
| **`templates/chat.html`** | **Vue Frontend (Espace de Discussion & Visioconférence)** | **Module Application Principal Front-Office :**<br/>• Disposition 3 colonnes responsive (Navigation des salons autorisés, Discussion, Profil & Appels).<br/>• Connexion temps réel Socket.IO (`recu_msg`, `announcement_join_room`).<br/>• Module Visioconférence & Téléphonie WebRTC avec file d'attente d'appels (`APPELS EN COURS`) et grille vidéo multi-participants (3+ caméras).<br/>• Module Sélecteur d'émojis (Popover interactif).<br/>• Module Téléversement de médias avec galeries partagées (`SHARED FILES`, `SHARED PHOTOS`). |
| **`requirement.txt`** | **Configuration Dépendances** | **Module de Gestion des Packages Python :** Spécifie l'ensemble des bibliothèques nécessaires à l'exécution du serveur backend en environnement virtuel. |
| **`README.md`** | **Documentation Technique** | **Guide d'Installation & Déploiement :** Fournit les instructions étape par étape pour l'installation, la configuration des bases de données (MySQL / SQLite) et l'exécution des scénarios de test. |

---

## 2. Cartographie des Bibliothèques & Leurs Fonctions

### A. Bibliothèques Backend (Python / Flask)

| Bibliothèque | Catégorie | Fonction & Rôle dans l'Application |
| :--- | :--- | :--- |
| **`Flask`** | Framework Web | Fournit le noyau d'application Web WSGI, le moteur de rendu de templates Jinja2, la gestion des requêtes HTTP, la redirection avec messages d'erreur et le routage des endpoints. |
| **`Flask-SocketIO`** | Websockets / Realtime | Permet la communication bidirectionnelle en temps réel à faible latence entre le serveur et les clients pour la messagerie instantanée et la signalisation d'appels WebRTC. |
| **`eventlet`** | Serveur Asynchrone / WSGI | Moteur d'E/S asynchrones basé sur les greenlets permettant de gérer simultanément un grand nombre de connexions Websockets actives sous Flask-SocketIO. |
| **`Flask-SQLAlchemy`** | ORM (Object-Relational Mapping) | Abstraction de la base de données permettant de manipuler les objets `User`, `Room`, `Message` et la table d'association d'autorisations `user_rooms`. |
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

## 3. Matrice d'Autorisations par Salle & Authentification Back-Office

Afin d'assurer la sécurité des échanges internes d'Oxalix, l'accès à chaque salle de discussion est strictement réglementé par la BDD du Back-Office via une relation **Many-To-Many** entre les utilisateurs et les salles.

### Matrice d'Accès Pré-Populée :

| ID Utilisateur | Nom & Prénom | Fonction Officielle | Salles Autorisées |
| :--- | :--- | :--- | :--- |
| **OX-001** | Alice Dupont | Chef de Projet | `101` (Général), `dev` (Développement), `reunion` (Réunion) |
| **OX-002** | Jean Martin | Développeur Senior | `101` (Général), `dev` (Développement) |
| **OX-003** | Sophie Bernard | UI/UX Designer | `101` (Général), `reunion` (Réunion) |
| **OX-004** | Thomas Dubois | Ingénieur DevOps | `101` (Général), `dev` (Développement) |
| **OX-005** | Claire Moreau | Directrice Générale | `101` (Général), `dev`, `reunion`, `directeur` (Direction) |

### Règle de Gestion des Erreurs :
1. **Confidentialité lors de la Saisie :** Le nom de l'utilisateur **n'est pas affiché publiquement** sur la page de connexion lors de la saisie de l'ID.
2. **Si l'ID n'existe pas :** L'utilisateur est redirigé vers `/` avec le message d'erreur :
   `"Identifiant 'OX-999' inexistant dans la base Back-Office."`
3. **Si l'utilisateur n'a pas accès à la salle :** L'accès est refusé et le serveur redirige avec le message :
   `"Accès refusé : L'identifiant OX-002 n'a pas l'autorisation pour la Salle Réunion (reunion)."`

---

## 4. Jeu de Tests (Test Suite & Verification)

Le tableau ci-dessous constitue le jeu de tests fonctionnels pour valider l'étanchéité du système d'authentification et d'autorisation :

| N° Test | ID Utilisateur | Salle Ciblée | Résultat Attendu | Statut |
| :---: | :---: | :---: | :--- | :---: |
| **TC-01** | `OX-001` | `dev` | **Succès :** Redirection vers `/chat`. Affichage d'Alice Dupont (Chef de Projet). | **PASSED** |
| **TC-02** | `OX-002` | `reunion` | **Échec :** Redirection vers `/`. Alerte *"Accès refusé : OX-002 n'a pas l'autorisation pour la Salle Réunion"*. | **PASSED** |
| **TC-03** | `OX-003` | `dev` | **Échec :** Redirection vers `/`. Alerte *"Accès refusé : OX-003 n'a pas l'autorisation pour la Salle Développement"*. | **PASSED** |
| **TC-04** | `OX-005` | `directeur` | **Succès :** Redirection vers `/chat`. Seule Claire Moreau (Direction) accède à cette salle. | **PASSED** |
| **TC-05** | `OX-999` | `101` | **Échec :** Redirection vers `/`. Alerte *"Identifiant 'OX-999' inexistant dans la base Back-Office"*. | **PASSED** |
| **TC-06** | `OX-001` | `salle-inconnue` | **Échec :** Redirection vers `/`. Alerte *"La salle 'salle-inconnue' n'existe pas"*. | **PASSED** |

---

## 5. Ergonomie & Interface Graphique (Layout 3 Colonnes)

L'interface du Front-Office (`chat.html`) utilise une structure responsive **100% Fullscreen (100vw x 100vh)** aux tons pastel clairs (dégradé violet/bleu `#E0C3FC` vers `#8EC5FC`).

### Structure des Colonnes :

```
+------------------+----------------------------------+------------------+
|                  |                                  |                  |
|  PANNEAU GAUCHE  |         PANNEAU CENTRAL          |   PANNEAU DROIT  |
|     (280px)      |             (Flex 1)             |     (320px)      |
|                  |                                  |                  |
| - Titre OXMEMBER | - En-tête du salon               | - Profil membre  |
| - Salons Autorisé| - Flux des messages (Sable/Bleu) | - Ecran vidéo    |
| - Barre recherche| - Sélecteur d'émojis (Popover)   | - Appels en cours|
|                  | - Zone de saisie & Téléversement | - Fichiers/Photos|
|                  |                                  |                  |
+------------------+----------------------------------+------------------+
```

---

## 6. Spécifications des Appels Audio & Vidéo WebRTC

1. **Aucune Pop-up Intrusive :** Les appels audio et vidéo sont publiés dans la section **APPELS EN COURS** du panneau droit.
2. **Rejoindre un Appel :** Bouton **Rejoindre** dynamique pour tous les membres autorisés.
3. **Affichage Multi-Participants :** Grille vidéo dynamique adaptative pour 3 participants ou plus.
4. **Fermeture d'Appel :** La fin d'appel par le créateur/hôte met fin à la session pour tous les participants.
