"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, File, AlertCircle, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { formatBytes } from "@/lib/utils";
import { Collection } from "@/lib/types";

interface UploadDropzoneProps {
  collections: Collection[];
  onUpload: (file: File, title?: string, collectionId?: string) => Promise<void>;
  isUploading: boolean;
}

export function UploadDropzone({ collections, onUpload, isUploading }: UploadDropzoneProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [customTitle, setCustomTitle] = useState("");
  const [selectedCollection, setSelectedCollection] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    const valid = [".pdf", ".docx", ".doc", ".txt", ".md", ".markdown"];
    if (!valid.includes(ext)) {
      setError(`Unsupported file type '${ext}'. Please upload a PDF, DOCX, TXT, or Markdown file.`);
      return;
    }
    setError(null);
    setSelectedFile(file);
    setCustomTitle(file.name.replace(/\.[^/.]+$/, ""));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    try {
      await onUpload(selectedFile, customTitle || undefined, selectedCollection || undefined);
      setSelectedFile(null);
      setCustomTitle("");
      setSelectedCollection("");
    } catch (err: any) {
      setError(err.message || "Failed to upload document");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Drop area */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
          dragActive
            ? "border-indigo-500 bg-indigo-50/50 scale-[0.99]"
            : "border-slate-300 hover:border-slate-400 bg-slate-50/50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.doc,.txt,.md"
          className="hidden"
          onChange={handleFileChange}
        />

        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center shadow-inner">
            <UploadCloud className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-800">
              Drag and drop your document here, or <span className="text-indigo-600 underline">browse</span>
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Supports PDF (with OCR fallback), DOCX, TXT, and Markdown up to 50MB
            </p>
          </div>
        </div>
      </div>

      {/* Selected file preview */}
      {selectedFile && (
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3 animate-in fade-in">
          <div className="flex items-center gap-3">
            <File className="w-6 h-6 text-indigo-600 shrink-0" />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-slate-800 truncate">{selectedFile.name}</p>
              <p className="text-xs text-slate-500">{formatBytes(selectedFile.size)}</p>
            </div>
            <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <div>
              <label className="text-xs font-semibold text-slate-600 block mb-1">Document Title</label>
              <Input
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
                placeholder="Title in library"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-600 block mb-1">Organize in Collection</label>
              <select
                value={selectedCollection}
                onChange={(e) => setSelectedCollection(e.target.value)}
                className="flex h-9 w-full rounded-lg border border-slate-300 bg-white px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
              >
                <option value="">No Collection (Default)</option>
                {collections.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 p-3 text-xs text-rose-700 bg-rose-50 border border-rose-200 rounded-lg">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {selectedFile && (
        <div className="flex justify-end gap-2 pt-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setSelectedFile(null)}
          >
            Cancel
          </Button>
          <Button type="submit" size="sm" isLoading={isUploading}>
            Process & Ingest Document
          </Button>
        </div>
      )}
    </form>
  );
}
