import { useQuery } from "@tanstack/react-query";
import { MapPin, TrainFront } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { getTrain, getTrainRoutes } from "@/api/trains";
import { TrainTypeBadge } from "@/components/common/Badges";
import { ErrorState } from "@/components/common/ErrorState";
import { DetailSkeleton } from "@/components/common/LoadingSkeleton";
import { RouteTimelineSection } from "@/components/routes/RouteTimelineSection";

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-border py-2.5 last:border-0">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-sm font-medium text-foreground">{value}</span>
    </div>
  );
}

export function TrainDetailPage() {
  const { id } = useParams();
  const trainId = Number(id);

  const {
    data: train,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["train", trainId],
    queryFn: () => getTrain(trainId),
    enabled: Boolean(trainId),
  });

  const { data: routes } = useQuery({
    queryKey: ["train-routes", trainId],
    queryFn: () => getTrainRoutes(trainId),
    enabled: Boolean(trainId),
  });

  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
        <DetailSkeleton />
      </div>
    );
  }

  if (isError || !train) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6">
        <ErrorState message="Train not found." onRetry={() => refetch()} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-primary">
              <TrainFront className="h-3.5 w-3.5" />
              Train #{train.train_number}
            </p>
            <h1 className="mt-1 text-2xl font-bold tracking-tight text-foreground">
              {train.train_name}
            </h1>
          </div>
          <TrainTypeBadge type={train.train_type} />
        </div>

        <div className="mt-4">
          <InfoRow label="Zone" value={train.zone ?? "—"} />
          <InfoRow
            label="Distance"
            value={train.distance_km ? `${train.distance_km} km` : "—"}
          />
          <InfoRow
            label="Duration"
            value={
              train.duration_minutes
                ? `${Math.floor(train.duration_minutes / 60)}h ${train.duration_minutes % 60}m`
                : "—"
            }
          />
          <InfoRow
            label="Return train"
            value={train.return_train_number ?? "—"}
          />
          <InfoRow
            label="Status"
            value={train.is_active ? "Active" : "Inactive"}
          />
        </div>
      </div>

      {routes && routes.length > 0 && (
        <div className="mt-8">
          <h2 className="mb-3 flex items-center gap-1.5 text-sm font-semibold text-foreground">
            <MapPin className="h-4 w-4 text-primary" />
            Route
          </h2>
          {routes.map((route) => (
            <div key={route.route_id} className="mb-6 last:mb-0">
              <p className="mb-2 text-sm text-muted-foreground">
                <Link
                  to={`/routes/${route.route_id}`}
                  className="font-medium text-foreground hover:text-primary hover:underline"
                >
                  {route.route_name}
                </Link>{" "}
                · {route.start_time.slice(0, 5)} — {route.end_time.slice(0, 5)}
              </p>
              <RouteTimelineSection routeId={route.route_id} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
