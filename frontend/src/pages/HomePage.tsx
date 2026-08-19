import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  ArrowRight,
  BarChart3,
  MapPin,
  Route as RouteIcon,
  Search,
  Sparkles,
  TrainFront,
  Zap,
} from "lucide-react";
import { Link } from "react-router-dom";
import { getNetworkOverview } from "@/api/analytics";
import { AnimatedCounter } from "@/components/common/AnimatedCounter";
import { SearchBox } from "@/components/search/SearchBox";
import { Button } from "@/components/ui/button";

function StatCard({
  icon: Icon,
  label,
  value,
  delay,
}: {
  icon: typeof MapPin;
  label: string;
  value: number;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4, delay }}
      className="group rounded-2xl border border-border bg-card px-6 py-6 text-center shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
    >
      <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary/15">
        <Icon className="h-5 w-5" strokeWidth={2} />
      </div>
      <p className="mt-3 text-3xl font-bold tracking-tight text-foreground">
        <AnimatedCounter value={value} />
      </p>
      <p className="mt-1 text-sm text-muted-foreground">{label}</p>
    </motion.div>
  );
}

const EXPLORE_SECTIONS = [
  {
    to: "/stations",
    icon: MapPin,
    title: "Stations",
    description:
      "Browse ~9,000 stations across every zone, searchable by name, code, or city.",
  },
  {
    to: "/trains",
    icon: TrainFront,
    title: "Trains",
    description:
      "~5,200 trains — Express, Superfast, Rajdhani, Passenger, and more.",
  },
  {
    to: "/routes",
    icon: RouteIcon,
    title: "Routes",
    description:
      "Full station-by-station sequences for ~5,200 routes, from 2-stop shuttles to the 689-stop Vivek Express.",
  },
];

const FEATURES = [
  {
    icon: Zap,
    title: "Live, real dataset",
    description:
      "Every result comes from a real relational database, not mock data — ~9,000 stations, ~5,200 trains, 416,000+ route-station records.",
  },
  {
    icon: Search,
    title: "Actual pathfinding",
    description:
      "Journey search walks real route sequences to find trains that genuinely pass through your origin and destination, in order.",
  },
  {
    icon: BarChart3,
    title: "Real network analytics",
    description:
      "Most-connected stations, longest routes, train-type distribution — computed live from the database, never fabricated.",
  },
];

export function HomePage() {
  const { data: overview } = useQuery({
    queryKey: ["network-overview"],
    queryFn: getNetworkOverview,
  });

  return (
    <div>
      <section className="rail-track-pattern relative overflow-hidden bg-gradient-to-br from-brand-900 via-brand-700 to-brand-600 px-4 py-20 text-white sm:px-6 sm:py-28">
        <div className="relative mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-3.5 py-1.5 text-xs font-medium text-brand-50 ring-1 ring-inset ring-white/20">
            <Sparkles className="h-3.5 w-3.5" />
            Real railway dataset, live database
          </span>
          <h1 className="mt-5 text-4xl font-bold tracking-tight sm:text-5xl">
            Explore the railway network
          </h1>
          <p className="mt-3 text-base text-brand-100 sm:text-lg">
            Search real routes and stations across the full network below.
          </p>
        </div>

        <div className="relative mx-auto mt-10 max-w-2xl">
          <SearchBox />
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-4 py-14 sm:px-6">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <StatCard
            icon={MapPin}
            label="Stations"
            value={overview?.total_stations ?? 0}
            delay={0}
          />
          <StatCard
            icon={TrainFront}
            label="Trains"
            value={overview?.total_trains ?? 0}
            delay={0.05}
          />
          <StatCard
            icon={RouteIcon}
            label="Routes"
            value={overview?.total_routes ?? 0}
            delay={0.1}
          />
          <StatCard
            icon={BarChart3}
            label="Route-Station links"
            value={overview?.total_route_stations ?? 0}
            delay={0.15}
          />
        </div>
      </section>

      <section className="border-t border-border bg-card px-4 py-16 sm:px-6">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-center text-2xl font-bold tracking-tight text-foreground">
            Explore the dataset
          </h2>
          <p className="mx-auto mt-2 max-w-xl text-center text-sm text-muted-foreground">
            Every section below is backed by real, queryable data.
          </p>

          <div className="mt-10 grid grid-cols-1 gap-5 sm:grid-cols-3">
            {EXPLORE_SECTIONS.map((section, i) => (
              <motion.div
                key={section.to}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
              >
                <Link
                  to={section.to}
                  className="group flex h-full flex-col rounded-2xl border border-border bg-background p-6 transition-all hover:-translate-y-1 hover:border-primary/30 hover:shadow-md"
                >
                  <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <section.icon className="h-5 w-5" strokeWidth={2} />
                  </div>
                  <h3 className="mt-4 text-base font-semibold text-foreground">
                    {section.title}
                  </h3>
                  <p className="mt-1.5 flex-1 text-sm leading-relaxed text-muted-foreground">
                    {section.description}
                  </p>
                  <span className="mt-4 flex items-center gap-1 text-sm font-medium text-primary">
                    Explore
                    <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
                  </span>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-4 py-16 sm:px-6">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-center text-2xl font-bold tracking-tight text-foreground">
            Not a demo with fake data
          </h2>
          <p className="mx-auto mt-2 max-w-xl text-center text-sm text-muted-foreground">
            Every number and every search result on this page comes from a
            production PostgreSQL database.
          </p>

          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-3">
            {FEATURES.map((feature) => (
              <div key={feature.title} className="text-center sm:text-left">
                <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary sm:mx-0">
                  <feature.icon className="h-5 w-5" strokeWidth={2} />
                </div>
                <h3 className="mt-4 text-sm font-semibold text-foreground">
                  {feature.title}
                </h3>
                <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-10 flex justify-center">
            <Button asChild variant="outline">
              <Link to="/analytics">
                <BarChart3 className="h-4 w-4" />
                View full network analytics
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
