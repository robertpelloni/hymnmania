# Submodule Inventory & Structural Map (v5.97.41)

Last updated: `2026-11-12`

## Repository Hierarchy

```text
hymnmania/ (L0 Root — https://github.com/robertpelloni/hymnmania, default branch: main, v5.97.41)
├── build.bat / start.bat / run_*.bat        # Portable Windows batch runners & task entrypoints
├── scheduler_v2.py                          # Quality-gated multi-platform publisher (YT + TT + FB + IG)
├── cap_cycle.py / suno_auth.py / gen_only.py # Suno CDP capture, live JWT auth & cover orchestration (port 9333)
├── quick_composer.py / compose_pending.py   # Beat-synced 16:9 & 9:16 video composer
├── post_to_youtube.py                       # YouTube Data API v3 uploader + quality gate
├── social_media_mirror.py                   # Multi-platform blog mirror (YT / FB / X / LinkedIn / Bluesky)
├── scripts/                                 # MIDI speed synthesis, vertical video cropper, Zernio/Catbox uploaders
├── hymn_remaker/                            # FastAPI/Streamlit core engine, OMR, MIDI database & tests
├── services/                                # Distributed render & automation worker services
└── submodules/
    └── ableton_psytrance_hymn_creator/ (L1 Submodule — v1.18.5)
        ├── src/                             # TypeScript Psy-Mono & House sequencers, Express server, Radio & AIBridge
        ├── pipeline/                        # Python sonic_vacuum & house_quantizer DSP scripts
        ├── tests/                           # Jest integration suite (pipeline.test.ts)
        └── hymnmania_src/ (L2 Nested Submodule — update = none cycle-break)
```

## Submodule Structural Table

| Layer | Path in Layout | Remote Source URL | Branch / Update Policy | Pinned Commit SHA | Package Version | Notes |
|---|---|---|---|---|---|---|
| **L0 (Root)** | `.` | `https://github.com/robertpelloni/hymnmania` | `main` (synced with `master`) | *(current HEAD)* | `v5.97.41` | Primary HymnMania automation workspace (`fork: false`). |
| **L1** | `submodules/ableton_psytrance_hymn_creator` | `https://github.com/robertpelloni/ableton_psytrance_hymn_creator` | `main` (standard tracking) | `522f7bc6f186611c0e442b0c30e53082da9dc676` | `v1.18.5` | TypeScript/Python algorithmic Psy-Mono + House creator, Matchering -7 LUFS mastering, Icecast radio, dual `udio_automation.py` + `HeadlessSuno` AI bridge. |
| **L2** | `submodules/ableton_psytrance_hymn_creator/hymnmania_src` | `https://github.com/robertpelloni/hymnmania.git` | `branch = main`, **`update = none`** | `cc236980a4a9687e8510e2d6195cd024ce92b085` | `v5.97.40` (at pin) | Intentional cycle-breaker (`update = none` in L1 `.gitmodules`) preventing infinite mutual recursion (`hymnmania` ↔ `ableton_psytrance_hymn_creator` ↔ `hymnmania_src`) during recursive clones. |

## Branch Reconciliation Matrix (Verified `2026-11-12`)

| Repository | Branch | Disposition | Details |
|---|---|---|---|
| `robertpelloni/hymnmania` | `main` & `master` | **Unified** | Local `main` fast-forwarded `+180` to `origin/main` (`0219502`), forward-merged `master` (`be45b31`), and unified at `v5.97.41`. |
| `robertpelloni/hymnmania` | `origin/backup/wip-leader-sync-20261107` | **Merged** | `2a7416a` (12 `.tormentnexus/handoffs/*.json` snapshots + `AGENTS.md`) merged into `main` & `master`. |
| `robertpelloni/hymnmania` | Closed PR #17 (`Dimensionalplane/TurntUpToddler`) | **Excluded (External Fork)** | Originated from external fork `Dimensionalplane/TurntUpToddler` (`TUT` rebrand, closed `2026-07-03`); not under `github.com/robertpelloni`. |
| `robertpelloni/ableton_psytrance_hymn_creator` | `main` | **Updated & Pushed (`522f7bc`)** | Fast-forwarded to `origin/main` (`0268265`), bumped to `v1.18.5`, `tsc` + Jest `3/3` green. |
| `robertpelloni/ableton_psytrance_hymn_creator` | `origin/feat/vertical-video-generation-3432640621787520051` | **Already Merged (`c10d152`)** | Verified ancestor of `main` (`0` unmerged commits). |
| `robertpelloni/ableton_psytrance_hymn_creator` | `origin/jules-12359894311656669020-972f5851` | **Already Merged (`7188cb6`) + Retained Fallback** | Verified ancestor of `main`; `src/integrators/headless_suno.ts` restored as alternate CDP adapter alongside `udio_automation.py`. |
| `robertpelloni/ableton_psytrance_hymn_creator` | `origin/jules-6626364804574846888-8b827c28` | **Already Merged (`20d1092`)** | Verified ancestor of `main` (`mastering_engine.py` relocated to `src/services/mastering/`). |
