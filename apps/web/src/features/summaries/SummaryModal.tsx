"use client";

import React, { useState } from "react";
import { Sparkles, Copy, CheckCircle, Download, Layers, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Dialog } from "@/components/ui/Dialog";
import { Badge } from "@/components/ui/Badge";
import { SummaryResponse } from "@/lib/types";
import { api } from "@/lib/api";

interface SummaryModalProps {
  documentId: string;
  documentTitle: string;
  isOpen: boolean;
  onClose: () => void;
}

export function SummaryModal({ documentId, documentTitle, isOpen, onClose }: SummaryModalProps) {
  const [summaryType, setSummaryType] = useState<string>("quick");
  const [summaryData, setSummaryData] = useState<SummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const summaryTypes = [
    { id: "quick", label: "Quick Summary", desc: "1-2 paragraphs" },
    { id: "detailed", label: "Detailed Executive", desc: "Comprehensive analysis" },
    { id: "chapters", label: "Section Breakdown", desc: "Hierarchical breakdown" },
    { id: "key_points", label: "Key Points", desc: "Bullet list" },
  ];

  const handleGenerate = async (type: string = summaryType) => {
    setIsLoading(true);
    setSummaryType(type);
    try {
      const res = await api.generateSummary({
        document_id: documentId,
        summary_type: type,
      });
      setSummaryData(res);
    } catch (err: any) {
      alert("Failed to generate summary: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    if (!summaryData) return;
    navigator.clipboard.writeText(summaryData.summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={`Intelligent Summarizer`}
      description={`Synthesizing: ${documentTitle}`}
      className="max-w-2xl"
    >
      <div className="space-y-4">
        {/* Type Selector */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {summaryTypes.map((t) => (
            <button
              key={t.id}
              onClick={() => handleGenerate(t.id)}
              disabled={isLoading}
              className={`p-2.5 rounded-lg border text-left transition-all ${
                summaryType === t.id
                  ? "border-indigo-600 bg-indigo-50/70 text-indigo-900 font-semibold shadow-xs"
                  : "border-slate-200 bg-white hover:bg-slate-50 text-slate-700"
              }`}
            >
              <div className="text-xs">{t.label}</div>
              <div className="text-[10px] text-slate-400 font-normal">{t.desc}</div>
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 min-h-[220px]">
          {isLoading ? (
            <div className="py-12 text-center space-y-2">
              <Sparkles className="w-6 h-6 text-indigo-600 animate-spin mx-auto" />
              <p className="text-xs font-medium text-slate-600">
                Running hierarchical multi-stage summarization...
              </p>
            </div>
          ) : summaryData ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between text-xs text-slate-500 border-b border-slate-200/80 pb-2">
                <span className="font-semibold text-slate-700 uppercase tracking-wider text-[11px]">
                  {summaryData.summary_type.replace("_", " ")} Output
                </span>
                <div className="flex items-center gap-2">
                  <span>{summaryData.word_count} words</span>
                  {summaryData.is_hierarchical && (
                    <Badge variant="info">Hierarchical Map-Reduce</Badge>
                  )}
                </div>
              </div>

              {/* Master summary */}
              <div className="text-sm text-slate-800 leading-relaxed whitespace-pre-line font-serif">
                {summaryData.summary}
              </div>

              {/* Section Accordions if hierarchical */}
              {summaryData.sections && summaryData.sections.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-200 space-y-2">
                  <h5 className="text-xs font-semibold uppercase text-slate-500 tracking-wider">
                    Section Analyses ({summaryData.sections.length})
                  </h5>
                  {summaryData.sections.map((sec, i) => (
                    <div key={i} className="p-3 bg-white border border-slate-200 rounded-lg text-xs space-y-1">
                      <div className="flex items-center justify-between font-semibold text-slate-800">
                        <span>{sec.title}</span>
                        <span className="text-[10px] text-indigo-600 font-normal">{sec.page_range}</span>
                      </div>
                      <p className="text-slate-600 leading-normal">{sec.summary}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="py-12 text-center space-y-2">
              <BookOpen className="w-8 h-8 text-slate-400 mx-auto" />
              <p className="text-xs text-slate-500">
                Select a summary style above to generate a grounded executive digest.
              </p>
              <Button size="sm" onClick={() => handleGenerate("quick")}>
                Generate Quick Summary
              </Button>
            </div>
          )}
        </div>

        {summaryData && (
          <div className="flex justify-between items-center pt-2">
            <span className="text-xs text-slate-400">Grounded in actual document content</span>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={handleCopy}>
                {copied ? <CheckCircle className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                {copied ? "Copied" : "Copy"}
              </Button>
              <Button size="sm" onClick={onClose}>
                Done
              </Button>
            </div>
          </div>
        )}
      </div>
    </Dialog>
  );
}
