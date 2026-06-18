"""
Best-effort scrapers for csstats.gg and ESEA.

Both sites sit behind Cloudflare, so these functions are written to *try* and
fail gracefully: every public function catches all errors, times out quickly,
and returns a typed dict with an `available` flag plus a human-readable
`status`. A failure here must NEVER break /me/ or crash a request.

Strategy (stop at first that works, no heavy infra):
  1. httpx with a full browser-like header set + a small delay.
  2. the `cloudscraper` library (optional dependency) which solves some
     Cloudflare JS challenges.
We deliberately do NOT use a headless browser (Playwright/Selenium) — too heavy
for this app. If only a headless browser would work, we report "blocked".
"""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Any, Dict, Optional

import httpx

log = logging.getLogger(__name__)

_TIMEOUT = 8.0

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Connection": "keep-alive",
}


def _empty(source: str, url: str, status: str) -> Dict[str, Any]:
    return {
        "available": False,
        "source": source,
        "url": url,
        "method": None,
        "status": status,
        "stats": {},
    }


async def _fetch_html(url: str) -> tuple[Optional[str], str, Optional[str]]:
    """
    Try httpx then cloudscraper. Returns (html_or_None, method, status_message).
    Never raises.
    """
    # --- Attempt 1: httpx with browser-like headers ---
    try:
        async with httpx.AsyncClient(
            timeout=_TIMEOUT, follow_redirects=True, headers=_BROWSER_HEADERS
        ) as client:
            resp = await client.get(url)
        if resp.status_code == 200 and resp.text:
            return resp.text, "httpx", "ok"
        httpx_status = f"HTTP {resp.status_code}"
    except Exception as exc:  # network error, timeout, etc.
        httpx_status = f"error ({type(exc).__name__})"

    # --- Attempt 2: cloudscraper (optional dependency) ---
    try:
        html = await asyncio.wait_for(
            asyncio.to_thread(_cloudscraper_get, url), timeout=_TIMEOUT + 4
        )
        if html:
            return html, "cloudscraper", "ok"
        cs_status = "blocked"
    except asyncio.TimeoutError:
        cs_status = "timeout"
    except Exception as exc:
        cs_status = f"error ({type(exc).__name__})"

    return None, "none", f"blocked (httpx: {httpx_status}; cloudscraper: {cs_status})"


def _cloudscraper_get(url: str) -> Optional[str]:
    """Synchronous cloudscraper fetch, run in a thread. Returns HTML or None."""
    try:
        import cloudscraper  # type: ignore
    except Exception:
        return None
    try:
        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        resp = scraper.get(url, timeout=_TIMEOUT)
        if resp.status_code == 200 and resp.text:
            return resp.text
    except Exception:
        return None
    return None


def _find_number(html: str, *patterns: str) -> Optional[str]:
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1).strip()
    return None


def parse_csstats(html: str) -> Dict[str, Any]:
    """
    Best-effort extraction from a csstats.gg player page HTML.

    csstats renders its aggregate stats (Rating 2.0, K/D, ADR, HS%) client-side
    via JS, so those are NOT present in the raw HTML. The rank "cards" however are
    server-rendered, so we reliably extract the FACEIT level and the CS2 Premier
    rating (current + best + season + tier) which is genuinely useful and real.
    """
    stats: Dict[str, Any] = {}

    faceit = re.search(r"ranks/faceit/level(\d+)\.png", html)
    if faceit:
        stats["faceit_level"] = int(faceit.group(1))

    idx = html.find("premier.png")
    if idx != -1:
        block = html[idx : idx + 1600]
        season = re.search(r'(?:alt|title)="Premier\s*-\s*([^"]+)"', block)
        if season:
            stats["premier_season"] = season.group(1).strip()
        ratings = re.findall(
            r"cs2rating\s+(\w+)\s+sm[^>]*>\s*<span[^>]*>(.*?)</span>",
            block,
            re.DOTALL,
        )
        if ratings:
            tier, raw = ratings[0]
            digits = re.sub(r"\D", "", raw)
            if digits:
                stats["premier_rating"] = int(digits)
                stats["premier_tier"] = tier
        if len(ratings) > 1:
            best_digits = re.sub(r"\D", "", ratings[1][1])
            if best_digits:
                stats["premier_best"] = int(best_digits)

    return stats


def parse_esea(html: str) -> Dict[str, Any]:
    """Best-effort extraction from an ESEA user page HTML."""
    stats: Dict[str, Any] = {}
    rws = _find_number(html, r"RWS[^0-9]{0,40}([0-9]+\.?[0-9]*)")
    kd = _find_number(html, r"K\s*/\s*D[^0-9]{0,40}([0-9]+\.?[0-9]*)")
    rank = _find_number(html, r"Rank[^A-Za-z0-9]{0,20}([A-Za-z+\-]{1,3})")
    if rws:
        stats["rws"] = rws
    if kd:
        stats["kd"] = kd
    if rank:
        stats["rank"] = rank
    return stats


async def scrape_csstats(steam_id: str) -> Dict[str, Any]:
    url = f"https://csstats.gg/player/{steam_id}"
    try:
        html, method, status = await _fetch_html(url)
        if not html:
            return _empty("csstats.gg", url, status)
        stats = parse_csstats(html)
        return {
            "available": bool(stats),
            "source": "csstats.gg",
            "url": url,
            "method": method,
            "status": "ok" if stats else "reached page but no parseable stats",
            "stats": stats,
        }
    except Exception as exc:  # pragma: no cover - defensive catch-all
        log.warning("csstats scrape failed: %s", exc)
        return _empty("csstats.gg", url, f"error ({type(exc).__name__})")


async def scrape_esea(user_id: str) -> Dict[str, Any]:
    url = f"https://play.esea.net/users/{user_id}"
    try:
        html, method, status = await _fetch_html(url)
        if not html:
            return _empty("ESEA", url, status)
        stats = parse_esea(html)
        return {
            "available": bool(stats),
            "source": "ESEA",
            "url": url,
            "method": method,
            "status": "ok" if stats else "reached page but no parseable stats",
            "stats": stats,
        }
    except Exception as exc:  # pragma: no cover - defensive catch-all
        log.warning("ESEA scrape failed: %s", exc)
        return _empty("ESEA", url, f"error ({type(exc).__name__})")
