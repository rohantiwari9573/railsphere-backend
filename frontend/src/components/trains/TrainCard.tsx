import { TrainFront } from "lucide-react";
import { Link } from "react-router-dom";
import type { Train } from "@/api/types";
import { TrainTypeBadge } from "@/components/common/Badges";

export function TrainCard({ train }: { train: Train }) {
  return (
    <Link
      to={`/trains/${train.id}`}
      className="flex items-center gap-3 rounded-xl border border-border bg-card p-4 transition-all hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-sm"
    >
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
        <TrainFront className="h-4.5 w-4.5" strokeWidth={2} />
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium text-foreground">
          {train.train_name}
        </p>
        <p className="truncate text-xs tabular-nums text-muted-foreground">
          #{train.train_number}
          {train.distance_km ? ` · ${train.distance_km} km` : ""}
        </p>
      </div>
      <TrainTypeBadge type={train.train_type} />
    </Link>
  );
}
