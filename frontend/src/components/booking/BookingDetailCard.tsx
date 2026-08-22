import { QRCodeCanvas } from "qrcode.react";
import { forwardRef } from "react";
import type { Booking } from "@/api/types";
import { BookingStatusBadge } from "@/components/common/Badges";
import { Badge } from "@/components/ui/badge";

const BERTH_LABEL: Record<string, string> = {
  LOWER: "Lower",
  MIDDLE: "Middle",
  UPPER: "Upper",
  SIDE_LOWER: "Side Lower",
  SIDE_UPPER: "Side Upper",
};

const PASSENGER_STATUS_STYLES: Record<string, string> = {
  CONFIRMED:
    "bg-emerald-50 text-emerald-700 border-emerald-200 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300",
  WAITLISTED:
    "bg-amber-50 text-amber-700 border-amber-200 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300",
  CANCELLED:
    "bg-slate-50 text-slate-600 border-slate-200 dark:border-slate-500/30 dark:bg-slate-500/10 dark:text-slate-400",
};

export const BookingDetailCard = forwardRef<
  HTMLCanvasElement,
  { booking: Booking }
>(function BookingDetailCard({ booking }, qrRef) {
  return (
    <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            PNR
          </p>
          <p className="font-mono text-2xl font-bold tracking-wider text-foreground">
            {booking.pnr}
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <BookingStatusBadge status={booking.status} />
          {!booking.is_paid && booking.status !== "CANCELLED" && (
            <Badge variant="outline" className="text-amber-600 dark:text-amber-400">
              Payment pending
            </Badge>
          )}
        </div>
      </div>

      <div className="mt-5 flex items-center justify-between border-t border-border pt-5">
        <div>
          <p className="font-semibold text-foreground">
            {booking.train_name}{" "}
            <span className="text-xs font-normal text-muted-foreground">
              #{booking.train_number}
            </span>
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            {booking.source_station_name} ({booking.source_station_code}) →{" "}
            {booking.destination_station_name} (
            {booking.destination_station_code})
          </p>
          <p className="mt-1 text-sm text-muted-foreground">
            {booking.journey_date} · {booking.class_name} (
            {booking.travel_class})
          </p>
        </div>
        <QRCodeCanvas
          ref={qrRef}
          value={`RailSphere PNR ${booking.pnr} | ${booking.train_number} | ${booking.journey_date}`}
          size={72}
          className="shrink-0 rounded-lg border border-border p-1.5"
        />
      </div>

      <div className="mt-5 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs text-muted-foreground">
              <th className="pb-2 font-medium">Passenger</th>
              <th className="pb-2 font-medium">Age/Gender</th>
              <th className="pb-2 font-medium">Seat</th>
              <th className="pb-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {booking.passengers.map((p) => (
              <tr key={p.id}>
                <td className="py-2 font-medium text-foreground">{p.name}</td>
                <td className="py-2 text-muted-foreground">
                  {p.age} / {p.gender}
                </td>
                <td className="py-2 tabular-nums text-foreground">
                  {p.seat_number
                    ? `${p.coach}-${p.seat_number}${
                        p.berth_type
                          ? ` (${BERTH_LABEL[p.berth_type] ?? p.berth_type})`
                          : ""
                      }`
                    : "—"}
                </td>
                <td className="py-2">
                  <span
                    className={`inline-flex rounded-full border px-2 py-0.5 text-xs font-medium ${
                      PASSENGER_STATUS_STYLES[p.status] ??
                      "border-border text-muted-foreground"
                    }`}
                  >
                    {p.status === "CANCELLED" ? "Cancelled" : p.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-5 flex items-center justify-between border-t border-border pt-4">
        <span className="text-sm text-muted-foreground">Total fare</span>
        <span className="text-lg font-bold tabular-nums text-foreground">
          ₹{booking.total_fare}
        </span>
      </div>
    </div>
  );
});
