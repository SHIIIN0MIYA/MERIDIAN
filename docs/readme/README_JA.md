<p align="center">
  <img src="../../assets/banner.png" alt="MERIDIAN Banner" width="800" onerror="this.style.display='none'">
</p>

<h1 align="center">🌐 MERIDIAN · 子午線</h1>

<p align="center"><strong>七つの世界。一つの装置。</strong></p>
<p align="center"><em>七界 · 一器 · Seven Worlds. One Device.</em></p>

<p align="center">
  <img src="https://github.com/CrescentXiong-1/MERIDIAN/actions/workflows/ci.yml/badge.svg" alt="CI ステータス">
  <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Python">
  <img src="https://img.shields.io/badge/pygame-2.x-green" alt="Pygame">
  <img src="https://img.shields.io/badge/ライセンス-MIT-yellow" alt="ライセンス">
  <img src="https://img.shields.io/badge/テスト-50%2B-brightgreen" alt="テスト">
  <img src="https://img.shields.io/badge/行数-~15,700-orange" alt="コード行数">
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
- [七つの世界](#-七つの世界)
- [主な機能](#-主な機能)
- [クイックスタート](#-クイックスタート)
- [操作方法](#-操作方法)
- [プロジェクト構造](#-プロジェクト構造)
- [アーキテクチャ](#-アーキテクチャ)
- [拡張API](#-拡張api)
- [ビルド](#-ビルド)
- [テスト](#-テスト)
- [変更履歴](#-変更履歴)
- [コントリビューション](#-コントリビューション)
- [ライセンス](#-ライセンス)
- [謝辞](#-謝辞)

---

## 🌌 概要

**MERIDIAN（子午線）** は、起源不明の携帯型装置です。その「画面」は通常のディスプレイではなく、**共鳴レンズ**です。七つの現実の破片が七つのクラシックアーケードゲームに封印され、それぞれが独立した世界への安定したポータルとして機能しています。

これは普通のゲーム機ではありません。これは**次元間観測デバイス**です。

**Python + Pygame** で構築されたこのプロジェクトは、完全なマルチゲームプラットフォームシミュレーターです。以下の要素を兼ね備えています：

- 🎮 **完全に再現された7つのクラシックアーケードゲーム**
- 📚 **深い世界観ナラティブシステム** — 各ゲームに独自の背景設定
- 🏆 **50以上の実績システム** — ゲーム間でプレイヤーの進行を追跡
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
  - 8つのカテゴリタブ（器物の起源 + 七世界）
  - デバイス背景ストーリー（起源 / ネクサスコア / 所持者）
  - 世界ごとに1〜2の深層設定エントリ
  - 統計や実績で解除される隠しエントリ
- **フレーバーテキスト**：各ゲームのメニューページに雰囲気のある世界観テキストを表示
- **完全バイリンガル**：すべてのテキストが中国語と英語に対応

---

## 🎮 七つの世界

| アイコン | ゲーム | 世界名 | 世界観設定 |
|:---:|------|--------|------------|
| ⚫⚪ | **GOMOKU**<br>五目並べ | 陰陽棋境<br>YIN-YANG BOARD | 混沌と秩序の古き神々が白黒の石で宇宙の運命を推論する |
| 🐍 | **SNAKE**<br>スネーク | 噬碼渊<br>CODE ABYSS | デジタルの深淵の底に棲む霊蛇、データの欠片を喰らって生きる |
| 🧱 | **BREAKOUT**<br>ブロック崩し | 星穹壁垒<br>STAR FORTRESS | 失われた宇宙文明が残したエネルギーの城壁と星の欠片 |
| 🔢 | **2048**<br>2048 | 数霊海<br>NUMEN SEA | 純粋な数字で構成された生命体、融合と進化の覚醒の道 |
| 💣 | **MINES**<br>マインスイーパ | 雷原遺跡<br>MINEFIELD RUINS | 大戦争から百年後の焦土で活動する地雷除去技師 |
| 🧊 | **TETRIS**<br>テトリス | 築天塔<br>TOWER OF HEAVEN | 異星の建築マトリックスが天空より降り注ぐ — 真実に触れる塔を築け |
| ✈️ | **AIR RAID**<br>エアレイド | 守望者戦線<br>WARDEN FRONT | 自律戦争ネットワークとの最後の戦い |

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
| **バージョン移行** | スキーマv4、レガシーセーブデータを自動マージ |
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
- 機能：全レベル解除、全スキン解除、毎時エフェクト発動、セーブ消去など
- セッション内のみ有効、永続データに影響なし

---

## 🚀 クイックスタート

### 必要環境

| 依存関係 | バージョン |
|----------|-----------|
| Python | **3.10以上** |
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

`MERIDIAN` フォルダ全体をZIP圧縮して送信してください。受信側は Python 3.10以上と `pip install pygame` のみ必要です。

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
| **AIR RAID** | 方向キーで移動 / `Z` 射撃 / `X` ミサイル / `Shift` フォーカスモード |

### 開発者用

| キー | 操作 |
|:---:|------|
| `F10` | 開発者パネルの表示/非表示 |

---

## 📁 プロジェクト構造

```
MERIDIAN/
├── MERIDIAN.py                  # エントリポイント
├── MERIDIAN.spec                # PyInstaller ビルド設定
├── BUILD_EXE.bat                # Windows ワンクリックビルドスクリプト
├── requirements.txt             # Python 依存関係
├── reasonix.toml                # エディター設定
│
├── meridian/                    # コアパッケージ
│   ├── __init__.py
│   ├── app.py                   # ゲーム構成、メインループ、状態ディスパッチ
│   ├── common.py                # グローバル定数、カラークラス、レイアウトパラメータ
│   ├── lore.py                  # 世界観データと登録API
│   ├── audio.py                 # プロシージャルBGM・効果音エンジン
│   ├── persistence.py           # バージョン管理クラッシュセーフセーブ管理
│   ├── localization.py          # ランタイムバイリンガルシステム + 中国語フォント
│   ├── developer.py             # 開発者パネル（セッションのみ）
│   │
│   ├── shell.py                 # シェルシステム集約
│   ├── shell_boot.py            # 起動シーケンス
│   ├── shell_password.py        # パスワードロック画面認証
│   ├── shell_desktop.py         # デスクトップ環境とアイコンシステム
│   ├── shell_transitions.py     # シーン遷移アニメーション
│   │
│   ├── arcade_common.py         # 共有アーケードUI + プロローグシステム
│   ├── arcade_levels.py         # Air Raid キャンプレーンデータ
│   │
│   ├── gomoku.py                # 五目並べ（陰陽棋境）
│   ├── snake.py                 # スネーク（噬碼渊）
│   ├── breakout.py              # ブロック崩し（星穹壁垒）
│   ├── g2048.py                 # 2048（数霊海）
│   ├── mines.py                 # マインスイーパ（雷原遺跡）
│   ├── tetris.py                # テトリス（築天塔）
│   ├── air_raid.py              # エアレイド（守望者戦線）
│   │
│   └── system.py                # 設定、プロフィール、実績、Loreリーダー
│
├── assets/                      # 静的アセット
│   └── fonts/                   # Fusion Pixel Font（SIL Open License 1.1）
│
├── tests/                       # テストスイート（50以上のテスト）
│   ├── conftest.py              # 共有フィクスチャ + SDLダミードライバー
│   ├── test_smoke.py            # スモークテスト
│   ├── test_arcade_games.py     # アーケードゲームテスト
│   └── test_persistence.py      # 永続化システムテスト
│
└── .github/workflows/
    └── ci.yml                   # GitHub Actions CI（Windows, Python 3.10–3.12）
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
    DeveloperMixin,     # 開発者ツール
    SystemMixin,        # 設定 / 実績 / Lore
)
```

### 主要デザインパターン

| パターン | 適用 |
|----------|------|
| **ステートマシン** | 3テーブルディスパッチ：`_EVENT_DISPATCH` + `_UPDATE_DISPATCH` + `_DRAW_DISPATCH` |
| **動的登録** | `_GAME_STATE_REGISTRY` により `app.py` を修正せずに新ゲームを追加可能 |
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
                                    ├── SETTINGS → SYSTEM_SETTINGS / PROFILE
                                    ├── ACHIEVEMENT_WALL
                                    └── LORE_READER → LORE_STORY
```

---

## 🔌 拡張API

新ゲームのために完全な登録APIが用意されています：

```python
from meridian.lore import register_game_world, register_device_lore
from meridian.shell_desktop import register_desktop_icon
from meridian.app import _register_game_states
from meridian.localization import register_game_translations

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
    lore_entries=[...],
    desktop_subtitle_en="MY WORLD",
    desktop_subtitle_zh="我的世界",
)

# 2. デスクトップアイコンを登録
register_desktop_icon("MYGAME", "open_mygame", page=0, ...)

# 3. 状態ディスパッチを動的登録（app.pyの修正不要）
_register_game_states("MYGAME_MENU", "_handle_mygame_menu", [], "_draw_mygame_menu")

# 4. 翻訳を登録
register_game_translations("mygame", {"PLAY": "开始", "SCORE": "得分"})
```

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

## 🧪 テスト

プロジェクトには **50以上のユニットテスト** が含まれています：

```bash
# 全テストを実行
python -m pytest tests/ -v

# 特定のテストファイルを実行
python -m pytest tests/test_smoke.py -v
python -m pytest tests/test_arcade_games.py -v
python -m pytest tests/test_persistence.py -v
```

### テストカバレッジ

| テストファイル | 内容 |
|---------------|------|
| `test_smoke.py` | スモークテスト：起動、状態遷移、基本レンダリング |
| `test_arcade_games.py` | アーケードゲーム：メニュー操作、ゲームロジック、セーブ再開 |
| `test_persistence.py` | 永続化：セーブ読み書き、バージョン移行、クラッシュリカバリ |

### CI / CD

GitHub Actionsによる **Windows** 上での **Python 3.10 / 3.11 / 3.12** に対する自動テスト。毎回のプッシュとプルリクエストで実行されます。

---

## 📝 変更履歴

完全な履歴は [CHANGELOG.md](../../CHANGELOG.md) を参照してください。

### 最新: V3.1.0 (2026-07-02) — 「MERIDIAN」

- 🌌 **世界観システム**：メタナラティブ、七世界設定、プロローグシステム、異界アーカイブ
- 🔌 **拡張API**：5つの登録関数、コード修正不要の統合
- 🏆 **実績ウォール**：V3.0.0で導入、V3.1.0で改良
- 💾 **ゲーム再開**：全7ゲームがセーブ・再開に対応
- ✈️ **Air Raid ストーリー**：8章キャンペーン + ストーリーアーカイブ
- 🎨 **ビジュアル強化**：デスクトップ粒子、終了遷移アニメーション、統一カラーパレット

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
  <sub>MERIDIAN · 七つの世界。一つの装置。 · 七界 · 一器</sub>
</p>
