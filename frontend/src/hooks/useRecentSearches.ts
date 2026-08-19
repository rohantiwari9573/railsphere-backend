import { useState } from "react";
import type { Station } from "@/api/types";

const STORAGE_KEY = "railsphere_recent_searches";
const MAX_RECENT = 5;

export interface RecentSearch {
  from: Station;
  to: Station;
  searchedAt: number;
}

function load(): RecentSearch[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function useRecentSearches() {
  const [recent, setRecent] = useState<RecentSearch[]>(load);

  function addRecentSearch(from: Station, to: Station) {
    const next = [
      { from, to, searchedAt: Date.now() },
      ...recent.filter(
        (r) => !(r.from.id === from.id && r.to.id === to.id)
      ),
    ].slice(0, MAX_RECENT);

    setRecent(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  }

  return { recent, addRecentSearch };
}
