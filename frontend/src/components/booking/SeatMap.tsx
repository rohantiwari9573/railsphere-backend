import { useState } from "react";
import type { SeatMapResponse } from "@/api/types";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { cn } from "@/lib/utils";

const BERTH_LABEL: Record<string, string> = {
  LOWER: "Lower",
  MIDDLE: "Middle",
  UPPER: "Upper",
  SIDE_LOWER: "Side Lower",
  SIDE_UPPER: "Side Upper",
};

export function SeatMap({ seatMap }: { seatMap: SeatMapResponse }) {
  const [activeCoach, setActiveCoach] = useState(seatMap.coaches[0]?.coach);

  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-semibold text-foreground">
          {seatMap.class_name} occupancy
        </p>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm border border-primary/40 bg-primary/10" />
            Available
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm border border-border bg-muted-foreground/40" />
            Booked
          </span>
        </div>
      </div>

      <Tabs
        value={activeCoach}
        onValueChange={setActiveCoach}
        className="mt-3"
      >
        <TabsList className="h-auto flex-wrap justify-start gap-1 bg-transparent p-0">
          {seatMap.coaches.map((coach) => (
            <TabsTrigger
              key={coach.coach}
              value={coach.coach}
              className="rounded-lg border border-border"
            >
              {coach.coach}
            </TabsTrigger>
          ))}
        </TabsList>

        {seatMap.coaches.map((coach) => (
          <TabsContent key={coach.coach} value={coach.coach} className="mt-3">
            <div className="grid grid-cols-6 gap-1.5 sm:grid-cols-8 md:grid-cols-10">
              {coach.seats.map((seat, i) => (
                <div
                  key={seat.seat_number}
                  title={
                    seat.berth_type
                      ? `${coach.coach} · Seat ${seat.seat_number} · ${BERTH_LABEL[seat.berth_type] ?? seat.berth_type}${seat.is_booked ? " · Booked" : " · Available"}`
                      : `${coach.coach} · Seat ${seat.seat_number}${seat.is_booked ? " · Booked" : " · Available"}`
                  }
                  className={cn(
                    "animate-in fade-in zoom-in-95 fill-mode-both flex aspect-square items-center justify-center rounded-md border text-[10px] font-medium tabular-nums duration-200",
                    seat.is_booked
                      ? "border-border bg-muted-foreground/40 text-muted-foreground/70 line-through"
                      : "border-primary/30 bg-primary/10 text-primary"
                  )}
                  style={{ animationDelay: `${Math.min(i * 4, 250)}ms` }}
                >
                  {seat.seat_number}
                </div>
              ))}
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
