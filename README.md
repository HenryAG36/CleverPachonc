# CleverPachonc
![Version](https://img.shields.io/badge/version-alpha_0.3.0-orange.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A personal League of Legends stats tracker named after the adorable TFT Little Legend, Pachonc.
Search any summoner by Riot ID and instantly see ranked stats, champion mastery, match history,
and per-champion performance breakdowns — all in a clean dark-themed web UI.

> **This is a personal project for personal use only.** It is not distributed as a service
> and is not monetised in any way.

---

## Features

- **Ranked stats** — tier, LP, win/loss record, and current win/loss streak per queue
- **Champion mastery** — top 5 champions with mastery level and points
- **Match history** — last 20 ranked solo/duo games with champion, KDA, CS, items, and role
- **Per-champion stats** — sortable table of win rate, KDA, CS/min across all tracked games
- **Win-rate chart** — visual 20-game history with overall win percentage

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 + Flask (Vercel serverless) |
| API calls | asyncio + aiohttp (concurrent, rate-limit-aware) |
| Frontend | React 18 + Vite + Tailwind CSS |
| Charts | Recharts |
| Deploy | Vercel |

## Local development

**Prerequisites:** Python 3.12+, Node 18+

```bash
# 1. Clone and install Python dependencies
git clone https://github.com/<you>/CleverPachonc.git
cd CleverPachonc
pip install -r requirements.txt

# 2. Set your Riot API key
cp .env.example .env
# Edit .env and set RIOT_API_KEY=RGAPI-...

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
3. In **Project Settings → Environment Variables**, add `RIOT_API_KEY`.
4. Deploy — Vercel uses `vercel.json` to build the frontend and serve the Flask function.

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
discarded. See the in-app Privacy Policy (footer) for full details.

## Project structure

```
CleverPachonc/
├── api/index.py          # Flask serverless entry point (Vercel)
├── backend/              # Pure Python business logic
│   ├── riot_api.py       # Async Riot API client
│   ├── data_dragon.py    # Data Dragon version/asset resolution
│   ├── analysis/         # Match, champion, and rune analysis
│   └── utils/            # Constants, exceptions, rate limiter
├── frontend/             # React 18 + Vite app
│   └── src/components/   # UI components
├── tests/                # pytest test suite (27 tests)
└── src/                  # Legacy desktop app (preserved, unused)
```

## Running tests

```bash
pytest tests/ -v
```

All 27 tests cover match analysis, champion stats aggregation, and rune analysis logic.

## Credits

**Developer:** Kaseash

**AI pair programming:** Claude (Anthropic)

- Twitch: [twitch.tv/Kaseash](https://twitch.tv/Kaseash)
- TikTok: [@Kaseash](https://tiktok.com/@Kaseash)
- YouTube: [@Kaseash](https://youtube.com/@Kaseash)

## License

MIT — see [LICENSE](LICENSE). If you use this code, please credit the original project.
