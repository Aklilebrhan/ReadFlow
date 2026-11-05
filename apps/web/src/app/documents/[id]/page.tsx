"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  BookOpen,
  Sparkles,
  GraduationCap,
  Download,
  Share2,
  AlertCircle,
  Loader2
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { ProcessingStatusBadge } from "@/components/ui/Badge";
import { DocumentReader } from "@/features/reader/DocumentReader";
import { ChatPanel } from "@/features/chat/ChatPanel";
import { SummaryModal } from "@/features/summaries/SummaryModal";
import { ExplainModal } from "@/features/explanation/ExplainModal";
import { DocumentItem, DocumentContent, Highlight } from "@/lib/types";
import { api } from "@/lib/api";

export default function DocumentWorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const documentId = params.id as string;

  const [document, setDocument] = useState<DocumentItem | null>(null);
  const [content, setContent] = useState<DocumentContent | null>(null);
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals & Cross-pane communication
  const [isSummaryOpen, setIsSummaryOpen] = useState(false);
  const [explainPassage, setExplainPassage] = useState<{ text: string; type: string } | null>(null);
  const [activeCitationPage, setActiveCitationPage] = useState<number | null>(null);
  const [externalPrompt, setExternalPrompt] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const [doc, docContent, hls] = await Promise.all([
        api.getDocument(documentId),
        api.getDocumentContent(documentId),
        api.listHighlights(documentId),
      ]);
      setDocument(doc);
      setContent(docContent);
      setHighlights(hls);
    } catch (err: any) {
      setError(err.message || "Failed to load document");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (documentId) {
      loadData();
    }
  }, [documentId]);

  if (isLoading) {
    return (
      <div className="h-screen w-full flex flex-col items-center justify-center bg-slate-50 gap-3">
        <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
        <p className="text-sm font-medium text-slate-600">Loading document workspace...</p>
      </div>
    );
  }

  if (error || !document || !content) {
    return (
      <div className="h-screen w-full flex flex-col items-center justify-center bg-slate-50 gap-4 p-4 text-center">
        <AlertCircle className="w-10 h-10 text-rose-500" />
        <h2 className="text-lg font-bold text-slate-800">Document Unavailable</h2>
        <p className="text-xs text-slate-500 max-w-md">{error || "Could not find document."}</p>
        <Link href="/">
          <Button size="sm">
            <ArrowLeft className="w-4 h-4 mr-1" /> Return to Library
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="h-screen w-full flex flex-col bg-slate-50 overflow-hidden">
      {/* Top Navigation & Workspace Actions Bar */}
      <header className="h-14 bg-white border-b border-slate-200 px-4 flex items-center justify-between shrink-0 shadow-xs z-20">
        <div className="flex items-center gap-3 min-w-0">
          <Link
            href="/"
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors shrink-0"
            title="Back to library"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="min-w-0 flex items-center gap-2">
            <h2 className="text-sm font-bold text-slate-900 truncate max-w-sm sm:max-w-md">
              {document.title}
            </h2>
            <ProcessingStatusBadge status={document.status} />
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setIsSummaryOpen(true)}
            className="text-xs shadow-xs"
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-600 mr-1" />
            Summarize
          </Button>

          <Button
            size="sm"
            variant="outline"
            onClick={() => router.push(`/study?doc=${document.id}`)}
            className="text-xs shadow-xs"
          >
            <GraduationCap className="w-3.5 h-3.5 text-violet-600 mr-1" />
            Study Tools
          </Button>
        </div>
      </header>

      {/* Main Split-Screen Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Side: Document Reader */}
        <div className="w-[55%] h-full">
          <DocumentReader
            documentId={document.id}
            content={content}
            highlights={highlights}
            onRefreshHighlights={() => api.listHighlights(document.id).then(setHighlights)}
            activeCitationPage={activeCitationPage}
            onAskAIAboutSelection={(text) => {
              setExternalPrompt(`Explain how this passage relates to the overall document:\n"${text}"`);
            }}
            onExplainSelection={(text, type) => {
              setExplainPassage({ text, type });
            }}
          />
        </div>

        {/* Right Side: AI Document Chat */}
        <div className="w-[45%] h-full border-l border-slate-200">
          <ChatPanel
            documentId={document.id}
            documentTitle={document.title}
            onCitationClick={(pageNum) => setActiveCitationPage(pageNum)}
            externalPrompt={externalPrompt}
            onClearExternalPrompt={() => setExternalPrompt(null)}
          />
        </div>
      </div>

      {/* Summarization Modal */}
      <SummaryModal
        isOpen={isSummaryOpen}
        onClose={() => setIsSummaryOpen(false)}
        documentId={document.id}
        documentTitle={document.title}
      />

      {/* Passage Explanation Modal */}
      {explainPassage && (
        <ExplainModal
          isOpen={!!explainPassage}
          onClose={() => setExplainPassage(null)}
          passage={explainPassage.text}
          initialType={explainPassage.type}
        />
      )}
    </div>
  );
}
