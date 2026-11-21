"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [tvMode, setTvMode] = useState(false);

  // Close mobile menu on resize to desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return (
    <div className={`min-h-screen bg-background text-text-primary ${tvMode ? "tv-display-mode" : ""}`}>
      {/* Sidebar for Desktop & Mobile Drawer */}
      <Sidebar
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        tvMode={tvMode}
      />

      {/* Main Content Area */}
      <div className={`flex flex-col min-h-screen transition-all duration-300 ${tvMode ? "lg:pl-0" : "lg:pl-64 2xl:pl-72"}`}>
        <Header
          onToggleMobileMenu={() => setMobileMenuOpen(!mobileMenuOpen)}
          tvMode={tvMode}
          onToggleTvMode={() => setTvMode(!tvMode)}
        />
        <main className={`flex-1 overflow-y-auto transition-all ${
          tvMode 
            ? "p-4 sm:p-6 lg:p-10 2xl:p-12 max-w-[2560px] mx-auto w-full" 
            : "p-3 sm:p-5 lg:p-8 2xl:p-10 max-w-[2000px] mx-auto w-full"
        }`}>
          {children}
        </main>
      </div>
    </div>
  );
}
