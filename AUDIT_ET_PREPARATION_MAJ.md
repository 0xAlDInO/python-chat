# Audit Approfondi & Guide de Préparation à la Mise à Jour — OXMEMBER

## 1. Résumé Exécutif & Objectifs de l'Analyse

Le présent document constitue l'analyse technique approfondie du projet **OXMEMBER** en vue de préparer sereinement de futures évolutions fonctionnelles et esthétiques sans risquer d'altérer le fonctionnement existant.

### Objectifs Principaux
1. **Évaluation de l'Architecture Existant :** Analyser le couplage entre Flask, Flask-SocketIO, SQLAlchemy et les flux WebRTC P2P.
2. **Identification des Zones à Risque :** Cartographier les goulots d'étranglement, les failles potentielles et la dette technique.
3. **Spécification d'Intégration du Nouveau Logo & Modes Visuels :** Définir la stratégie d'intégration de la nouvelle identité visuelle **OXALIX** (Logo Trèfle Vert & Typographie) pour le **Mode Clair** et le **Mode Sombre**.
4. **Feuille de Route & Recommandations de Déploiement :** Établir le plan d'action étape par étape pour sécuriser les futures mises à jour.

---

## 2. Cartographie de l'Architecture & Dépendances

### Stack Technique Backend & Frontend
```
                  +-----------------------------------+
                  |   Navigateur Client (Web App)     |
                  |  - HTML5 / CSS3 (Variables)       |
                  |  - Socket.IO Client JS            |
                  |  - WebRTC Native API              |
                  +-----------------+-----------------+
                                    |
            +-----------------------+-----------------------+
            | HTTP REST API                                 | Websockets (Realtime)
            v                                               v
+-----------------------+                       +-----------------------+
|  Flask Application    |                       | Flask-SocketIO        |
|  - Auth & Controller  |                       | - Chat Messages       |
|  - File Uploads       |                       | - WebRTC Signaling    |
|  - DB Routing         |                       | - Call State (RAM)    |
+-----------+-----------+                       +-----------+-----------+
            |                                               |
            +-----------------------+-----------------------+
                                    |
                                    v
                        +-----------------------+
                        |  Flask-SQLAlchemy     |
                        |  (MySQL / SQLite)     |
                        +-----------------------+
```

### Inventaire des Fichiers & Dépendances

