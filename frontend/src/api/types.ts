export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface Station {
  id: number;
  code: string;
  name: string;
  city: string | null;
  state: string | null;
  zone: string | null;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  is_active: boolean;
}

export interface Train {
  id: number;
  train_number: string;
  train_name: string;
  train_type: string;
  zone: string | null;
  distance_km: number;
  duration_minutes: number;
  return_train_number: string | null;
  is_active: boolean;
}

export interface Route {
  id: number;
  route_code: string;
  route_name: string;
  is_active: boolean;
}

export interface RouteStation {
  id: number;
  route_id: number;
  station_id: number;
  sequence_number: number;
  arrival_time: string | null;
  departure_time: string | null;
  halt_minutes: number;
  distance_from_source: string;
}

export interface JourneySearchResult {
  train_id: number;
  train_number: string;
  train_name: string;
  train_type: string;
  route_id: number;
  route_code: string;
  route_name: string;
  departure_time: string | null;
  arrival_time: string | null;
}

export interface StationRouteInfo {
  route_id: number;
  route_code: string;
  route_name: string;
  sequence_number: number;
  arrival_time: string | null;
  departure_time: string | null;
}

export interface StationTrainInfo {
  train_id: number;
  train_number: string;
  train_name: string;
  train_type: string;
  route_id: number;
  route_code: string;
}

export interface TrainRouteInfo {
  route_id: number;
  route_code: string;
  route_name: string;
  start_time: string;
  end_time: string;
}

export interface NetworkOverview {
  total_stations: number;
  total_trains: number;
  total_routes: number;
  total_route_stations: number;
  total_schedules: number;
  avg_stations_per_route: number;
}

export interface TopStation {
  station_id: number;
  name: string;
  code: string;
  route_count: number;
}

export interface TopRoute {
  route_id: number;
  route_code: string;
  route_name: string;
  stop_count: number;
}

export interface TrainTypeCount {
  train_type: string;
  count: number;
}

export interface User {
  id: number;
  full_name: string;
  email: string;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface ApiError {
  detail: string;
}
