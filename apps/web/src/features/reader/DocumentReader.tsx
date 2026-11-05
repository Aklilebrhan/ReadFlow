"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Search,
  Highlighter,
  Sparkles,
  HelpCircle,
  BookOpen,
  Bookmark,
  Share2,
  FileText,
  List
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { DocumentContent, Highlight } from "@/lib/types";
import { api } from "@/lib/api";

interface DocumentReaderProps {
  documentId: string;
  content: DocumentContent;
  highlights: Highlight[];
  onRefreshHighlights: () => void;
  activeCitationPage?: number | null;
  onAskAIAboutSelection?: (text: string) => void;
  onExplainSelection?: (text: string, type: string) => void;
}

export function DocumentReader({
  documentId,
  content,
  highlights,
  onRefreshHighlights,
  activeCitationPage,
  onAskAIAboutSelection,
  onExplainSelection
}: DocumentReaderProps) {
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedText, setSelectedText] = useState("");
  const [toolbarPosition, setToolbarPosition] = useState<{ top: number; left: number } | null>(null);
  const [showOutline, setShowOutline] = useState(false);
  const readerContainerRef = useRef<HTMLDivElement>(null);

  // Jump to page when citation is clicked
  useEffect(() => {
    if (activeCitationPage && activeCitationPage >= 1 && activeCitationPage <= content.page_count) {
      setCurrentPage(activeCitationPage);
    }
  }, [activeCitationPage, content.page_count]);

  const currentPageData = content.pages.find((p) => p.page_number === currentPage) || content.pages[0];

  // Text selection handler
  const handleMouseUp = () => {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) {
      setToolbarPosition(null);
      setSelectedText("");
      return;
    }

    const text = selection.toString().trim();
    if (text.length > 3) {
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      const containerRect = readerContainerRef.current?.getBoundingClientRect();

      if (containerRect) {
        setToolbarPosition({
          top: rect.top - containerRect.top - 44,
          left: Math.max(10, rect.left - containerRect.left + (rect.width / 2) - 140),
        });
        setSelectedText(text);
      }
    }
  };

  const handleSaveHighlight = async (color: string = "yellow") => {
    if (!selectedText) return;
    try {
      await api.addHighlight(documentId, {
        page_number: currentPage,
        selected_text: selectedText,
        color
      });
      onRefreshHighlights();
      setToolbarPosition(null);
      window.getSelection()?.removeAllRanges();
    } catch (err: any) {
      alert("Failed to save highlight: " + err.message);
    }
  };

  const pageHighlights = highlights.filter((h) => h.page_number === currentPage);

  return (
    <div className="flex flex-col h-full bg-slate-100/70 border-r border-slate-200 relative select-text" ref={readerContainerRef}>
      {/* Reader Control Bar */}
      <div className="h-12 bg-white border-b border-slate-200 px-4 flex items-center justify-between shrink-0 shadow-sm z-10">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setShowOutline(!showOutline)}
            className={`h-8 w-8 ${showOutline ? "bg-slate-100 text-indigo-600" : "text-slate-600"}`}
            title="Toggle Document Outline"
          >
            <List className="w-4 h-4" />
          </Button>

          <div className="h-4 w-px bg-slate-200" />

          {/* Page Navigator */}
          <div className="flex items-center gap-1.5 text-xs text-slate-600 font-medium">
            <Button
              variant="ghost"
              size="icon"
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="h-7 w-7"
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <span>
              Page <span className="font-semibold text-slate-900">{currentPage}</span> of{" "}
              <span className="font-semibold text-slate-900">{content.page_count}</span>
            </span>
            <Button
              variant="ghost"
              size="icon"
              disabled={currentPage >= content.page_count}
              onClick={() => setCurrentPage((p) => Math.min(content.page_count, p + 1))}
              className="h-7 w-7"
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Search inside page */}
        <div className="relative w-48">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search text..."
            className="pl-8 h-7 text-xs bg-slate-50"
          />
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden relative">
        {/* Outline Sidebar Drawer */}
        {showOutline && (
          <div className="w-64 bg-white border-r border-slate-200 p-4 overflow-y-auto shrink-0 animate-in slide-in-from-left">
            <h4 className="text-xs font-semibold uppercase text-slate-400 tracking-wider mb-3">
              Document Outline
            </h4>
            <div className="space-y-1">
              {content.pages.map((p) => (
                <div key={p.page_number} className="space-y-1">
                  <button
                    onClick={() => {
                      setCurrentPage(p.page_number);
                      setShowOutline(false);
                    }}
                    className={`w-full text-left text-xs px-2.5 py-1.5 rounded-md transition-colors flex items-center justify-between ${
                      currentPage === p.page_number
                        ? "bg-indigo-50 text-indigo-700 font-semibold"
                        : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    <span>Page {p.page_number}</span>
                    <span className="text-[10px] text-slate-400">{p.word_count} words</span>
                  </button>
                  {p.headings.map((h, hi) => (
                    <button
                      key={hi}
                      onClick={() => {
                        setCurrentPage(p.page_number);
                        setShowOutline(false);
                      }}
                      className="w-full text-left text-[11px] text-slate-500 hover:text-indigo-600 pl-5 pr-2 py-0.5 truncate block"
                    >
                      • {h}
                    </button>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Paper Canvas */}
        <div
          className="flex-1 overflow-y-auto p-6 flex justify-center"
          onMouseUp={handleMouseUp}
        >
          <div className="w-full max-w-3xl bg-white rounded-xl border border-slate-200 shadow-sm min-h-[800px] p-10 font-serif leading-relaxed text-slate-800 text-[15px] relative">
            {/* Header info */}
            <div className="border-b border-slate-100 pb-3 mb-6 flex items-center justify-between font-sans text-xs text-slate-400">
              <span className="truncate max-w-md">{content.title}</span>
              <span className="shrink-0">Page {currentPage} of {content.page_count}</span>
            </div>

            {/* Section Headings */}
            {currentPageData?.headings && currentPageData.headings.length > 0 && (
              <div className="mb-6 font-sans">
                {currentPageData.headings.map((h, i) => (
                  <h3 key={i} className="text-xl font-bold text-slate-900 tracking-tight mb-2">
                    {h}
                  </h3>
                ))}
              </div>
            )}

            {/* Page Text Body */}
            <div className="whitespace-pre-line select-text">
              {currentPageData?.text ? (
                currentPageData.text
              ) : (
                <div className="text-center py-20 text-slate-400 font-sans text-sm">
                  No text extracted for page {currentPage}.
                </div>
              )}
            </div>

            {/* Highlights on this page */}
            {pageHighlights.length > 0 && (
              <div className="mt-8 pt-4 border-t border-slate-100 font-sans">
                <h5 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Saved Highlights on this Page ({pageHighlights.length})
                </h5>
                <div className="space-y-1.5">
                  {pageHighlights.map((hl) => (
                    <div
                      key={hl.id}
                      className="text-xs p-2 rounded bg-amber-50/80 border border-amber-200 text-amber-900 italic flex items-center justify-between"
                    >
                      <span>"{hl.selected_text}"</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Floating Text Selection Toolbar */}
        {toolbarPosition && (
          <div
            style={{ top: `${toolbarPosition.top}px`, left: `${toolbarPosition.left}px` }}
            className="absolute z-30 bg-slate-900 text-white rounded-lg shadow-xl px-2 py-1.5 flex items-center gap-1 text-xs animate-in fade-in zoom-in-95 select-none"
          >
            <button
              onClick={() => {
                if (onExplainSelection) onExplainSelection(selectedText, "simple");
                setToolbarPosition(null);
              }}
              className="flex items-center gap-1 px-2 py-1 rounded hover:bg-slate-800 text-slate-200 hover:text-white transition-colors"
              title="Explain simply"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              Explain
            </button>

            <button
              onClick={() => {
                if (onExplainSelection) onExplainSelection(selectedText, "define");
                setToolbarPosition(null);
              }}
              className="flex items-center gap-1 px-2 py-1 rounded hover:bg-slate-800 text-slate-200 hover:text-white transition-colors"
              title="Define terms"
            >
              <HelpCircle className="w-3.5 h-3.5 text-indigo-400" />
              Define
            </button>

            <button
              onClick={() => handleSaveHighlight("yellow")}
              className="flex items-center gap-1 px-2 py-1 rounded hover:bg-slate-800 text-slate-200 hover:text-white transition-colors"
              title="Save highlight"
            >
              <Highlighter className="w-3.5 h-3.5 text-emerald-400" />
              Highlight
            </button>

            <div className="h-3 w-px bg-slate-700 mx-0.5" />

            <button
              onClick={() => {
                if (onAskAIAboutSelection) onAskAIAboutSelection(selectedText);
                setToolbarPosition(null);
              }}
              className="flex items-center gap-1 px-2 py-1 rounded bg-indigo-600 hover:bg-indigo-700 text-white transition-colors font-medium"
            >
              Ask AI
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
