"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ChatPanel } from "@/features/chat/ChatPanel";
import { DocumentItem, Collection } from "@/lib/types";
import { api } from "@/lib/api";
import { BookOpen, Folder, CheckSquare, Square, Layers } from "lucide-react";
import { Badge } from "@/components/ui/Badge";

export default function MultiDocumentChatPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [selectedCollectionId, setSelectedCollectionId] = useState<string>("");

  useEffect(() => {
    Promise.all([api.listDocuments(), api.listCollections()]).then(([docs, cols]) => {
      setDocuments(docs.filter((d) => d.status === "Ready"));
      setCollections(cols);
      // Select all ready docs by default
      setSelectedDocIds(docs.filter((d) => d.status === "Ready").map((d) => d.id));
    });
  }, []);

  const toggleDocument = (id: string) => {
    setSelectedDocIds((prev) =>
      prev.includes(id) ? prev.filter((dId) => dId !== id) : [...prev, id]
    );
  };

  const selectAll = () => {
    setSelectedDocIds(documents.map((d) => d.id));
  };

  const deselectAll = () => {
    setSelectedDocIds([]);
  };

  return (
    <AppShell>
      <div className="flex h-full overflow-hidden">
        {/* Left Sidebar: Knowledge Source Selector */}
        <div className="w-80 bg-white border-r border-slate-200 flex flex-col shrink-0">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Knowledge Sources
              </h3>
              <p className="text-[11px] text-slate-500">
                {selectedDocIds.length} of {documents.length} selected
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={selectAll}
                className="text-[11px] font-medium text-indigo-600 hover:underline"
              >
                All
              </button>
              <button
                onClick={deselectAll}
                className="text-[11px] font-medium text-slate-500 hover:underline"
              >
                None
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-1">
            {documents.length === 0 ? (
              <div className="text-center py-8 text-xs text-slate-400">
                No indexed documents ready yet.
              </div>
            ) : (
              documents.map((doc) => {
                const isSelected = selectedDocIds.includes(doc.id);
                return (
                  <button
                    key={doc.id}
                    onClick={() => toggleDocument(doc.id)}
                    className={`w-full text-left p-2.5 rounded-lg border transition-all flex items-start gap-2.5 ${
                      isSelected
                        ? "bg-indigo-50/60 border-indigo-200 text-indigo-900 shadow-xs"
                        : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
                    }`}
                  >
                    <div className="mt-0.5 shrink-0 text-indigo-600">
                      {isSelected ? <CheckSquare className="w-4 h-4" /> : <Square className="w-4 h-4 text-slate-300" />}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-semibold truncate leading-tight">{doc.title}</p>
                      <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400">
                        <span>{doc.page_count} p.</span>
                        <span>•</span>
                        <span>{doc.file_type.toUpperCase()}</span>
                      </div>
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Right Main Panel: Multi-Doc RAG Chat */}
        <div className="flex-1 h-full bg-white">
          <ChatPanel
            documentTitle={`Cross-Document Synthesis (${selectedDocIds.length} Sources)`}
            documentId={selectedDocIds.length === 1 ? selectedDocIds[0] : undefined}
          />
        </div>
      </div>
    </AppShell>
  );
}
