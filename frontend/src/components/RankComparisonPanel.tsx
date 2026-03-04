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

type Props = {
  userId: number;
};

export const RankComparisonPanel: React.FC<Props> = ({ userId }) => {
  const [data, setData] = useState<RankComparisonMetric[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setError(null);
    cachedGet<AnalyticsResponse>(`/analytics/users/${userId}`)
      .then((d) => {
        if (active) setData(d.rank_comparison);
      })
      .catch((err: unknown) => {
        if (active) setError("Failed to load rank comparison.");
        // eslint-disable-next-line no-console
        console.error(err);
      });
    return () => {
      active = false;
    };
  }, [userId]);

  if (error) return <p className="error">{error}</p>;
  if (!data.length) return <p>No comparison data yet.</p>;

  return (
    <div>
      <h2>Comparison vs Rank Average</h2>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="metric" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="player_value" fill="#60a5fa" name="You" />
          <Bar dataKey="average_value" fill="#a855f7" name="Rank Average" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

