import { useQuery } from "@tanstack/react-query";
import { BarChart3, MapPin, Route as RouteIcon, TrainFront } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  getNetworkOverview,
  getTopRoutes,
  getTopStations,
  getTrainTypeDistribution,
} from "@/api/analytics";
import { AnimatedCounter } from "@/components/common/AnimatedCounter";
import { ErrorState } from "@/components/common/ErrorState";
import { PageHeader } from "@/components/common/PageHeader";
import { Skeleton } from "@/components/ui/skeleton";

const CHART_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];

function KpiCard({
  icon: Icon,
  label,
  value,
  suffix,
}: {
  icon: typeof MapPin;
  label: string;
  value: number;
  suffix?: string;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="flex items-center gap-2 text-muted-foreground">
        <Icon className="h-4 w-4" strokeWidth={2} />
        <span className="text-xs font-medium uppercase tracking-wide">
          {label}
        </span>
      </div>
      <p className="mt-2 text-2xl font-bold tabular-nums text-foreground">
        <AnimatedCounter value={value} />
        {suffix}
      </p>
    </div>
  );
}

function ChartCard({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h2 className="text-sm font-semibold text-foreground">{title}</h2>
      <p className="text-xs text-muted-foreground">{description}</p>
      <div className="mt-4">{children}</div>
    </div>
  );
}

export function AnalyticsPage() {
  const {
    data: overview,
    isLoading: isOverviewLoading,
    isError: isOverviewError,
    refetch: refetchOverview,
  } = useQuery({
    queryKey: ["network-overview"],
    queryFn: getNetworkOverview,
  });

  const { data: topStations, isLoading: areTopStationsLoading } = useQuery({
    queryKey: ["top-stations"],
    queryFn: () => getTopStations(10),
  });

  const { data: topRoutes, isLoading: areTopRoutesLoading } = useQuery({
    queryKey: ["top-routes"],
    queryFn: () => getTopRoutes(10),
  });

  const { data: trainTypes, isLoading: areTrainTypesLoading } = useQuery({
    queryKey: ["train-types"],
    queryFn: getTrainTypeDistribution,
  });

  if (isOverviewError) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6">
        <ErrorState
          message="Couldn't load network analytics."
          onRetry={() => refetchOverview()}
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <PageHeader
        icon={BarChart3}
        title="Network Analytics"
        subtitle="Computed live from the database — nothing here is estimated."
      />

      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {isOverviewLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))
        ) : (
          <>
            <KpiCard
              icon={MapPin}
              label="Stations"
              value={overview?.total_stations ?? 0}
            />
            <KpiCard
              icon={TrainFront}
              label="Trains"
              value={overview?.total_trains ?? 0}
            />
            <KpiCard
              icon={RouteIcon}
              label="Routes"
              value={overview?.total_routes ?? 0}
            />
            <KpiCard
              icon={BarChart3}
              label="Avg stops / route"
              value={overview?.avg_stations_per_route ?? 0}
            />
          </>
        )}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-5 lg:grid-cols-2">
        <ChartCard
          title="Most-connected stations"
          description="Ranked by number of routes passing through"
        >
          {areTopStationsLoading ? (
            <Skeleton className="h-72 w-full" />
          ) : (
            <ResponsiveContainer width="100%" height={288}>
              <BarChart
                data={topStations}
                layout="vertical"
                margin={{ left: 8, right: 16 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  horizontal={false}
                  stroke="var(--border)"
                />
                <XAxis type="number" hide />
                <YAxis
                  type="category"
                  dataKey="code"
                  width={48}
                  tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  cursor={{ fill: "var(--accent)" }}
                  contentStyle={{
                    borderRadius: 8,
                    border: "1px solid var(--border)",
                    fontSize: 12,
                  }}
                  formatter={(value) => [String(value), "Routes"]}
                  labelFormatter={(_, payload) =>
                    payload?.[0]?.payload?.name ?? ""
                  }
                />
                <Bar
                  dataKey="route_count"
                  fill="var(--chart-1)"
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard
          title="Longest routes"
          description="Ranked by number of stops"
        >
          {areTopRoutesLoading ? (
            <Skeleton className="h-72 w-full" />
          ) : (
            <ResponsiveContainer width="100%" height={288}>
              <BarChart
                data={topRoutes}
                layout="vertical"
                margin={{ left: 8, right: 16 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  horizontal={false}
                  stroke="var(--border)"
                />
                <XAxis type="number" hide />
                <YAxis
                  type="category"
                  dataKey="route_code"
                  width={56}
                  tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  cursor={{ fill: "var(--accent)" }}
                  contentStyle={{
                    borderRadius: 8,
                    border: "1px solid var(--border)",
                    fontSize: 12,
                  }}
                  formatter={(value) => [String(value), "Stops"]}
                  labelFormatter={(_, payload) =>
                    payload?.[0]?.payload?.route_name ?? ""
                  }
                />
                <Bar
                  dataKey="stop_count"
                  fill="var(--chart-2)"
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard
          title="Train type distribution"
          description="Every train, grouped by type"
        >
          {areTrainTypesLoading ? (
            <Skeleton className="h-72 w-full" />
          ) : (
            <ResponsiveContainer width="100%" height={288}>
              <PieChart>
                <Pie
                  data={trainTypes?.slice(0, 8)}
                  dataKey="count"
                  nameKey="train_type"
                  innerRadius={55}
                  outerRadius={95}
                  paddingAngle={2}
                >
                  {trainTypes?.slice(0, 8).map((entry, index) => (
                    <Cell
                      key={entry.train_type}
                      fill={CHART_COLORS[index % CHART_COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    borderRadius: 8,
                    border: "1px solid var(--border)",
                    fontSize: 12,
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard
          title="Network summary"
          description="Every figure below is a live database count"
        >
          <dl className="space-y-3">
            <div className="flex justify-between border-b border-border pb-2.5">
              <dt className="text-sm text-muted-foreground">
                Route-station links
              </dt>
              <dd className="text-sm font-semibold tabular-nums text-foreground">
                {(overview?.total_route_stations ?? 0).toLocaleString()}
              </dd>
            </div>
            <div className="flex justify-between border-b border-border pb-2.5">
              <dt className="text-sm text-muted-foreground">Schedules</dt>
              <dd className="text-sm font-semibold tabular-nums text-foreground">
                {(overview?.total_schedules ?? 0).toLocaleString()}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm text-muted-foreground">
                Avg. stops per route
              </dt>
              <dd className="text-sm font-semibold tabular-nums text-foreground">
                {overview?.avg_stations_per_route ?? 0}
              </dd>
            </div>
          </dl>
        </ChartCard>
      </div>
    </div>
  );
}
