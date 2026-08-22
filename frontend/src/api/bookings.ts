import { apiClient } from "./client";
import type {
  AvailabilityClass,
  Booking,
  BookingCreate,
  CancelResult,
  PaymentResult,
  SeatMapResponse,
} from "./types";

export async function getAvailability(
  trainId: number,
  journeyDate: string,
  journeyContext?: {
    routeId: number;
    sourceStationId: number;
    destinationStationId: number;
  }
): Promise<AvailabilityClass[]> {
  const response = await apiClient.get<AvailabilityClass[]>(
    `/trains/${trainId}/availability`,
    {
      params: {
        journey_date: journeyDate,
        route_id: journeyContext?.routeId,
        source_station_id: journeyContext?.sourceStationId,
        destination_station_id: journeyContext?.destinationStationId,
      },
    }
  );
  return response.data;
}

export async function getSeatMap(
  trainId: number,
  journeyDate: string,
  travelClass: string
): Promise<SeatMapResponse> {
  const response = await apiClient.get<SeatMapResponse>(
    `/trains/${trainId}/seat-map`,
    { params: { journey_date: journeyDate, travel_class: travelClass } }
  );
  return response.data;
}

export async function createBooking(data: BookingCreate): Promise<Booking> {
  const response = await apiClient.post<Booking>("/bookings", data);
  return response.data;
}

export async function getBooking(bookingId: number): Promise<Booking> {
  const response = await apiClient.get<Booking>(`/bookings/${bookingId}`);
  return response.data;
}

export async function payForBooking(
  bookingId: number,
  method: string
): Promise<PaymentResult> {
  const response = await apiClient.post<PaymentResult>(
    `/bookings/${bookingId}/pay`,
    { method }
  );
  return response.data;
}

export async function getBookingByPnr(pnr: string): Promise<Booking> {
  const response = await apiClient.get<Booking>(`/bookings/pnr/${pnr}`);
  return response.data;
}

export async function getMyBookings(): Promise<Booking[]> {
  const response = await apiClient.get<Booking[]>("/bookings/mine");
  return response.data;
}

export async function cancelBooking(bookingId: number): Promise<CancelResult> {
  const response = await apiClient.post<CancelResult>(
    `/bookings/${bookingId}/cancel`
  );
  return response.data;
}
