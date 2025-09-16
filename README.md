# Game Jam ESIEE 2025

Mini-jeu réalisé pour la Game Jam 2025 sur le thème : **"Vous n'êtes pas au centre de l'histoire"**.

## 🎮 Description
Le projet contient plusieurs mini-scènes :
- **Au centre du mot** : une barre bouge automatiquement et vous devez l'arrêter au centre exact du mot **HISTOIRE**.
- **La pomme de Newton** : arrêtez la chute d'une pomme exactement à mi-hauteur de sa trajectoire.

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
python -m game.main
```
Ou conservez la compatibilité existante :
```bash
python game_jam.py
```

## 📂 Arborescence
```text
.
├─ game/                        # Package principal
│  ├─ __init__.py
│  ├─ config.py                 # Constantes et chemins
│  ├─ core.py                   # Game loop & base Scene
│  ├─ utils.py                  # Helpers (blit, clamp, load_image/sound)
│  ├─ main.py                   # Entrypoint (python -m game.main)
│  ├─ minigames/                # Système de minijeux + enregistrements
│  │  ├─ __init__.py
│  │  ├─ base.py                # Interface MiniGame + registre
│  │  ├─ center_word/           # Mini-jeu "Au centre du mot"
│  │  │  ├─ __init__.py         # Enregistrement du minijeu
│  │  │  └─ scene.py            # Scene du mini-jeu
│  │  └─ newton_apple/          # Mini-jeu "La pomme de Newton"
│  │     ├─ __init__.py         # Enregistrement du minijeu
│  │     └─ scene.py            # Scene du mini-jeu
│  └─ scenes/
│     ├─ __init__.py
│     ├─ menu.py                # MenuScene
│     ├─ center_word.py         # CenterWordScene
│     └─ session.py             # SessionScene (enchaîne 5 mini-jeux)
├─ game_jam.py                  # Wrapper: lance game.main
├─ requirements.txt             # Dépendances Python
├─ assets/
│  ├─ images/                   # Images pour la galerie
│  └─ sounds/                   # Effets sonores (click.wav, success.wav, fail.wav)
└─ README.md                    # Ce fichier
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

---

👾 Bon jeu, et souvenez-vous : **Vous n'êtes pas au centre de l'histoire** 😉