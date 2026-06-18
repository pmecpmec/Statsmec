# API variables and where to get them

Set these in your **backend** environment (e.g. Render → your Web Service → **Environment**). Never commit real keys to git.

### `APP_ENV`

- **`production`** (default if unset in code): API responses use short, public-safe messages when keys or config are missing (no file paths or env-var setup hints).
- **`development`** (recommended in local `.env` and Docker Compose): verbose hints in JSON for debugging.
- The **frontend** hides setup copy in **production builds** (`astro build`, e.g. deploy from `main`). `astro dev` shows developer-oriented banners. Do not set **`PUBLIC_DEV_UI=true`** on the GitHub Pages build (the deploy workflow sets `PUBLIC_DEV_UI=false`).

---

## Required for core features

### `FACEIT_API_KEY`
- **Used for:** Match history, FACEIT Elo/level, sync.
- **Get it:** https://developers.faceit.com  
  1. Sign in with your FACEIT account  
  2. Create an App in **App Studio**  
  3. **API Keys** → Create **Server-side** key  
- **Docs:** https://developers.faceit.com/docs

---

## Optional but recommended

### `STEAM_API_KEY`
- **Used for:** Steam profile avatar, CS:GO / Classic stats (kills, deaths, wins, hours).
- **Get it:** https://steamcommunity.com/dev/apikey  
  - Register a key (domain can be `localhost` for dev).
- **Steam Web API:** https://developer.valvesoftware.com/wiki/Steam_Web_API

### `RIOT_API_KEY`
- **Used for:** Riot APIs behind `X-Riot-Token` (keys often look like `RGAPI-...`). Your app must have each **product** enabled in the developer portal for the routes you call.
- **Statsmec today:**
  - **`/api/v1/me/valorant`** needs **riot/account/v1** (Riot ID → PUUID) and **val/match/v1** (match list).
  - **`/api/v1/valorant/content`** → **val-content-v1** (`GET .../val/content/v1/contents`, ~250 / 10s).
  - **`/api/v1/valorant/platform-status`** → **val-status-v1** (`GET .../val/status/v1/platform-data`, very high limits).
  - **`/api/v1/valorant/leaderboards/by-act/{actId}`** → **val-ranked-v1** (`GET .../val/ranked/v1/leaderboards/by-act/{actId}`, **10 / 10s** — cache if you poll).
- **Get it:** https://developer.riotgames.com/ — create an app and copy the API key.
- **Related env (optional):**
  - `RIOT_ROUTING_REGION` — `americas` | `europe` | `asia` (default `europe`) for **account-v1**.
  - `RIOT_VAL_SHARD` — `na` | `latam` | `br` | `eu` | `ap` | `kr` (default `eu`) for **Valorant** game endpoints.
  - `RIOT_RIOT_IDS` — comma-separated Riot IDs (`gameName#tagLine`) for multiple Valorant accounts on `GET /api/v1/me/valorant` (e.g. `pmecc#pmec,peemec#pmec`). Overrides `RIOT_GAME_NAME` / `RIOT_TAG_LINE` when set.
  - `RIOT_GAME_NAME` / `RIOT_TAG_LINE` — single default Riot ID when `RIOT_RIOT_IDS` is empty.

### `PMEC_PREMIER_REMOTE_URL`
- **Used for:** Live CS2 Premier rating (and backup FACEIT Elo) on the profile.
- **Get it:** https://api.jakobkristensen.com  
  1. Enter your **Steam ID** (17-digit, e.g. `76561198245080640`)  
  2. Pick timezone (e.g. Europe/Amsterdam)  
  3. Set **Output** to: `{{rating}}|{{elo}}` or `{{elo}} {{rating}}`  
  4. Copy the **full URL** the page gives you (e.g. for Nightbot) and set that as `PMEC_PREMIER_REMOTE_URL`.  
- **Note:** Premier data may require a linked Leetify profile on that site.

### `ALLSTAR_SERVER_API_KEY` or `ALLSTAR_PUBLIC_API_KEY`
- **Used for:** Highlights section (Allstar.gg clips).
- **Get it:** Partner API at https://prt.allstar.gg (or contact Allstar for API access).  
- **Header:** Requests use `X-API-Key: <your_key>`.

---

## Optional overrides / extras

### `PMEC_PREMIER_RATING`
- **Used for:** Fallback Premier rating if `PMEC_PREMIER_REMOTE_URL` is not set or fails.
- **Example:** `18500`

### `PMEC_PREMIER_COLOR`
- **Used for:** Override the Premier ring color (hex).
- **Example:** `#a78bfa`

### `MONGODB_URI`
- **Used for:** Optional rolling cache (e.g. match summaries).
- **Example:** `mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/`  
- **Get it:** https://www.mongodb.com/atlas (free tier).

### `MONGODB_DB_NAME`
- **Default:** `statsmec`

---

## Summary table

| Variable | Purpose | Link |
|----------|---------|------|
| `FACEIT_API_KEY` | Matches, Elo, level | https://developers.faceit.com |
| `STEAM_API_KEY` | Avatar, CS:GO classic stats | https://steamcommunity.com/dev/apikey |
| `RIOT_API_KEY` | Valorant matches, Riot account | https://developer.riotgames.com/ |
| `PMEC_PREMIER_REMOTE_URL` | Live Premier (+ backup Elo) | https://api.jakobkristensen.com |
| `ALLSTAR_SERVER_API_KEY` or `ALLSTAR_PUBLIC_API_KEY` | Highlights | https://prt.allstar.gg / Allstar partner |
| `PMEC_PREMIER_RATING` | Fallback Premier number | — |
| `PMEC_PREMIER_COLOR` | Fallback Premier ring color (hex) | — |
| `MONGODB_URI` | Optional cache | https://www.mongodb.com/atlas |

---

## Frontend (build / deploy)

For the site to call your backend in production, set:

- **`PUBLIC_API_URL`** = your backend base URL, e.g. `https://api.pmec.dev`  
  (no trailing slash; the app appends `/api/v1` for requests.)

Set this in your **frontend** build environment (e.g. GitHub Actions env or Vite/Astro env for the deploy that builds the static site).
