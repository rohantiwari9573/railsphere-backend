import { useQuery } from "@tanstack/react-query";
import { Route as RouteIcon } from "lucide-react";
import { useState } from "react";
import { getRoutes } from "@/api/routes";
import type { Route } from "@/api/types";
import { Badge } from "@/components/ui/badge";
import { DataTable, type DataTableColumn } from "@/components/common/DataTable";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { FilterBar } from "@/components/common/FilterBar";
import {
  CardGridSkeleton,
  ListRowSkeleton,
} from "@/components/common/LoadingSkeleton";
import { PageHeader } from "@/components/common/PageHeader";
import { Pagination } from "@/components/common/Pagination";
import { RouteCard } from "@/components/routes/RouteCard";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";

const LIMIT = 20;

const columns: DataTableColumn<Route>[] = [
  {
    header: "Route",
    accessor: (r) => <span className="font-medium">{r.route_name}</span>,
  },
  { header: "Code", accessor: (r) => r.route_code },
  {
    header: "Status",
    accessor: (r) => (
      <Badge variant={r.is_active ? "secondary" : "outline"}>
        {r.is_active ? "Active" : "Inactive"}
      </Badge>
    ),
  },
];

export function RoutesPage() {
  const [search, setSearch] = useState("");
  const [skip, setSkip] = useState(0);
  const debouncedSearch = useDebouncedValue(search, 300);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["routes", debouncedSearch, skip],
    queryFn: () =>
      getRoutes({ search: debouncedSearch, skip, limit: LIMIT }),
  });

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <PageHeader
        icon={RouteIcon}
        title="Routes"
        subtitle={
          data ? `${data.total.toLocaleString()} routes` : "Browse the full route dataset"
        }
      />

      <div className="mt-5">
        <FilterBar
          value={search}
          onChange={(v) => {
            setSearch(v);
            setSkip(0);
          }}
          placeholder="Search by name or route code"
        />
      </div>

      <div className="mt-5">
        {isLoading && (
          <>
            <div className="hidden sm:block">
              <ListRowSkeleton />
            </div>
            <div className="sm:hidden">
              <CardGridSkeleton count={4} />
            </div>
          </>
        )}
        {isError && (
          <ErrorState message="Couldn't load routes." onRetry={() => refetch()} />
        )}
        {!isLoading && !isError && data?.items.length === 0 && (
          <EmptyState
            icon={RouteIcon}
            title="No routes match your search."
            message="Try a different name or route code."
          />
        )}
        {!isLoading && !isError && data && data.items.length > 0 && (
          <>
            <div className="hidden sm:block">
              <DataTable
                columns={columns}
                data={data.items}
                getRowKey={(r) => r.id}
                getRowHref={(r) => `/routes/${r.id}`}
              />
            </div>
            <div className="grid grid-cols-1 gap-3 sm:hidden">
              {data.items.map((route) => (
                <RouteCard key={route.id} route={route} />
              ))}
            </div>
          </>
        )}
      </div>

      {data && (
        <Pagination
          skip={skip}
          limit={LIMIT}
          total={data.total}
          onPageChange={setSkip}
        />
      )}
    </div>
  );
}
