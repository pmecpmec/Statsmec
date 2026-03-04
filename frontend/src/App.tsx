import React, { useState } from "react";
import { MatchHistoryPanel } from "./components/MatchHistoryPanel";
import { WeaponHeatmapPanel } from "./components/WeaponHeatmapPanel";
import { PerformanceTrendsPanel } from "./components/PerformanceTrendsPanel";
import { RankComparisonPanel } from "./components/RankComparisonPanel";

export const App: React.FC = () => {
  const [userId, setUserId] = useState<number>(1);

  return (
    <div className="app">
      <header className="header">
        <h1>Statsmec Dashboard</h1>
        <div className="controls">
          <label>
            User ID:
            <input
              type="number"
              value={userId}
              min={1}
              onChange={(e) => setUserId(Number(e.target.value))}
            />
          </label>
        </div>
      </header>
      <main className="layout">
        <section className="panel wide">
          <MatchHistoryPanel userId={userId} />
        </section>
        <section className="panel">
          <WeaponHeatmapPanel userId={userId} />
        </section>
        <section className="panel">
          <PerformanceTrendsPanel userId={userId} />
        </section>
        <section className="panel">
          <RankComparisonPanel userId={userId} />
        </section>
      </main>
    </div>
  );
};

