# HymnMania

An automation pipeline that turns classical hymns and classical pieces
(MIDI) into electronic covers and beat-synced videos, then publishes
them: MIDI → speed-adjusted render → Suno AI covers across multiple
electronic genres → AI-visual music videos synced to the beat → upload
to YouTube, Facebook, Instagram, and TikTok.

Version **5.97.41**. Python & TypeScript.

## What it does

1. **Source** — hymns/classical MIDI files (see `CLASSICAL_PIECES.md`;
   `BLOCKED_HYMNS.md` tracks pieces that can't be used)
2. **Render** — speed/tempo-adjusted audio renders of the source pieces
3. **Cover** — Suno AI generates electronic covers in multiple genres
   per piece (`gen_cover_*.py`, `full_hymn_pipeline.py`)
4. **Video** — beat-synced music videos assembled with AI-generated
   visuals (`regen_beat_videos.py`)
5. **Publish** — scheduled uploads to YouTube, Facebook, Instagram, and
   TikTok, with caption generation and throttling
   (`scheduler_v2.py`, `*_poster.py`, `post_all_platforms.py`)

## A note on the tree

This repo is a **live bot workspace**, not a clean package: the root is
full of runtime state files (`.upload_queue.json`,
`.social_posted.json`, `.suno_credits_before.json`,
`.throttle_state.json`, caption drafts, promo-sprint logs) written by
the pipeline as it runs, plus session markers from the AI tools that
operate it, and committed SQLite databases (`classicalmania.db`,
`borg.db`, `tormentnexus.db`). The state files are the pipeline's
memory — deleting them changes what it will do next. Start from the
docs (`AGENTS.md`, `CHANGELOG.md`, and the pipeline scripts) rather
than treating the root as source layout.

## Related

Harry's fork of this project (GitHub user Dimensionalplane) grew into
**TurntUpToddler** (~209 commits) — the hymn-cover idea taken further
as its own thing.

## Status

Operated automation, single-purpose and personal. Last commit
2026-11-08 (submodule re-pin); recent commits are maintenance and
syncs rather than new pipeline features. Expect the tree to change
while it is running; there is no stable release to consume.
