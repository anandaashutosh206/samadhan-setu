"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useTheme } from "next-themes";
import { Bell, Moon, Sun, MapPinned } from "lucide-react";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/Button";

export function NavBar() {
  const { user, isHydrated, hydrate, logout } = useAuthStore();
  const { theme, setTheme } = useTheme();

  useEffect(() => {
    hydrate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <header className="sticky top-0 z-40 border-b border-border-light/60 bg-surface-light/70 backdrop-blur-lg dark:border-border-dark/60 dark:bg-surface-dark/70">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2 font-sora text-lg font-bold">
          <MapPinned className="h-5 w-5 text-primary" />
          Samadhan Setu
        </Link>

        <nav className="hidden items-center gap-6 text-sm font-medium md:flex">
          <Link href="/challenges" className="hover:text-primary">Challenges</Link>
          <Link href="/universities" className="hover:text-primary">Universities</Link>
          <Link href="/industries" className="hover:text-primary">Industries</Link>
          <Link href="/analytics" className="hover:text-primary">Analytics</Link>
        </nav>

        <div className="flex items-center gap-2">
          <button
            aria-label="Toggle theme"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="rounded-lg p-2 hover:bg-black/5 dark:hover:bg-white/10"
          >
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>

          {isHydrated && user ? (
            <>
              <Link href="/notifications" aria-label="Notifications" className="rounded-lg p-2 hover:bg-black/5 dark:hover:bg-white/10">
                <Bell className="h-4 w-4" />
              </Link>
              <span className="hidden text-sm text-muted sm:inline">{user.name}</span>
              <Button size="sm" variant="ghost" onClick={logout}>
                Log out
              </Button>
            </>
          ) : isHydrated ? (
            <>
              <Link href="/login">
                <Button size="sm" variant="ghost">Log in</Button>
              </Link>
              <Link href="/register">
                <Button size="sm">Sign up</Button>
              </Link>
            </>
          ) : null}
        </div>
      </div>
    </header>
  );
}
