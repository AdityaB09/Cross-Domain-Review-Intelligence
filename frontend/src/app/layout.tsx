// frontend/src/app/layout.tsx
import "./styles/globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "CDRI",
  description: "Cross-Domain Review Intelligence",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        <header className="border-b bg-white">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
            <div className="text-lg font-semibold tracking-tight text-gray-900">
              CDRI
              <span className="ml-2 text-xs font-normal text-gray-500">
                Review Intelligence
              </span>
            </div>
            <nav className="flex gap-4 text-sm font-medium text-gray-700">
              <a className="hover:text-black" href="/">Home</a>
              <a className="hover:text-black" href="/dashboard">Dashboard</a>
              <a className="hover:text-black" href="/search">Search</a>
              <a className="hover:text-black" href="/explain">Explain</a>
              <a className="hover:text-black" href="/eda">Insights</a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
