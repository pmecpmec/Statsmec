import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { cachedGet } from "../api/client";

type WinRatePoint = {
  date: string;
  matches: number;
  wins: number;
  losses: number;
  win_rate: number;
};

type AnalyticsResponse = {
  win_rate_trend: WinRatePoint[];
};

type Props = { userId: number };

export const PerformanceTrendsPanel: React.FC<Props> = ({ userId }) => {
  const [data, setData] = useState<WinRatePoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setError(null);
    cachedGet<AnalyticsResponse>(`/analytics/users/${userId}`)
      .then((d) => { if (active) setData(d.win_rate_trend); })
      .catch(() => { if (active) setError("Failed to load trends."); });
    return () => { active = false; };
  }, [userId]);

  if (error) return <p className="error">{error}</p>;
  if (!data.length) return <div><h2>Win Rate Trend</h2><p style={{ color: "var(--text-dim)" }}>No data yet.</p></div>;

  return (
    <div>
      <h2>Win Rate Trend</h2>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="date" tick={{ fill: "var(--text-dim)", fontSize: 11 }} />
          <YAxis
            tickFormatter={(v) => `${Math.round(v * 100)}%`}
            tick={{ fill: "var(--text-dim)", fontSize: 11 }}
          />
          <Tooltip
            contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8 }}
            labelStyle={{ color: "var(--text)" }}
            formatter={(value: number) => [`${Math.round(value * 100)}%`, "Win Rate"]}
          />
          <Line
            type="monotone"
            dataKey="win_rate"
            stroke="var(--green)"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: "var(--green)" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
