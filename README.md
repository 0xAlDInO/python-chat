# OXMEMBER - Plateforme de Chat & Visioconférence Oxalix

OXMEMBER est la plateforme collaborative interne d'**Oxalix**, conçue pour permettre aux employés d'échanger en temps réel via une messagerie instantanée dynamique et d'effectuer des appels vidéo (visioconférence peer-to-peer) directement depuis leur navigateur.

---

## 🚀 Fonctionnalités principales

- **Authentification & Salons de discussion (Rooms) :**
  - Connexion rapide avec un nom d'utilisateur et un numéro de salon.
  - Salons virtuels étanches permettant le regroupement par équipes ou projets.

- **Interface Utilisateur Moderne (Dark Mode OXMEMBER) :**
  - Design professionnel et épuré.
  - Différenciation claire des messages (expéditeur vs destinataires).
  - Notifications système d'arrivée de nouveaux collaborateurs dans la salle.
  - Horodatage automatique des messages.

- **Sélecteur d'Emojis (Emoji Picker) :**
  - Intégration d'une grille d'emojis popover directement accessible depuis le champ d'écriture.

- **Appel Vidéo HD (WebRTC & Socket.IO) :**
  - Établissement de visioconférence P2P temps réel entre participants d'une même chambre.
  - Incrustation vidéo locale (picture-in-picture) et flux distant HD.
  - Contrôles d'appel complets : Activer/Désactiver le microphone, Activer/Désactiver la caméra, Raccrocher.

---

## 🛠️ Environnement Requis & Prérequis

- **Python :** Version 3.8 ou supérieure.
- **Dépendances Python :**
  - `Flask`
  - `Flask-SocketIO`
  - `eventlet`

- **Navigateurs recommandés :**
  - Google Chrome, Mozilla Firefox, Microsoft Edge ou Safari (supportant WebRTC et HTML5 `getUserMedia`).

---

## ⚙️ Procédure d'installation et démarrage

### 1. Cloner ou télécharger le dépôt

```bash
git clone <url-du-repo>
cd simple-chat
```

### 2. Créer et activer un environnement virtuel (recommandé)

```bash
# Sous Linux / macOS :
python3 -m venv venv
source venv/bin/activate

# Sous Windows :
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirement.txt
```

*Remarque : si vous ajoutez des dépendances, vérifiez qu'elles figurent bien dans `requirement.txt`.*

### 4. Lancer l'application

```bash
python app.py
```

L'application démarrera par défaut sur `http://127.0.0.1:5000`.

---

## 🧪 Guide de Test & Validation

1. **Test du Chat :**
   - Ouvrez deux onglets ou fenêtres de navigateur séparés (ou deux navigateurs différents).
   - Accédez à `http://127.0.0.1:5000/`.
   - Dans le premier onglet, entrez le nom `Alice` et le salon `101`.
   - Dans le second onglet, entrez le nom `Bob` et le même salon `101`.
   - Envoyez des messages texte depuis chaque onglet pour vérifier la réception instantanée.

2. **Test des Emojis :**
   - Cliquez sur l'icône Smile 😃 dans la barre de saisie.
   - Sélectionnez un emoji. Il s'insère automatiquement dans votre message.

3. **Test des Appels Vidéo WebRTC :**
   - Dans l'un des onglets, cliquez sur le bouton **"Démarrer Appel Vidéo"** dans la barre supérieure.
   - Autorisez l'accès à la caméra et au microphone si le navigateur le demande.
   - L'appel se connecte automatiquement avec l'autre utilisateur présent dans le salon.
   - Testez les boutons du panneau vidéo : coupure micro, coupure caméra et bouton raccrocher.

---

## 🛡️ Sécurité & Confidentialité

La plateforme **OXMEMBER** est réservée à un usage professionnel interne pour les collaborateurs d'Oxalix. Les échanges audio et vidéo transitent en direct en peer-to-peer (P2P) via WebRTC.
