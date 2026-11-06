# SecondBrain — Design System

Tokens live in `apps/web/src/design/tokens.css` (`:root` dark, `[data-theme=light]` light): `--bg/surface/surface2/border/text/muted/accent/danger/warn/ok`, radii 12/8px, single accent (blue), no gradient abuse. Typography: system stack, 15px base, 24px page titles. Components: cards, buttons (primary/ghost/danger), inputs, badges, timeline, modal, toasts, skeletons. States: every async view has loading/empty/error-with-retry. Outside this file, see `ACCESSIBILITY.md`, `INFORMATION_ARCHITECTURE.md`.
