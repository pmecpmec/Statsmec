"""Seed the local DB with realistic pmec data based on known FACEIT stats."""
import asyncio
import random
from datetime import datetime, timedelta, timezone

from app.db.session import AsyncSessionLocal, engine
from app.models.base import Base
from app.models.user import User
from app.models.match import Match, Round, WeaponStat


MAPS = ["de_dust2", "de_mirage", "de_inferno", "de_nuke", "de_anubis", "de_ancient", "de_overpass"]
MAP_WEIGHTS = [20, 22, 18, 8, 14, 10, 8]

WEAPONS = ["AK-47", "M4A4", "M4A1-S", "AWP", "Desert Eagle", "USP-S", "Glock-18", "FAMAS", "Galil AR", "MP9"]
WEAPON_WEIGHTS = [28, 15, 12, 14, 8, 7, 6, 4, 3, 3]

NUM_MATCHES = 50
WIN_RATE = 0.54
TARGET_KD = 1.29
TARGET_HS = 0.524


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

            match = Match(
                external_match_id=f"1-{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}",
                user_id=user.id,
                provider="faceit",
                map_name=map_name,
                started_at=now - timedelta(days=NUM_MATCHES - i, hours=random.randint(0, 12), minutes=random.randint(0, 59)),
                duration_seconds=random.randint(1800, 3600),
                score_team=team_score,
                score_opponent=opp_score,
                result=result,
            )
            db.add(match)
            await db.flush()

            total_rounds = team_score + opp_score
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
        print(f"Seeded pmec (user #{user.id}) with {NUM_MATCHES} matches")


if __name__ == "__main__":
    asyncio.run(seed())
