import { apiClient } from "./client";
import type { PaginatedResponse, Train, TrainRouteInfo } from "./types";

export async function getTrains(params: {
  skip?: number;
  limit?: number;
  search?: string;
}): Promise<PaginatedResponse<Train>> {
  const response = await apiClient.get<PaginatedResponse<Train>>("/trains", {
    params,
  });
  return response.data;
}

export async function getTrain(id: number): Promise<Train> {
  const response = await apiClient.get<Train>(`/trains/${id}`);
  return response.data;
}

export async function getTrainRoutes(
  id: number
): Promise<TrainRouteInfo[]> {
  const response = await apiClient.get<TrainRouteInfo[]>(
    `/trains/${id}/routes`
  );
  return response.data;
}
