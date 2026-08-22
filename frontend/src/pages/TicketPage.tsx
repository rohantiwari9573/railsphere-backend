import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import jsPDF from "jspdf";
import { Download, Ticket } from "lucide-react";
import { useRef } from "react";
import { useParams } from "react-router-dom";
import { cancelBooking, getBooking } from "@/api/bookings";
import type { Booking } from "@/api/types";
import { BookingDetailCard } from "@/components/booking/BookingDetailCard";
import { DetailSkeleton } from "@/components/common/LoadingSkeleton";
import { ErrorState } from "@/components/common/ErrorState";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";

function downloadTicket(booking: Booking, qrCanvas: HTMLCanvasElement | null) {
  const doc = new jsPDF();

  doc.setFontSize(18);
  doc.setFont("helvetica", "bold");
  doc.text("RailSphere e-Ticket", 14, 18);

  doc.setFontSize(11);
  doc.setFont("helvetica", "normal");
  doc.text(`PNR: ${booking.pnr}`, 14, 30);
  doc.text(`Status: ${booking.status}`, 14, 37);
  doc.text(`Train: ${booking.train_name} (#${booking.train_number})`, 14, 44);
  doc.text(
    `Route: ${booking.source_station_name} -> ${booking.destination_station_name}`,
    14,
    51
  );
  doc.text(
    `Date: ${booking.journey_date}   Class: ${booking.class_name}`,
    14,
    58
  );
  doc.text(`Total fare: Rs ${booking.total_fare}`, 14, 65);

  if (qrCanvas) {
    doc.addImage(qrCanvas.toDataURL("image/png"), "PNG", 155, 12, 40, 40);
  }

  let y = 82;
  doc.setFont("helvetica", "bold");
  doc.text("Passenger", 14, y);
  doc.text("Age/Gender", 90, y);
  doc.text("Seat", 135, y);
  doc.text("Status", 165, y);
  doc.setFont("helvetica", "normal");
  y += 3;
  doc.line(14, y, 196, y);
  y += 7;

  for (const p of booking.passengers) {
    doc.text(p.name, 14, y);
    doc.text(`${p.age}/${p.gender}`, 90, y);
    doc.text(p.seat_number ? `${p.coach}-${p.seat_number}` : "-", 135, y);
    doc.text(p.status, 165, y);
    y += 7;
  }

  doc.setFontSize(9);
  doc.setTextColor(120);
  doc.text(
    "Simulated ticket for a portfolio project. Not valid for travel.",
    14,
    285
  );

  doc.save(`RailSphere-${booking.pnr}.pdf`);
}

export function TicketPage() {
  const { bookingId } = useParams();
  const bookingIdNum = Number(bookingId);
  const qrRef = useRef<HTMLCanvasElement>(null);
  const queryClient = useQueryClient();

  const {
    data: booking,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["booking", bookingIdNum],
    queryFn: () => getBooking(bookingIdNum),
    enabled: Boolean(bookingIdNum),
  });

  const cancelMutation = useMutation({
    mutationFn: () => cancelBooking(bookingIdNum),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["booking", bookingIdNum] });
      queryClient.invalidateQueries({ queryKey: ["my-bookings"] });
    },
  });

  if (isLoading) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
        <DetailSkeleton />
      </div>
    );
  }

  if (isError || !booking) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
        <ErrorState message="Couldn't load this ticket." />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
      <PageHeader icon={Ticket} title="Your e-Ticket" />

      <div className="mt-5">
        <BookingDetailCard booking={booking} ref={qrRef} />
      </div>

      {cancelMutation.data && (
        <div className="mt-4 rounded-xl border border-border bg-card p-4 text-sm text-muted-foreground">
          Refund: ₹{cancelMutation.data.refund_amount} · Cancellation charge: ₹
          {cancelMutation.data.cancellation_charge}
        </div>
      )}

      <div className="mt-5 flex flex-wrap gap-3">
        <Button
          variant="outline"
          onClick={() => downloadTicket(booking, qrRef.current)}
        >
          <Download className="h-4 w-4" />
          Download e-ticket
        </Button>
        {booking.status !== "CANCELLED" && (
          <Button
            variant="destructive"
            disabled={cancelMutation.isPending}
            onClick={() => {
              if (window.confirm("Cancel this booking?")) {
                cancelMutation.mutate();
              }
            }}
          >
            {cancelMutation.isPending ? "Cancelling…" : "Cancel booking"}
          </Button>
        )}
      </div>
    </div>
  );
}
