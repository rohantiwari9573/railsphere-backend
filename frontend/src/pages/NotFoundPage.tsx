import { TrainFront } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

export function NotFoundPage() {
  return (
    <div className="mx-auto flex min-h-[calc(100vh-8rem)] max-w-md flex-col items-center justify-center px-4 text-center sm:px-6">
      <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
        <TrainFront className="h-6 w-6" strokeWidth={2} />
      </span>
      <h1 className="mt-4 text-xl font-bold text-foreground">
        Page not found
      </h1>
      <p className="mt-2 text-sm text-muted-foreground">
        This track doesn't lead anywhere.
      </p>
      <Button asChild className="mt-6">
        <Link to="/">Back to search</Link>
      </Button>
    </div>
  );
}
