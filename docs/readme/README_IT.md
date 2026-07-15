<p align="center">
  <img src="../../assets/banner.png" alt="MERIDIAN Banner" width="800" onerror="this.style.display='none'">
</p>

<h1 align="center">🌐 MERIDIAN · 子午线</h1>

<p align="center"><strong>Molti Mondi. Un Solo Dispositivo.</strong></p>
<p align="center"><em>诸界 · 一器 · Many Worlds. One Device.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python">
  <img src="https://img.shields.io/badge/pygame-2.x-green" alt="Pygame">
  <img src="https://img.shields.io/badge/licenza-MIT-yellow" alt="Licenza">
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
- [I Mondi Connessi](#-i-mondi-connessi)
- [Funzionalità](#-funzionalità)
- [Avvio Rapido](#-avvio-rapido)
- [Controlli](#-controlli)
- [Struttura del Progetto](#-struttura-del-progetto)
- [Architettura](#-architettura)
- [API di Estensione](#-api-di-estensione)
- [Compilazione](#-compilazione)
- [Registro delle Modifiche](#-registro-delle-modifiche)
- [Contribuire](#-contribuire)
- [Licenza](#-licenza)
- [Ringraziamenti](#-ringraziamenti)

---

## 🌌 Introduzione

**MERIDIAN** è un dispositivo portatile di origine sconosciuta. Il suo "schermo" non è un normale display — è una **Lente di Risonanza**. Frammenti di molte realtà sono sigillati nei suoi moduli di gioco, ognuno dei quali funge da portale stabile verso un mondo indipendente.

Non è una normale console di gioco. È un **dispositivo di osservazione interdimensionale**.

Costruito con **Python + Pygame**, questo progetto è un simulatore completo di piattaforma multi-gioco. Combina:

- 🎮 **Otto giochi arcade classici completamente ricreati**
- 📚 **Un profondo sistema narrativo**, ogni gioco con la propria lore
- 🏆 **60 obiettivi** che tracciano i progressi del giocatore
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
  - Schede generate dall'Artefatto e da ogni mondo registrato
  - Storie di background del dispositivo (Origine / Nucleo Nexus / Il Portatore)
  - Le voci ordinarie di ogni mondo sono sempre leggibili
  - Le condizioni statistiche o degli obiettivi assegnano credito di completamento Lore
  - Quattro archivi di Risonanza si aprono al 25% / 50% / 75% / 100% del completamento globale
- **Testo d'Atmosfera**: La pagina del menu di ogni gioco mostra testo narrativo
- **Completamente Bilingue**: Tutto il testo supporta cinese e inglese

---

## 🎮 I Mondi Connessi

| Icona | Gioco | Nome del Mondo | Lore |
|:---:|------|----------------|------|
| ⚫⚪ | **GOMOKU** | Yin-Yang Board<br>阴阳棋境 | Gli antichi dèi Caos e Ordine deducono il destino dell'universo con pietre bianche e nere |
| 🐍 | **SNAKE** | Code Abyss<br>噬码渊 | Un serpente spirituale che dimora nelle profondità dell'abisso digitale, nutrendosi di frammenti di dati |
| 🧱 | **BREAKOUT** | Star Fortress<br>星穹壁垒 | Bastioni energetici e frammenti stellari lasciati da una civiltà spaziale perduta |
| 🔢 | **2048** | Numen Sea<br>数灵海 | Esseri senzienti fatti puramente di numeri, su un cammino di fusione ed evoluzione |
| 💣 | **MINES** | Minefield Ruins<br>雷原遗迹 | Un geniere sminatore sulla terra bruciata un secolo dopo la Grande Guerra |
| 🧊 | **TETRIS** | Tower of Heaven<br>筑天塔 | Matrici di costruzione aliene scendono dal cielo — costruisci una torre che tocchi la verità |
| ✈️ | **AIR RAID** | Warden Front<br>守望者战线 | La battaglia finale contro la rete di guerra autonoma |
| 🛡️ | **TANK DUEL** | Iron Arena<br>钢铁斗场 | I carri rosso e blu contendono i rifornimenti in un'arena speculare, con morte improvvisa in caso di pareggio |

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
| **Migrazione di Versione** | Schema v5, unisce automaticamente i dati legacy |
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
- Funzioni: sblocca contenuti di test, forza risultati, regola la velocità e attiva gli effetti orari
- Effetti limitati alla sessione, nessun impatto sui dati persistenti

---

## 🚀 Avvio Rapido

### Requisiti

| Dipendenza | Versione |
|------------|----------|
| Python | **3.10–3.12** |
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

Comprimi l'intera cartella `MERIDIAN` e inviala. Il destinatario ha bisogno di Python 3.10–3.12 e `pip install pygame`.

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
| **AIR RAID** | Fuoco automatico; frecce per muoversi / `Shift` Focus / `Spazio` missile |
| **TANK DUEL (Rosso)** | `WASD` per movimento in otto direzioni / `F` oggetto; fuoco automatico |
| **TANK DUEL (Blu)** | Frecce per movimento in otto direzioni / `Enter` oggetto; fuoco automatico |

### Sviluppatore

| Tasto | Azione |
|:---:|--------|
| `F10` | Attiva/disattiva pannello sviluppatore |

---

## 📁 Struttura del Progetto

```text
MERIDIAN/
├── MERIDIAN.py                  # Punto di ingresso
├── meridian/                    # Loop, Shell, otto giochi e sistemi condivisi
│   ├── shell_*.py               # Avvio, accesso, desktop e transizioni
│   ├── gomoku.py … tetris.py    # Sei giochi classici in singolo
│   ├── air_raid.py              # Campagna e modalità arcade Air Raid
│   ├── tank_engine.py           # Regole deterministiche di Tank Duel
│   ├── tank_battle.py           # Presentazione Pygame di Tank Duel
│   └── system.py e affini       # Salvataggi, completamento, Lore, audio, lingua, UI
├── tests/                       # Test di regole, salvataggi, registrazione, regressione
├── tools/                       # Controlli release e strumenti di sviluppo
├── assets/                      # Font e risorse statiche
├── docs/                        # Traduzioni e documenti di design
└── Development_Log/            # Storia dello sviluppo e delle decisioni
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
    TankBattleMixin,    # Presentazione Tank Duel
    DeveloperMixin,     # Strumenti sviluppatore
    SystemMixin,        # Impostazioni / Obiettivi / Lore
)
```

### Pattern di Design Principali

| Pattern | Applicazione |
|---------|-------------|
| **Macchina a Stati** | Tripla tabella di dispatch: `_EVENT_DISPATCH` + `_UPDATE_DISPATCH` + `_DRAW_DISPATCH` |
| **Registrazione limitata** | Stati, inizializzatori, icone, Lore e traduzioni si registrano prima di creare `Game` |
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
                                    ├── TANK_MENU → TANK_PLAYING → TANK_END
                                    ├── SETTINGS → SYSTEM_SETTINGS / PROFILE
                                    ├── ACHIEVEMENT_WALL
                                    └── LORE_READER → LORE_STORY
```

---

## 🔌 API di Estensione

Il modulo di estensione deve essere importato esplicitamente prima di creare `Game()`. Non esistono scansione automatica, hot reload o protocollo di salvataggio di terze parti; le registrazioni valgono solo per le istanze successive.

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
    lore_entries=[],
    desktop_subtitle_en="MY WORLD",
    desktop_subtitle_zh="我的世界",
)

# 2. Aggiungere credito Lore condizionale e inizializzare l'estensione
register_lore_entry(
    "mygame", "mygame_mastery",
    title_en="CRYSTAL MASTERY", title_zh="水晶精通",
    content_en=["The crystal answers."], content_zh=["水晶作出了回应。"],
    unlock="stat:mygame:score:100",
)
register_game_initializer(init_mygame)

# 3. Registrare lo stato e l'icona sulla terza pagina
register_game_state("MYGAME_MENU", handle_event, [update], draw)
register_desktop_icon(
    "MYGAME", "open_mygame", page=2,
    subtitle_en="MY WORLD", subtitle_zh="我的世界",
    target_state="MYGAME_MENU", transition_effect="fade",
)

# 4. Registrare traduzioni
register_game_translations("mygame", {"MYGAME_PLAY": "开始"})
```

Gli handler possono essere nomi di metodi `Game` o callable che ricevono `game`. Un'icona attiva usa esattamente uno tra `target_state` e `on_activate(game)`. Le chiavi di traduzione appartengono al `game_id`; un conflitto richiede `replace=True`. `_register_game_states()` resta solo come wrapper di compatibilità.

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

## 📝 Registro delle Modifiche

Vedi [CHANGELOG.md](../../CHANGELOG.md) per la storia completa.

### Ultima stabile: V3.2.0 (13/07/2026) — "Tank Duel"

- 🛡️ **Tank Duel**: Duello locale rosso contro blu, otto oggetti, tre minuti e morte improvvisa
- 💾 **Salvataggi**: Schema v5; tutti gli otto giochi supportano salvataggio e ripresa
- 🏆 **Progressi**: 60 obiettivi negli otto mondi connessi
- 🌌 **Lore**: Il testo ordinario resta leggibile; le condizioni danno credito e le soglie globali aprono gli archivi di Risonanza

Le modifiche successive alla release stabile sono riportate in `Unreleased` in [CHANGELOG.md](../../CHANGELOG.md).

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
  <sub>MERIDIAN · Molti Mondi. Un Solo Dispositivo. · 诸界 · 一器</sub>
</p>
