"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { StudyWorkspace } from "@/features/study/StudyWorkspace";
import { DocumentItem } from "@/lib/types";
import { api } from "@/lib/api";
import { Loader2 } from "lucide-react";

function StudyContent() {
  const searchParams = useSearchParams();
  const docParam = searchParams.get("doc");
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api.listDocuments().then((docs) => {
      setDocuments(docs.filter((d) => d.status === "Ready"));
      setIsLoading(false);
    });
  }, []);

  if (isLoading) {
    return (
      <div className="py-24 text-center">
        <Loader2 className="w-8 h-8 text-indigo-600 animate-spin mx-auto" />
      </div>
    );
  }

  return (
    <StudyWorkspace
      documents={documents}
      defaultDocumentId={docParam || undefined}
    />
  );
}

export default function StudyPage() {
  return (
    <AppShell>
      <Suspense fallback={<div className="p-8 text-center text-xs text-slate-400">Loading study center...</div>}>
        <StudyContent />
      </Suspense>
    </AppShell>
  );
}
