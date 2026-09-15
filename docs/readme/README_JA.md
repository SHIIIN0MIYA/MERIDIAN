<p align="center">
  <img src="../../assets/banner.png" alt="MERIDIAN Banner" width="800" onerror="this.style.display='none'">
</p>

<h1 align="center">🌐 MERIDIAN · 子午線</h1>

<p align="center"><strong>幾多の世界。一つの装置。</strong></p>
<p align="center"><em>诸界 · 一器 · Many Worlds. One Device.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python">
  <img src="https://img.shields.io/badge/pygame-2.x-green" alt="Pygame">
  <img src="https://img.shields.io/badge/ライセンス-MIT-yellow" alt="ライセンス">
  <img src="https://img.shields.io/badge/実績-60-brightgreen" alt="実績">
</p>

<p align="center">
  <a href="../../README.md">中文</a> |
  <a href="README_EN.md">English</a> |
  <a href="README_FR.md">Français</a> |
  <a href="README_RU.md">Русский</a> |
  <a href="README_IT.md">Italiano</a> |
  <strong>日本語</strong> |
  <a href="README_AR.md">العربية</a>
</p>

---

## 📖 目次

- [概要](#-概要)
- [世界観](#-世界観)
- [接続された世界](#-接続された世界)
- [主な機能](#-主な機能)
- [クイックスタート](#-クイックスタート)
- [操作方法](#-操作方法)
- [プロジェクト構造](#-プロジェクト構造)
- [アーキテクチャ](#-アーキテクチャ)
- [拡張API](#-拡張api)
- [ビルド](#-ビルド)
- [変更履歴](#-変更履歴)
- [コントリビューション](#-コントリビューション)
- [ライセンス](#-ライセンス)
- [謝辞](#-謝辞)

---

## 🌌 概要

**MERIDIAN（子午線）** は、起源不明の携帯型装置です。その「画面」は通常のディスプレイではなく、**共鳴レンズ**です。幾多の現実から来た破片がゲームモジュールに封印され、それぞれが独立した世界への安定したポータルとして機能しています。

これは普通のゲーム機ではありません。これは**次元間観測デバイス**です。

**Python + Pygame** で構築されたこのプロジェクトは、完全なマルチゲームプラットフォームシミュレーターです。以下の要素を兼ね備えています：

- 🎮 **完全再現された8本のクラシックアーケードゲーム**
- 📚 **深い世界観ナラティブシステム** — 各ゲームに独自の背景設定
- 🏆 **60個の実績** — ゲーム間でプレイヤーの進行を追跡
- 🌍 **完全バイリンガル対応**（簡体字中国語 / 英語）
- 💾 **クラッシュセーフな永続化保存** — ゲーム中断からの再開に対応
- 🎵 **プロシージャルオーディオエンジン** — 動的なBGMと効果音を生成
- 🛠 **内蔵開発者パネル** — デバッグとテスト用

---

## 🌠 世界観

MERIDIANは単なるゲームコレクションではありません — 完全な**メタナラティブ**フレームワークを備えています：

- **起動シーケンス**：共鳴調整 → 次元スキャン → アンカー安定化 → コア接続
- **パスワード認証**：「NEXUS AUTHENTICATION」— 共鳴一致検証
- **デスクトップ環境**：ステータスバーに「MERIDIAN」デバイス識別子を表示
- **プロローグシステム**：各ゲーム初回訪問時に3〜5行の世界観プロローグを表示
- **異界アーカイブ（LORE）**：デスクトップ2ページ目の独立したリーダー、以下を含む：
  - 器物と登録済みの各世界から動的に生成されるカテゴリタブ
  - デバイス背景ストーリー（起源 / ネクサスコア / 所持者）
  - 各世界の通常エントリは常に閲覧可能
  - 統計・実績条件の達成時にLore完成度へ加算
  - 全体完成度25% / 50% / 75% / 100%で4つの共鳴アーカイブを開放
- **フレーバーテキスト**：各ゲームのメニューページに雰囲気のある世界観テキストを表示
- **完全バイリンガル**：すべてのテキストが中国語と英語に対応

---

## 🎮 接続された世界

| アイコン | ゲーム | 世界名 | 世界観設定 |
|:---:|------|--------|------------|
| ⚫⚪ | **GOMOKU**<br>五目並べ | 陰陽棋境<br>YIN-YANG BOARD | 混沌と秩序の古き神々が白黒の石で宇宙の運命を推論する |
| 🐍 | **SNAKE**<br>スネーク | 噬碼渊<br>CODE ABYSS | デジタルの深淵の底に棲む霊蛇、データの欠片を喰らって生きる |
| 🧱 | **BREAKOUT**<br>ブロック崩し | 星穹壁垒<br>STAR FORTRESS | 失われた宇宙文明が残したエネルギーの城壁と星の欠片 |
| 🔢 | **2048**<br>2048 | 数霊海<br>NUMEN SEA | 純粋な数字で構成された生命体、融合と進化の覚醒の道 |
| 💣 | **MINES**<br>マインスイーパ | 雷原遺跡<br>MINEFIELD RUINS | 大戦争から百年後の焦土で活動する地雷除去技師 |
| 🧊 | **TETRIS**<br>テトリス | 築天塔<br>TOWER OF HEAVEN | 異星の建築マトリックスが天空より降り注ぐ — 真実に触れる塔を築け |
| ✈️ | **AIR RAID**<br>エアレイド | 守望者戦線<br>WARDEN FRONT | 自律戦争ネットワークとの最後の戦い |
| 🛡️ | **TANK DUEL**<br>タンクデュエル | 鋼鉄闘場<br>IRON ARENA | 赤青の戦車が鏡像アリーナで補給を争い、同点ならサドンデスへ進む |

---

## ✨ 主な機能

### 🎯 コア体験

- **起動アニメーション**：4段階プログレスバーによるMERIDIAN世界観起動シーケンス
- **パスワードロック画面**：数字キーパッド + 削除キー、ピクセルアート認証インターフェース
- **デスクトップ環境**：2ページのアイコンレイアウト、マウストレイル粒子エフェクト、毎時時計アニメーション
- **ゲーム内メニュー**：統一されたアーケードスタイルUI（続行 / ニューゲーム / 設定）

### 🏆 実績ウォール

- 8×6 実績バッジグリッド
- バッジをクリックして詳細カードを展開（イーズアウトバックアニメーション）
- ピクセルアート閉じるボタン
- 解除進捗統計、グラデーション背景、ゴールド区切り線
- 解除済みバッジにゴールドスターを表示
- 最大3つの実績通知を同時にスタック表示

### 💾 セーブシステム

| 機能 | 説明 |
|------|------|
| **自動セーブ** | ゲーム終了時に実行状態を自動保存 |
| **再開** | ゲーム再入場時に「続行」ボタンを表示 |
| **クラッシュセーフ** | アトミック書き込み + バックアップ機構でセーブ破損を防止 |
| **バージョン移行** | スキーマv5、レガシーセーブデータを自動マージ |
| **クロスゲーム統計** | プレイ時間、勝率、ベストスコアを統合追跡 |

### ✈️ Air Raid 専用コンテンツ

- **機体スキンシステム**：4種のアンロックスキン（DEFAULT / CRIMSON / AZURE / GOLD）
- **ストーリーシステム**：プロローグ + 8章のストーリーライン、完全ローカライズ済み
- **ストーリーアーカイブ**：9エントリのフルスクリーンリーダー
- **16標準ミッション** + ボスラッシュ + チャレンジモード
- **武器アップグレードシステム**：Cannon / Spread / Laser / Missile

### 🎨 ビジュアルエフェクト

- 統一カラーパレット（クラス `C` が45色以上のAir Raidカラーを一元管理）
- デスクトップ粒子システム（マウストレイル / アイコンホバースパーク / 毎時クロックバースト）
- ゲーム固有の終了遷移アニメーション（各ゲームが入場エフェクトを逆再生）
- Air Raid 3層遷移（星空オーバーレイ + 弾幕カーテン + 同心レーダーリング）
- 実績詳細カードの装飾ボーダー（Cuphead風コーナースクエア）

### 🌍 ローカライゼーション

- ランタイム動的言語切り替え
- Fusion Pixel Font（縫合ピクセルフォント）簡体字中国語プロポーショナル幅バージョン
- `localization.py` 翻訳一元管理、バッチ登録対応
- カバレッジ：UIラベル、ゲームメニュー、実績説明、ストーリーテキスト、Loreエントリ

### 🛠 開発者ツール

- **F10 開発者パネル**：マウスホバーハイライト + クリックで有効化
- 機能：テスト用コンテンツ解除、結果の強制、速度調整、毎時エフェクト発動など
- セッション内のみ有効、永続データに影響なし

---

## 🚀 クイックスタート

### 必要環境

| 依存関係 | バージョン |
|----------|-----------|
| Python | **3.10–3.12** |
| pygame | **2.0以上**（3.0未満） |
| OS | Windows / macOS / Linux |

### インストールと実行

```bash
# 1. リポジトリをクローン
git clone https://github.com/CrescentXiong-1/MERIDIAN.git
cd MERIDIAN

# 2. 依存関係をインストール
pip install -r requirements.txt

# 3. 起動
python MERIDIAN.py
```

> 💡 **ヒント**：依存ライブラリは `pygame` のみです。他のサードパーティライブラリは不要です。

### 共有方法

`MERIDIAN` フォルダ全体をZIP圧縮して送信してください。受信側には Python 3.10–3.12 と `pip install pygame` が必要です。

---

## 🕹 操作方法

### 基本操作

| キー | 操作 |
|:---:|------|
| `ESC` | 前のメニューに戻る / シャットダウン（デスクトップ） |
| `Enter` | 確認 / プロローグスキップ |
| `方向キー / WASD` | ナビゲーション / ゲーム操作 |
| `マウス` | デスクトップアイコン選択、実績ウォール操作 |

### ゲーム別操作

| ゲーム | 特殊キー |
|--------|----------|
| **GOMOKU** | マウスクリックで石を配置、`U` で一手戻す |
| **SNAKE** | 方向キーでヘビの移動方向を制御 |
| **BREAKOUT** | 方向キー / マウスでパドルを制御 |
| **2048** | 方向キーでタイルを結合 |
| **MINES** | 左クリックで開示 / 右クリックでフラグ |
| **TETRIS** | `↑` 回転 / `↓` ソフトドロップ / `Space` ハードドロップ / `C` ホールド / `P` 一時停止 |
| **AIR RAID** | 自動射撃；方向キーで移動 / `Shift` フォーカス / `Space` ミサイル |
| **TANK DUEL（赤）** | `WASD` 8方向移動 / `F` アイテム；自動射撃 |
| **TANK DUEL（青）** | 方向キーで8方向移動 / `Enter` アイテム；自動射撃 |

### 開発者用

| キー | 操作 |
|:---:|------|
| `F10` | 開発者パネルの表示/非表示 |

---

## 📁 プロジェクト構造

```text
MERIDIAN/
├── MERIDIAN.py                  # アプリケーション入口
├── meridian/                    # メインループ、Shell、8ゲーム、共有システム
│   ├── shell_*.py               # 起動、認証、デスクトップ、遷移
│   ├── gomoku.py … tetris.py    # 6本のクラシック1人用ゲーム
│   ├── air_raid.py              # Air Raidのキャンペーンとアーケード
│   ├── tank_engine.py           # Tank Duelの決定論的ルール
│   ├── tank_battle.py           # Tank DuelのPygame表示層
│   └── system.py ほか           # セーブ、完成度、Lore、音声、翻訳、共有UI
├── tests/                       # ルール、セーブ、登録、回帰テスト
├── tools/                       # リリース確認と開発補助
├── assets/                      # フォントなどの静的アセット
├── docs/                        # 翻訳と設計文書
└── Development_Log/            # 開発・意思決定の履歴
```

---

## 🏗 アーキテクチャ

MERIDIANは **Mixinコンポジションパターン** を採用しています：

```
Game(
    ShellMixin,         # 起動 / デスクトップ / パスワード / 遷移
    GomokuMixin,        # 五目並べ
    MinesMixin,         # マインスイーパ
    Game2048Mixin,      # 2048
    BreakoutMixin,      # ブロック崩し
    SnakeMixin,         # スネーク
    TetrisMixin,        # テトリス
    ArcadeHubMixin,     # 共有アーケードシステム
    AirRaidMixin,       # エアレイド
    TankBattleMixin,    # Tank Duel表示層
    DeveloperMixin,     # 開発者ツール
    SystemMixin,        # 設定 / 実績 / Lore
)
```

### 主要デザインパターン

| パターン | 適用 |
|----------|------|
| **ステートマシン** | 3テーブルディスパッチ：`_EVENT_DISPATCH` + `_UPDATE_DISPATCH` + `_DRAW_DISPATCH` |
| **境界付き登録** | 状態、初期化処理、アイコン、Lore、翻訳を `Game` 作成前に明示登録 |
| **Mixinコンポジション** | 各ゲーム・システムモジュールをMixin経由で `Game` に注入 |
| **アトミック書き込み** | 一時ファイルに保存後リネーム、部分書き込みによる破損を防止 |
| **バージョン移行** | `SaveManager._deep_merge()` が新フィールドを自動補完 |

### 状態遷移フロー

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

## 🔌 拡張API

拡張モジュールは `Game()` 作成前にホストが明示的にインポートします。自動プラグイン探索、ホットリロード、第三者向けセーブプロトコルはなく、登録は以後に作成するインスタンスだけに適用されます。

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

# 1. ゲーム世界を登録（世界観、プロローグ、フレーバーテキスト、深層Lore）
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

# 2. 条件付きLore完成度と初期化処理を登録
register_lore_entry(
    "mygame", "mygame_mastery",
    title_en="CRYSTAL MASTERY", title_zh="水晶精通",
    content_en=["The crystal answers."], content_zh=["水晶作出了回应。"],
    unlock="stat:mygame:score:100",
)
register_game_initializer(init_mygame)

# 3. 状態と3ページ目のアイコンを登録
register_game_state("MYGAME_MENU", handle_event, [update], draw)
register_desktop_icon(
    "MYGAME", "open_mygame", page=2,
    subtitle_en="MY WORLD", subtitle_zh="我的世界",
    target_state="MYGAME_MENU", transition_effect="fade",
)

# 4. 翻訳を登録
register_game_translations("mygame", {"MYGAME_PLAY": "开始"})
```

ハンドラには `Game` のメソッド名、または `game` を受け取るcallableを指定できます。有効なアイコンは `target_state` と `on_activate(game)` のどちらか一方だけを使用します。翻訳キーは `game_id` ごとに所有され、競合の上書きには `replace=True` の明示が必要です。`_register_game_states()` は互換ラッパーとしてのみ残ります。

> 📝 完全なAPIドキュメントはソースコードのdocstringを参照してください。

---

## 📦 ビルド

### Windows ワンクリックビルド

```bash
# ビルドスクリプトを実行（PyInstallerが必要）
BUILD_EXE.bat
```

生成された `MERIDIAN.exe` は `dist/` ディレクトリに配置されます。

### 手動ビルド

```bash
pip install pyinstaller
python -m PyInstaller --noconfirm --clean MERIDIAN.spec
```

> ⚠️ ビルド前に `pygame` がインストールされ、`MERIDIAN.spec` のパスが正しいことを確認してください。

---

## 🔎 ローカルリリースチェック

リポジトリのルートで読み取り専用のリリースチェッカーを実行します：

```bash
python tools/check_release.py
```

このコマンドはバージョンと `CHANGELOG.md` のメタデータ、および作業ツリーとローカルバージョンタグの Git 状態のみを確認します。タグを作成せず、プッシュもビルドも行いません。ソースの静的解析は別途実行できます：

```bash
python -m ruff check MERIDIAN.py meridian tools
python -m compileall -q MERIDIAN.py meridian tools
```

---

## 📝 変更履歴

完全な履歴は [CHANGELOG.md](../../CHANGELOG.md) を参照してください。

### 最新安定版: V3.2.0 (2026-07-13) — 「Tank Duel」

- 🛡️ **Tank Duel**：赤対青のローカル対戦、8種のアイテム、3分制とサドンデス
- 💾 **セーブ**：Schema v5、8本すべてが中断セーブと再開に対応
- 🏆 **進行**：8つの接続世界に60個の実績
- 🌌 **Lore**：通常本文は常に読め、条件達成で完成度へ加算し、全体閾値で共鳴アーカイブを開放

安定版以降の変更は [CHANGELOG.md](../../CHANGELOG.md) の `Unreleased` に記録します。

---

## 🤝 コントリビューション

あらゆる形での貢献を歓迎します！バグ報告、機能提案、コード提出など。

### 貢献の流れ

1. このリポジトリを **Fork**
2. 機能ブランチを作成：`git checkout -b feature/amazing-feature`
3. 変更をコミット：`git commit -m 'feat: 素晴らしい機能を追加'`
4. ブランチをプッシュ：`git push origin feature/amazing-feature`
5. **プルリクエスト** を作成

### コミット規約

このプロジェクトは [Conventional Commits](https://www.conventionalcommits.org/) を採用しています：
- `feat:` 新機能
- `fix:` バグ修正
- `docs:` ドキュメント
- `refactor:` コードリファクタリング
- `test:` テスト
- `chore:` ビルド / ツール

---

## 📄 ライセンス

このプロジェクトは **MITライセンス** の下でオープンソース公開されています。

内蔵の **Fusion Pixel Font（縫合ピクセルフォント）** は [SIL Open Font License 1.1](../../assets/fonts/FusionPixelFont-LICENSE-OFL.txt) に基づきます。

---

## 🙏 謝辞

- **[Pygame](https://www.pygame.org/)** — ゲーム開発フレームワーク
- **[Fusion Pixel Font](https://github.com/TakWolf/fusion-pixel-font)** — 中国語表示のための美しいピクセルフォント
- **すべてのコントリビューター** — MERIDIANに貢献してくださった全ての開発者に感謝します

---

<p align="center">
  <sub>MERIDIAN · 幾多の世界。一つの装置。 · 诸界 · 一器</sub>
</p>
