import { useQuery } from "@tanstack/react-query";
import { MapPin, Route as RouteIcon } from "lucide-react";
import { useParams } from "react-router-dom";
import { getRoute, getRouteStations } from "@/api/routes";
import { ErrorState } from "@/components/common/ErrorState";
import { DetailSkeleton } from "@/components/common/LoadingSkeleton";
import { Badge } from "@/components/ui/badge";
import { RouteTimelineSection } from "@/components/routes/RouteTimelineSection";

export function RouteDetailPage() {
  const { id } = useParams();
  const routeId = Number(id);

  const {
    data: route,
    isLoading: isRouteLoading,
    isError: isRouteError,
    refetch: refetchRoute,
  } = useQuery({
    queryKey: ["route", routeId],
    queryFn: () => getRoute(routeId),
    enabled: Boolean(routeId),
  });

  const { data: stops } = useQuery({
    queryKey: ["route-stations", routeId],
    queryFn: () => getRouteStations(routeId),
    enabled: Boolean(routeId),
  });

  if (isRouteLoading) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
        <DetailSkeleton />
      </div>
    );
  }

  if (isRouteError || !route) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6">
        <ErrorState message="Route not found." onRetry={() => refetchRoute()} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-primary">
              <RouteIcon className="h-3.5 w-3.5" />
              Route {route.route_code}
            </p>
            <h1 className="mt-1 text-2xl font-bold tracking-tight text-foreground">
              {route.route_name}
            </h1>
          </div>
          <Badge variant={route.is_active ? "secondary" : "outline"}>
            {route.is_active ? "Active" : "Inactive"}
          </Badge>
        </div>

        {stops && (
          <p className="mt-3 text-sm text-muted-foreground">
            {stops.length} stop{stops.length === 1 ? "" : "s"} across this
            route
          </p>
        )}
      </div>

      <h2 className="mt-8 mb-3 flex items-center gap-1.5 text-sm font-semibold text-foreground">
        <MapPin className="h-4 w-4 text-primary" />
        Stops in sequence
      </h2>

      <RouteTimelineSection routeId={routeId} />
    </div>
  );
}
