import { TrainFront } from "lucide-react";
import { Link } from "react-router-dom";

const EXPLORE_LINKS = [
  { to: "/search", label: "Search trains" },
  { to: "/pnr-status", label: "PNR status" },
  { to: "/my-bookings", label: "My bookings" },
];

const PROJECT_LINKS = [
  {
    href: "https://github.com/rohantiwari9573/railsphere-backend",
    label: "Source code",
  },
  {
    href: `${import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000"}/docs`,
    label: "API docs",
  },
];

export function Footer() {
  return (
    <footer className="border-t border-border bg-background">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <div className="flex flex-col justify-between gap-6 sm:flex-row">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <TrainFront className="h-3.5 w-3.5" strokeWidth={2.25} />
              </span>
              <span className="font-bold text-foreground">RailSphere</span>
            </div>
            <p className="mt-3 max-w-sm text-sm text-muted-foreground">
              A railway data explorer built on a real dataset of ~9,000
              stations, ~5,200 trains, and 416,000+ route-station records.
            </p>
          </div>

          <div className="flex gap-12">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Explore
              </p>
              <ul className="mt-3 space-y-2">
                {EXPLORE_LINKS.map((link) => (
                  <li key={link.to}>
                    <Link
                      to={link.to}
                      className="text-sm text-muted-foreground hover:text-primary"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Project
              </p>
              <ul className="mt-3 space-y-2">
                {PROJECT_LINKS.map((link) => (
                  <li key={link.href}>
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noreferrer"
                      className="text-sm text-muted-foreground hover:text-primary"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <p className="mt-8 border-t border-border pt-6 text-sm text-muted-foreground">
          Built by{" "}
          <a
            href="https://github.com/rohantiwari9573"
            target="_blank"
            rel="noreferrer"
            className="font-medium text-primary hover:underline"
          >
            Rohan Tiwari
          </a>
        </p>
      </div>
    </footer>
  );
}
