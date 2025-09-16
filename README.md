# Game Jam ESIEE 2025

Mini-jeu réalisé pour la Game Jam 2025 sur le thème : **"Vous n'êtes pas au centre de l'histoire"**.

## 🎮 Description
Le projet contient plusieurs mini-scènes :
- **Centre du mot** : une barre bouge automatiquement et vous devez l'arrêter au centre exact du mot **HISTOIRE**.
- **Galerie d'images** : affiche les images placées dans `assets/images/`.
- **Verre à remplir** : maintenez ESPACE pour remplir un verre d'eau sans déborder.

## ⚙️ Installation
### 1. Cloner le dépôt
```bash
git clone https://github.com/tiago-narciso/game_jam_esiee_2025.git
cd game_jam_esiee_2025
```

### 2. Créer un environnement virtuel
```bash
python -m venv .venv
```

### 3. Activer l'environnement virtuel
- **Linux / macOS** :
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell)** :
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

### 4. Installer les dépendances
```bash
pip install -r requirements.txt
```

## 🚀 Lancer le jeu
Depuis la racine du projet (avec le venv activé) :
```bash
python game_jam.py
```

## 📂 Arborescence
```text
.
├─ game_jam.py           # Script principal
├─ requirements.txt      # Dépendances Python
├─ assets/
│  ├─ images/            # Images pour la galerie
│  └─ sounds/            # Effets sonores (click.wav, success.wav, fail.wav)
└─ README.md             # Ce fichier
```

## 🎵 Assets
- Placez vos **images** dans `assets/images/` (formats supportés : .png, .jpg, .jpeg, .bmp, .gif).
- Placez vos **sons** dans `assets/sounds/` (`click.wav`, `success.wav`, `fail.wav`).
- Si les fichiers n’existent pas, le jeu utilisera des placeholders (placeholders silencieux ou visuels).

## ⌨️ Contrôles
### Menu principal
- `↑ / ↓` : naviguer
- `Entrée` : sélectionner
- `Échap` : quitter

### Centre du mot
- `Espace` ou clic : arrêter le curseur
- `R` : rejouer
- `M` ou `Échap` : retour menu

### Galerie d’images
- `← / →` : naviguer entre les images
- `M` ou `Échap` : retour menu

### Verre à remplir
- `Espace` : remplir le verre (relâcher pour arrêter)
- `R` : rejouer
- `M` ou `Échap` : retour menu

---

👾 Bon jeu, et souvenez-vous : **Vous n'êtes pas au centre de l'histoire** 😉