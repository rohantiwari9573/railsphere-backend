import { apiClient } from "./client";
import type {
  NetworkOverview,
  TopRoute,
  TopStation,
  TrainTypeCount,
} from "./types";

export async function getNetworkOverview(): Promise<NetworkOverview> {
  const response = await apiClient.get<NetworkOverview>(
    "/analytics/overview"
  );
  return response.data;
}

export async function getTopStations(limit = 10): Promise<TopStation[]> {
  const response = await apiClient.get<TopStation[]>(
    "/analytics/top-stations",
    { params: { limit } }
  );
  return response.data;
}

export async function getTopRoutes(limit = 10): Promise<TopRoute[]> {
  const response = await apiClient.get<TopRoute[]>("/analytics/top-routes", {
    params: { limit },
  });
  return response.data;
}

export async function getTrainTypeDistribution(): Promise<
  TrainTypeCount[]
> {
  const response = await apiClient.get<TrainTypeCount[]>(
    "/analytics/train-types"
  );
  return response.data;
}
