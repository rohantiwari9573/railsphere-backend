import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const TRAIN_TYPE_STYLES: Record<string, string> = {
  Raj: "bg-purple-50 text-purple-700 border-purple-200 dark:border-purple-500/30 dark:bg-purple-500/10 dark:text-purple-300",
  JShtb:
    "bg-purple-50 text-purple-700 border-purple-200 dark:border-purple-500/30 dark:bg-purple-500/10 dark:text-purple-300",
  Shtb: "bg-purple-50 text-purple-700 border-purple-200 dark:border-purple-500/30 dark:bg-purple-500/10 dark:text-purple-300",
  Drnt: "bg-amber-50 text-amber-700 border-amber-200 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300",
  SF: "bg-blue-50 text-blue-700 border-blue-200 dark:border-blue-500/30 dark:bg-blue-500/10 dark:text-blue-300",
  Exp: "bg-slate-50 text-slate-700 border-slate-200 dark:border-slate-500/30 dark:bg-slate-500/10 dark:text-slate-300",
  MEMU: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300",
  Pass: "bg-slate-50 text-slate-600 border-slate-200 dark:border-slate-500/30 dark:bg-slate-500/10 dark:text-slate-400",
};

export function TrainTypeBadge({ type }: { type: string }) {
  const style =
    TRAIN_TYPE_STYLES[type] ??
    "bg-slate-50 text-slate-700 border-slate-200 dark:border-slate-500/30 dark:bg-slate-500/10 dark:text-slate-300";
  return (
    <Badge
      variant="outline"
      className={cn("font-medium", style)}
    >
      {type}
    </Badge>
  );
}

export function StationCodeBadge({ code }: { code: string }) {
  return (
    <Badge
      variant="outline"
      className="border-primary/20 bg-primary/5 font-mono text-[11px] font-semibold text-primary"
    >
      {code}
    </Badge>
  );
}

const BOOKING_STATUS_STYLES: Record<string, string> = {
  CONFIRMED:
    "bg-emerald-50 text-emerald-700 border-emerald-200 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300",
  PARTIALLY_CONFIRMED:
    "bg-amber-50 text-amber-700 border-amber-200 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300",
  WAITLISTED:
    "bg-amber-50 text-amber-700 border-amber-200 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300",
  PENDING_PAYMENT:
    "bg-blue-50 text-blue-700 border-blue-200 dark:border-blue-500/30 dark:bg-blue-500/10 dark:text-blue-300",
  CANCELLED:
    "bg-slate-50 text-slate-600 border-slate-200 dark:border-slate-500/30 dark:bg-slate-500/10 dark:text-slate-400",
};

const BOOKING_STATUS_LABEL: Record<string, string> = {
  CONFIRMED: "Confirmed",
  PARTIALLY_CONFIRMED: "Partially Confirmed",
  WAITLISTED: "Waitlisted",
  PENDING_PAYMENT: "Payment Pending",
  CANCELLED: "Cancelled",
};

export function BookingStatusBadge({ status }: { status: string }) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "font-medium",
        BOOKING_STATUS_STYLES[status] ??
          "bg-slate-50 text-slate-700 border-slate-200"
      )}
    >
      {BOOKING_STATUS_LABEL[status] ?? status}
    </Badge>
  );
}
