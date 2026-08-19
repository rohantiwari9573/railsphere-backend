import { apiClient } from "./client";
import type { PaginatedResponse, Route, RouteStation } from "./types";

export async function getRoutes(params: {
  skip?: number;
  limit?: number;
  search?: string;
}): Promise<PaginatedResponse<Route>> {
  const response = await apiClient.get<PaginatedResponse<Route>>("/routes", {
    params,
  });
  return response.data;
}

export async function getRoute(id: number): Promise<Route> {
  const response = await apiClient.get<Route>(`/routes/${id}`);
  return response.data;
}

export async function getRouteStations(
  routeId: number
): Promise<RouteStation[]> {
  const response = await apiClient.get<RouteStation[]>("/route-stations", {
    params: { route_id: routeId },
  });
  return response.data;
}