| Fichier / Dossier | Rôle Fonctionnel | Statut / Risque lors de la Maj |
| :--- | :--- | :--- |
| `app.py` | Serveur backend principal, routes, événements Socket.IO, ORM SQLAlchemy | **Élevé** (Contient la logique d'état réseau et BDD) |
| `templates/index.html` | Page de connexion / Authentification | **Moyen** (Impacté par la nouvelle charte graphique) |
| `templates/chat.html` | Interface 3 colonnes, WebRTC, Chat | **Élevé** (Complexité JS/CSS élevée) |
| `static/logo.png` | Nouvel asset du logo Oxalix (Trèfle Vert + Texte) | **Faible** (Asset statique ajouté) |
| `static/uploads/` | Stockage des pièces jointes et images partagées | **Moyen** (Persistance des données utilisateurs) |
| `requirement.txt` | Dépendances Python (`Flask`, `Flask-SocketIO`, `eventlet`, etc.) | **Moyen** (Versionning à stabiliser) |

---

## 3. Analyse Modulaire et Flux de Données

### 3.1 Authentification & Autorisations
- **Mécanisme :** Authentification basée sur l'identifiant employé (`user_id`, ex: `OX-001`).
- **Contrôle d'Accès :** Relation N:N via la table `user_rooms`. La route `/chat` effectue 3 vérifications strictes :
  1. Existence de l'utilisateur (`User.query.filter_by(id=user_id)`).
  2. Existence de la salle (`Room.query.filter_by(id=room_id)`).
  3. Habilitation de l'utilisateur pour la salle demandée (`room in user.authorized_rooms`).
- **Incapacité d'Affichage Direct :** Aucune liste globale d'utilisateurs n'est divulguée sur la page de login pour des raisons de confidentialité entreprise.

### 3.2 Messagerie Temps Réel & Historique
- **Événement `envoie_message` :** Reçoit le message, persiste dans la table `messages` via SQLAlchemy, puis diffuse via `recu_msg` à tous les clients connectés dans la room.
- **Restauration d'historique :** Apporté au chargement du client via l'endpoint REST `/api/history/<room>`.

### 3.3 Signalisation WebRTC Multi-participants
- **Gestion des appels en mémoire (`active_calls`) :** Les sessions d'appels sont enregistrées dans un dictionnaire global en mémoire vive backend.
- **Signalisation Peer-to-Peer (`webrtc_signal`) :** Le serveur transmet les offres (`offer`), réponses (`answer`) et candidats ICE (`candidate`) aux participants cibles sans intercepter le flux vidéo/audio.

---

## 4. Matrice des Risques de Régression & Points de Vigilance

| N° | Zone de Risque | Description du Problème | Impact | Action Corrective Préventive |
| :---: | :--- | :--- | :---: | :--- |
| **R-01** | **Volatilité de l'état des appels** | Les appels en cours (`active_calls`) sont stockés dans un dictionnaire Python en mémoire dans `app.py`. En cas de redémarrage du serveur, les appels sautent. | **Élevé** | Découpler l'état des appels vers Redis ou SQLite en cas de montée en charge. |
| **R-02** | **Avertissement de dépréciation Eventlet** | Python 3.12 émet un avertissement `EventletDeprecationWarning` au démarrage. | **Moyen** | Anticiper la migration vers `gevent` ou un serveur ASGI (ex: `Uvicorn` / `Gunicorn` + `gevent`). |
| **R-03** | **Sécurité des Téléversements** | Les fichiers téléchargés dans `/upload` sont filtrés par extension mais pourraient engendre des surcharges disques sans nettoyage automatisé. | **Moyen** | Implémenter une tâche de nettoyage périodique dans `static/uploads/`. |
| **R-04** | **Adaptation Graphique / CSS** | Les couleurs vives actuelles (dégradé violet/bleu `#E0C3FC` -> `#8EC5FC`) doivent intégrer le nouveau logo Trèfle Vert Oxalix en mode clair et sombre. | **Faible** | Utiliser une architecture de variables CSS réutilisables (`:root` et `[data-theme="dark"]`). |

---

## 5. Spécification Technique : Intégration du Logo & Mode Clair / Sombre

Le nouveau logo officiel (`Green Clover OXALIX Logo.png` copié vers `static/logo.png`) se compose :
- D'un **Trèfle à 3 feuilles vert dégradé**.
- Du texte **OXALIX** en typographie moderne blanche ou sombre selon le fond.

### 5.1 Architecture des Themes CSS (Mode Clair & Mode Sombre)

Afin d'adapter parfaitement l'interface au logo sans casser le design actuel, les variables CSS de `index.html` et `chat.html` doivent être restructurées comme suit :

```css
/* Mode Clair (Par défaut) */
:root {
    --primary-green: #10B981;
    --primary-green-hover: #059669;
    --bg-gradient: linear-gradient(135deg, #E0C3FC 0%, #8EC5FC 100%);
    --card-bg: rgba(255, 255, 255, 0.95);
    --app-bg: #FFFFFF;
    --sidebar-left-bg: #F8FAFC;
    --sidebar-right-bg: #FFFFFF;
    --text-main: #1E293B;
    --text-muted: #64748B;
    --border-color: #E2E8F0;
    --logo-filter: none; /* Logo couleur originale avec texte adapté */
}

/* Mode Sombre (Dark Mode) */
[data-theme="dark"] {
    --bg-gradient: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    --card-bg: rgba(30, 41, 59, 0.95);
    --app-bg: #0F172A;
    --sidebar-left-bg: #1E293B;
    --sidebar-right-bg: #1E293B;
    --text-main: #F8FAFC;
    --text-muted: #94A3B8;
    --border-color: #334155;
    --bubble-other: #334155;
    --bubble-me: #1E3A8A;
}
```

### 5.2 Emplacements d'Intégration du Logo
1. **Page de Login (`index.html`) :**
   - Remplacement du titre texte `OXMEMBER` par l'élément image `<img src="/static/logo.png" alt="Oxalix Logo" class="brand-logo">`.
   - Ajout d'un bouton de basculement Theme Switcher (Clair/Sombre) en haut à droite.

2. **Sidebar Gauche du Chat (`chat.html`) :**
   - Remplacement du texte `OXMEMBER` par le logo corporate intégrant le Trèfle Vert Oxalix (`/static/logo.png`).

---

## 6. Plan de Tests & Validation de Non-Régression

Avant de valider toute mise à jour en production, le plan de qualification suivant doit être exécuté :

| Réf. Test | Scénario à Tester | Action | Résultat Attendu |
| :---: | :--- | :--- | :--- |
| **TC-01** | Initialisation BDD | `flask init-db` | Tables créées et données de test (utilisateurs `OX-001` à `OX-005`) insérées sans erreur. |
| **TC-02** | Login Autorisé | Connexion avec `OX-001` dans `dev` | Accès autorisé, redirection vers `/chat`. |
| **TC-03** | Login Refusé (Salle) | Connexion avec `OX-002` dans `reunion` | Redirection `/` avec alerte rouge d'accès refusé. |
| **TC-04** | Envoi de Message Chat | Saisie message texte dans le chat | Réception instantanée via WebSockets. |
| **TC-05** | Téléversement Fichier | Envoi d'une image PNG | Affichage miniature dans le chat et dans `SHARED PHOTOS`. |
| **TC-06** | Appel Vidéo WebRTC | Clic sur bouton Vidéo | Création de la carte dans `APPELS EN COURS` et ouverture du canal WebRTC. |
| **TC-07** | Mode Sombre / Clair | Basculement via le bouton thème | Adaptation instantanée des couleurs et lisibilité parfaite du logo Oxalix. |

---

## 7. Feuille de Route pour la Mise à Jour Utile (Roadmap)

```
+-------------------------------------------------------------------+
| PHASE 1 : Préparation & Assets (Terminée)                         |
| - Copie et validation du logo Oxalix dans static/logo.png         |
| - Rédaction de l'audit et spécifications d'évolution               |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| PHASE 2 : Refactoring CSS & Thèmes (Prochaine étape)              |
| - Mise en place des variables CSS Light / Dark Mode               |
| - Intégration du logo static/logo.png dans index.html et chat.html|
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
| PHASE 3 : Consolidation Backend & Sécurité                        |
| - Validation de l'isolation du stockage static/uploads/          |
| - Ajout de tests unitaires automatisés pour les autorisations     |
+-------------------------------------------------------------------+
```

---
*Rapport d'audit et guide de mise à jour finalisé pour le projet OXMEMBER / Oxalix.*
