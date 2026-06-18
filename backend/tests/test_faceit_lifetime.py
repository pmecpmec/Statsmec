from app.services.faceit_lifetime import parse_faceit_lifetime

STATS_PAYLOAD = {
    "lifetime": {
        "Matches": "1500",
        "Wins": "825",
        "Win Rate %": "55",
        "Average K/D Ratio": "1.12",
        "Average Headshots %": "48.5",
        "Current Win Streak": "3",
        "Longest Win Streak": "12",
        "Recent Results": ["1", "0", "1", "1", "0"],
    },
    "segments": [
        {
            "type": "Map",
            "label": "de_mirage",
            "img_regular": "https://example/mirage.jpg",
            "stats": {
                "Matches": "300",
                "Win Rate %": "60",
                "Average K/D Ratio": "1.2",
                "Average Headshots %": "50",
            },
        },
        {
            "type": "Map",
            "label": "de_inferno",
            "stats": {
                "Matches": "100",
                "Win Rate %": "45",
                "Average K/D Ratio": "0.95",
                "Average Headshots %": "47",
            },
        },
        # 0-match segment should be dropped
        {"type": "Map", "label": "de_vertigo", "stats": {"Matches": "0"}},
        # non-map segment ignored
        {"type": "Weapon", "label": "ak47", "stats": {"Matches": "999"}},
    ],
}

BANS_PAYLOAD = {
    "items": [
        {"reason": "afk", "game": "cs2", "starts_at": "2020-01-01", "ends_at": "2020-01-02"}
    ]
}


def test_parse_lifetime_core_fields():
    out = parse_faceit_lifetime(STATS_PAYLOAD, BANS_PAYLOAD)
    assert out["available"] is True
    assert out["matches"] == 1500
    assert out["wins"] == 825
    assert out["win_rate"] == 55.0
    assert out["avg_kd"] == 1.12
    assert out["avg_hs_pct"] == 48.5
    assert out["current_win_streak"] == 3
    assert out["longest_win_streak"] == 12
    assert out["recent_results"] == ["W", "L", "W", "W", "L"]


def test_parse_segments_sorted_and_filtered():
    out = parse_faceit_lifetime(STATS_PAYLOAD)
    segs = out["segments"]
    # vertigo (0 matches) and ak47 (weapon) dropped -> 2 maps left
    assert len(segs) == 2
    # sorted by matches desc -> mirage (300) first
    assert segs[0]["map"] == "de_mirage"
    assert segs[0]["matches"] == 300
    assert segs[0]["win_rate"] == 60.0
    assert segs[0]["kd"] == 1.2
    assert segs[1]["map"] == "de_inferno"


def test_parse_bans():
    out = parse_faceit_lifetime(STATS_PAYLOAD, BANS_PAYLOAD)
    assert len(out["bans"]) == 1
    assert out["bans"][0]["reason"] == "afk"


def test_parse_handles_none_and_malformed():
    out = parse_faceit_lifetime(None, None)
    assert out["available"] is False
    assert out["matches"] == 0
    assert out["segments"] == []
    assert out["recent_results"] == []
    assert out["bans"] == []

    out2 = parse_faceit_lifetime({"lifetime": "not-a-dict", "segments": "nope"}, {"items": "bad"})
    assert out2["available"] is False
    assert out2["segments"] == []
    assert out2["bans"] == []
