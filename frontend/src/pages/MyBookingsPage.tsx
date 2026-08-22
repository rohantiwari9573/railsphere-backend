import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Ticket } from "lucide-react";
import { Link } from "react-router-dom";
import { getMyBookings } from "@/api/bookings";
import { BookingStatusBadge } from "@/components/common/Badges";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { CardGridSkeleton } from "@/components/common/LoadingSkeleton";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";

export function MyBookingsPage() {
  const { user } = useAuth();

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["my-bookings"],
    queryFn: getMyBookings,
    enabled: Boolean(user),
  });

  if (!user) {
    return (
      <div className="mx-auto max-w-md px-4 py-16 text-center sm:px-6">
        <p className="text-sm font-medium text-foreground">
          Log in to see your bookings.
        </p>
        <Button asChild className="mt-4">
          <Link to="/login">Log in</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <PageHeader
        icon={Ticket}
        title="My Bookings"
        subtitle={data ? `${data.length} booking${data.length === 1 ? "" : "s"}` : undefined}
      />

      <div className="mt-5">
        {isLoading && <CardGridSkeleton count={3} />}
        {isError && (
          <ErrorState message="Couldn't load your bookings." onRetry={() => refetch()} />
        )}
        {!isLoading && !isError && data?.length === 0 && (
          <EmptyState
            icon={Ticket}
            title="No bookings yet"
            message="Search for a train and book your first ticket."
          />
        )}
        {!isLoading && !isError && data && data.length > 0 && (
          <div className="space-y-3">
            {data.map((booking, i) => (
              <Link
                key={booking.id}
                to={`/ticket/${booking.id}`}
                className="block animate-in fade-in slide-in-from-bottom-1 fill-mode-both rounded-xl border border-border bg-card p-4 duration-300 transition-shadow hover:shadow-md"
                style={{ animationDelay: `${Math.min(i * 40, 300)}ms` }}
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-foreground">
                      {booking.train_name}{" "}
                      <span className="text-xs font-normal text-muted-foreground">
                        #{booking.train_number}
                      </span>
                    </p>
                    <p className="mt-1 flex items-center gap-1.5 text-sm text-muted-foreground">
                      {booking.source_station_code}
                      <ArrowRight className="h-3 w-3" />
                      {booking.destination_station_code}
                      <span className="mx-1">·</span>
                      {booking.journey_date}
                      <span className="mx-1">·</span>
                      {booking.class_name}
                    </p>
                    <p className="mt-1 font-mono text-xs text-muted-foreground">
                      PNR {booking.pnr}
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <BookingStatusBadge status={booking.status} />
                    <span className="text-sm font-semibold tabular-nums text-foreground">
                      ₹{booking.total_fare}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
