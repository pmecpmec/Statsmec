import React, { useEffect, useState } from "react";
import { cachedGet } from "../api/client";

type HeatmapCell = {
  x: number;
  y: number;
  intensity: number;
};

type WeaponHeatmap = {
  match_id: number;
  weapon_name: string;
  cells: HeatmapCell[];
};

type AnalyticsResponse = {
  weapon_heatmaps: Record<string, WeaponHeatmap[]>;
};

type Props = {
  userId: number;
};

export const WeaponHeatmapPanel: React.FC<Props> = ({ userId }) => {
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setError(null);
    cachedGet<AnalyticsResponse>(`/analytics/users/${userId}`)
      .then((d) => {
        if (active) setData(d);
      })
      .catch((err: unknown) => {
        if (active) setError("Failed to load weapon heatmaps.");
        // eslint-disable-next-line no-console
        console.error(err);
      });
    return () => {
      active = false;
    };
  }, [userId]);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading weapon heatmaps…</p>;

  return (
    <div>
      <h2>Weapon Accuracy Heatmaps</h2>
      {Object.entries(data.weapon_heatmaps).map(([weapon, heatmaps]) => (
        <div key={weapon} className="heatmap-group">
          <h3>{weapon}</h3>
          <div className="heatmap-row">
            {heatmaps.map((h) => (
              <div key={h.match_id} className="heatmap">
                <div className="heatmap-grid">
                  {h.cells.map((cell) => (
                    <div
                      key={`${cell.x}-${cell.y}`}
                      className="heatmap-cell"
                      style={{ opacity: Math.min(1, cell.intensity) }}
                    />
                  ))}
                </div>
                <span className="heatmap-caption">Match {h.match_id}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

