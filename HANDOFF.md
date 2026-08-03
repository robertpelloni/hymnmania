# HANDOFF — v5.97.6 Repository Sync

## Session: 2026-08-03 — TikTok + Shorts + Crossfade

### New Features
- **Crossfade transitions**: 0.4s ffmpeg xfade between all clips
- **Custom thumbnails**: Genre + hymn + RESURRECTING BEATS overlay
- **YouTube Shorts**: 9:16 vertical converter + uploader
- **TikTok**: 9:16 converter, SEO caption template, CDB upload script
- **Weekly Scheduler**: Mon-Fri auto-posting to TikTok + Facebook
- **SpiritualEDM hashtag**: Replaced #ChristianPsytrance across all platforms
- **AI Metadata**: JSON-LD Schema.org hidden in descriptions for AI crawler indexing
- **Tempo-scaled beats**: 4/8/12/16 beat phrases based on BPM

### Pipeline Scripts
| Script | Purpose |
|--------|---------|
| `quick_composer.py` | Beat videos with intro/outro + thumbnails + crossfade |
| `post_all_platforms.py` | Post to YouTube + Shorts + TikTok simultaneously |
| `tiktok_poster.py` | 9:16 vertical convert + TikTok CDP upload |
| `scheduler_bot.py` | Weekly auto-poster Mon-Fri |
| `daily_scheduler.py` | Facebook poster (bare URL → preview method) |
| `youtube_update_descriptions.py` | YT description template |
| `rename_youtube_titles.py` | Standard title format |

### Platform Status
| Platform | Status | Notes |
|----------|--------|-------|
| YouTube Full | 700+ videos | API uploads working |
| YouTube Shorts | 1 test | Need batch converter |
| YouTube Community | Blocked | Requires 500 subscribers |
| Facebook | 50+ posts | CDP working |
| TikTok | Ready | Need @resurrecting.beat login |
| Instagram | Credentials saved | No automator yet |

### Known Blockers
- TikTok logged into @hypernexusllc, not @resurrecting.beat
- YouTube Community tab: 500 sub minimum
- Magnific credits: check ~/.env for remaining
