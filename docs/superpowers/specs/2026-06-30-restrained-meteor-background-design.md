# Restrained Meteor Background Design

Date: 2026-06-30

## Goal
Add a restrained meteor animation to the desktop screen and boot screen backgrounds without distracting from icons, boot text, progress UI, or the existing pixel-art style.

## Chosen Direction
Use the user's B setting: a slightly visible but still restrained effect. At most two meteors are visible at once. Each follows a deterministic staggered cycle of roughly 2-4 seconds, so the motion feels alive but not noisy.

## Design
Create one shared Pygame drawing helper in `haos_game_deck/common.py`. The helper accepts a target rect, animation tick, density preset, and alpha scale. It draws short diagonal pixel-style streaks from upper-right toward lower-left using the existing desktop cyan palette. The helper clips to the supplied rect so meteors stay inside the boot panel or desktop display.

Desktop wallpaper calls the helper after static star dots and before desktop icons/status content. Boot screen calls the helper after boot star dots and before text/progress content. The animation is purely visual and deterministic, with no state mutation and no new assets.

## Testing
Run the existing pytest suite to catch regressions. Run a syntax compile pass. Launch the app and capture screenshots for visual verification of boot/desktop rendering.
