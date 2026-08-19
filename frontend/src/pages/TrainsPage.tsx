import { useQuery } from "@tanstack/react-query";
import { TrainFront } from "lucide-react";
import { useState } from "react";
import { getTrains } from "@/api/trains";
import type { Train } from "@/api/types";
import { TrainTypeBadge } from "@/components/common/Badges";
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
import { TrainCard } from "@/components/trains/TrainCard";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";

const LIMIT = 20;

const columns: DataTableColumn<Train>[] = [
  {
    header: "Train",
    accessor: (t) => <span className="font-medium">{t.train_name}</span>,
  },
  { header: "Number", accessor: (t) => `#${t.train_number}` },
  { header: "Type", accessor: (t) => <TrainTypeBadge type={t.train_type} /> },
  { header: "Zone", accessor: (t) => t.zone ?? "—" },
  {
    header: "Distance",
    accessor: (t) => (t.distance_km ? `${t.distance_km} km` : "—"),
  },
];

export function TrainsPage() {
  const [search, setSearch] = useState("");
  const [skip, setSkip] = useState(0);
  const debouncedSearch = useDebouncedValue(search, 300);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["trains", debouncedSearch, skip],
    queryFn: () =>
      getTrains({ search: debouncedSearch, skip, limit: LIMIT }),
  });

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <PageHeader
        icon={TrainFront}
        title="Trains"
        subtitle={
          data ? `${data.total.toLocaleString()} trains` : "Browse the full train dataset"
        }
      />

      <div className="mt-5">
        <FilterBar
          value={search}
          onChange={(v) => {
            setSearch(v);
            setSkip(0);
          }}
          placeholder="Search by name or train number"
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
          <ErrorState message="Couldn't load trains." onRetry={() => refetch()} />
        )}
        {!isLoading && !isError && data?.items.length === 0 && (
          <EmptyState
            icon={TrainFront}
            title="No trains match your search."
            message="Try a different name or train number."
          />
        )}
        {!isLoading && !isError && data && data.items.length > 0 && (
          <>
            <div className="hidden sm:block">
              <DataTable
                columns={columns}
                data={data.items}
                getRowKey={(t) => t.id}
                getRowHref={(t) => `/trains/${t.id}`}
              />
            </div>
            <div className="grid grid-cols-1 gap-3 sm:hidden">
              {data.items.map((train) => (
                <TrainCard key={train.id} train={train} />
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
