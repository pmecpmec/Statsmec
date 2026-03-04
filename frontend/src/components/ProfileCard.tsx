import React from "react";
import type { ProfileOverview } from "../types";

type Props = {
  profile: ProfileOverview | null;
};

export const ProfileCard: React.FC<Props> = ({ profile }) => {
  if (!profile) {
    return <div className="profile-card loading">Loading profile...</div>;
  }

  return (
    <div className="profile-card">
      <div className="profile-left">
        <img src={profile.avatar_url} alt={profile.nickname} className="avatar" />
        <div className="profile-info">
          <h1 className="nickname">{profile.nickname}</h1>
          <div className="profile-meta">
            <span className="rank">{profile.rank}</span>
            <span className="elo">ELO {profile.elo}</span>
            <span className="hours">{profile.total_hours.toLocaleString()}h played</span>
          </div>
        </div>
      </div>

      <div className="profile-stats">
        <div className="stat">
          <span className="stat-value">{profile.total_matches}</span>
          <span className="stat-label">Matches</span>
        </div>
        <div className="stat">
          <span className="stat-value win">{profile.win_rate}%</span>
          <span className="stat-label">Win Rate</span>
        </div>
        <div className="stat">
          <span className="stat-value">{profile.overall_kd}</span>
          <span className="stat-label">K/D</span>
        </div>
        <div className="stat">
          <span className="stat-value">{profile.headshot_pct}%</span>
          <span className="stat-label">HS %</span>
        </div>
        <div className="stat">
          <span className="stat-value">{profile.total_wins}</span>
          <span className="stat-label">Wins</span>
        </div>
        <div className="stat">
          <span className="stat-value loss">{profile.total_losses}</span>
          <span className="stat-label">Losses</span>
        </div>
        {profile.favorite_map && (
          <div className="stat">
            <span className="stat-value">{profile.favorite_map.replace("de_", "")}</span>
            <span className="stat-label">Top Map</span>
          </div>
        )}
        {profile.favorite_weapon && (
          <div className="stat">
            <span className="stat-value">{profile.favorite_weapon}</span>
            <span className="stat-label">Top Gun</span>
          </div>
        )}
      </div>
    </div>
  );
};
