"use client";

import React, { useState, useEffect } from "react";
import {
  GraduationCap,
  Layers,
  HelpCircle,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  RotateCw,
  CheckCircle2,
  XCircle,
  Sparkles,
  FileText
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { StudyResponse, DocumentItem } from "@/lib/types";
import { api } from "@/lib/api";

interface StudyWorkspaceProps {
  documents: DocumentItem[];
  defaultDocumentId?: string;
}

export function StudyWorkspace({ documents, defaultDocumentId }: StudyWorkspaceProps) {
  const [selectedDocId, setSelectedDocId] = useState<string>(
    defaultDocumentId || (documents[0]?.id || "")
  );
  const [activeTab, setActiveTab] = useState<"flashcards" | "quiz" | "key_terms" | "notes">("flashcards");
  const [studyData, setStudyData] = useState<StudyResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Flashcards state
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  // Quiz state
  const [userAnswers, setUserAnswers] = useState<Record<number, number>>({});

  useEffect(() => {
    if (selectedDocId) {
      loadStudyMaterials(selectedDocId, activeTab);
    }
  }, [selectedDocId, activeTab]);

  const loadStudyMaterials = async (docId: string, type: string) => {
    setIsLoading(true);
    setIsFlipped(false);
    setCurrentCardIndex(0);
    setUserAnswers({});
    try {
      const res = await api.generateStudyMaterials({
        document_id: docId,
        material_type: type,
      });
      setStudyData(res);
    } catch (err: any) {
      console.error("Failed to load study materials:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const selectedDoc = documents.find((d) => d.id === selectedDocId);

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      {/* Header Selector */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-indigo-600" />
            Study & Knowledge Workspace
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Grounded revision tools synthesized directly from your uploaded documents
          </p>
        </div>

        {/* Document Selector */}
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <label className="text-xs font-semibold text-slate-600 shrink-0">Source Document:</label>
          <select
            value={selectedDocId}
            onChange={(e) => setSelectedDocId(e.target.value)}
            className="h-9 rounded-lg border border-slate-300 bg-white px-3 text-xs shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 max-w-xs truncate"
          >
            {documents.map((d) => (
              <option key={d.id} value={d.id}>
                {d.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Mode Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setActiveTab("flashcards")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === "flashcards"
              ? "bg-indigo-600 text-white shadow-sm"
              : "bg-white text-slate-600 hover:bg-slate-100"
          }`}
        >
          <Layers className="w-4 h-4" />
          Interactive Flashcards
        </button>
        <button
          onClick={() => setActiveTab("quiz")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === "quiz"
              ? "bg-indigo-600 text-white shadow-sm"
              : "bg-white text-slate-600 hover:bg-slate-100"
          }`}
        >
          <HelpCircle className="w-4 h-4" />
          Knowledge Quiz
        </button>
        <button
          onClick={() => setActiveTab("key_terms")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === "key_terms"
              ? "bg-indigo-600 text-white shadow-sm"
              : "bg-white text-slate-600 hover:bg-slate-100"
          }`}
        >
          <BookOpen className="w-4 h-4" />
          Key Terms & Definitions
        </button>
        <button
          onClick={() => setActiveTab("notes")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === "notes"
              ? "bg-indigo-600 text-white shadow-sm"
              : "bg-white text-slate-600 hover:bg-slate-100"
          }`}
        >
          <FileText className="w-4 h-4" />
          Study Notes
        </button>
      </div>

      {/* Main Workspace Canvas */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 min-h-[420px]">
        {isLoading ? (
          <div className="py-24 text-center space-y-3">
            <Sparkles className="w-8 h-8 text-indigo-600 animate-spin mx-auto" />
            <p className="text-sm font-medium text-slate-600">
              Extracting concepts and synthesizing study set...
            </p>
          </div>
        ) : !studyData ? (
          <div className="py-20 text-center text-slate-400 text-sm">
            Please select a document to generate study materials.
          </div>
        ) : (
          <>
            {/* 1. Flashcards View */}
            {activeTab === "flashcards" && (
              <div className="max-w-xl mx-auto space-y-6">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>Card {currentCardIndex + 1} of {studyData.items.length || 1}</span>
                  <span className="flex items-center gap-1 text-slate-500">
                    <RotateCw className="w-3 h-3" /> Click card to flip
                  </span>
                </div>

                {/* 3D Flip Card */}
                {studyData.items && studyData.items.length > 0 ? (
                  <div
                    onClick={() => setIsFlipped(!isFlipped)}
                    className="cursor-pointer h-72 w-full rounded-2xl bg-gradient-to-br from-indigo-50/50 to-white border-2 border-indigo-100 shadow-md p-8 flex flex-col justify-between transition-all duration-300 hover:shadow-lg hover:border-indigo-200"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <Badge variant={isFlipped ? "success" : "info"}>
                        {isFlipped ? "Answer / Back" : "Question / Front"}
                      </Badge>
                      <span className="text-[11px] text-slate-400">Tap to flip</span>
                    </div>

                    <div className="text-center my-auto">
                      <p className={`text-lg font-medium leading-relaxed ${isFlipped ? "text-indigo-900 font-serif" : "text-slate-900 font-sans font-semibold"}`}>
                        {isFlipped
                          ? studyData.items[currentCardIndex]?.back
                          : studyData.items[currentCardIndex]?.front}
                      </p>
                    </div>

                    <div className="text-center text-[11px] text-slate-400">
                      Grounded in {selectedDoc?.title || "Document"}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-slate-400 text-xs">No cards generated.</div>
                )}

                {/* Controls */}
                <div className="flex items-center justify-center gap-4">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={currentCardIndex <= 0}
                    onClick={() => {
                      setIsFlipped(false);
                      setCurrentCardIndex((c) => Math.max(0, c - 1));
                    }}
                  >
                    <ChevronLeft className="w-4 h-4 mr-1" /> Previous
                  </Button>
                  <Button
                    size="sm"
                    disabled={currentCardIndex >= (studyData.items.length - 1)}
                    onClick={() => {
                      setIsFlipped(false);
                      setCurrentCardIndex((c) => Math.min(studyData.items.length - 1, c + 1));
                    }}
                  >
                    Next Card <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </div>
              </div>
            )}

            {/* 2. Quiz View */}
            {activeTab === "quiz" && (
              <div className="max-w-2xl mx-auto space-y-6">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">Knowledge Verification Quiz</h3>
                    <p className="text-xs text-slate-500">Test your comprehension of the source document</p>
                  </div>
                  <Badge variant="outline">
                    Answered {Object.keys(userAnswers).length} / {studyData.items.length}
                  </Badge>
                </div>

                <div className="space-y-6">
                  {studyData.items.map((q, qIndex) => {
                    const selectedOpt = userAnswers[qIndex];
                    const isAnswered = selectedOpt !== undefined;
                    return (
                      <div key={qIndex} className="p-5 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                        <div className="flex items-start gap-3">
                          <span className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-700 font-bold text-xs flex items-center justify-center shrink-0">
                            {qIndex + 1}
                          </span>
                          <h4 className="text-sm font-semibold text-slate-900 leading-snug">
                            {q.question}
                          </h4>
                        </div>

                        {/* Options */}
                        <div className="space-y-2 pt-1 pl-9">
                          {q.options.map((opt: string, optIndex: number) => {
                            const isSelected = selectedOpt === optIndex;
                            const isCorrect = q.correct_index === optIndex;

                            let btnStyle = "bg-white border-slate-200 text-slate-700 hover:bg-slate-100";
                            if (isAnswered) {
                              if (isCorrect) {
                                btnStyle = "bg-emerald-50 border-emerald-400 text-emerald-900 font-medium";
                              } else if (isSelected) {
                                btnStyle = "bg-rose-50 border-rose-400 text-rose-900";
                              } else {
                                btnStyle = "bg-white border-slate-100 text-slate-400 opacity-60";
                              }
                            }

                            return (
                              <button
                                key={optIndex}
                                disabled={isAnswered}
                                onClick={() => setUserAnswers((prev) => ({ ...prev, [qIndex]: optIndex }))}
                                className={`w-full text-left text-xs p-3 rounded-lg border transition-all flex items-center justify-between ${btnStyle}`}
                              >
                                <span>{opt}</span>
                                {isAnswered && isCorrect && (
                                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 ml-2" />
                                )}
                                {isAnswered && isSelected && !isCorrect && (
                                  <XCircle className="w-4 h-4 text-rose-600 shrink-0 ml-2" />
                                )}
                              </button>
                            );
                          })}
                        </div>

                        {/* Explanation */}
                        {isAnswered && (
                          <div className="pl-9 pt-2">
                            <div className="p-3 bg-white border border-slate-200 rounded-lg text-xs text-slate-600 space-y-1">
                              <span className="font-semibold text-indigo-600 uppercase tracking-wider text-[10px]">
                                Explanation
                              </span>
                              <p>{q.explanation}</p>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* 3. Key Terms View */}
            {activeTab === "key_terms" && (
              <div className="max-w-2xl mx-auto space-y-4">
                <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">
                  Key Terminology & Glossary
                </h3>
                <div className="space-y-3">
                  {studyData.items.map((term, i) => (
                    <div key={i} className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm text-indigo-900">{term.term}</span>
                      </div>
                      <p className="text-xs text-slate-700 leading-relaxed">{term.definition}</p>
                      {term.context && (
                        <p className="text-[11px] text-slate-400 italic pt-1 border-t border-slate-200/60">
                          Context: "{term.context}"
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 4. Notes View */}
            {activeTab === "notes" && (
              <div className="max-w-2xl mx-auto space-y-4">
                <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">
                  Structured Study Notes
                </h3>
                <div className="p-6 bg-slate-50 border border-slate-200 rounded-xl text-sm leading-relaxed whitespace-pre-line font-serif text-slate-800">
                  {studyData.notes_content || "No study notes synthesized."}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
