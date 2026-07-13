# MERIDIAN v3.2.0 Release and v3.3.0 Upgrade Design

Date: 2026-07-13
Status: Confirmed design, pending implementation plan

## 1. Scope and release boundary

This program is split into two releases.

- `v3.2.0` freezes the current Tank Duel release as a stable local milestone.
- `v3.3.0-dev` contains the following upgrade work, in order:
  1. bilingual screenshot regression tests;
  2. shared UI and three-level volume controls;
  3. Tank Duel second-pass visuals and item effects;
  4. cross-world lore and global completion.

No remote push, executable packaging, or PyInstaller command is part of this work. The local
annotated `v3.2.0` tag is created only after a final user confirmation.

## 2. v3.2.0 local release system

### 2.1 Changelog

`CHANGELOG.md` will be normalized to UTF-8 and a Keep a Changelog-style structure. Existing
history remains available, but visible encoding damage and malformed headings are repaired.

The top of the file contains:

- `Unreleased`, used for all work not yet assigned to a release;
- `[3.2.0] - 2026-07-13`, documenting Tank Duel;
- the preserved older release history.

The `3.2.0` entry covers local two-player rules, eight items, twelve achievements, Schema v5,
bilingual presentation, dynamic original music, the dedicated transition, statistics, and
interrupted-match restoration.

### 2.2 Single version source

The application gains one authoritative version module, for example
`meridian/version.py::__version__`. User-visible version text and release checks read from this
module. Version strings must not be independently duplicated across UI code.

The stable release reports `3.2.0`. Subsequent development reports `3.3.0-dev` and writes changes
under `Unreleased`.

### 2.3 Release check and tag

A local release-check command verifies:

- version and changelog agreement;
- a clean tracked worktree;
- absence of a duplicate tag;
- pytest, Ruff, compileall, and the existing rendering smoke tests.

The command checks only. It does not build, package, tag, or push. After all gates pass, the user
is asked once more before creation of the annotated local tag `v3.2.0`.

The new screenshot suite belongs to `v3.3.0-dev` and therefore is not a prerequisite for freezing
the earlier `v3.2.0` milestone.

## 3. Bilingual screenshot regression system

### 3.1 Baseline matrix

The initial suite contains twelve deterministic scenes in English and Simplified Chinese, for 24
baseline PNGs:

1. desktop page one;
2. desktop page two;
3. system settings;
4. player profile statistics;
5. achievement wall page one;
6. lore category and entry list;
7. Tank Duel menu;
8. Tank Duel controls;
9. Tank Duel normal combat HUD;
10. Tank Duel pause overlay;
11. Tank Duel sudden death;
12. Tank Duel results.

### 3.2 Determinism

Scenes are constructed directly from fixed state rather than replayed mouse input. Rendering uses:

- a 1280 by 720 logical surface;
- SDL dummy video and audio drivers;
- fixed random seeds, clock, battery value, animation frame, and language;
- disabled shake;
- fixed particles where a scene requires particles;
- a bundled font with no operating-system CJK fallback.

Dynamic regions that do not belong to the assertion are frozen or masked. Animation scenes use a
named, fixed frame.

### 3.3 Comparison and baseline updates

The test first checks exact dimensions, then compares pixels with a very small documented tolerance
for Pygame patch-level raster differences. Failure output includes the scene name, differing-pixel
ratio, actual PNG, and a visual diff PNG.

Text and controls also receive rectangle-boundary assertions to catch clipping and overlap that a
small pixel tolerance could hide.

Baselines live under `tests/visual_baselines/en/` and `tests/visual_baselines/zh_hans/`. A dedicated
explicit command updates them. Normal tests and CI never overwrite baselines. CI retains diff
artifacts only on failure.

## 4. Shared UI and volume system

### 4.1 Shared presentation primitives

Common primitives cover title frames, panels, buttons, pause overlays, result overlays, label rows,
and sliders. They own text measurement, fallback sizing, fixed CJK baselines, center/right anchors,
and overflow detection.

Games retain their own palettes, motifs, and decorative art. The shared layer standardizes
structure, spacing, focus, hover, pressed, disabled, and keyboard-focus behavior without erasing
world identity.

Migration starts with the pages protected by screenshot tests. Other pages move incrementally; the
upgrade does not require an all-at-once rendering rewrite.

### 4.2 Audio model

Persistence gains `master_volume`, defaulting to `1.0` for old saves. Effective levels are:

- music: `master_volume * music_volume * scene_scale`;
- sound effects: `master_volume * sfx_volume * event_gain`.

Mute is independent and does not destroy saved slider values. Every system click, shot, explosion,
and notification uses the same mixer entry point. Persistence migration must preserve existing
music and SFX values.

### 4.3 Expandable desktop control

The collapsed state is a speaker button. Clicking it expands a panel from left to right. The width
passes the final width to approximately 108 percent, then springs back to 100 percent using a
deterministic ease-out-back curve.

