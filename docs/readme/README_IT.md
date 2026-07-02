<p align="center">
  <img src="../../assets/banner.png" alt="MERIDIAN Banner" width="800" onerror="this.style.display='none'">
</p>

<h1 align="center">🌐 MERIDIAN · 子午线</h1>

<p align="center"><strong>Sette Mondi. Un Solo Dispositivo.</strong></p>
<p align="center"><em>七界 · 一器 · Seven Worlds. One Device.</em></p>

<p align="center">
  <img src="https://github.com/CrescentXiong-1/MERIDIAN/actions/workflows/ci.yml/badge.svg" alt="Stato CI">
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python">
  <img src="https://img.shields.io/badge/pygame-2.x-green" alt="Pygame">
  <img src="https://img.shields.io/badge/licenza-MIT-yellow" alt="Licenza">
  <img src="https://img.shields.io/badge/test-50%2B-brightgreen" alt="Test">
  <img src="https://img.shields.io/badge/righe-~15.700-orange" alt="Righe di codice">
</p>

<p align="center">
  <a href="../../README.md">中文</a> |
  <a href="README_EN.md">English</a> |
  <a href="README_FR.md">Français</a> |
  <a href="README_RU.md">Русский</a> |
  <strong>Italiano</strong> |
  <a href="README_JA.md">日本語</a> |
  <a href="README_AR.md">العربية</a>
</p>

---

## 📖 Indice

