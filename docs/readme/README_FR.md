<p align="center">
  <img src="../../assets/banner.png" alt="MERIDIAN Banner" width="800" onerror="this.style.display='none'">
</p>

<h1 align="center">🌐 MERIDIAN · 子午线</h1>

<p align="center"><strong>Plusieurs Mondes. Un Seul Appareil.</strong></p>
<p align="center"><em>诸界 · 一器 · Many Worlds. One Device.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python">
  <img src="https://img.shields.io/badge/pygame-2.x-green" alt="Pygame">
  <img src="https://img.shields.io/badge/licence-MIT-yellow" alt="Licence">
  <img src="https://img.shields.io/badge/succ%C3%A8s-60-brightgreen" alt="Succès">
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
- [Journal des modifications](#-journal-des-modifications)
- [Contribuer](#-contribuer)
- [Licence](#-licence)
- [Remerciements](#-remerciements)

---

## 🌌 Introduction

**MERIDIAN** est un appareil portable d'origine inconnue. Son « écran » n'est pas un affichage ordinaire — c'est une **Lentille de Résonance**. Des fragments de nombreuses réalités sont scellés dans ses modules de jeu, chacun servant de portail stable vers un monde indépendant.

Ce n'est pas une console de jeu ordinaire. C'est un **dispositif d'observation interdimensionnelle**.

Construit avec **Python + Pygame**, ce projet est un simulateur complet de plateforme multi-jeux. Il combine :

- 🎮 **Huit jeux d'arcade classiques entièrement recréés**
- 📚 **Un système narratif profond**, chaque jeu ayant son propre univers
- 🏆 **60 succès** suivant la progression du joueur à travers les jeux
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
  - Les entrées ordinaires de chaque monde restent toujours lisibles
  - Les conditions de statistiques ou de succès accordent le crédit de progression Lore
  - Quatre archives de Résonance s'ouvrent à 25 % / 50 % / 75 % / 100 % de progression globale
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
| 🛡️ | **TANK DUEL** | Iron Arena<br>钢铁斗场 | Les chars rouge et bleu se disputent les ravitaillements dans une arène miroir, puis passent en mort subite en cas d'égalité |

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
| **Migration de Version** | Schema v5, fusionne automatiquement les données de sauvegarde héritées |
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
- Fonctions : débloquer le contenu de test, forcer les résultats, régler la vitesse et déclencher les effets horaires
- Effets limités à la session, sans impact sur les données persistantes

---

## 🚀 Démarrage rapide

### Prérequis

| Dépendance | Version |
|------------|---------|
| Python | **3.10–3.12** |
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

Compressez le dossier `MERIDIAN` entier et envoyez-le. Le destinataire a besoin de Python 3.10–3.12 et `pip install pygame`.

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
| **AIR RAID** | Tir automatique ; flèches pour se déplacer / `Shift` mode Focus / `Espace` missile |
| **TANK DUEL (Rouge)** | `WASD` pour le déplacement à huit directions / `F` objet ; tir automatique |
| **TANK DUEL (Bleu)** | Flèches pour le déplacement à huit directions / `Entrée` objet ; tir automatique |

### Développeur

| Touche | Action |
|:---:|--------|
| `F10` | Basculer le panneau développeur |

---

## 📁 Structure du projet

```text
MERIDIAN/
├── MERIDIAN.py                  # Point d'entrée
├── meridian/                    # Boucle, Shell, huit jeux et systèmes partagés
│   ├── shell_*.py               # Démarrage, authentification, bureau, transitions
│   ├── gomoku.py … tetris.py    # Six jeux classiques en solo
│   ├── air_raid.py              # Campagne et mode arcade Air Raid
│   ├── tank_engine.py           # Règles déterministes de Tank Duel
│   ├── tank_battle.py           # Présentation Pygame de Tank Duel
│   └── system.py et associés    # Sauvegarde, progression, Lore, audio, traduction, UI
├── tests/                       # Tests de règles, sauvegarde, enregistrement, régression
├── tools/                       # Vérifications de version et outils de développement
├── assets/                      # Polices et ressources statiques
├── docs/                        # Traductions et documents de conception
└── Development_Log/            # Historique du développement et des décisions
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
    TankBattleMixin,    # Présentation Tank Duel
    DeveloperMixin,     # Outils développeur
    SystemMixin,        # Paramètres / Succès / Lore
)
```

### Patterns de Conception Principaux

| Pattern | Application |
|---------|------------|
| **Machine d'États** | Triple table de dispatch : `_EVENT_DISPATCH` + `_UPDATE_DISPATCH` + `_DRAW_DISPATCH` |
| **Enregistrement borné** | États, initialiseurs, icônes, Lore et traductions sont enregistrés avant la création de `Game` |
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
                                    ├── TANK_MENU → TANK_PLAYING → TANK_END
                                    ├── SETTINGS → SYSTEM_SETTINGS / PROFILE
                                    ├── ACHIEVEMENT_WALL
                                    └── LORE_READER → LORE_STORY
```

---

## 🔌 API d'extension

Le module d'extension doit être importé explicitement avant de créer `Game()`. Il n'existe ni découverte automatique, ni rechargement à chaud, ni protocole de sauvegarde tiers ; l'enregistrement ne concerne que les instances créées ensuite.

```python
from meridian.lore import register_game_world, register_lore_entry
from meridian.shell_desktop import register_desktop_icon
from meridian.app import register_game_initializer, register_game_state
from meridian.localization import register_game_translations

def init_mygame(game):
    game.mygame_score = 0

def handle_event(game, event): ...
def update(game): ...
def draw(game): ...

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
    lore_entries=[],
    desktop_subtitle_en="MY WORLD",
    desktop_subtitle_zh="我的世界",
)

# 2. Ajouter un crédit Lore conditionnel et initialiser l'extension
register_lore_entry(
    "mygame", "mygame_mastery",
    title_en="CRYSTAL MASTERY", title_zh="水晶精通",
    content_en=["The crystal answers."], content_zh=["水晶作出了回应。"],
    unlock="stat:mygame:score:100",
)
register_game_initializer(init_mygame)

# 3. Enregistrer l'état et l'entrée de la troisième page
register_game_state("MYGAME_MENU", handle_event, [update], draw)
register_desktop_icon(
    "MYGAME", "open_mygame", page=2,
    subtitle_en="MY WORLD", subtitle_zh="我的世界",
    target_state="MYGAME_MENU", transition_effect="fade",
)

# 4. Enregistrer les traductions
register_game_translations("mygame", {"MYGAME_PLAY": "开始"})
```

Les handlers peuvent être des noms de méthodes de `Game` ou des callables recevant `game`. Une icône active utilise exactement un seul de `target_state` et `on_activate(game)`. Les clés de traduction appartiennent au `game_id` et un conflit exige `replace=True`. `_register_game_states()` reste un wrapper de compatibilité.

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

## 🔎 Vérification de version locale

Exécutez le vérificateur de version en lecture seule depuis la racine du dépôt :

```bash
python tools/check_release.py
```

Cette commande vérifie uniquement la version, les métadonnées de `CHANGELOG.md` et l'état Git de l'arbre de travail et des tags de version locaux. Elle ne crée pas de tag, ne pousse rien et ne compile rien. L'analyse statique du code peut être lancée séparément :

```bash
python -m ruff check MERIDIAN.py meridian tools
python -m compileall -q MERIDIAN.py meridian tools
```

---

## 📝 Journal des modifications

Voir [CHANGELOG.md](../../CHANGELOG.md) pour l'historique complet.

### Dernière version stable : V3.2.0 (13/07/2026) — « Tank Duel »

- 🛡️ **Tank Duel** : Duel local rouge contre bleu, huit objets, trois minutes et mort subite
- 💾 **Sauvegarde** : Schema v5 ; les huit jeux prennent en charge la sauvegarde et la reprise
- 🏆 **Progression** : 60 succès dans huit mondes connectés
- 🌌 **Lore** : Le texte ordinaire reste lisible ; les conditions donnent le crédit de progression et les seuils globaux ouvrent les archives de Résonance

Les changements postérieurs à la version stable sont consignés sous `Unreleased` dans [CHANGELOG.md](../../CHANGELOG.md).

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
