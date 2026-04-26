# CleverPachonc
![Version](https://img.shields.io/badge/version-alpha_0.6.0-orange.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A League of Legends coaching platform named after the adorable TFT Little Legend, Pachonc.
Search any summoner by Riot ID to get ranked stats, champion mastery, match history, and
AI-powered coaching — all in a clean dark-themed web UI.

---

## Features

- **Ranked stats** — tier, LP, win/loss record per queue
- **Champion mastery** — top 5 champions with mastery level and points
- **Match history** — last 20 ranked solo/duo games with champion, KDA, CS, items, and role
- **Per-champion stats** — sortable table of win rate, KDA, and CS/min across all tracked games
- **Win-rate chart** — 20-game visual history with overall win percentage
- **AI coaching** — session-level analysis powered by Claude: strongest habits, key mistake, improvement path, and meta awareness
- **Per-match AI coach** — click any match for a detailed breakdown: champion assessment, key mistake, ward map heatmap, scoreboard, and rune display
- **Pre-session advisor** — before your next session, see your best meta pick today, a ban recommendation, and a tilt alert if you're on a loss streak
- **Champion pick rates** — browse champions by role sorted by pick rate, click any for splash art and detail view

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 + Flask (Vercel serverless) |
| API calls | asyncio + aiohttp (concurrent, rate-limit-aware) |
| AI coaching | Anthropic Claude API |
| Frontend | React 18 + Vite + Tailwind CSS |
| Charts | Recharts |
| Champion data | Riot Data Dragon CDN |
| Pick rate data | Meraki Analytics CDN |
| Deploy | Vercel |
| Meta cache | GitHub Actions (daily cron) |

## Local development

**Prerequisites:** Python 3.12+, Node 18+

```bash
# 1. Clone and install Python dependencies
git clone https://github.com/HenryGarban/CleverPachonc.git
cd CleverPachonc
pip install -r requirements.txt

# 2. Set your environment variables
cp .env.example .env
# Edit .env and set:
#   RIOT_API_KEY=RGAPI-...
#   ANTHROPIC_API_KEY=sk-ant-...

# 3. Start the Flask backend
FLASK_APP=api/index.py flask run --port 5000

# 4. In a second terminal, start the React frontend
cd frontend
npm install
npm run dev
# Visit http://localhost:5173
```

## Vercel deployment

1. Push the repo to GitHub.
2. Import the project into Vercel.
3. In **Project Settings → Environment Variables**, add `RIOT_API_KEY` and `ANTHROPIC_API_KEY`.
4. Deploy — Vercel uses `vercel.json` to build the frontend and serve the Flask function.

## Meta cache (GitHub Actions)

Champion pick rate data is fetched daily from [Meraki Analytics](https://meraki.gg) and
committed to `backend/meta_cache.json` by the workflow in `.github/workflows/fetch_meta.yml`.
To refresh manually: **Actions → Fetch Meta Cache → Run workflow**.

## Riot Games API compliance

This application:

- Uses the Riot Games API solely to display publicly available summoner statistics.
- Does **not** store, log, or share any summoner data. All data is fetched on demand and
  lives only in the user's browser session.
- Does **not** collect cookies, run analytics, or monetise user data in any form.
- Respects rate limits via an `asyncio.Semaphore` cap on concurrent requests and exponential
  backoff with `Retry-After` header support on HTTP 429 responses.
- Displays the required Riot Games legal notice on every page of the application.

### Legal notice

CleverPachonc isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot
Games or anyone officially involved in producing or managing Riot Games properties. Riot Games,
League of Legends and all associated properties are trademarks or registered trademarks of
Riot Games, Inc.

## Privacy

CleverPachonc has no database. The only data transmitted to the server is the Riot ID and
region you type into the search box, which is forwarded to the Riot Games API and immediately
discarded. AI coaching submits match statistics (no personal account details) to the Anthropic
Claude API. See the in-app Privacy Policy (footer) for full details.

## Project structure

```
CleverPachonc/
├── api/index.py              # Flask serverless entry point (Vercel)
├── backend/
│   ├── riot_api.py           # Async Riot API client
│   ├── data_dragon.py        # Data Dragon version/asset resolution
│   ├── ai_coach.py           # Claude coaching prompt + response parsing
│   ├── meta_cache.json       # Committed champion pick rate cache
│   └── analysis/
│       ├── match_analysis.py     # Match history aggregation
│       ├── champion_stats.py     # Per-champion stat breakdowns
│       ├── meta_fetcher.py       # Reads meta_cache.json / Meraki fallback
│       ├── meta_analysis.py      # Meta gap and tilt detection logic
│       └── coach_analysis.py     # Combines stats + meta for coaching
├── frontend/
│   └── src/components/       # React UI components (18 total)
├── scripts/
│   └── fetch_meta_cache.py   # Meraki CDN fetch script (run by Actions)
├── .github/workflows/
│   └── fetch_meta.yml        # Daily cache refresh workflow
└── tests/                    # pytest test suite (54 tests)
```

## Running tests

```bash
pytest tests/ -v
```

54 tests cover match analysis, champion stats aggregation, rune analysis, and meta gap logic.

## Credits

**Developer:** Henry Garban

**AI pair programming:** Claude (Anthropic)

## License

MIT — see [LICENSE](LICENSE). If you use this code, please credit the original project.