- [Introduzione](#-introduzione)
- [Mondo Narrativo](#-mondo-narrativo)
- [I Sette Mondi](#-i-sette-mondi)
- [Funzionalità](#-funzionalità)
- [Avvio Rapido](#-avvio-rapido)
- [Controlli](#-controlli)
- [Struttura del Progetto](#-struttura-del-progetto)
- [Architettura](#-architettura)
- [API di Estensione](#-api-di-estensione)
- [Compilazione](#-compilazione)
- [Test](#-test)
- [Registro delle Modifiche](#-registro-delle-modifiche)
- [Contribuire](#-contribuire)
- [Licenza](#-licenza)
- [Ringraziamenti](#-ringraziamenti)

---

## 🌌 Introduzione

**MERIDIAN** è un dispositivo portatile di origine sconosciuta. Il suo "schermo" non è un normale display — è una **Lente di Risonanza**. Sette frammenti di realtà sono sigillati in sette classici giochi arcade, ognuno dei quali funge da portale stabile verso un mondo indipendente.

Non è una normale console di gioco. È un **dispositivo di osservazione interdimensionale**.

Costruito con **Python + Pygame**, questo progetto è un simulatore completo di piattaforma multi-gioco. Combina:

- 🎮 **Sette giochi arcade classici completamente ricreati**
- 📚 **Un profondo sistema narrativo**, ogni gioco con la propria lore
- 🏆 **Oltre 50 obiettivi** che tracciano i progressi del giocatore
- 🌍 **Supporto bilingue completo** (Cinese semplificato / Inglese)
- 💾 **Salvataggi anti-crash** con ripresa a metà partita
- 🎵 **Motore audio procedurale** che genera BGM ed effetti sonori dinamici
- 🛠 **Pannello sviluppatore integrato** per debugging e test

---

## 🌠 Mondo Narrativo

MERIDIAN è più di una collezione di giochi — ha una cornice **meta-narrativa** completa:

- **Sequenza di Avvio**: Calibrazione Risonanza → Scansione Dimensionale → Stabilizzazione Ancora → Connessione Nucleo
- **Autenticazione Password**: "NEXUS AUTHENTICATION" — verifica di corrispondenza risonante
- **Ambiente Desktop**: La barra di stato mostra l'identificativo "MERIDIAN"
- **Sistema di Prologo**: Ogni gioco mostra un prologo di 3-5 righe alla prima visita
- **Archivio delle Conoscenze (LORE)**: Un lettore indipendente nella seconda pagina del desktop, contenente:
  - 8 schede di categoria (Origine dell'Artefatto + Sette Mondi)
  - Storie di background del dispositivo (Origine / Nucleo Nexus / Il Portatore)
  - 1-2 voci di lore profonda per mondo
  - Voci nascoste sbloccabili tramite statistiche o obiettivi
- **Testo d'Atmosfera**: La pagina del menu di ogni gioco mostra testo narrativo
- **Completamente Bilingue**: Tutto il testo supporta cinese e inglese

---

## 🎮 I Sette Mondi

| Icona | Gioco | Nome del Mondo | Lore |
|:---:|------|----------------|------|
| ⚫⚪ | **GOMOKU** | Yin-Yang Board<br>阴阳棋境 | Gli antichi dèi Caos e Ordine deducono il destino dell'universo con pietre bianche e nere |
| 🐍 | **SNAKE** | Code Abyss<br>噬码渊 | Un serpente spirituale che dimora nelle profondità dell'abisso digitale, nutrendosi di frammenti di dati |
| 🧱 | **BREAKOUT** | Star Fortress<br>星穹壁垒 | Bastioni energetici e frammenti stellari lasciati da una civiltà spaziale perduta |
| 🔢 | **2048** | Numen Sea<br>数灵海 | Esseri senzienti fatti puramente di numeri, su un cammino di fusione ed evoluzione |
| 💣 | **MINES** | Minefield Ruins<br>雷原遗迹 | Un geniere sminatore sulla terra bruciata un secolo dopo la Grande Guerra |
| 🧊 | **TETRIS** | Tower of Heaven<br>筑天塔 | Matrici di costruzione aliene scendono dal cielo — costruisci una torre che tocchi la verità |
| ✈️ | **AIR RAID** | Warden Front<br>守望者战线 | La battaglia finale contro la rete di guerra autonoma |

---

## ✨ Funzionalità

### 🎯 Esperienza Principale

- **Animazione di Avvio**: Sequenza completa MERIDIAN con barra di progressione a quattro fasi
- **Schermata di Blocco**: Tastierino numerico + tasto cancella, interfaccia pixel art
- **Ambiente Desktop**: Layout icone su due pagine, particelle scia mouse, animazione orologio oraria
- **Menu di Gioco**: Interfaccia unificata stile arcade con Continua / Nuova Partita / Impostazioni

### 🏆 Parete degli Obiettivi

- Griglia di badge 8×6
- Clicca un badge per espandere una scheda dettaglio (animazione ease-out-back)
- Pulsante di chiusura pixel art
- Statistiche di progresso, sfondo sfumato, linea separatrice dorata
- Stelle dorate sui badge sbloccati
- Fino a 3 notifiche di obiettivi impilate simultaneamente

### 💾 Sistema di Salvataggio

| Funzione | Descrizione |
|----------|-------------|
| **Salvataggio Automatico** | Stato della partita salvato automaticamente all'uscita |
| **Riprendi** | Pulsante "Continua" quando rientri in un gioco |
| **Anti-Crash** | Scrittura atomica + meccanismo di backup |
| **Migrazione di Versione** | Schema v4, unisce automaticamente i dati legacy |
| **Statistiche Cross-Gioco** | Tracciamento unificato di tempo di gioco, vittorie e record |

### ✈️ Esclusive Air Raid

- **Sistema Skin Navicella**: 4 skin sbloccabili (DEFAULT / CRIMSON / AZURE / GOLD)
- **Sistema Storia**: Prologo + campagna in 8 capitoli, completamente localizzato
- **Archivio Storie**: Lettore a schermo intero con 9 voci
- **16 Missioni Standard** + Boss Rush + Modalità Sfida
- **Sistema Potenziamento Armi**: Cannon / Spread / Laser / Missile

### 🎨 Effetti Visivi

- Tavolozza colori unificata (classe `C` che gestisce oltre 45 colori di Air Raid)
- Sistema particellare desktop (scia mouse / scintille hover / scoppio orario)
- Animazioni di uscita specifiche per ogni gioco
- Transizione Air Raid a tre strati (cielo stellato + cortina di proiettili + anelli radar concentrici)
- Bordi decorativi delle schede obiettivo (angoli stile Cuphead)

### 🌍 Localizzazione

- Cambio dinamico della lingua a runtime
- Fusion Pixel Font — variante proporzionale in cinese semplificato
- `localization.py` gestione centralizzata delle traduzioni con registrazione batch
- Copertura: etichette UI, menu di gioco, descrizioni obiettivi, testo storie, voci Lore

### 🛠 Strumenti Sviluppatore

- **Pannello Sviluppatore F10**: Evidenziazione hover + clic per attivare
- Funzioni: sblocca tutti i livelli, skin, attiva effetti orari, cancella salvataggi, ecc.
- Effetti limitati alla sessione, nessun impatto sui dati persistenti

---

## 🚀 Avvio Rapido

### Requisiti

| Dipendenza | Versione |
|------------|----------|
| Python | **3.10+** |
| pygame | **2.0+** (<3.0) |
| OS | Windows / macOS / Linux |

### Installazione e Avvio

```bash
# 1. Clona il repository
git clone https://github.com/CrescentXiong-1/MERIDIAN.git
cd MERIDIAN

# 2. Installa le dipendenze
pip install -r requirements.txt

# 3. Avvia
python MERIDIAN.py
```

> 💡 **Nota**: L'unica dipendenza è `pygame`. Nessun'altra libreria di terze parti richiesta.

### Condivisione

Comprimi l'intera cartella `MERIDIAN` e inviala. Il destinatario ha solo bisogno di Python 3.10+ e `pip install pygame`.

---

## 🕹 Controlli

### Generali

| Tasto | Azione |
|:---:|--------|
| `ESC` | Torna al menu precedente / Spegni (desktop) |
| `Invio` | Conferma / Salta prologo |
| `Frecce / WASD` | Navigazione / Controlli di gioco |
| `Mouse` | Selezione icone desktop, Parete Obiettivi |

### Specifici per Gioco

| Gioco | Tasti Speciali |
|-------|---------------|
| **GOMOKU** | Clic mouse per piazzare pietra, `U` per annullare |
| **SNAKE** | Frecce per controllare il serpente |
| **BREAKOUT** | Frecce / mouse per controllare la racchetta |
| **2048** | Frecce per unire le tessere |
| **MINES** | Clic sinistro per rivelare / Clic destro per bandiera |
| **TETRIS** | `↑` Ruota / `↓` Discesa morbida / `Spazio` Discesa dura / `C` Riserva / `P` Pausa |
| **AIR RAID** | Frecce per muoversi / `Z` Fuoco / `X` Missile / `Shift` Modalità Focus |

### Sviluppatore

| Tasto | Azione |
|:---:|--------|
| `F10` | Attiva/disattiva pannello sviluppatore |

---

## 📁 Struttura del Progetto

```
MERIDIAN/
├── MERIDIAN.py                  # Punto di ingresso
├── MERIDIAN.spec                # Configurazione PyInstaller
├── BUILD_EXE.bat                # Script build Windows one-click
├── requirements.txt             # Dipendenze Python
├── reasonix.toml                # Configurazione editor
│
├── meridian/                    # Pacchetto principale
│   ├── __init__.py
│   ├── app.py                   # Composizione gioco, loop principale, dispatch
│   ├── common.py                # Costanti globali, classe colori, parametri layout
│   ├── lore.py                  # Dati mondo narrativo e API registrazione
│   ├── audio.py                 # Motore BGM procedurale ed effetti sonori
│   ├── persistence.py           # Gestione salvataggi versionati anti-crash
│   ├── localization.py          # Sistema bilingue runtime + font cinese
│   ├── developer.py             # Pannello sviluppatore (solo sessione)
│   │
│   ├── shell.py                 # Aggregatore sistema shell
│   ├── shell_boot.py            # Sequenza di avvio
│   ├── shell_password.py        # Autenticazione schermata di blocco
│   ├── shell_desktop.py         # Ambiente desktop e sistema icone
│   ├── shell_transitions.py     # Animazioni di transizione
│   │
│   ├── arcade_common.py         # UI arcade condivisa + sistema prologo
│   ├── arcade_levels.py         # Dati campagna Air Raid
│   │
│   ├── gomoku.py                # Gomoku (Yin-Yang Board)
│   ├── snake.py                 # Snake (Code Abyss)
│   ├── breakout.py              # Breakout (Star Fortress)
│   ├── g2048.py                 # 2048 (Numen Sea)
│   ├── mines.py                 # Campo Minato (Minefield Ruins)
│   ├── tetris.py                # Tetris (Tower of Heaven)
│   ├── air_raid.py              # Air Raid (Warden Front)
│   │
│   └── system.py                # Impostazioni, profilo, obiettivi, lettore Lore
│
├── assets/                      # Risorse statiche
│   └── fonts/                   # Fusion Pixel Font (SIL Open License 1.1)
│
├── tests/                       # Suite di test (50+ test)
│   ├── conftest.py              # Fixture condivise + driver SDL fittizio
│   ├── test_smoke.py            # Test di fumo
│   ├── test_arcade_games.py     # Test giochi arcade
│   └── test_persistence.py      # Test sistema persistenza
│
└── .github/workflows/
    └── ci.yml                   # GitHub Actions CI (Windows, Python 3.10–3.12)
```

---

## 🏗 Architettura

MERIDIAN utilizza un **pattern di composizione Mixin**:

```
Game(
    ShellMixin,         # Avvio / Desktop / Password / Transizioni
    GomokuMixin,        # Gomoku
    MinesMixin,         # Campo Minato
    Game2048Mixin,      # 2048
    BreakoutMixin,      # Breakout
    SnakeMixin,         # Snake
    TetrisMixin,        # Tetris
    ArcadeHubMixin,     # Sistemi arcade condivisi
    AirRaidMixin,       # Air Raid
    DeveloperMixin,     # Strumenti sviluppatore
    SystemMixin,        # Impostazioni / Obiettivi / Lore
)
```

### Pattern di Design Principali

| Pattern | Applicazione |
|---------|-------------|
| **Macchina a Stati** | Tripla tabella di dispatch: `_EVENT_DISPATCH` + `_UPDATE_DISPATCH` + `_DRAW_DISPATCH` |
| **Registrazione Dinamica** | `_GAME_STATE_REGISTRY` permette nuovi giochi senza modificare `app.py` |
| **Composizione Mixin** | Ogni modulo gioco e sistema iniettato in `Game` tramite Mixin |
| **Scrittura Atomica** | Salvataggi su file temporaneo poi rinominato, prevenendo corruzione |
| **Migrazione di Versione** | `SaveManager._deep_merge()` riempie automaticamente i nuovi campi |

### Flusso degli Stati

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

## 🔌 API di Estensione

È fornita un'API completa per nuovi giochi:

```python
from meridian.lore import register_game_world, register_device_lore
from meridian.shell_desktop import register_desktop_icon
from meridian.app import _register_game_states
from meridian.localization import register_game_translations

# 1. Registrare un mondo di gioco
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

# 2. Registrare icona desktop
register_desktop_icon("MYGAME", "open_mygame", page=0, ...)

# 3. Registrare dispatch stati (nessuna modifica a app.py)
_register_game_states("MYGAME_MENU", "_handle_mygame_menu", [], "_draw_mygame_menu")

# 4. Registrare traduzioni
register_game_translations("mygame", {"PLAY": "开始", "SCORE": "得分"})
```

> 📝 Vedi i docstring del codice sorgente per la documentazione API completa.

---

## 📦 Compilazione

### Build Windows One-Click

```bash
# Esegui lo script di build (richiede PyInstaller)
BUILD_EXE.bat
```

Il file `MERIDIAN.exe` generato si troverà nella cartella `dist/`.

### Build Manuale

```bash
pip install pyinstaller
python -m PyInstaller --noconfirm --clean MERIDIAN.spec
```

> ⚠️ Assicurati che `pygame` sia installato e che i percorsi in `MERIDIAN.spec` siano corretti.

---

## 🧪 Test

Il progetto include **oltre 50 test unitari**:

```bash
# Esegui tutti i test
python -m pytest tests/ -v

# Esegui file di test specifici
python -m pytest tests/test_smoke.py -v
python -m pytest tests/test_arcade_games.py -v
python -m pytest tests/test_persistence.py -v
```

### Copertura dei Test

| File Test | Contenuto |
|-----------|-----------|
| `test_smoke.py` | Test di fumo: avvio, transizioni di stato, rendering base |
| `test_arcade_games.py` | Giochi arcade: menu, logica di gioco, ripristino salvataggi |
| `test_persistence.py` | Persistenza: lettura/scrittura, migrazione versione, recupero crash |

### CI / CD

Test automatici tramite GitHub Actions su **Windows** per **Python 3.10 / 3.11 / 3.12**. Attivati ad ogni push e pull request.

---

## 📝 Registro delle Modifiche

Vedi [CHANGELOG.md](../../CHANGELOG.md) per la storia completa.

### Ultima: V3.1.0 (02/07/2026) — "MERIDIAN"

- 🌌 **Sistema Mondo Narrativo**: Meta-narrativa, lore sette mondi, sistema prologo, archivio Lore
- 🔌 **API Estensione**: 5 funzioni di registrazione, integrazione senza modifiche
- 🏆 **Parete Obiettivi**: Introdotta in V3.0.0, perfezionata in V3.1.0
- 💾 **Ripresa Partita**: Tutti e 7 i giochi supportano salvataggio e ripresa
- ✈️ **Storia Air Raid**: Campagna 8 capitoli con archivio storie
- 🎨 **Rifiniture Visive**: Particelle desktop, animazioni transizione, tavolozza unificata

---

## 🤝 Contribuire

Contributi di ogni tipo sono benvenuti! Segnalazioni bug, suggerimenti e codice.

### Flusso di Contribuzione

1. **Forka** questo repository
2. Crea un branch: `git checkout -b feature/funzionalita-incredibile`
3. Committa: `git commit -m 'feat: aggiungi funzionalità incredibile'`
4. Pusha: `git push origin feature/funzionalita-incredibile`
5. Apri una **Pull Request**

### Convenzione Commit

Questo progetto usa [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` Nuova funzionalità
- `fix:` Correzione bug
- `docs:` Documentazione
- `refactor:` Refactoring codice
- `test:` Test
- `chore:` Build / strumenti

---

## 📄 Licenza

Questo progetto è open source sotto **Licenza MIT**.

Il font **Fusion Pixel Font** incluso è sotto [SIL Open Font License 1.1](../../assets/fonts/FusionPixelFont-LICENSE-OFL.txt).

---

## 🙏 Ringraziamenti

- **[Pygame](https://www.pygame.org/)** — Framework per sviluppo di giochi
- **[Fusion Pixel Font](https://github.com/TakWolf/fusion-pixel-font)** — Font pixel per il rendering del cinese
- **Tutti i Contributori** — Grazie ad ogni sviluppatore che ha contribuito a MERIDIAN

---

<p align="center">
  <sub>MERIDIAN · Sette Mondi. Un Solo Dispositivo. · 七界 · 一器</sub>
</p>
