export type ProfileOverview = {
  nickname: string;
  steam_id: string;
  faceit_nickname: string;
  avatar_url: string;
  rank: string;
  elo: number;
  total_matches: number;
  total_wins: number;
  total_losses: number;
  win_rate: number;
  overall_kd: number;
  headshot_pct: number;
  total_hours: number;
  favorite_map: string | null;
  favorite_weapon: string | null;
};
