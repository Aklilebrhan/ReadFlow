import React from "react";
import { BookOpen, FileCheck, Layers, FileText } from "lucide-react";
import { DocumentItem } from "@/lib/types";

export function StatsCards({ documents }: { documents: DocumentItem[] }) {
  const totalDocs = documents.length;
  const readyDocs = documents.filter((d) => d.status === "Ready").length;
  const totalPages = documents.reduce((acc, d) => acc + (d.page_count || 1), 0);
  const totalWords = documents.reduce((acc, d) => acc + (d.word_count || 0), 0);

  const stats = [
    {
      title: "Total Documents",
      value: totalDocs,
      subtext: `${readyDocs} ready for AI chat`,
      icon: BookOpen,
      color: "text-indigo-600 bg-indigo-50",
    },
    {
      title: "Indexed Pages",
      value: totalPages,
      subtext: "Extracted with page grounding",
      icon: Layers,
      color: "text-violet-600 bg-violet-50",
    },
    {
      title: "Total Corpus Words",
      value: totalWords.toLocaleString(),
      subtext: "Segmented into vector chunks",
      icon: FileText,
      color: "text-emerald-600 bg-emerald-50",
    },
    {
      title: "RAG Status",
      value: readyDocs === totalDocs && totalDocs > 0 ? "100% Ready" : `${readyDocs}/${totalDocs} Ready`,
      subtext: "Semantic vector retrieval active",
      icon: FileCheck,
      color: "text-amber-600 bg-amber-50",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, i) => {
        const Icon = stat.icon;
        return (
          <div
            key={i}
            className="p-5 bg-white border border-slate-200 rounded-xl shadow-sm flex items-center justify-between"
          >
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{stat.title}</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{stat.value}</h3>
              <p className="text-xs text-slate-400 mt-0.5">{stat.subtext}</p>
            </div>
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${stat.color}`}>
              <Icon className="w-6 h-6" />
            </div>
          </div>
        );
      })}
    </div>
  );
}
