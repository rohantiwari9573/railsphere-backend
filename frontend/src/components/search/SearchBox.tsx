import { ArrowLeftRight, Clock, Search } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { StationAutocomplete } from "@/components/ui/StationAutocomplete";
import { useRecentSearches } from "@/hooks/useRecentSearches";
import type { Station } from "@/api/types";

export function SearchBox() {
  const navigate = useNavigate();
  const { recent, addRecentSearch } = useRecentSearches();
  const [from, setFrom] = useState<Station | null>(null);
  const [to, setTo] = useState<Station | null>(null);
  const [validationError, setValidationError] = useState<string | null>(
    null
  );

  function handleSwap() {
    setFrom(to);
    setTo(from);
  }

  function runSearch(fromStation: Station, toStation: Station) {
    addRecentSearch(fromStation, toStation);
    navigate(`/search?from=${fromStation.id}&to=${toStation.id}`);
  }

  function handleSearch() {
    if (!from || !to) {
      setValidationError("Choose both an origin and destination station.");
      return;
    }
    if (from.id === to.id) {
      setValidationError("Origin and destination must be different.");
      return;
    }
    setValidationError(null);
    runSearch(from, to);
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") {
      handleSearch();
    }
  }

  return (
    <div
      className="rounded-2xl bg-card p-5 text-foreground shadow-2xl shadow-black/10 sm:p-6"
      onKeyDown={handleKeyDown}
    >
      <div className="grid items-end gap-4 sm:grid-cols-[1fr_auto_1fr]">
        <StationAutocomplete label="From" value={from} onChange={setFrom} />

        <Button
          type="button"
          variant="outline"
          size="icon"
          className="mb-0.5 hidden shrink-0 sm:flex"
          onClick={handleSwap}
          aria-label="Swap origin and destination"
        >
          <ArrowLeftRight className="h-4 w-4" />
        </Button>

        <StationAutocomplete label="To" value={to} onChange={setTo} />
      </div>

      <Button
        type="button"
        variant="outline"
        size="sm"
        className="mt-3 w-full sm:hidden"
        onClick={handleSwap}
      >
        <ArrowLeftRight className="h-3.5 w-3.5" />
        Swap
      </Button>

      {validationError && (
        <p className="mt-3 text-sm font-medium text-destructive">
          {validationError}
        </p>
      )}

      <Button onClick={handleSearch} className="mt-4 w-full" size="lg">
        <Search className="h-4 w-4" strokeWidth={2.5} />
        Search trains
      </Button>

      {recent.length > 0 && (
        <div className="mt-4 border-t border-border pt-4">
          <p className="mb-2 flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
            <Clock className="h-3.5 w-3.5" />
            Recent searches
          </p>
          <div className="flex flex-wrap gap-2">
            {recent.map((search) => (
              <button
                key={`${search.from.id}-${search.to.id}-${search.searchedAt}`}
                onClick={() => runSearch(search.from, search.to)}
                className="rounded-full border border-border bg-muted/50 px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:border-primary/30 hover:bg-primary/5"
              >
                {search.from.code} → {search.to.code}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
