"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { StatsCards } from "@/features/dashboard/StatsCards";
import { DocumentLibrary } from "@/features/dashboard/DocumentLibrary";
import { UploadDropzone } from "@/features/dashboard/UploadDropzone";
import { Dialog } from "@/components/ui/Dialog";
import { DocumentItem, Collection } from "@/lib/types";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [collections, setCollections] = useState<Collection[]>([]);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const loadData = async () => {
    try {
      const [docs, cols] = await Promise.all([
        api.listDocuments(),
        api.listCollections(),
      ]);
      setDocuments(docs);
      setCollections(cols);
    } catch (err) {
      console.error("Failed to load library data:", err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpload = async (file: File, title?: string, collectionId?: string) => {
    setIsUploading(true);
    try {
      await api.uploadDocument(file, title, collectionId);
      setIsUploadOpen(false);
      await loadData();
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <AppShell onOpenUpload={() => setIsUploadOpen(true)}>
      <div className="max-w-7xl mx-auto p-8 space-y-8">
        {/* Statistics Overview */}
        <StatsCards documents={documents} />

        {/* Document Library Table */}
        <DocumentLibrary
          documents={documents}
          collections={collections}
          onRefresh={loadData}
          onOpenUpload={() => setIsUploadOpen(true)}
        />

        {/* Upload Modal */}
        <Dialog
          isOpen={isUploadOpen}
          onClose={() => setIsUploadOpen(false)}
          title="Upload Research Document"
          description="Upload a PDF, DOCX, TXT, or Markdown document to begin AI-powered indexing."
          className="max-w-xl"
        >
          <UploadDropzone
            collections={collections}
            onUpload={handleUpload}
            isUploading={isUploading}
          />
        </Dialog>
      </div>
    </AppShell>
  );
}
