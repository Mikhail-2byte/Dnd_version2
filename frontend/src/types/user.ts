export interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface UserStats {
  characters_count: number;
  games_as_master_count: number;
  games_as_player_count: number;
  total_games_count: number;
}

