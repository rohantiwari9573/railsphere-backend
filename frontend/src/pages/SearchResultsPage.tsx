import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { ArrowRight, MapPin, TrainFront } from "lucide-react";
import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { searchJourneys } from "@/api/journeys";
import { getStation } from "@/api/stations";
import { TrainTypeBadge } from "@/components/common/Badges";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { CardGridSkeleton } from "@/components/common/LoadingSkeleton";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

function formatTime(value: string | null): string {
  if (!value) return "—";
  return value.slice(0, 5);
}

type SortKey = "departure" | "name";

export function SearchResultsPage() {
  const [searchParams] = useSearchParams();
  const fromId = Number(searchParams.get("from"));
  const toId = Number(searchParams.get("to"));
  const validParams = Boolean(fromId && toId);
  const [sortKey, setSortKey] = useState<SortKey>("departure");

  const { data: fromStation } = useQuery({
    queryKey: ["station", fromId],
    queryFn: () => getStation(fromId),
    enabled: validParams,
  });
  const { data: toStation } = useQuery({
    queryKey: ["station", toId],
    queryFn: () => getStation(toId),
    enabled: validParams,
  });

  const {
    data: results,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["journey-search", fromId, toId],
    queryFn: () => searchJourneys(fromId, toId),
    enabled: validParams,
  });

  const sortedResults = useMemo(() => {
    if (!results) return [];
    const copy = [...results];
    if (sortKey === "departure") {
      copy.sort((a, b) =>
        (a.departure_time ?? "99:99:99").localeCompare(
          b.departure_time ?? "99:99:99"
        )
      );
    } else {
      copy.sort((a, b) => a.train_name.localeCompare(b.train_name));
    }
    return copy;
  }, [results, sortKey]);

  if (!validParams) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <ErrorState message="Missing or invalid search parameters. Go back and search again." />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
      <div className="flex flex-wrap items-center gap-2 text-xl font-bold text-foreground">
        <MapPin className="h-5 w-5 text-primary" />
        <span>{fromStation?.name ?? "…"}</span>
        <ArrowRight className="h-4 w-4 text-muted-foreground" />
        <span>{toStation?.name ?? "…"}</span>
      </div>
      <p className="mt-1 text-sm text-muted-foreground">
        {isLoading
          ? "Searching…"
          : `${sortedResults.length} train${sortedResults.length === 1 ? "" : "s"} found, sorted by ${sortKey === "departure" ? "departure time" : "name"}.`}
      </p>

      {!isLoading && sortedResults.length > 0 && (
        <div className="mt-4 flex items-center justify-end gap-2">
          <span className="text-xs font-medium text-muted-foreground">
            Sort by
          </span>
          <Select
            value={sortKey}
            onValueChange={(v) => setSortKey(v as SortKey)}
          >
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="departure">Departure time</SelectItem>
              <SelectItem value="name">Train name</SelectItem>
            </SelectContent>
          </Select>
        </div>
      )}

      <div className="mt-4">
        {isLoading && <CardGridSkeleton count={4} />}
        {isError && (
          <ErrorState
            message="Couldn't load results. Try again in a moment."
            onRetry={() => refetch()}
          />
        )}
        {!isLoading && !isError && sortedResults.length === 0 && (
          <EmptyState
            icon={TrainFront}
            title="No direct trains found"
            message="There's no route in our data going directly from this origin to this destination."
          />
        )}
        {!isLoading && !isError && sortedResults.length > 0 && (
          <ul className="space-y-3">
            {sortedResults.map((journey, i) => (
              <motion.li
                key={`${journey.train_id}-${journey.route_id}`}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, delay: Math.min(i * 0.03, 0.3) }}
                className="rounded-xl border border-border bg-card p-4 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <Link
                        to={`/trains/${journey.train_id}`}
                        className="font-semibold text-foreground hover:text-primary hover:underline"
                      >
                        {journey.train_name}
                      </Link>
                      <TrainTypeBadge type={journey.train_type} />
                    </div>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      #{journey.train_number} · via{" "}
                      <Link
                        to={`/routes/${journey.route_id}`}
                        className="hover:text-primary hover:underline"
                      >
                        {journey.route_name}
                      </Link>
                    </p>
                  </div>

                  <div className="flex shrink-0 gap-2">
                    <Button variant="outline" size="sm" asChild>
                      <Link to={`/routes/${journey.route_id}`}>
                        View route
                      </Link>
                    </Button>
                    <Button size="sm" asChild>
                      <Link
                        to={`/book/${journey.train_id}/${journey.route_id}?from=${fromId}&to=${toId}`}
                      >
                        Book
                      </Link>
                    </Button>
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-3">
                  <div className="text-center">
                    <p className="text-sm font-semibold tabular-nums text-foreground">
                      {formatTime(journey.departure_time)}
                    </p>
                    <p className="text-[11px] text-muted-foreground">
                      {fromStation?.code}
                    </p>
                  </div>
                  <div className="flex flex-1 items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                    <span className="h-px flex-1 border-t border-dashed border-border" />
                    <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-semibold tabular-nums text-foreground">
                      {formatTime(journey.arrival_time)}
                    </p>
                    <p className="text-[11px] text-muted-foreground">
                      {toStation?.code}
                    </p>
                  </div>
                </div>
              </motion.li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
