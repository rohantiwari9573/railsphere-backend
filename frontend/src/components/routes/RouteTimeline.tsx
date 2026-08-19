import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

export interface TimelineStop {
  id: number;
  sequenceNumber: number;
  stationId: number;
  stationName: string;
  stationCode: string;
  arrivalTime: string | null;
  departureTime: string | null;
}

interface Props {
  stops: TimelineStop[];
  highlightStationIds?: number[];
}

function formatTime(value: string | null): string | null {
  if (!value) return null;
  return value.slice(0, 5);
}

export function RouteTimeline({ stops, highlightStationIds = [] }: Props) {
  return (
    <ol className="relative">
      {stops.map((stop, index) => {
        const isFirst = index === 0;
        const isLast = index === stops.length - 1;
        const isTerminus = isFirst || isLast;
        const isHighlighted = highlightStationIds.includes(stop.stationId);

        return (
          <motion.li
            key={stop.id}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.25, delay: Math.min(index * 0.02, 0.4) }}
            className="relative flex gap-4 pb-6 last:pb-0"
          >
            {!isLast && (
              <span
                className="absolute left-[15px] top-7 h-full w-px bg-border"
                aria-hidden
              />
            )}

            <span
              className={cn(
                "z-10 flex h-7.5 w-7.5 shrink-0 items-center justify-center rounded-full border-2 text-[11px] font-bold",
                isTerminus
                  ? "border-primary bg-primary text-primary-foreground"
                  : isHighlighted
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border bg-background text-muted-foreground"
              )}
            >
              {stop.sequenceNumber}
            </span>

            <div className="flex min-w-0 flex-1 items-center justify-between gap-3 pt-0.5">
              <div className="min-w-0">
                <Link
                  to={`/stations/${stop.stationId}`}
                  className={cn(
                    "block truncate text-sm hover:text-primary hover:underline",
                    isTerminus
                      ? "font-semibold text-foreground"
                      : "font-medium text-foreground/90"
                  )}
                >
                  {stop.stationName}
                </Link>
                <p className="text-xs text-muted-foreground">
                  {stop.stationCode}
                  {isFirst && " · Origin"}
                  {isLast && " · Destination"}
                </p>
              </div>

              <div className="shrink-0 text-right text-xs tabular-nums text-muted-foreground">
                {formatTime(stop.arrivalTime) && (
                  <p>Arr {formatTime(stop.arrivalTime)}</p>
                )}
                {formatTime(stop.departureTime) && (
                  <p>Dep {formatTime(stop.departureTime)}</p>
                )}
              </div>
            </div>
          </motion.li>
        );
      })}
    </ol>
  );
}
