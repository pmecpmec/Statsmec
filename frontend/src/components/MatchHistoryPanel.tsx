import React, { useEffect, useState } from "react";
import { cachedGet } from "../api/client";

type MatchSummary = {
  id: number;
  external_match_id: string;
  provider: string;
  map_name: string | null;
  started_at: string;
  duration_seconds: number | null;
  score_team: number | null;
  score_opponent: number | null;
  result: string | null;
};

type WeaponStatDetail = {
  weapon_name: string;
  shots: number;
  hits: number;
  headshots: number;
};

type RoundDetail = {
  id: number;
  match_id: number;
  round_number: number;
  winning_team: string | null;
  kills: number | null;
  deaths: number | null;
  weapon_used: string | null;
  weapon_stats: WeaponStatDetail[];
};

type Props = { userId: number };

function formatMap(name: string | null): string {
  if (!name) return "—";
  return name.replace("de_", "").charAt(0).toUpperCase() + name.replace("de_", "").slice(1);
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const hours = Math.floor(diff / 3_600_000);
  if (hours < 1) return "just now";
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days === 1) return "yesterday";
  return `${days}d ago`;
}

export const MatchHistoryPanel: React.FC<Props> = ({ userId }) => {
  const [matches, setMatches] = useState<MatchSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedMatchId, setSelectedMatchId] = useState<number | null>(null);
  const [rounds, setRounds] = useState<RoundDetail[] | null>(null);
  const [roundsError, setRoundsError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    cachedGet<MatchSummary[]>(`/users/${userId}/matches?limit=20`)
      .then((data) => {
        if (active) {
          setMatches(data);
          if (data.length && !selectedMatchId) setSelectedMatchId(data[0].id);
        }
      })
      .catch(() => { if (active) setError("Failed to load match history."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [userId]);

  useEffect(() => {
    if (!selectedMatchId) { setRounds(null); return; }
    let active = true;
    setRoundsError(null);
    cachedGet<RoundDetail[]>(`/users/${userId}/matches/${selectedMatchId}/rounds`)
      .then((data) => { if (active) setRounds(data); })
      .catch(() => { if (active) setRoundsError("Failed to load round breakdown."); });
    return () => { active = false; };
  }, [userId, selectedMatchId]);

  return (
    <div>
      <h2>Recent Matches</h2>
      {loading && <p style={{ color: "var(--text-dim)" }}>Loading...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && (
        <>
          <table className="table">
            <thead>
              <tr>
                <th>When</th>
                <th>Map</th>
                <th>Score</th>
                <th>Result</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {matches.map((m) => (
                <tr
                  key={m.id}
                  className={m.id === selectedMatchId ? "selected" : undefined}
                  onClick={() => setSelectedMatchId(m.id)}
                  style={{ cursor: "pointer" }}
                >
                  <td>{timeAgo(m.started_at)}</td>
                  <td>{formatMap(m.map_name)}</td>
                  <td>
                    <span className={m.result === "win" ? "win-text" : "loss-text"}>
                      {m.score_team ?? "-"}
                    </span>
                    {" : "}
                    {m.score_opponent ?? "-"}
                  </td>
                  <td>
                    <span className={m.result === "win" ? "win-text" : "loss-text"}>
                      {m.result === "win" ? "W" : m.result === "loss" ? "L" : "-"}
                    </span>
                  </td>
                  <td>{m.duration_seconds ? `${Math.round(m.duration_seconds / 60)}m` : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {selectedMatchId && (
            <div style={{ marginTop: "1rem" }}>
              <h3 style={{ fontSize: "0.85rem", color: "var(--text-dim)", marginBottom: "0.5rem" }}>
                Round Breakdown
              </h3>
              {roundsError && <p className="error">{roundsError}</p>}
              {!roundsError && !rounds && <p style={{ color: "var(--text-dim)" }}>Loading rounds...</p>}
              {!roundsError && rounds && !rounds.length && (
                <p style={{ color: "var(--text-dim)" }}>No round data for this match.</p>
              )}
              {!roundsError && rounds && rounds.length > 0 && (
                <table className="table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Side</th>
                      <th>K</th>
                      <th>D</th>
                      <th>Weapon</th>
                      <th>Accuracy</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rounds.map((r) => (
                      <tr key={r.id}>
                        <td>{r.round_number}</td>
                        <td>{r.winning_team ?? "-"}</td>
                        <td className={r.kills && r.kills > 0 ? "win-text" : undefined}>
                          {r.kills ?? 0}
                        </td>
                        <td className={r.deaths && r.deaths > 0 ? "loss-text" : undefined}>
                          {r.deaths ?? 0}
                        </td>
                        <td>{r.weapon_used ?? "-"}</td>
                        <td style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>
                          {r.weapon_stats.map((ws) => (
                            <span key={ws.weapon_name} style={{ marginRight: "0.5rem" }}>
                              {ws.hits}/{ws.shots}
                              {ws.headshots > 0 && (
                                <span style={{ color: "var(--orange)", marginLeft: "2px" }}>
                                  ({ws.headshots} HS)
                                </span>
                              )}
                            </span>
                          ))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};
