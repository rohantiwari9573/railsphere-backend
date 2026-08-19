import { useQuery } from "@tanstack/react-query";
import { MapPin, Route as RouteIcon, TrainFront } from "lucide-react";
import { Suspense, lazy } from "react";
import { Link, useParams } from "react-router-dom";
import { getStation, getStationRoutes, getStationTrains } from "@/api/stations";
import { TrainTypeBadge } from "@/components/common/Badges";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { DetailSkeleton, ListRowSkeleton } from "@/components/common/LoadingSkeleton";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const StationMap = lazy(() =>
  import("@/components/stations/StationMap").then((m) => ({
    default: m.StationMap,
  }))
);
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-border py-2.5 last:border-0">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-sm font-medium text-foreground">{value}</span>
    </div>
  );
}

export function StationDetailPage() {
  const { id } = useParams();
  const stationId = Number(id);

  const {
    data: station,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["station", stationId],
    queryFn: () => getStation(stationId),
    enabled: Boolean(stationId),
  });

  const { data: trains, isLoading: areTrainsLoading } = useQuery({
    queryKey: ["station-trains", stationId],
    queryFn: () => getStationTrains(stationId),
    enabled: Boolean(stationId),
  });

  const { data: routes, isLoading: areRoutesLoading } = useQuery({
    queryKey: ["station-routes", stationId],
    queryFn: () => getStationRoutes(stationId),
    enabled: Boolean(stationId),
  });

  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
        <DetailSkeleton />
      </div>
    );
  }

  if (isError || !station) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6">
        <ErrorState message="Station not found." onRetry={() => refetch()} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-primary">
              <MapPin className="h-3.5 w-3.5" />
              Station
            </p>
            <h1 className="mt-1 text-2xl font-bold tracking-tight text-foreground">
              {station.name}
            </h1>
          </div>
          <Badge
            variant="outline"
            className="border-primary/20 bg-primary/5 font-mono text-primary"
          >
            {station.code}
          </Badge>
        </div>

        <div className="mt-4">
          <InfoRow label="City" value={station.city ?? "—"} />
          <InfoRow label="State" value={station.state ?? "—"} />
          <InfoRow label="Zone" value={station.zone ?? "—"} />
          <InfoRow label="Address" value={station.address ?? "—"} />
          <InfoRow
            label="Status"
            value={station.is_active ? "Active" : "Inactive"}
          />
        </div>
      </div>

      {station.latitude != null && station.longitude != null && (
        <div className="mt-6">
          <Suspense fallback={<Skeleton className="h-64 w-full rounded-xl" />}>
            <StationMap
              latitude={station.latitude}
              longitude={station.longitude}
              name={station.name}
              code={station.code}
            />
          </Suspense>
        </div>
      )}

      <div className="mt-8">
        <Tabs defaultValue="trains">
          <TabsList>
            <TabsTrigger value="trains">
              <TrainFront className="h-4 w-4" />
              Trains{" "}
              {trains ? `(${trains.length})` : ""}
            </TabsTrigger>
            <TabsTrigger value="routes">
              <RouteIcon className="h-4 w-4" />
              Routes{" "}
              {routes ? `(${routes.length})` : ""}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="trains" className="mt-4">
            {areTrainsLoading && <ListRowSkeleton count={4} />}
            {!areTrainsLoading && trains?.length === 0 && (
              <EmptyState
                icon={TrainFront}
                title="No trains recorded through this station."
              />
            )}
            {!areTrainsLoading && trains && trains.length > 0 && (
              <ul className="divide-y divide-border overflow-hidden rounded-xl border border-border bg-card">
                {trains.map((train) => (
                  <li key={`${train.train_id}-${train.route_id}`}>
                    <Link
                      to={`/trains/${train.train_id}`}
                      className="flex items-center gap-3 px-4 py-3.5 transition-colors hover:bg-accent"
                    >
                      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <TrainFront className="h-4 w-4" strokeWidth={2} />
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate font-medium text-foreground">
                          {train.train_name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          #{train.train_number}
                        </p>
                      </div>
                      <TrainTypeBadge type={train.train_type} />
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </TabsContent>

          <TabsContent value="routes" className="mt-4">
            {areRoutesLoading && <ListRowSkeleton count={4} />}
            {!areRoutesLoading && routes?.length === 0 && (
              <EmptyState
                icon={RouteIcon}
                title="No routes recorded through this station."
              />
            )}
            {!areRoutesLoading && routes && routes.length > 0 && (
              <ul className="divide-y divide-border overflow-hidden rounded-xl border border-border bg-card">
                {routes.map((route) => (
                  <li key={route.route_id}>
                    <Link
                      to={`/routes/${route.route_id}`}
                      className="flex items-center gap-3 px-4 py-3.5 transition-colors hover:bg-accent"
                    >
                      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <RouteIcon className="h-4 w-4" strokeWidth={2} />
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate font-medium text-foreground">
                          {route.route_name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Stop #{route.sequence_number}
                        </p>
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
