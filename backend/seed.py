"""Seed the local DB with realistic pmec data based on known FACEIT stats."""
import asyncio
import random
from datetime import datetime, timedelta, timezone

from app.db.session import AsyncSessionLocal, engine
from app.models.base import Base
from app.models.user import User
from app.models.match import Match, MatchPlayer, Round, WeaponStat


MAPS = ["de_dust2", "de_mirage", "de_inferno", "de_nuke", "de_anubis", "de_ancient", "de_overpass"]
MAP_WEIGHTS = [20, 22, 18, 8, 14, 10, 8]

WEAPONS = ["AK-47", "M4A4", "M4A1-S", "AWP", "Desert Eagle", "USP-S", "Glock-18", "FAMAS", "Galil AR", "MP9"]
WEAPON_WEIGHTS = [28, 15, 12, 14, 8, 7, 6, 4, 3, 3]

PLAYER_NAMES = [
    "pmec", "NiKo", "ZywOo", "s1mple", "donk", "m0NESY", "ropz", "Twistzz",
    "rain", "broky", "frozen", "tabseN", "blameF", "Magisk", "gla1ve",
    "device", "stavn", "TeSeS", "cadiaN", "Spinx", "huNter", "nexa",
    "jL", "Brollan", "mezii", "siuhy", "Jimpphat", "xertioN", "torzsi",
]

NUM_MATCHES = 50
WIN_RATE = 0.54
TARGET_KD = 1.29
TARGET_HS = 0.524


def gen_player_stats(name: str, team: str, is_self: bool, is_win: bool, total_rounds: int) -> dict:
    if is_self:
        avg_kills = TARGET_KD * total_rounds * 0.065
        kills = max(0, int(random.gauss(avg_kills, avg_kills * 0.25)))
        deaths = max(1, int(kills / max(0.8, random.gauss(TARGET_KD, 0.15))))
    else:
        base = total_rounds * 0.065
        skill = random.uniform(0.7, 1.4)
        kills = max(0, int(random.gauss(base * skill, base * 0.3)))
        deaths = max(1, int(random.gauss(base * 0.9, base * 0.25)))

    assists = random.randint(0, min(kills, 8))
    adr = round(random.gauss(80 if is_self else 70, 15), 1)
    adr = max(30, min(150, adr))
    hs_pct = round(random.gauss(TARGET_HS * 100 if is_self else 45, 10), 1)
    hs_pct = max(10, min(90, hs_pct))
    kd = kills / max(1, deaths)
    rating = round(0.5 + kd * 0.3 + (kills / max(1, total_rounds)) * 2 + random.uniform(-0.1, 0.1), 2)
    rating = max(0.3, min(2.5, rating))

    return {
        "player_name": name,
        "team": team,
        "is_self": is_self,
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "adr": adr,
        "headshot_pct": hs_pct,
        "rating": rating,
    }


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        user = User(
            steam_id="76561198245080640",
            faceit_id="pmec",
            nickname="pmec",
            rank="Global Sentinel",
            avatar_url="https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg",
        )
        db.add(user)
        await db.flush()

        now = datetime.now(tz=timezone.utc)

        for i in range(NUM_MATCHES):
            map_name = random.choices(MAPS, weights=MAP_WEIGHTS, k=1)[0]
            is_win = random.random() < WIN_RATE
            result = "win" if is_win else "loss"

            if is_win:
                team_score = random.randint(13, 16)
                opp_score = random.randint(max(0, team_score - 8), team_score - 1)
            else:
                opp_score = random.randint(13, 16)
                team_score = random.randint(max(0, opp_score - 8), opp_score - 1)

            match_time = now - timedelta(
                days=NUM_MATCHES - i,
                hours=random.randint(0, 12),
                minutes=random.randint(0, 59),
            )

            match = Match(
                external_match_id=f"1-{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}",
                user_id=user.id,
                provider="faceit",
                map_name=map_name,
                started_at=match_time,
                duration_seconds=random.randint(1800, 3600),
                score_team=team_score,
                score_opponent=opp_score,
                result=result,
            )
            db.add(match)
            await db.flush()

            total_rounds = team_score + opp_score

            # Generate scoreboard: 5 CT + 5 T
            pool = random.sample([n for n in PLAYER_NAMES if n != "pmec"], 9)
            pmec_team = random.choice(["CT", "T"])
            opp_team = "T" if pmec_team == "CT" else "CT"

            teammates = pool[:4]
            enemies = pool[4:]

            for name in [user.nickname] + teammates:
                stats = gen_player_stats(name, pmec_team, name == user.nickname, is_win, total_rounds)
                db.add(MatchPlayer(match_id=match.id, **stats))

            for name in enemies:
                stats = gen_player_stats(name, opp_team, False, not is_win, total_rounds)
                db.add(MatchPlayer(match_id=match.id, **stats))

            # Generate rounds
            for rn in range(1, total_rounds + 1):
                weapon = random.choices(WEAPONS, weights=WEAPON_WEIGHTS, k=1)[0]
                kills = max(0, int(random.gauss(TARGET_KD * 0.85, 0.9)))
                kills = min(kills, 5)
                deaths = max(0, int(random.gauss(0.85, 0.6)))
                deaths = min(deaths, 3)
                winning_team = "CT" if random.random() > 0.5 else "T"

                rnd = Round(
                    match_id=match.id,
                    round_number=rn,
                    winning_team=winning_team,
                    kills=kills,
                    deaths=deaths,
                    weapon_used=weapon,
                )
                db.add(rnd)
                await db.flush()

                shots = random.randint(max(kills + 2, 8), 28)
                hits = random.randint(kills, min(shots, kills + 6))
                headshots = int(hits * TARGET_HS * random.uniform(0.6, 1.4))
                headshots = min(headshots, hits)

                db.add(WeaponStat(
                    round_id=rnd.id,
                    weapon_name=weapon,
                    shots=shots,
                    hits=hits,
                    headshots=headshots,
                ))

        await db.commit()
        print(f"Seeded pmec (user #{user.id}) with {NUM_MATCHES} matches + full scoreboards")


if __name__ == "__main__":
    asyncio.run(seed())
