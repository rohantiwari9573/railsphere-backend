import { apiClient } from "./client";
import type {
  PaginatedResponse,
  Station,
  StationRouteInfo,
  StationTrainInfo,
} from "./types";

export async function getStations(params: {
  skip?: number;
  limit?: number;
  search?: string;
}): Promise<PaginatedResponse<Station>> {
  const response = await apiClient.get<PaginatedResponse<Station>>(
    "/stations",
    { params }
  );
  return response.data;
}

export async function getStation(id: number): Promise<Station> {
  const response = await apiClient.get<Station>(`/stations/${id}`);
  return response.data;
}

export async function getStationRoutes(
  id: number
): Promise<StationRouteInfo[]> {
  const response = await apiClient.get<StationRouteInfo[]>(
    `/stations/${id}/routes`
  );
  return response.data;
}

export async function getStationTrains(
  id: number
): Promise<StationTrainInfo[]> {
  const response = await apiClient.get<StationTrainInfo[]>(
    `/stations/${id}/trains`
  );
  return response.data;
}
