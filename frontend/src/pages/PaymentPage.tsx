import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, CreditCard, Landmark, Smartphone } from "lucide-react";
import { useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";
import { getBooking, payForBooking } from "@/api/bookings";
import { BookingStatusBadge } from "@/components/common/Badges";
import { DetailSkeleton } from "@/components/common/LoadingSkeleton";
import { ErrorState } from "@/components/common/ErrorState";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const METHODS = [
  { value: "UPI", label: "UPI", icon: Smartphone },
  { value: "CARD", label: "Card", icon: CreditCard },
  { value: "NETBANKING", label: "Net Banking", icon: Landmark },
] as const;

export function PaymentPage() {
  const { bookingId } = useParams();
  const bookingIdNum = Number(bookingId);
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [method, setMethod] = useState<(typeof METHODS)[number]["value"]>("UPI");

  const {
    data: booking,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["booking", bookingIdNum],
    queryFn: () => getBooking(bookingIdNum),
    enabled: Boolean(bookingIdNum),
  });

  const payMutation = useMutation({
    mutationFn: () => payForBooking(bookingIdNum, method),
    onSuccess: (result) => {
      if (result.status === "SUCCESS" && result.booking) {
        queryClient.setQueryData(["booking", bookingIdNum], result.booking);
        queryClient.invalidateQueries({ queryKey: ["my-bookings"] });
      }
    },
  });

  if (isLoading) {
    return (
      <div className="mx-auto max-w-lg px-4 py-10 sm:px-6">
        <DetailSkeleton />
      </div>
    );
  }

  if (isError || !booking) {
    return (
      <div className="mx-auto max-w-lg px-4 py-10 sm:px-6">
        <ErrorState message="Couldn't load this booking." />
      </div>
    );
  }

  if (booking.is_paid) {
    return <Navigate to={`/ticket/${booking.id}`} replace />;
  }

  const result = payMutation.data;

  return (
    <div className="mx-auto max-w-lg px-4 py-10 sm:px-6">
      <PageHeader
        icon={CreditCard}
        title="Payment"
        subtitle={`PNR ${booking.pnr}`}
      />

      <div className="mt-5 rounded-xl border border-border bg-card p-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-semibold text-foreground">
              {booking.train_name}{" "}
              <span className="text-xs font-normal text-muted-foreground">
                #{booking.train_number}
              </span>
            </p>
            <p className="mt-0.5 text-xs text-muted-foreground">
              {booking.source_station_code} → {booking.destination_station_code}{" "}
              · {booking.journey_date} · {booking.class_name}
            </p>
          </div>
          <BookingStatusBadge status={booking.status} />
        </div>
        <div className="mt-4 flex items-center justify-between border-t border-border pt-4">
          <span className="text-sm text-muted-foreground">
            {booking.passengers.length} passenger
            {booking.passengers.length === 1 ? "" : "s"}
          </span>
          <span className="text-xl font-bold tabular-nums text-foreground">
            ₹{booking.total_fare}
          </span>
        </div>
      </div>

      {result?.status === "FAILED" ? (
        <div className="mt-5 flex items-start gap-3 rounded-xl border border-destructive/20 bg-destructive/5 p-4">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
          <p className="text-sm text-destructive">{result.message}</p>
        </div>
      ) : null}

      <div className="mt-5">
        <p className="mb-2 text-sm font-medium text-foreground">
          Payment method
        </p>
        <div className="grid grid-cols-3 gap-2">
          {METHODS.map((m) => (
            <button
              key={m.value}
              type="button"
              onClick={() => setMethod(m.value)}
              className={cn(
                "flex flex-col items-center gap-1.5 rounded-xl border p-3 text-xs font-medium transition-all",
                method === m.value
                  ? "border-primary bg-primary/5 text-primary"
                  : "border-border text-muted-foreground hover:border-primary/30"
              )}
            >
              <m.icon className="h-4 w-4" />
              {m.label}
            </button>
          ))}
        </div>
      </div>

      <Button
        size="lg"
        className="mt-6 w-full"
        onClick={() => payMutation.mutate()}
        disabled={payMutation.isPending}
      >
        {payMutation.isPending
          ? "Processing…"
          : `Pay ₹${booking.total_fare}`}
      </Button>

      {result?.status === "SUCCESS" && (
        <div className="mt-4 animate-in fade-in slide-in-from-bottom-1 duration-300">
          <Button
            variant="outline"
            className="w-full"
            onClick={() => navigate(`/ticket/${booking.id}`)}
          >
            View e-ticket
          </Button>
        </div>
      )}

      <p className="mt-4 text-center text-xs text-muted-foreground">
        This is a simulated payment for demonstration purposes only. No real
        money moves.
      </p>
    </div>
  );
}
