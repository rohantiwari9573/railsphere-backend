import { useQuery } from "@tanstack/react-query";
import { Loader2, MapPin } from "lucide-react";
import { useState } from "react";
import { getStations } from "@/api/stations";
import type { Station } from "@/api/types";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { Input } from "@/components/ui/input";

interface Props {
  label: string;
  placeholder?: string;
  value: Station | null;
  onChange: (station: Station | null) => void;
}

export function StationAutocomplete({
  label,
  placeholder = "Station name or code",
  value,
  onChange,
}: Props) {
  const [query, setQuery] = useState(value?.name ?? "");
  const [isOpen, setIsOpen] = useState(false);
  const debouncedQuery = useDebouncedValue(query, 250);

  const { data, isFetching } = useQuery({
    queryKey: ["station-search", debouncedQuery],
    queryFn: () => getStations({ search: debouncedQuery, limit: 8 }),
    enabled: debouncedQuery.trim().length >= 2,
  });

  function handleSelect(station: Station) {
    onChange(station);
    setQuery(station.name);
    setIsOpen(false);
  }

  function handleInputChange(text: string) {
    setQuery(text);
    setIsOpen(true);
    if (value) {
      onChange(null);
    }
  }

  return (
    <div className="relative">
      <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        {label}
      </label>
      <div className="relative">
        <MapPin
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          strokeWidth={2}
        />
        <Input
          type="text"
          value={query}
          placeholder={placeholder}
          onChange={(e) => handleInputChange(e.target.value)}
          onFocus={() => setIsOpen(true)}
          onBlur={() => setTimeout(() => setIsOpen(false), 150)}
          autoComplete="off"
          autoCorrect="off"
          spellCheck={false}
          className="pl-9"
        />
        {isFetching && (
          <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
        )}
      </div>

      {isOpen && debouncedQuery.trim().length >= 2 && (
        <div className="absolute z-20 mt-1.5 w-full overflow-hidden rounded-lg border border-border bg-popover shadow-lg">
          {!isFetching && data?.items.length === 0 && (
            <div className="px-3 py-3 text-sm text-muted-foreground">
              No stations found
            </div>
          )}
          {!isFetching &&
            data?.items.map((station) => (
              <button
                key={station.id}
                type="button"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => handleSelect(station)}
                className="flex w-full flex-col items-start px-3 py-2 text-left text-sm hover:bg-accent"
              >
                <span className="font-medium text-foreground">
                  {station.name}
                </span>
                <span className="text-xs text-muted-foreground">
                  {station.code}
                  {station.state ? ` · ${station.state}` : ""}
                </span>
              </button>
            ))}
        </div>
      )}
    </div>
  );
}
