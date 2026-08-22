import {
  BarChart3,
  MapPin,
  Menu,
  Route as RouteIcon,
  Search,
  TrainFront,
} from "lucide-react";
import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/common/ThemeToggle";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

const NAV_ITEMS = [
  { to: "/", label: "Search", icon: Search, end: true },
  { to: "/stations", label: "Stations", icon: MapPin, end: false },
  { to: "/trains", label: "Trains", icon: TrainFront, end: false },
  { to: "/routes", label: "Routes", icon: RouteIcon, end: false },
  { to: "/analytics", label: "Analytics", icon: BarChart3, end: false },
];

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `text-sm font-medium transition-colors ${
    isActive ? "text-primary" : "text-muted-foreground hover:text-foreground"
  }`;

function Logo() {
  return (
    <Link to="/" className="flex items-center gap-2">
      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm shadow-primary/30">
        <TrainFront className="h-4.5 w-4.5" strokeWidth={2.25} />
      </span>
      <span className="text-lg font-bold tracking-tight text-foreground">
        RailSphere
      </span>
    </Link>
  );
}

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isSheetOpen, setIsSheetOpen] = useState(false);

  function handleLogout() {
    logout();
    setIsSheetOpen(false);
    navigate("/");
  }

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-background/85 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3.5 sm:px-6">
        <Logo />

        <nav className="hidden items-center gap-7 sm:flex">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={navLinkClass}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-3 sm:flex">
          {user ? (
            <>
              <span className="text-sm text-muted-foreground">
                {user.full_name}
              </span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Log out
              </Button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm font-medium text-muted-foreground hover:text-foreground"
              >
                Log in
              </Link>
              <Button size="sm" asChild>
                <Link to="/register">Sign up</Link>
              </Button>
            </>
          )}
          <ThemeToggle />
        </div>

        <div className="flex items-center gap-1 sm:hidden">
          <ThemeToggle />
          <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-72">
            <SheetHeader>
              <SheetTitle>
                <Logo />
              </SheetTitle>
            </SheetHeader>
            <nav className="flex flex-col gap-1 px-4">
              {NAV_ITEMS.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.end}
                  onClick={() => setIsSheetOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "text-foreground hover:bg-accent"
                    }`
                  }
                >
                  <item.icon className="h-4 w-4" strokeWidth={2} />
                  {item.label}
                </NavLink>
              ))}
            </nav>
            <div className="mt-auto border-t border-border px-4 py-4">
              {user ? (
                <div className="space-y-3">
                  <p className="text-sm text-muted-foreground">
                    Signed in as{" "}
                    <span className="font-medium text-foreground">
                      {user.full_name}
                    </span>
                  </p>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={handleLogout}
                  >
                    Log out
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  <Button asChild className="w-full">
                    <Link to="/register" onClick={() => setIsSheetOpen(false)}>
                      Sign up
                    </Link>
                  </Button>
                  <Button
                    asChild
                    variant="outline"
                    className="w-full"
                  >
                    <Link to="/login" onClick={() => setIsSheetOpen(false)}>
                      Log in
                    </Link>
                  </Button>
                </div>
              )}
            </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
