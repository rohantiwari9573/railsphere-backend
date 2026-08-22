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

export interface AvailabilityClass {
  class_code: string;
  class_name: string;
  fare: string;
  total_seats: number;
  available_seats: number;
  waitlist_count: number;
  status_label: string;
}

export interface SeatInfo {
  seat_number: number;
  coach: string;
  berth_type: string | null;
  is_booked: boolean;
}

export interface CoachSeatMap {
  coach: string;
  seats: SeatInfo[];
}

export interface SeatMapResponse {
  class_code: string;
  class_name: string;
  coaches: CoachSeatMap[];
}

export interface PassengerInput {
  name: string;
  age: number;
  gender: "M" | "F" | "O";
}

export interface Passenger {
  id: number;
  name: string;
  age: number;
  gender: string;
  status: "CONFIRMED" | "WAITLISTED" | "CANCELLED";
  seat_number: number | null;
  coach: string | null;
  berth_type: string | null;
}

export type BookingStatus =
  | "PENDING_PAYMENT"
  | "CONFIRMED"
  | "PARTIALLY_CONFIRMED"
  | "WAITLISTED"
  | "CANCELLED";

export interface Booking {
  id: number;
  pnr: string;
  status: BookingStatus;
  travel_class: string;
  class_name: string;
  journey_date: string;
  total_fare: string;
  train_id: number;
  train_number: string;
  train_name: string;
  source_station_id: number;
  source_station_name: string;
  source_station_code: string;
  destination_station_id: number;
  destination_station_name: string;
  destination_station_code: string;
  passengers: Passenger[];
  is_paid: boolean;
  created_at: string;
}

export interface BookingCreate {
  train_id: number;
  route_id: number;
  source_station_id: number;
  destination_station_id: number;
  journey_date: string;
  travel_class: string;
  passengers: PassengerInput[];
}

export interface PaymentResult {
  status: "SUCCESS" | "FAILED";
  transaction_id: string | null;
  message: string;
  booking: Booking | null;
}

export interface CancelResult {
  booking: Booking;
  refund_amount: string;
  cancellation_charge: string;
}
