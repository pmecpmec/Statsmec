import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from "recharts";
import { cachedGet } from "../api/client";

type RankComparisonMetric = {
  metric: string;
  player_value: number;
  average_value: number;
};

type AnalyticsResponse = {
  rank_comparison: RankComparisonMetric[];
};

type Props = { userId: number };

export const RankComparisonPanel: React.FC<Props> = ({ userId }) => {
  const [data, setData] = useState<RankComparisonMetric[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setError(null);
    cachedGet<AnalyticsResponse>(`/analytics/users/${userId}`)
      .then((d) => { if (active) setData(d.rank_comparison); })
      .catch(() => { if (active) setError("Failed to load comparison."); });
    return () => { active = false; };
  }, [userId]);

  if (error) return <p className="error">{error}</p>;
  if (!data.length) return <div><h2>vs Rank Average</h2><p style={{ color: "var(--text-dim)" }}>No data yet.</p></div>;

  return (
    <div>
      <h2>You vs Rank Average</h2>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="metric" tick={{ fill: "var(--text-dim)", fontSize: 11 }} />
          <YAxis tick={{ fill: "var(--text-dim)", fontSize: 11 }} />
          <Tooltip
            contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8 }}
            labelStyle={{ color: "var(--text)" }}
          />
          <Legend wrapperStyle={{ fontSize: 12, color: "var(--text-dim)" }} />
          <Bar dataKey="player_value" fill="var(--accent)" name="pmec" radius={[4, 4, 0, 0]} />
          <Bar dataKey="average_value" fill="#8b5cf6" name="Rank Avg" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
