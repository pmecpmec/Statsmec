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

type Props = {
  userId: number;
};

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
          if (data.length && !selectedMatchId) {
            setSelectedMatchId(data[0].id);
          }
        }
      })
      .catch((err: unknown) => {
        if (active) setError("Failed to load match history.");
        // eslint-disable-next-line no-console
        console.error(err);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [userId]);

  useEffect(() => {
    if (!selectedMatchId) {
      setRounds(null);
      return;
    }
    let active = true;
    setRoundsError(null);
    cachedGet<RoundDetail[]>(`/users/${userId}/matches/${selectedMatchId}/rounds`)
      .then((data) => {
        if (active) setRounds(data);
      })
      .catch((err: unknown) => {
        if (active) setRoundsError("Failed to load round breakdown.");
        // eslint-disable-next-line no-console
        console.error(err);
      });

    return () => {
      active = false;
    };
  }, [userId, selectedMatchId]);

  return (
    <div>
      <h2>Match History</h2>
      {loading && <p>Loading…</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && (
        <>
          <table className="table">
            <thead>
              <tr>
                <th>Started</th>
                <th>Provider</th>
                <th>Match ID</th>
                <th>Map</th>
                <th>Score</th>
                <th>Result</th>
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
                  <td>{new Date(m.started_at).toLocaleString()}</td>
                  <td>{m.provider.toUpperCase()}</td>
                  <td>{m.external_match_id}</td>
                  <td>{m.map_name ?? "Unknown"}</td>
                  <td>
                    {m.score_team ?? "-"} : {m.score_opponent ?? "-"}
                  </td>
                  <td className={m.result ?? undefined}>{m.result ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ marginTop: "0.75rem" }}>
            <h3>Round‑by‑round breakdown</h3>
            {roundsError && <p className="error">{roundsError}</p>}
            {!roundsError && !rounds && <p>Select a match to see details.</p>}
            {!roundsError && rounds && !rounds.length && (
              <p>No round data available for this match yet.</p>
            )}
            {!roundsError && rounds && rounds.length > 0 && (
              <table className="table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Winner</th>
                    <th>Kills</th>
                    <th>Deaths</th>
                    <th>Primary Weapon</th>
                    <th>Weapon Stats</th>
                  </tr>
                </thead>
                <tbody>
                  {rounds.map((r) => (
                    <tr key={r.id}>
                      <td>{r.round_number}</td>
                      <td>{r.winning_team ?? "-"}</td>
                      <td>{r.kills ?? "-"}</td>
                      <td>{r.deaths ?? "-"}</td>
                      <td>{r.weapon_used ?? "-"}</td>
                      <td>
                        {r.weapon_stats.map((ws) => (
                          <span key={ws.weapon_name} style={{ marginRight: "0.5rem" }}>
                            {ws.weapon_name} ({ws.hits}/{ws.shots})
                          </span>
                        ))}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
};

