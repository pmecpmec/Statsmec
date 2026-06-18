from app.services.valorant_stats import (
    _name_maps_from_content,
    summarize_player_matches,
)

PUUID = "player-puuid-1"

MAP_NAMES = {"/game/maps/ascent/ascent": "Ascent", "/game/maps/bind/duality": "Bind"}
AGENT_NAMES = {"add6443a-41bd-e414-f6ad-e58d267f4e95": "Jett"}


def _match(map_id, char_id, kills, deaths, assists, score, rounds, my_team, won, my_won, opp_won, mid="m"):
    return {
        "matchInfo": {"matchId": mid, "mapId": map_id, "queueId": "competitive", "gameStartMillis": 1700000000000},
        "players": [
            {"puuid": PUUID, "teamId": my_team, "characterId": char_id,
             "stats": {"kills": kills, "deaths": deaths, "assists": assists, "score": score, "roundsPlayed": rounds}},
            {"puuid": "other", "teamId": "Red" if my_team == "Blue" else "Blue", "characterId": char_id,
             "stats": {"kills": 1, "deaths": 1, "assists": 1, "score": 100, "roundsPlayed": rounds}},
        ],
        "teams": [
            {"teamId": my_team, "won": won, "roundsWon": my_won},
            {"teamId": "Red" if my_team == "Blue" else "Blue", "won": not won, "roundsWon": opp_won},
        ],
    }


def test_summary_aggregates_kd_acs_winrate():
    matches = [
        # 20 kills, 10 deaths, score 5000 over 20 rounds -> acs 250, won
        _match("/Game/Maps/Ascent/Ascent", "ADD6443A-41BD-E414-F6AD-E58D267F4E95", 20, 10, 5, 5000, 20, "Blue", True, 13, 7, mid="m1"),
        # 10 kills, 10 deaths, score 3000 over 20 rounds -> acs 150, lost
        _match("/Game/Maps/Bind/Duality", "add6443a-41bd-e414-f6ad-e58d267f4e95", 10, 10, 8, 3000, 20, "Red", False, 9, 13, mid="m2"),
    ]
    out = summarize_player_matches(PUUID, matches, map_names=MAP_NAMES, agent_names=AGENT_NAMES)

    s = out["summary"]
    assert s["matches"] == 2
    assert s["wins"] == 1
    assert s["losses"] == 1
    assert s["win_rate"] == 50.0
    assert s["kd"] == 1.5  # 30 kills / 20 deaths
    assert s["acs"] == 200  # 8000 score / 40 rounds
    assert s["kills"] == 30

    # both matches are Jett -> one top agent with 2 games
    assert len(s["top_agents"]) == 1
    jett = s["top_agents"][0]
    assert jett["name"] == "Jett"
    assert jett["games"] == 2
    assert jett["win_rate"] == 50.0


def test_per_match_rows_map_and_score():
    matches = [
        _match("/Game/Maps/Ascent/Ascent", "ADD6443A-41BD-E414-F6AD-E58D267F4E95", 20, 10, 5, 5000, 20, "Blue", True, 13, 7, mid="m1"),
    ]
    out = summarize_player_matches(PUUID, matches, map_names=MAP_NAMES, agent_names=AGENT_NAMES)
    row = out["matches"][0]
    assert row["map"] == "Ascent"
    assert row["agent"] == "Jett"
    assert row["acs"] == 250
    assert row["kd"] == 2.0
    assert row["score"] == "13-7"
    assert row["won"] is True


def test_unknown_map_falls_back_to_leaf_segment():
    matches = [_match("/Game/Maps/Sunset/Sunset", "unknown-agent", 5, 5, 0, 1000, 20, "Blue", True, 13, 0, mid="m1")]
    out = summarize_player_matches(PUUID, matches, map_names={}, agent_names={})
    row = out["matches"][0]
    assert row["map"] == "Sunset"
    assert row["agent"] == "Unknown"


def test_player_absent_is_skipped():
    match = _match("/Game/Maps/Ascent/Ascent", "x", 5, 5, 0, 1000, 20, "Blue", True, 13, 0)
    match["players"] = [p for p in match["players"] if p["puuid"] != PUUID]
    out = summarize_player_matches(PUUID, [match], map_names=MAP_NAMES, agent_names=AGENT_NAMES)
    assert out["summary"]["matches"] == 0
    assert out["matches"] == []


def test_empty_and_malformed_inputs():
    out = summarize_player_matches(PUUID, [None, {}, {"players": []}])
    assert out["summary"]["matches"] == 0
    assert out["summary"]["kd"] == 0.0
    assert out["summary"]["acs"] == 0


def test_name_maps_from_content():
    content = {
        "maps": [{"name": "Ascent", "id": "ABC", "assetPath": "/Game/Maps/Ascent/Ascent"}],
        "characters": [{"name": "Jett", "id": "ADD6443A"}],
    }
    map_names, agent_names = _name_maps_from_content(content)
    assert map_names["/game/maps/ascent/ascent"] == "Ascent"
    assert map_names["abc"] == "Ascent"
    assert agent_names["add6443a"] == "Jett"
