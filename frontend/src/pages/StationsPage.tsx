import { useQuery } from "@tanstack/react-query";
import { MapPin } from "lucide-react";
import { useState } from "react";
import { getStations } from "@/api/stations";
import type { Station } from "@/api/types";
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
import { StationCard } from "@/components/stations/StationCard";
import { StationCodeBadge } from "@/components/common/Badges";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";

const LIMIT = 20;

const columns: DataTableColumn<Station>[] = [
  {
    header: "Station",
    accessor: (s) => <span className="font-medium">{s.name}</span>,
  },
  { header: "Code", accessor: (s) => <StationCodeBadge code={s.code} /> },
  { header: "City", accessor: (s) => s.city ?? "—" },
  { header: "State", accessor: (s) => s.state ?? "—" },
  { header: "Zone", accessor: (s) => s.zone ?? "—" },
];

export function StationsPage() {
  const [search, setSearch] = useState("");
  const [skip, setSkip] = useState(0);
  const debouncedSearch = useDebouncedValue(search, 300);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["stations", debouncedSearch, skip],
    queryFn: () =>
      getStations({ search: debouncedSearch, skip, limit: LIMIT }),
  });

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <PageHeader
        icon={MapPin}
        title="Stations"
        subtitle={
          data ? `${data.total.toLocaleString()} stations` : "Browse the full station dataset"
        }
      />

      <div className="mt-5">
        <FilterBar
          value={search}
          onChange={(v) => {
            setSearch(v);
            setSkip(0);
          }}
          placeholder="Search by name, code, or city"
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
          <ErrorState message="Couldn't load stations." onRetry={() => refetch()} />
        )}
        {!isLoading && !isError && data?.items.length === 0 && (
          <EmptyState
            icon={MapPin}
            title="No stations match your search."
            message="Try a different name, code, or city."
          />
        )}
        {!isLoading && !isError && data && data.items.length > 0 && (
          <>
            <div className="hidden sm:block">
              <DataTable
                columns={columns}
                data={data.items}
                getRowKey={(s) => s.id}
                getRowHref={(s) => `/stations/${s.id}`}
              />
            </div>
            <div className="grid grid-cols-1 gap-3 sm:hidden">
              {data.items.map((station) => (
                <StationCard key={station.id} station={station} />
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
