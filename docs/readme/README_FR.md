<p align="center">
  <img src="../../assets/banner.png" alt="MERIDIAN Banner" width="800" onerror="this.style.display='none'">
</p>

<h1 align="center">🌐 MERIDIAN · 子午线</h1>

<p align="center"><strong>Plusieurs Mondes. Un Seul Appareil.</strong></p>
<p align="center"><em>诸界 · 一器 · Many Worlds. One Device.</em></p>

<p align="center">
  <img src="https://github.com/CrescentXiong-1/MERIDIAN/actions/workflows/ci.yml/badge.svg" alt="Statut CI">
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python">
  <img src="https://img.shields.io/badge/pygame-2.x-green" alt="Pygame">
  <img src="https://img.shields.io/badge/licence-MIT-yellow" alt="Licence">
  <img src="https://img.shields.io/badge/tests-50%2B-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/lignes-~15%20700-orange" alt="Lignes de code">
</p>

<p align="center">
  <a href="../../README.md">中文</a> |
  <a href="README_EN.md">English</a> |
  <strong>Français</strong> |
  <a href="README_RU.md">Русский</a> |
  <a href="README_IT.md">Italiano</a> |
  <a href="README_JA.md">日本語</a> |
  <a href="README_AR.md">العربية</a>
</p>

---

## 📖 Table des matières

