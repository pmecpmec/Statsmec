"""Seed the local DB with sample data so the dashboard has something to display."""
import asyncio
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, engine
from app.models.base import Base
from app.models.user import User
from app.models.match import Match, Round, WeaponStat


MAPS = ["de_dust2", "de_mirage", "de_inferno", "de_nuke", "de_anubis", "de_ancient", "de_overpass"]
WEAPONS = ["AK-47", "M4A4", "M4A1-S", "AWP", "Desert Eagle", "USP-S", "Glock-18", "FAMAS", "Galil AR", "MP9"]
RESULTS = ["win", "loss", "win", "win", "loss", "win", "loss", "win", "win", "loss"]


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        user = User(steam_id="76561198000000001", faceit_id="abc-def-123", nickname="DemoPlayer", rank="Level 8")
        db.add(user)
        await db.flush()

        now = datetime.now(tz=timezone.utc)
        for i in range(20):
            map_name = random.choice(MAPS)
            result = RESULTS[i % len(RESULTS)]
            team_score = random.randint(13, 16) if result == "win" else random.randint(5, 12)
            opp_score = random.randint(5, 12) if result == "win" else random.randint(13, 16)

            match = Match(
                external_match_id=f"DEMO-MATCH-{i+1:04d}",
                user_id=user.id,
                provider="faceit",
                map_name=map_name,
                started_at=now - timedelta(days=20 - i, hours=random.randint(0, 8)),
                duration_seconds=random.randint(1800, 3600),
                score_team=team_score,
                score_opponent=opp_score,
                result=result,
            )
            db.add(match)
            await db.flush()

            total_rounds = team_score + opp_score
            for rn in range(1, total_rounds + 1):
                weapon = random.choice(WEAPONS)
                kills = random.randint(0, 4)
                deaths = random.randint(0, 2)
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

                shots = random.randint(max(kills, 5), 30)
                hits = random.randint(kills, min(shots, kills + 5))
                headshots = random.randint(0, min(kills, 3))

                ws = WeaponStat(
                    round_id=rnd.id,
                    weapon_name=weapon,
                    shots=shots,
                    hits=hits,
                    headshots=headshots,
                )
                db.add(ws)

        await db.commit()
        print(f"Seeded user #{user.id} with 20 matches")


if __name__ == "__main__":
    asyncio.run(seed())
