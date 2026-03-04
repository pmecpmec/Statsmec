import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";
import { cachedGet } from "../api/client";

type HeatmapCell = { x: number; y: number; intensity: number };
type WeaponHeatmap = { match_id: number; weapon_name: string; cells: HeatmapCell[] };
type AnalyticsResponse = { weapon_heatmaps: Record<string, WeaponHeatmap[]> };

type Props = { userId: number };

type WeaponAgg = { weapon: string; avgIntensity: number };

const COLORS = ["#22c55e", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16"];

export const WeaponHeatmapPanel: React.FC<Props> = ({ userId }) => {
  const [data, setData] = useState<WeaponAgg[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setError(null);
    cachedGet<AnalyticsResponse>(`/analytics/users/${userId}`)
      .then((d) => {
        if (!active) return;
        const agg: WeaponAgg[] = Object.entries(d.weapon_heatmaps).map(([weapon, heatmaps]) => {
          const allCells = heatmaps.flatMap((h) => h.cells);
          const avg = allCells.length ? allCells.reduce((s, c) => s + c.intensity, 0) / allCells.length : 0;
          return { weapon, avgIntensity: Math.round(avg * 100) };
        });
        agg.sort((a, b) => b.avgIntensity - a.avgIntensity);
        setData(agg);
      })
      .catch(() => { if (active) setError("Failed to load weapon data."); });
    return () => { active = false; };
  }, [userId]);

  if (error) return <p className="error">{error}</p>;
  if (!data.length) return <div><h2>Weapon Accuracy</h2><p style={{ color: "var(--text-dim)" }}>No data yet.</p></div>;

  return (
    <div>
      <h2>Weapon Accuracy</h2>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
          <XAxis type="number" tick={{ fill: "var(--text-dim)", fontSize: 11 }} unit="%" />
          <YAxis
            type="category"
            dataKey="weapon"
            width={90}
            tick={{ fill: "var(--text)", fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8 }}
            labelStyle={{ color: "var(--text)" }}
            formatter={(v: number) => [`${v}%`, "Accuracy"]}
          />
          <Bar dataKey="avgIntensity" radius={[0, 4, 4, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
