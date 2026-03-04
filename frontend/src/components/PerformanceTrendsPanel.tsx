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

type Props = {
  userId: number;
};

export const PerformanceTrendsPanel: React.FC<Props> = ({ userId }) => {
  const [data, setData] = useState<WinRatePoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setError(null);
    cachedGet<AnalyticsResponse>(`/analytics/users/${userId}`)
      .then((d) => {
        if (active) setData(d.win_rate_trend);
      })
      .catch((err: unknown) => {
        if (active) setError("Failed to load performance trends.");
        // eslint-disable-next-line no-console
        console.error(err);
      });
    return () => {
      active = false;
    };
  }, [userId]);

  if (error) return <p className="error">{error}</p>;
  if (!data.length) return <p>No trend data yet.</p>;

  return (
    <div>
      <h2>Win Rate Over Time</h2>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis tickFormatter={(v) => `${Math.round(v * 100)}%`} />
          <Tooltip formatter={(value: number) => `${Math.round(value * 100)}%`} />
          <Line type="monotone" dataKey="win_rate" stroke="#4ade80" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

