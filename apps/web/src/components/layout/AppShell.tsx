"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  FileText,
  MessageSquare,
  GraduationCap,
  FolderOpen,
  Sparkles,
  UploadCloud,
  Layers,
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { api } from "@/lib/api";

interface AppShellProps {
  children: React.ReactNode;
  onOpenUpload?: () => void;
}

export function AppShell({ children, onOpenUpload }: AppShellProps) {
  const pathname = usePathname();
  const [health, setHealth] = useState<{ status: string; ai_provider: string } | null>(null);

  useEffect(() => {
    api.getHealth()
      .then(res => setHealth(res))
      .catch(() => setHealth({ status: "disconnected", ai_provider: "mock" }));
  }, []);

  const navItems = [
    { label: "Document Library", href: "/", icon: BookOpen },
    { label: "AI Document Chat", href: "/chat", icon: MessageSquare },
    { label: "Study & Research", href: "/study", icon: GraduationCap },
  ];

  return (
    <div className="flex h-screen w-full bg-slate-50 text-slate-900 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-200 bg-white flex flex-col justify-between shrink-0">
        <div>
          {/* Logo */}
          <div className="h-16 px-6 flex items-center gap-3 border-b border-slate-100">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-indigo-100">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight text-slate-900">ReadFlow</span>
              <span className="text-[10px] block font-semibold uppercase tracking-wider text-indigo-600 -mt-1">
                Document AI
              </span>
            </div>
          </div>

          {/* Primary Nav */}
          <div className="p-4 space-y-1">
            <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-3 mb-2">
              Workspace
            </div>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (item.href !== "/" && pathname?.startsWith(item.href));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? "bg-indigo-50 text-indigo-700 font-semibold shadow-sm"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? "text-indigo-600" : "text-slate-400"}`} />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>

        {/* Bottom Provider & Engine Status */}
        <div className="p-4 border-t border-slate-100 space-y-3">
          <div className="bg-slate-50 rounded-xl p-3 border border-slate-200">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-500 font-medium">AI Engine</span>
              {health?.ai_provider === "mock" ? (
                <Badge variant="info">Mock Mode</Badge>
              ) : (
                <Badge variant="success">{health?.ai_provider || "Ready"}</Badge>
              )}
            </div>
            <div className="flex items-center gap-1.5 mt-2 text-[11px] text-slate-500">
              {health?.status === "healthy" ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                  <span>RAG Pipeline Active</span>
                </>
              ) : (
                <>
                  <AlertCircle className="w-3.5 h-3.5 text-amber-500 shrink-0" />
                  <span>Checking Backend API...</span>
                </>
              )}
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 px-8 border-b border-slate-200 bg-white flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold text-slate-800">
              {pathname === "/" && "Document Library"}
              {pathname === "/chat" && "Multi-Document AI Chat"}
              {pathname?.startsWith("/documents/") && "Interactive Document Intelligence"}
              {pathname === "/study" && "Study & Research Center"}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            {onOpenUpload && (
              <Button onClick={onOpenUpload} size="sm" className="shadow-sm">
                <UploadCloud className="w-4 h-4" />
                Upload Document
              </Button>
            )}
          </div>
        </header>

        {/* Viewport Content */}
        <main className="flex-1 overflow-y-auto min-w-0">
          {children}
        </main>
      </div>
    </div>
  );
}
