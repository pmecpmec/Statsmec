import React, { useEffect, useState } from "react";
import { ProfileCard } from "./components/ProfileCard";
import { MatchHistoryPanel } from "./components/MatchHistoryPanel";
import { WeaponHeatmapPanel } from "./components/WeaponHeatmapPanel";
import { PerformanceTrendsPanel } from "./components/PerformanceTrendsPanel";
import { RankComparisonPanel } from "./components/RankComparisonPanel";
import { cachedGet } from "./api/client";
import type { ProfileOverview } from "./types";

export const App: React.FC = () => {
  const userId = 1;
  const [profile, setProfile] = useState<ProfileOverview | null>(null);

  useEffect(() => {
    cachedGet<ProfileOverview>("/me").then(setProfile).catch(() => {});
  }, []);

  return (
    <div className="app">
      <header className="header">
        <div className="header-brand">
          <span className="logo">Statsmec</span>
        </div>
        <nav className="header-links">
          <a href="https://steamcommunity.com/id/pmec" target="_blank" rel="noreferrer">Steam</a>
          <a href="https://www.faceit.com/en/players/pmec" target="_blank" rel="noreferrer">FACEIT</a>
          <a href="https://www.twitch.tv/pmec" target="_blank" rel="noreferrer">Twitch</a>
        </nav>
      </header>

      <main className="dashboard">
        <ProfileCard profile={profile} />

        <div className="grid">
          <section className="card span-2">
            <MatchHistoryPanel userId={userId} />
          </section>
          <section className="card">
            <PerformanceTrendsPanel userId={userId} />
          </section>
          <section className="card">
            <RankComparisonPanel userId={userId} />
          </section>
          <section className="card span-2">
            <WeaponHeatmapPanel userId={userId} />
          </section>
        </div>
      </main>
    </div>
  );
};
