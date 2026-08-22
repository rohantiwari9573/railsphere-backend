import { useMutation } from "@tanstack/react-query";
import axios from "axios";
import { Search, Ticket } from "lucide-react";
import { useState, type FormEvent } from "react";
import { getBookingByPnr } from "@/api/bookings";
import { BookingDetailCard } from "@/components/booking/BookingDetailCard";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function PnrStatusPage() {
  const [pnr, setPnr] = useState("");
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => getBookingByPnr(pnr.trim()),
    onError: (err) => {
      if (axios.isAxiosError(err) && err.response?.status === 404) {
        setError("No booking found for this PNR.");
      } else {
        setError("Something went wrong. Try again.");
      }
    },
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (pnr.trim().length !== 10) {
      setError("Enter a valid 10-digit PNR.");
      return;
    }
    mutation.mutate();
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
      <PageHeader
        icon={Ticket}
        title="PNR Status"
        subtitle="Check the confirmation status of any booking with its PNR."
      />

      <form onSubmit={handleSubmit} className="mt-5 flex gap-2">
        <Input
          value={pnr}
          onChange={(e) => setPnr(e.target.value.replace(/\D/g, ""))}
          placeholder="10-digit PNR"
          maxLength={10}
          className="font-mono"
        />
        <Button type="submit" disabled={mutation.isPending}>
          <Search className="h-4 w-4" />
          {mutation.isPending ? "Checking…" : "Check"}
        </Button>
      </form>

      {error && (
        <p className="mt-3 text-sm font-medium text-destructive">{error}</p>
      )}

      {mutation.data && (
        <div className="mt-6 animate-in fade-in slide-in-from-bottom-1 duration-300">
          <BookingDetailCard booking={mutation.data} />
        </div>
      )}
    </div>
  );
}
