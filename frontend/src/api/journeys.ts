import { apiClient } from "./client";
import type { JourneySearchResult } from "./types";

export async function searchJourneys(
  fromStationId: number,
  toStationId: number
): Promise<JourneySearchResult[]> {
  const response = await apiClient.get<JourneySearchResult[]>(
    "/journeys/search",
    {
      params: {
        from_station_id: fromStationId,
        to_station_id: toStationId,
      },
    }
  );
  return response.data;
}
