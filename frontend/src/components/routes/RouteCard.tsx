import { Route as RouteIcon } from "lucide-react";
import { Link } from "react-router-dom";
import type { Route } from "@/api/types";
import { Badge } from "@/components/ui/badge";

export function RouteCard({ route }: { route: Route }) {
  return (
    <Link
      to={`/routes/${route.id}`}
      className="flex items-center gap-3 rounded-xl border border-border bg-card p-4 transition-all hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-sm"
    >
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
        <RouteIcon className="h-4.5 w-4.5" strokeWidth={2} />
      </span>
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium text-foreground">
          {route.route_name}
        </p>
        <p className="truncate text-xs tabular-nums text-muted-foreground">
          {route.route_code}
        </p>
      </div>
      <Badge variant={route.is_active ? "secondary" : "outline"}>
        {route.is_active ? "Active" : "Inactive"}
      </Badge>
    </Link>
  );
}
