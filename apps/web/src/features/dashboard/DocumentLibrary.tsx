"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Search,
  BookOpen,
  FileText,
  Trash2,
  ExternalLink,
  Sparkles,
  GraduationCap,
  Folder,
  AlertCircle,
  MoreVertical,
  Plus
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { ProcessingStatusBadge } from "@/components/ui/Badge";
import { formatBytes, formatRelativeTime } from "@/lib/utils";
import { DocumentItem, Collection } from "@/lib/types";
import { api } from "@/lib/api";

interface DocumentLibraryProps {
  documents: DocumentItem[];
  collections: Collection[];
  onRefresh: () => void;
  onOpenUpload: () => void;
}

export function DocumentLibrary({ documents, collections, onRefresh, onOpenUpload }: DocumentLibraryProps) {
  const [search, setSearch] = useState("");
  const [selectedCollection, setSelectedCollection] = useState<string>("all");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Poll processing documents
  useEffect(() => {
    const hasProcessing = documents.some(
      (d) => d.status !== "Ready" && d.status !== "Failed"
    );

    if (!hasProcessing) return;

    const interval = setInterval(() => {
      onRefresh();
    }, 2500);

    return () => clearInterval(interval);
  }, [documents, onRefresh]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this document and all its indexed chunks?")) return;

    setDeletingId(id);
    try {
      await api.deleteDocument(id);
      onRefresh();
    } catch (err: any) {
      alert(err.message || "Failed to delete document");
    } finally {
      setDeletingId(null);
    }
  };

  const filtered = documents.filter((doc) => {
    const matchesSearch =
      doc.title.toLowerCase().includes(search.toLowerCase()) ||
      doc.filename.toLowerCase().includes(search.toLowerCase());
    const matchesCollection =
      selectedCollection === "all" || doc.collection_id === selectedCollection;
    return matchesSearch && matchesCollection;
  });

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      {/* Header Controls */}
      <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-3">
        {/* Search */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search documents by title or file..."
            className="pl-9 h-9"
          />
        </div>

        {/* Collection Filter */}
        <div className="flex items-center gap-2 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          <button
            onClick={() => setSelectedCollection("all")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors shrink-0 ${
              selectedCollection === "all"
                ? "bg-slate-900 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            All Docs ({documents.length})
          </button>
          {collections.map((c) => (
            <button
              key={c.id}
              onClick={() => setSelectedCollection(c.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors shrink-0 ${
                selectedCollection === c.id
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {c.name}
            </button>
          ))}
        </div>
      </div>

      {/* Table / List */}
      {filtered.length === 0 ? (
        <div className="p-12 text-center">
          <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 mx-auto flex items-center justify-center mb-3">
            <BookOpen className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-semibold text-slate-800">No documents found</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            {search
              ? "No files match your search criteria. Try a different query."
              : "Upload your first research paper, textbook chapter, or report to start exploring with AI."}
          </p>
          {!search && (
            <Button onClick={onOpenUpload} size="sm" className="mt-4">
              <Plus className="w-4 h-4 mr-1" /> Upload Document
            </Button>
          )}
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="bg-slate-50/75 border-b border-slate-100 text-slate-500 text-xs font-semibold uppercase tracking-wider">
                <th className="py-3 px-5">Document</th>
                <th className="py-3 px-4">Status & Ingestion</th>
                <th className="py-3 px-4">Size & Pages</th>
                <th className="py-3 px-4">Collection</th>
                <th className="py-3 px-4">Added</th>
                <th className="py-3 px-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((doc) => {
                const isReady = doc.status === "Ready";
                const isFailed = doc.status === "Failed";
                return (
                  <tr
                    key={doc.id}
                    className="hover:bg-slate-50/70 transition-colors group"
                  >
                    {/* Title & Icon */}
                    <td className="py-3.5 px-5">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
                          <FileText className="w-5 h-5" />
                        </div>
                        <div className="min-w-0">
                          <Link
                            href={isReady ? `/documents/${doc.id}` : "#"}
                            className={`font-semibold block truncate ${
                              isReady
                                ? "text-slate-900 hover:text-indigo-600 cursor-pointer"
                                : "text-slate-700 cursor-default"
                            }`}
                          >
                            {doc.title}
                          </Link>
                          <span className="text-xs text-slate-400 block truncate">
                            {doc.filename}
                          </span>
                        </div>
                      </div>
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-4">
                      <div className="space-y-1">
                        <ProcessingStatusBadge status={doc.status} progress={doc.progress_percent} />
                        {doc.status_message && !isReady && (
                          <p className="text-[11px] text-slate-500 max-w-xs truncate">
                            {doc.status_message}
                          </p>
                        )}
                        {!isReady && !isFailed && (
                          <div className="w-28 bg-slate-100 h-1 rounded-full overflow-hidden">
                            <div
                              className="bg-indigo-600 h-full transition-all duration-300"
                              style={{ width: `${doc.progress_percent}%` }}
                            />
                          </div>
                        )}
                      </div>
                    </td>

                    {/* Pages & Words */}
                    <td className="py-3.5 px-4 text-xs text-slate-600">
                      <div>{doc.page_count} page{doc.page_count === 1 ? "" : "s"}</div>
                      <div className="text-slate-400">{formatBytes(doc.file_size)}</div>
                    </td>

                    {/* Collection */}
                    <td className="py-3.5 px-4">
                      {doc.collection ? (
                        <span className="inline-flex items-center gap-1 text-xs text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md font-medium">
                          <Folder className="w-3 h-3" />
                          {doc.collection.name}
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400">—</span>
                      )}
                    </td>

                    {/* Added */}
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {formatRelativeTime(doc.created_at)}
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-5 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        {isReady ? (
                          <Link href={`/documents/${doc.id}`}>
                            <Button size="sm" variant="subtle" className="text-xs">
                              <BookOpen className="w-3.5 h-3.5" />
                              Reader & AI Chat
                            </Button>
                          </Link>
                        ) : null}

                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={(e) => handleDelete(doc.id, e)}
                          isLoading={deletingId === doc.id}
                          className="text-slate-400 hover:text-rose-600 hover:bg-rose-50"
                          title="Delete document"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
