import { useMutation, useQuery } from "@tanstack/react-query";
import axios from "axios";
import { ArrowRight, Plus, Trash2, TrainFront } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { createBooking, getAvailability, getSeatMap } from "@/api/bookings";
import { getStation } from "@/api/stations";
import { getTrain } from "@/api/trains";
import type { PassengerInput } from "@/api/types";
import { TrainTypeBadge } from "@/components/common/Badges";
import { SeatMap } from "@/components/booking/SeatMap";
import { ErrorState } from "@/components/common/ErrorState";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/context/AuthContext";
import { cn } from "@/lib/utils";

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function tomorrowIso(): string {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().slice(0, 10);
}

function maxDateIso(): string {
  const d = new Date();
  d.setDate(d.getDate() + 120);
  return d.toISOString().slice(0, 10);
}

const GENDERS: { value: PassengerInput["gender"]; label: string }[] = [
  { value: "M", label: "Male" },
  { value: "F", label: "Female" },
  { value: "O", label: "Other" },
];

export function BookingPage() {
  const { trainId, routeId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const trainIdNum = Number(trainId);
  const routeIdNum = Number(routeId);
  const sourceId = Number(searchParams.get("from"));
  const destinationId = Number(searchParams.get("to"));

  const [journeyDate, setJourneyDate] = useState(tomorrowIso());
  const [travelClass, setTravelClass] = useState<string | null>(null);
  const [showSeatMap, setShowSeatMap] = useState(false);
  const [passengers, setPassengers] = useState<PassengerInput[]>([
    { name: "", age: 0, gender: "M" },
  ]);
  const [formError, setFormError] = useState<string | null>(null);

  const { data: train } = useQuery({
    queryKey: ["train", trainIdNum],
    queryFn: () => getTrain(trainIdNum),
    enabled: Boolean(trainIdNum),
  });

  const { data: source } = useQuery({
    queryKey: ["station", sourceId],
    queryFn: () => getStation(sourceId),
    enabled: Boolean(sourceId),
  });

  const { data: destination } = useQuery({
    queryKey: ["station", destinationId],
    queryFn: () => getStation(destinationId),
    enabled: Boolean(destinationId),
  });

  const {
    data: availability,
    isLoading: isAvailabilityLoading,
    isError: isAvailabilityError,
  } = useQuery({
    queryKey: [
      "availability",
      trainIdNum,
      journeyDate,
      routeIdNum,
      sourceId,
      destinationId,
    ],
    queryFn: () =>
      getAvailability(trainIdNum, journeyDate, {
        routeId: routeIdNum,
        sourceStationId: sourceId,
        destinationStationId: destinationId,
      }),
    enabled: Boolean(trainIdNum && journeyDate),
  });

  useEffect(() => {
    if (!availability || availability.length === 0) return;
    if (!availability.some((a) => a.class_code === travelClass)) {
      setTravelClass(availability[0].class_code);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [availability]);

  const { data: seatMap } = useQuery({
    queryKey: ["seat-map", trainIdNum, journeyDate, travelClass],
    queryFn: () => getSeatMap(trainIdNum, journeyDate, travelClass as string),
    enabled: Boolean(trainIdNum && journeyDate && travelClass && showSeatMap),
  });

  const selected = availability?.find((a) => a.class_code === travelClass);
  const totalFare = selected ? Number(selected.fare) * passengers.length : 0;

  const createMutation = useMutation({
    mutationFn: () =>
      createBooking({
        train_id: trainIdNum,
        route_id: routeIdNum,
        source_station_id: sourceId,
        destination_station_id: destinationId,
        journey_date: journeyDate,
        travel_class: travelClass as string,
        passengers,
      }),
    onSuccess: (booking) => navigate(`/payment/${booking.id}`),
    onError: (err) => {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setFormError(err.response.data.detail);
      } else {
        setFormError("Something went wrong. Please try again.");
      }
    },
  });

  function updatePassenger(index: number, patch: Partial<PassengerInput>) {
    setPassengers((prev) =>
      prev.map((p, i) => (i === index ? { ...p, ...patch } : p))
    );
  }

  function addPassenger() {
    if (passengers.length >= 6) return;
    setPassengers((prev) => [...prev, { name: "", age: 0, gender: "M" }]);
  }

  function removePassenger(index: number) {
    if (passengers.length <= 1) return;
    setPassengers((prev) => prev.filter((_, i) => i !== index));
  }

  function handleSubmit() {
    setFormError(null);
    if (!travelClass) return;
    if (passengers.some((p) => !p.name.trim() || p.age < 1 || p.age > 120)) {
      setFormError("Enter a valid name and age (1-120) for every passenger.");
      return;
    }
    createMutation.mutate();
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-md px-4 py-16 text-center sm:px-6">
        <p className="text-sm font-medium text-foreground">
          Log in to book tickets.
        </p>
        <Button asChild className="mt-4">
          <Link to="/login">Log in</Link>
        </Button>
      </div>
    );
  }

  if (!sourceId || !destinationId || !trainIdNum || !routeIdNum) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6">
        <ErrorState message="Missing journey details. Go back and search again." />
      </div>
    );
  }

  const canSubmit =
    Boolean(travelClass) &&
    (selected ? selected.available_seats > 0 || true : false) &&
    !createMutation.isPending;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <PageHeader
        icon={TrainFront}
        title={train ? train.train_name : "Book tickets"}
        subtitle={train ? `#${train.train_number}` : undefined}
        action={train ? <TrainTypeBadge type={train.train_type} /> : undefined}
      />

      <div className="mt-4 flex items-center gap-3 rounded-xl border border-border bg-card p-4">
        <div className="flex-1 text-center">
          <p className="text-sm font-semibold text-foreground">
            {source?.name ?? "…"}
          </p>
          <p className="text-xs text-muted-foreground">{source?.code}</p>
        </div>
        <ArrowRight className="h-4 w-4 shrink-0 text-muted-foreground" />
        <div className="flex-1 text-center">
          <p className="text-sm font-semibold text-foreground">
            {destination?.name ?? "…"}
          </p>
          <p className="text-xs text-muted-foreground">{destination?.code}</p>
        </div>
      </div>

      <div className="mt-6">
        <label className="mb-1.5 block text-sm font-medium text-foreground">
          Journey date
        </label>
        <Input
          type="date"
          value={journeyDate}
          min={todayIso()}
          max={maxDateIso()}
          onChange={(e) => {
            setJourneyDate(e.target.value);
            setShowSeatMap(false);
          }}
          className="w-48"
        />
      </div>

      <div className="mt-6">
        <p className="mb-2 text-sm font-medium text-foreground">Class</p>
        {isAvailabilityLoading && (
          <p className="text-sm text-muted-foreground">Checking availability…</p>
        )}
        {isAvailabilityError && (
          <ErrorState message="Couldn't check seat availability." />
        )}
        {availability && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {availability.map((cls) => (
              <button
                key={cls.class_code}
                type="button"
                onClick={() => {
                  setTravelClass(cls.class_code);
                  setShowSeatMap(false);
                }}
                className={cn(
                  "rounded-xl border p-4 text-left transition-all",
                  travelClass === cls.class_code
                    ? "border-primary bg-primary/5 shadow-sm"
                    : "border-border bg-card hover:border-primary/30"
                )}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-foreground">
                    {cls.class_name}
                  </span>
                  <span className="text-xs font-medium text-muted-foreground">
                    {cls.class_code}
                  </span>
                </div>
                <div className="mt-2 flex items-baseline justify-between">
                  <span className="text-lg font-bold tabular-nums text-foreground">
                    ₹{cls.fare}
                  </span>
                  <span
                    className={cn(
                      "text-xs font-medium tabular-nums",
                      cls.available_seats > 0
                        ? "text-emerald-600 dark:text-emerald-400"
                        : "text-amber-600 dark:text-amber-400"
                    )}
                  >
                    {cls.status_label}
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}

        {travelClass && (
          <button
            type="button"
            onClick={() => setShowSeatMap((v) => !v)}
            className="mt-3 text-sm font-medium text-primary hover:underline"
          >
            {showSeatMap ? "Hide seat map" : "View live seat map"}
          </button>
        )}
      </div>

      {showSeatMap && seatMap && (
        <div className="mt-4">
          <SeatMap seatMap={seatMap} />
        </div>
      )}

      <div className="mt-6">
        <div className="flex items-center justify-between">
          <p className="text-sm font-medium text-foreground">
            Passengers ({passengers.length}/6)
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={addPassenger}
            disabled={passengers.length >= 6}
          >
            <Plus className="h-3.5 w-3.5" />
            Add
          </Button>
        </div>

        <div className="mt-3 space-y-3">
          {passengers.map((passenger, i) => (
            <div
              key={i}
              className="flex flex-wrap items-end gap-3 rounded-xl border border-border bg-card p-3"
            >
              <div className="min-w-[10rem] flex-1">
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Name
                </label>
                <Input
                  value={passenger.name}
                  onChange={(e) =>
                    updatePassenger(i, { name: e.target.value })
                  }
                  placeholder="Full name"
                />
              </div>
              <div className="w-20">
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Age
                </label>
                <Input
                  type="number"
                  min={1}
                  max={120}
                  value={passenger.age || ""}
                  onChange={(e) =>
                    updatePassenger(i, { age: Number(e.target.value) })
                  }
                />
              </div>
              <div className="w-28">
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Gender
                </label>
                <select
                  value={passenger.gender}
                  onChange={(e) =>
                    updatePassenger(i, {
                      gender: e.target.value as PassengerInput["gender"],
                    })
                  }
                  className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 dark:bg-input/30"
                >
                  {GENDERS.map((g) => (
                    <option key={g.value} value={g.value}>
                      {g.label}
                    </option>
                  ))}
                </select>
              </div>
              {passengers.length > 1 && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removePassenger(i)}
                  aria-label="Remove passenger"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 flex items-center justify-between rounded-xl border border-border bg-card p-4">
        <div>
          <p className="text-xs text-muted-foreground">Total fare</p>
          <p className="text-xl font-bold tabular-nums text-foreground">
            ₹{totalFare.toFixed(0)}
          </p>
        </div>
        <Button
          size="lg"
          onClick={handleSubmit}
          disabled={!canSubmit}
        >
          {createMutation.isPending ? "Booking…" : "Proceed to pay"}
        </Button>
      </div>

      {formError && (
        <p className="mt-3 text-sm font-medium text-destructive">
          {formError}
        </p>
      )}
    </div>
  );
}
