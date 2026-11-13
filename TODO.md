# HymnMania Immediate Tasks (v5.97.41)

- [x] Fetch all remotes and tags recursively across `hymnmania` (`L0`), `ableton_psytrance_hymn_creator` (`L1`), and `hymnmania_src` (`L2`)
- [x] Reconcile `main` and `master` branches + `origin/backup/wip-leader-sync-20261107` into unified `main` (`v5.97.41`)
- [x] Reconcile `submodules/ableton_psytrance_hymn_creator` to `v1.18.5` (`522f7bc`), retain `HeadlessSuno` fallback, fix Windows test spawn, and pass `tsc` + Jest (`3/3`)
- [x] Track Zernio/Catbox TikTok uploader scripts (`scripts/zernio_*.py`), `social_media_mirror.py`, and non-sensitive posting logs
- [x] Harden `.gitignore` against credential leaks (`token_*.json`, `.social_config/`, `magnific_cookies.json`) while tracking AI memory/handoffs/docs
- [x] Make all root `.bat` runners (`run_scheduler.bat`, `run_scheduler_backup.bat`, `build.bat`, `start.bat`, etc.) portable across machines
- [x] Synchronize version `5.97.41` across `VERSION`, `VERSION.md`, `docs/VERSION.md`, `hymn_remaker/VERSION.md`, `CHANGELOG.md`, `AGENTS.md`, `README.md`, and `HANDOFF.md`
- [x] Generate complete `SUBMODULE_INVENTORY.md` structural map
- [ ] Capture & compose remaining banked cover clips from `.promo_sprint.json` / `.promo_sprint_r2.json` (~1,487 clips) via `cap_cycle.py` → `compose_pending.py`
- [ ] Investigate Suno's post-`v5.97.40` cover flow inside `Studio` (`Edit in Studio` / `/api/generate` request capture) to restore `gen_only.py` cover triggering
- [ ] Resume Zernio TikTok batch queue (`scripts/zernio_tiktok_batch.py`, 135 vertical videos remaining in queue)
- [ ] Set up separate scheduler queue for `@SymphonicPsychedelic` classical channel (`youtube_channels.json`)
- [ ] Reach 500 YouTube subscribers on `@ResurrectingBeats` for Community tab access
