"use client";

import React, { useState, useEffect } from "react";
import { Sparkles, Copy, CheckCircle, HelpCircle, Code, Lightbulb, Languages, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Dialog } from "@/components/ui/Dialog";
import { ExplainResponse } from "@/lib/types";
import { api } from "@/lib/api";

interface ExplainModalProps {
  isOpen: boolean;
  onClose: () => void;
  passage: string;
  initialType?: string;
}

export function ExplainModal({ isOpen, onClose, passage, initialType = "simple" }: ExplainModalProps) {
  const [explainType, setExplainType] = useState<string>(initialType);
  const [result, setResult] = useState<ExplainResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const types = [
    { id: "simple", label: "Explain Simply", icon: Lightbulb },
    { id: "technical", label: "Technical Deep-Dive", icon: Code },
    { id: "define", label: "Define Terms", icon: HelpCircle },
    { id: "example", label: "Give Example", icon: Sparkles },
    { id: "translate", label: "Paraphrase", icon: Languages },
  ];

  const handleExplain = async (type: string) => {
    if (!passage) return;
    setIsLoading(true);
    setExplainType(type);
    try {
      const res = await api.explainPassage({
        passage,
        explanation_type: type,
      });
      setResult(res);
    } catch (err: any) {
      alert("Failed to explain passage: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && passage) {
      handleExplain(initialType);
    }
  }, [isOpen, passage, initialType]);

  const handleCopy = () => {
    if (!result) return;
    navigator.clipboard.writeText(result.explanation);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title="Passage Intelligence"
      description="Deep contextual explanation of selected text"
      className="max-w-xl"
    >
      <div className="space-y-4">
        {/* Selected passage quote preview */}
        <div className="p-3 bg-slate-50 border-l-4 border-indigo-500 rounded-r-lg text-xs italic text-slate-700 max-h-24 overflow-y-auto">
          "{passage}"
        </div>

        {/* Style Selector */}
        <div className="flex flex-wrap gap-1.5">
          {types.map((t) => {
            const Icon = t.icon;
            return (
              <button
                key={t.id}
                onClick={() => handleExplain(t.id)}
                disabled={isLoading}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  explainType === t.id
                    ? "bg-indigo-600 text-white shadow-xs"
                    : "bg-slate-100 hover:bg-slate-200 text-slate-700"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {t.label}
              </button>
            );
          })}
        </div>

        {/* Output Area */}
        <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl min-h-[140px]">
          {isLoading ? (
            <div className="py-8 text-center text-xs text-slate-500 flex items-center justify-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-600 animate-spin" />
              Generating contextual explanation...
            </div>
          ) : result ? (
            <div className="text-sm text-slate-800 leading-relaxed whitespace-pre-line font-serif">
              {result.explanation}
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="flex justify-between items-center pt-2">
          <Button variant="outline" size="sm" onClick={handleCopy} disabled={!result}>
            {copied ? <CheckCircle className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? "Copied" : "Copy Explanation"}
          </Button>
          <Button size="sm" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </Dialog>
  );
}
