"use client";

import Link from "next/link";
import { useState } from "react";
import type { User } from "@/types/user";

export function Navbar({ user }: { user?: User | null }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  async function logout() {
    await fetch("/api/auth/logout", { method: "POST" }).catch(() => null);
    window.location.assign("/login");
  }

  return (
    <header className="glass-effect sticky top-0 z-40">
      <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4">
        <Link href="/dashboard" className="font-bold text-white text-xl">
          📝 Todo App
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          <Link href="/tasks" className="text-white/80 hover:text-white transition-colors">
            Tasks
          </Link>

          {user ? (
            <div className="flex items-center gap-4">
              <span className="text-white/80 text-sm">
                {user.displayName || user.email}
              </span>
              <button
                type="button"
                onClick={() => void logout()}
                className="bg-white/20 backdrop-blur-sm text-white px-4 py-2 rounded-md hover:bg-white/30 transition-colors border border-white/30"
              >
                Logout
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="bg-white/20 backdrop-blur-sm text-white px-4 py-2 rounded-md hover:bg-white/30 transition-colors border border-white/30"
            >
              Login
            </Link>
          )}
        </nav>

        <button
          type="button"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-label={isMenuOpen ? "Close menu" : "Open menu"}
          className="md:hidden p-2 rounded-md text-white hover:bg-white/20 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {isMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {isMenuOpen && (
        <div className="md:hidden glass-effect border-t border-white/20">
          <nav className="px-4 py-4 space-y-4">
            <Link 
              href="/tasks" 
              className="block text-white/80 hover:text-white transition-colors"
              onClick={() => setIsMenuOpen(false)}
            >
              Tasks
            </Link>
            
            {user ? (
              <div className="space-y-4">
                <div className="text-sm text-white/80">
                  {user.displayName || user.email}
                </div>
                <button
                  type="button"
                  onClick={() => void logout()}
                  className="block w-full text-left bg-white/20 text-white px-4 py-2 rounded-md hover:bg-white/30 transition-colors border border-white/30"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                href="/login"
                className="block bg-white/20 text-white px-4 py-2 rounded-md hover:bg-white/30 transition-colors border border-white/30"
                onClick={() => setIsMenuOpen(false)}
              >
                Login
              </Link>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
