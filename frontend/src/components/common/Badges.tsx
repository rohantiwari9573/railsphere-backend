import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const TRAIN_TYPE_STYLES: Record<string, string> = {
  Raj: "bg-purple-50 text-purple-700 border-purple-200",
  JShtb: "bg-purple-50 text-purple-700 border-purple-200",
  Shtb: "bg-purple-50 text-purple-700 border-purple-200",
  Drnt: "bg-amber-50 text-amber-700 border-amber-200",
  SF: "bg-blue-50 text-blue-700 border-blue-200",
  Exp: "bg-slate-50 text-slate-700 border-slate-200",
  MEMU: "bg-emerald-50 text-emerald-700 border-emerald-200",
  Pass: "bg-slate-50 text-slate-600 border-slate-200",
};

export function TrainTypeBadge({ type }: { type: string }) {
  const style =
    TRAIN_TYPE_STYLES[type] ?? "bg-slate-50 text-slate-700 border-slate-200";
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
