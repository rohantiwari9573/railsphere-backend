import { useQueries, useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { getRouteStations } from "@/api/routes";
import { getStation } from "@/api/stations";
import { EmptyState } from "@/components/common/EmptyState";
import { TimelineSkeleton } from "@/components/common/LoadingSkeleton";
import { RouteTimeline, type TimelineStop } from "./RouteTimeline";

export function RouteTimelineSection({ routeId }: { routeId: number }) {
  const { data: stops, isLoading } = useQuery({
    queryKey: ["route-stations", routeId],
    queryFn: () => getRouteStations(routeId),
    enabled: Boolean(routeId),
  });

  const stationQueries = useQueries({
    queries: (stops ?? []).map((stop) => ({
      queryKey: ["station", stop.station_id],
      queryFn: () => getStation(stop.station_id),
      enabled: Boolean(stops),
    })),
  });

  const timelineStops: TimelineStop[] = useMemo(() => {
    if (!stops) return [];
    return stops.map((stop, index) => ({
      id: stop.id,
      sequenceNumber: stop.sequence_number,
      stationId: stop.station_id,
      stationName: stationQueries[index]?.data?.name ?? "Loading…",
      stationCode: stationQueries[index]?.data?.code ?? "",
      arrivalTime: stop.arrival_time,
      departureTime: stop.departure_time,
    }));
  }, [stops, stationQueries]);

  if (isLoading) return <TimelineSkeleton count={6} />;

  if (stops?.length === 0) {
    return <EmptyState title="No stops recorded for this route." />;
  }

  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <RouteTimeline stops={timelineStops} />
    </div>
  );
}
