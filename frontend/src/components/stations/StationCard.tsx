import { MapPin } from "lucide-react";
import { Link } from "react-router-dom";
import type { Station } from "@/api/types";
import { StationCodeBadge } from "@/components/common/Badges";

export function StationCard({ station }: { station: Station }) {
  return (
    <Link
      to={`/stations/${station.id}`}
      className="flex items-center gap-3 rounded-xl border border-border bg-card p-4 transition-all hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-sm"
    >
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
        <MapPin className="h-4.5 w-4.5" strokeWidth={2} />
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium text-foreground">
          {station.name}
        </p>
        <p className="truncate text-xs text-muted-foreground">
          {station.state ?? "—"}
          {station.zone ? ` · ${station.zone} Zone` : ""}
        </p>
      </div>
      <StationCodeBadge code={station.code} />
    </Link>
  );
}
