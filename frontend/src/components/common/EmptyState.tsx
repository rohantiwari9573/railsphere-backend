import type { LucideIcon } from "lucide-react";
import { SearchX } from "lucide-react";

interface Props {
  icon?: LucideIcon;
  title: string;
  message?: string;
}

export function EmptyState({ icon: Icon = SearchX, title, message }: Props) {
  return (
    <div className="flex flex-col items-center rounded-xl border border-dashed border-border bg-card px-6 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted text-muted-foreground">
        <Icon className="h-6 w-6" strokeWidth={1.75} />
      </div>
      <p className="mt-4 text-sm font-medium text-foreground">{title}</p>
      {message && (
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">
          {message}
        </p>
      )}
    </div>
  );
}