- [Introduction](#-introduction)
- [Univers](#-univers)
- [Les Mondes Connectés](#-les-mondes-connectés)
- [Fonctionnalités](#-fonctionnalités)
- [Démarrage rapide](#-démarrage-rapide)
- [Contrôles](#-contrôles)
- [Structure du projet](#-structure-du-projet)
- [Architecture](#-architecture)
- [API d'extension](#-api-dextension)
- [Compilation](#-compilation)
- [Tests](#-tests)
- [Journal des modifications](#-journal-des-modifications)
- [Contribuer](#-contribuer)
- [Licence](#-licence)
- [Remerciements](#-remerciements)

---

## 🌌 Introduction

**MERIDIAN** est un appareil portable d'origine inconnue. Son « écran » n'est pas un affichage ordinaire — c'est une **Lentille de Résonance**. Des fragments de nombreuses réalités sont scellés dans ses modules de jeu, chacun servant de portail stable vers un monde indépendant.

Ce n'est pas une console de jeu ordinaire. C'est un **dispositif d'observation interdimensionnelle**.

Construit avec **Python + Pygame**, ce projet est un simulateur complet de plateforme multi-jeux. Il combine :

- 🎮 **Une collection évolutive de jeux d'arcade classiques entièrement recréés**
- 📚 **Un système narratif profond**, chaque jeu ayant son propre univers
- 🏆 **Plus de 50 succès** suivant la progression du joueur à travers les jeux
- 🌍 **Support bilingue complet** (Chinois simplifié / Anglais)
- 💾 **Sauvegarde anti-crash** avec reprise en cours de partie
- 🎵 **Moteur audio procédural** générant BGM et effets sonores dynamiques
- 🛠 **Panneau développeur intégré** pour le débogage et les tests

---

## 🌠 Univers

MERIDIAN est plus qu'une collection de jeux — il possède un cadre **méta-narratif** complet :

- **Séquence de démarrage** : Calibration de Résonance → Scan Dimensionnel → Stabilisation d'Ancrage → Connexion Noyau
- **Authentification** : « NEXUS AUTHENTICATION » — vérification de correspondance de résonance
- **Environnement bureau** : La barre d'état affiche l'identifiant « MERIDIAN »
- **Système de prologue** : Chaque jeu affiche un prologue de 3-5 lignes à la première visite
- **Archives du Savoir (LORE)** : Un lecteur indépendant sur la deuxième page du bureau, contenant :
  - Onglets générés depuis l'Artéfact et chaque monde enregistré
  - Histoires de fond de l'appareil (Origine / Noyau Nexus / Le Porteur)
  - 1-2 entrées de savoir profond par monde
  - Entrées cachées débloquées via les statistiques ou les succès
- **Texte d'ambiance** : La page menu de chaque jeu affiche du texte atmosphérique
- **Entièrement bilingue** : Tout le texte prend en charge le chinois et l'anglais

---

## 🎮 Les Mondes Connectés

| Icône | Jeu | Nom du Monde | Univers |
|:---:|------|-------------|---------|
| ⚫⚪ | **GOMOKU** | Yin-Yang Board<br>阴阳棋境 | Les anciens dieux Chaos et Ordre déduisent le destin de l'univers avec des pierres noires et blanches |
| 🐍 | **SNAKE** | Code Abyss<br>噬码渊 | Un serpent spirituel habitant les profondeurs de l'abîme numérique, se nourrissant de fragments de données |
| 🧱 | **BREAKOUT** | Star Fortress<br>星穹壁垒 | Remparts d'énergie et fragments stellaires laissés par une civilisation spatiale disparue |
| 🔢 | **2048** | Numen Sea<br>数灵海 | Êtres conscients faits purement de nombres, sur un chemin d'éveil de fusion et d'évolution |
| 💣 | **MINES** | Minefield Ruins<br>雷原遗迹 | Un ingénieur de déminage sur la terre brûlée un siècle après la Grande Guerre |
| 🧊 | **TETRIS** | Tower of Heaven<br>筑天塔 | Des matrices de construction extraterrestres descendent du ciel — construisez une tour qui touche la vérité |
| ✈️ | **AIR RAID** | Warden Front<br>守望者战线 | La bataille finale contre le réseau de guerre autonome |

---

## ✨ Fonctionnalités

### 🎯 Expérience principale

- **Animation de démarrage** : Séquence complète de l'univers MERIDIAN avec barre de progression en quatre étapes
- **Écran de verrouillage** : Pavé numérique + touche supprimer, interface d'authentification pixel art
- **Environnement bureau** : Disposition d'icônes sur deux pages, particules de traînée de souris, animation d'horloge horaire
- **Menus en jeu** : Interface unifiée style arcade avec Continuer / Nouvelle Partie / Paramètres

### 🏆 Mur de Succès

- Grille de badges 8×6
- Cliquez sur un badge pour déplier une carte de détail (animation ease-out-back)
- Bouton de fermeture en pixel art
- Statistiques de progression, fond dégradé, ligne de séparation dorée
- Étoiles dorées sur les badges débloqués
- Jusqu'à 3 notifications de succès superposées simultanément

### 💾 Système de Sauvegarde

| Fonction | Description |
|----------|-------------|
| **Sauvegarde Auto** | État de partie sauvegardé automatiquement à la sortie |
| **Reprise** | Bouton « Continuer » affiché en rentrant dans un jeu |
| **Anti-Crash** | Écriture atomique + mécanisme de sauvegarde empêchant la corruption |
| **Migration de Version** | Schema v4, fusionne automatiquement les données de sauvegarde héritées |
| **Stats Cross-Jeu** | Suivi unifié du temps de jeu, taux de victoire et meilleurs scores |

### ✈️ Exclusivités Air Raid

- **Système de skins de vaisseau** : 4 skins déblocables (DEFAULT / CRIMSON / AZURE / GOLD)
- **Système d'histoire** : Prologue + campagne en 8 chapitres, entièrement localisé
- **Archive d'histoires** : Lecteur plein écran de 9 entrées
- **16 Missions Standard** + Boss Rush + Mode Challenge
- **Système d'amélioration d'armes** : Cannon / Spread / Laser / Missile

### 🎨 Effets Visuels

- Palette de couleurs unifiée (classe `C` gérant centralement plus de 45 couleurs Air Raid)
- Système de particules du bureau (traînée de souris / étincelles au survol / éclatement horaire)
- Animations de transition de sortie spécifiques à chaque jeu
- Transition Air Raid à trois couches (ciel étoilé + rideau de balles + anneaux radar concentriques)
- Bordures décoratives des cartes de succès (coins style Cuphead)

### 🌍 Localisation

- Changement dynamique de langue en cours d'exécution
- Fusion Pixel Font — variante proportionnelle en chinois simplifié
- `localization.py` : gestion centralisée des traductions avec enregistrement par lot
- Couverture : étiquettes UI, menus de jeu, descriptions de succès, texte d'histoire, entrées Lore

### 🛠 Outils Développeur

- **Panneau Développeur F10** : Survol souris + clic pour activer
- Fonctions : débloquer tous les niveaux, tous les skins, déclencher effets horaires, effacer sauvegardes, etc.
- Effets limités à la session, sans impact sur les données persistantes

---

## 🚀 Démarrage rapide

### Prérequis

| Dépendance | Version |
|------------|---------|
| Python | **3.10+** |
| pygame | **2.0+** (<3.0) |
| OS | Windows / macOS / Linux |

### Installation et Lancement

```bash
# 1. Cloner le dépôt
git clone https://github.com/CrescentXiong-1/MERIDIAN.git
cd MERIDIAN

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer
python MERIDIAN.py
```

> 💡 **Note** : La seule dépendance est `pygame`. Aucune autre bibliothèque tierce n'est requise.

### Partage

Compressez le dossier `MERIDIAN` entier et envoyez-le. Le destinataire a seulement besoin de Python 3.10+ et `pip install pygame`.

---

## 🕹 Contrôles

### Généraux

| Touche | Action |
|:---:|--------|
| `ESC` | Retour au menu précédent / Éteindre (bureau) |
| `Entrée` | Confirmer / Passer le prologue |
| `Flèches / ZQSD` | Navigation / Contrôles de jeu |
| `Souris` | Sélection d'icônes du bureau, interaction Mur de Succès |

### Spécifiques aux Jeux

| Jeu | Touches Spéciales |
|-----|-------------------|
| **GOMOKU** | Clic pour placer une pierre, `U` pour annuler |
| **SNAKE** | Flèches pour diriger le serpent |
| **BREAKOUT** | Flèches / souris pour contrôler la raquette |
| **2048** | Flèches pour fusionner les tuiles |
| **MINES** | Clic gauche pour révéler / Clic droit pour drapeau |
| **TETRIS** | `↑` Tourner / `↓` Descente douce / `Espace` Chute dure / `C` Réserve / `P` Pause |
| **AIR RAID** | Flèches pour se déplacer / `Z` Tirer / `X` Missile / `Shift` Mode Focus |

### Développeur

| Touche | Action |
|:---:|--------|
| `F10` | Basculer le panneau développeur |

---

## 📁 Structure du projet

```
MERIDIAN/
├── MERIDIAN.py                  # Point d'entrée
├── MERIDIAN.spec                # Configuration PyInstaller
├── BUILD_EXE.bat                # Script de build Windows en un clic
├── requirements.txt             # Dépendances Python
├── reasonix.toml                # Configuration éditeur
│
├── meridian/                    # Package principal
│   ├── __init__.py
│   ├── app.py                   # Composition du jeu, boucle principale, dispatch
│   ├── common.py                # Constantes globales, classe de couleurs, paramètres de disposition
│   ├── lore.py                  # Données d'univers et API d'enregistrement
│   ├── audio.py                 # Moteur BGM procédural et effets sonores
│   ├── persistence.py           # Gestion de sauvegarde versionnée anti-crash
│   ├── localization.py          # Système bilingue d'exécution + police chinoise
│   ├── developer.py             # Panneau développeur (session seulement)
│   │
│   ├── shell.py                 # Agrégateur du système shell
│   ├── shell_boot.py            # Séquence de démarrage
│   ├── shell_password.py        # Authentification écran de verrouillage
│   ├── shell_desktop.py         # Environnement bureau et système d'icônes
│   ├── shell_transitions.py     # Animations de transition
│   │
│   ├── arcade_common.py         # UI arcade partagée + système de prologue
│   ├── arcade_levels.py         # Données de campagne Air Raid
│   │
│   ├── gomoku.py                # Gomoku (Yin-Yang Board)
│   ├── snake.py                 # Snake (Code Abyss)
│   ├── breakout.py              # Breakout (Star Fortress)
│   ├── g2048.py                 # 2048 (Numen Sea)
│   ├── mines.py                 # Démineur (Minefield Ruins)
│   ├── tetris.py                # Tetris (Tower of Heaven)
│   ├── air_raid.py              # Air Raid (Warden Front)
│   │
│   └── system.py                # Paramètres, profil, succès, lecteur Lore
│
├── assets/                      # Ressources statiques
│   └── fonts/                   # Fusion Pixel Font (SIL Open License 1.1)
│
├── tests/                       # Suite de tests (50+ tests)
│   ├── conftest.py              # Fixtures partagées + pilote SDL factice
│   ├── test_smoke.py            # Tests de fumée
│   ├── test_arcade_games.py     # Tests de jeux d'arcade
│   └── test_persistence.py      # Tests du système de persistance
│
└── .github/workflows/
    └── ci.yml                   # GitHub Actions CI (Windows, Python 3.10–3.12)
```

---

## 🏗 Architecture

MERIDIAN utilise un **modèle de composition par Mixins** :

```
Game(
    ShellMixin,         # Démarrage / Bureau / Mot de passe / Transitions
    GomokuMixin,        # Gomoku
    MinesMixin,         # Démineur
    Game2048Mixin,      # 2048
    BreakoutMixin,      # Breakout
    SnakeMixin,         # Snake
    TetrisMixin,        # Tetris
    ArcadeHubMixin,     # Systèmes d'arcade partagés
    AirRaidMixin,       # Air Raid
    DeveloperMixin,     # Outils développeur
    SystemMixin,        # Paramètres / Succès / Lore
)
```

### Patterns de Conception Principaux

| Pattern | Application |
|---------|------------|
| **Machine d'États** | Triple table de dispatch : `_EVENT_DISPATCH` + `_UPDATE_DISPATCH` + `_DRAW_DISPATCH` |
| **Enregistrement Dynamique** | `_GAME_STATE_REGISTRY` permet d'ajouter des jeux sans modifier `app.py` |
| **Composition Mixin** | Chaque module de jeu et système injecté dans `Game` via Mixins |
| **Écriture Atomique** | Sauvegardes dans un fichier temporaire puis renommage, empêchant la corruption |
| **Migration de Version** | `SaveManager._deep_merge()` remplit automatiquement les nouveaux champs |

### Flux d'États

```
BOOT → SYSTEM_READY → PASSWORD → DESKTOP
                                    ├── GOMOKU_MENU → GOMOKU_PLAYING → GOMOKU_END
                                    ├── SNAKE_MENU → SNAKE_PLAYING → SNAKE_END
                                    ├── BREAKOUT_MENU → BREAKOUT_PLAYING → BREAKOUT_END
                                    ├── G2048_MENU → G2048_PLAYING → G2048_END
                                    ├── MINES_MENU → MINES_PLAYING → MINES_END
                                    ├── TETRIS_MENU → TETRIS_PLAYING → TETRIS_END
                                    ├── AIR_MENU → AIR_SELECT → AIR_PLAYING → AIR_END
                                    ├── SETTINGS → SYSTEM_SETTINGS / PROFILE
                                    ├── ACHIEVEMENT_WALL
                                    └── LORE_READER → LORE_STORY
```

---

## 🔌 API d'extension

Une API complète est fournie pour les nouveaux jeux, couvrant tout, de l'univers aux icônes du bureau :

```python
from meridian.lore import register_game_world, register_device_lore
from meridian.shell_desktop import register_desktop_icon
from meridian.app import _register_game_states
from meridian.localization import register_game_translations

# 1. Enregistrer un monde de jeu (univers, prologue, texte d'ambiance, lore profond)
register_game_world(
    "mygame",
    world_name_en="MY WORLD",
    world_name_zh="我的世界",
    world_summary_en="A world of wonder",
    world_summary_zh="奇妙的世界",
    prologue_en=["Line 1", "Line 2", "Line 3"],
    prologue_zh=["第一行", "第二行", "第三行"],
    menu_flavor_en="The crystals hum with ancient power...",
    menu_flavor_zh="水晶随着古老的力量嗡嗡作响…",
    lore_entries=[...],
    desktop_subtitle_en="MY WORLD",
    desktop_subtitle_zh="我的世界",
)

# 2. Enregistrer une icône de bureau
register_desktop_icon("MYGAME", "open_mygame", page=0, ...)

# 3. Enregistrer le dispatch d'états (aucune modification de app.py)
_register_game_states("MYGAME_MENU", "_handle_mygame_menu", [], "_draw_mygame_menu")

# 4. Enregistrer les traductions
register_game_translations("mygame", {"PLAY": "开始", "SCORE": "得分"})
```

> 📝 Voir les docstrings source pour la documentation complète de l'API.

---

## 📦 Compilation

### Build Windows en un clic

```bash
# Exécuter le script de build (nécessite PyInstaller)
BUILD_EXE.bat
```

Le fichier `MERIDIAN.exe` généré se trouvera dans le dossier `dist/`.

### Build Manuel

```bash
pip install pyinstaller
python -m PyInstaller --noconfirm --clean MERIDIAN.spec
```

> ⚠️ Assurez-vous que `pygame` est installé et que les chemins dans `MERIDIAN.spec` sont corrects.

---

## 🧪 Tests

Le projet inclut **plus de 50 tests unitaires** couvrant les modules principaux :

```bash
# Exécuter tous les tests
python -m pytest tests/ -v

# Exécuter des fichiers de test spécifiques
python -m pytest tests/test_smoke.py -v
python -m pytest tests/test_arcade_games.py -v
python -m pytest tests/test_persistence.py -v
```

### Couverture de Tests

| Fichier de Test | Contenu |
|-----------------|---------|
| `test_smoke.py` | Tests de fumée : lancement, transitions d'état, rendu de base |
| `test_arcade_games.py` | Jeux d'arcade : interaction menu, logique de jeu, reprise de sauvegarde |
| `test_persistence.py` | Persistance : lecture/écriture, migration de version, récupération crash |

### CI / CD

Tests automatisés via GitHub Actions sur **Windows** contre **Python 3.10 / 3.11 / 3.12**. Déclenchés à chaque push et pull request.

---

## 📝 Journal des modifications

Voir [CHANGELOG.md](../../CHANGELOG.md) pour l'historique complet.

### Dernière : V3.1.0 (02/07/2026) — « MERIDIAN »

- 🌌 **Système d'Univers** : Cadre méta-narratif, lore des mondes connectés, système de prologue, archives Lore
- 🔌 **API d'Extension** : 5 fonctions d'enregistrement, intégration sans modification
- 🏆 **Mur de Succès** : Introduit en V3.0.0, peaufiné en V3.1.0
- 💾 **Reprise de Jeu** : Les 7 jeux prennent en charge la sauvegarde et reprise
- ✈️ **Histoire Air Raid** : Campagne en 8 chapitres avec archive d'histoires
- 🎨 **Finition Visuelle** : Particules du bureau, animations de transition, palette unifiée

---

## 🤝 Contribuer

Les contributions de toute nature sont les bienvenues ! Rapports de bugs, suggestions de fonctionnalités et soumissions de code.

### Flux de Contribution

1. **Fork** ce dépôt
2. Créez une branche : `git checkout -b feature/super-fonctionnalite`
3. Commitez : `git commit -m 'feat: ajouter une super fonctionnalité'`
4. Poussez : `git push origin feature/super-fonctionnalite`
5. Ouvrez une **Pull Request**

### Convention de Commits

Ce projet utilise les [Conventional Commits](https://www.conventionalcommits.org/) :
- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Documentation
- `refactor:` Refactorisation du code
- `test:` Tests
- `chore:` Build / outillage

---

## 📄 Licence

Ce projet est open source sous la **licence MIT**.

La police **Fusion Pixel Font** incluse est sous [SIL Open Font License 1.1](../../assets/fonts/FusionPixelFont-LICENSE-OFL.txt).

---

## 🙏 Remerciements

- **[Pygame](https://www.pygame.org/)** — Framework de développement de jeux
- **[Fusion Pixel Font](https://github.com/TakWolf/fusion-pixel-font)** — Police pixel pour le rendu du chinois simplifié
- **Tous les Contributeurs** — Merci à chaque développeur ayant contribué à MERIDIAN

---

<p align="center">
  <sub>MERIDIAN · Plusieurs Mondes. Un Seul Appareil. · 诸界 · 一器</sub>
</p>