The panel contains, from top to bottom:

1. master volume;
2. music volume;
3. sound-effect volume.

Each row contains an icon, localized label, track, thumb, and percentage. Rows fade and slide in
with a short stagger. A left-arrow button fixed to the right edge closes the panel: content fades,
then the panel contracts smoothly toward the speaker button.

Animation timings are approximately 420 ms in Full, 240 ms in Reduced, and immediate in Off. Mouse
hit areas follow the visual geometry throughout expansion, overshoot, dragging, and collapse.
Escape, desktop page changes, and game entry cancel drag state safely. Values use the existing
delayed persistence mechanism.

Collapsed, overshoot, settled, and closing geometry are covered by deterministic component-render
tests. They do not expand the confirmed twelve-scene full-screen baseline matrix.

## 5. Tank Duel second-pass polish

### 5.1 Event-driven combat feedback

Visuals consume engine events and never alter collision or damage rules. The second pass adds:

- animated tracks and turning frames;
- turret recoil, muzzle flash, and short-lived shell cases;
- faction-colored projectile trails;
- a gold core and longer trail for piercing shells;
- distinct shield, normal-hit, piercing-hit, and destruction feedback;
- a pixel shock ring, armor fragments, smoke, and score popups on destruction;
- a warning frame and scan-in before respawn.

### 5.2 Eight item identities

Letter placeholders are replaced by eight distinct pixel icons. Pickup, HUD slot, use, active,
impact, and expiry states are visually distinguishable.

- Repair: green pixels converge on life cells.
- Shield: a ring surrounds the tank and breaks on absorption.
- Overdrive: track afterimages and a duration bar.
- Mine: placement pulse and proximity blinking.
- EMP: purple scan wave, enemy HUD interference, and fire-lock countdown.
- Piercing: gold muzzle state and remaining enhanced-shot count.
- Smoke: layered pixel smoke with stronger center occlusion.
- Warp: pixel disassembly at origin and reconstruction at destination.

Each item has a dedicated effect sound routed through master and SFX volume.

### 5.3 Effect levels

- Full: all animation, particles, afterimages, shock rings, and light shake.
- Reduced: essential muzzle, hit, item-state, and danger feedback with fewer particles and no
  persistent afterimage.
- Off: static icons, state bars, required smoke occlusion, and rule-critical indicators only.

Rule information remains readable at every level. Screenshot baselines use Reduced. Full receives
event-level rendering tests with deterministic particle inputs.

Tank menu and result pages migrate to the shared UI. The menu presents both control schemes, match
rules, and access to the eight-item guide. Results emphasize winner, score, accuracy, item use, and
rematch.

## 6. Cross-world lore and global completion

### 6.1 Completion calculation

The eight worlds are equally weighted. A world score is:

- achievements: 40 percent;
- key objectives: 35 percent;
- collected lore: 25 percent.

Global completion is the integer average of the eight world scores. Percentages are derived by a
pure calculator from stored facts and are not persisted as redundant values.

Old saves derive progress from statistics, level/campaign data, achievements, and unlocked lore.
Missing evidence contributes zero and never clears the save or grants an unprovable completion.

### 6.2 Key objectives

Objectives reflect each game's structure:

- Gomoku: completed games, wins with both sides, and a cumulative-win milestone.
- Snake: score and length milestones.
- Breakout: representative clears and final clear.
- 2048: reach 512, 1024, and 2048.
- Mines: completion milestones across configured difficulty/board targets.
- Tetris: level, line, and four-line-clear milestones.
- Air Raid: standard campaign, challenge campaign, and boss rush.
- Tank Duel: first match, first win, all eight items, and a sudden-death win.

Exact thresholds are fixed in the implementation plan and covered by boundary tests.

### 6.3 UI and cross-world archive

The profile shows a global completion bar or pixel ring plus eight world cards. Each card exposes
the total and the achievement/objective/lore breakdown. Opening a card lists unfinished objectives
without revealing locked lore prose.

Cross-world archive entries unlock at 25, 50, 75, and 100 percent. Each entry links at least three
worlds into the central resonance narrative. At 100 percent, a final MERIDIAN archive and a desktop
visual variation unlock. This is cosmetic and never blocks normal play.

All new prose is paired English and Simplified Chinese. Unlock notifications use the existing queue
and fire once. Developer mode does not write official completion or lore unlocks.

## 7. Ordering, compatibility, and verification

Implementation order is mandatory because each stage protects the next:

1. freeze and locally tag `v3.2.0` after confirmation;
2. move to `3.3.0-dev` and establish screenshots;
3. refactor shared UI and audio under screenshot protection;
4. polish Tank Duel using shared primitives and effect levels;
5. add completion and cross-world lore;
6. run final bilingual visual review and full verification.

Each stage has focused tests, full pytest, Ruff, compileall, and `git diff --check`. Schema migrations
must preserve old saves. No stage authorizes packaging or remote pushes.
