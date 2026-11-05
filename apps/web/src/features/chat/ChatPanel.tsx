"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Sparkles,
  BookOpen,
  CheckCircle,
  AlertCircle,
  Copy,
  ChevronDown,
  Info,
  ExternalLink,
  Coins
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { ChatMessage, ChatCitation, TokenUsage } from "@/lib/types";
import { api } from "@/lib/api";

interface ChatPanelProps {
  documentId?: string;
  documentTitle?: string;
  onCitationClick?: (pageNumber: number) => void;
  externalPrompt?: string | null;
  onClearExternalPrompt?: () => void;
}

export function ChatPanel({
  documentId,
  documentTitle,
  onCitationClick,
  externalPrompt,
  onClearExternalPrompt
}: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Suggested prompt pills
  const samplePrompts = [
    "What is the main objective of this document?",
    "Summarize the key findings and methodology.",
    "What are the limitations mentioned?",
    "Explain the core concept in simpler terms."
  ];

  // Auto-fill prompt if external trigger arrives (e.g. from text selection "Ask AI")
  useEffect(() => {
    if (externalPrompt) {
      setInputQuery(externalPrompt);
      if (onClearExternalPrompt) onClearExternalPrompt();
    }
  }, [externalPrompt, onClearExternalPrompt]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: "usr-" + Date.now(),
      role: "user",
      content: textToSend.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery("");
    setIsLoading(true);

    try {
      const history = messages.slice(-4).map((m) => ({ role: m.role, content: m.content }));
      const response = await api.sendChatMessage({
        query: textToSend.trim(),
        document_id: documentId,
        conversation_history: history,
      });

      const assistantMsg: ChatMessage = {
        id: "ast-" + Date.now(),
        role: "assistant",
        content: response.answer,
        citations: response.citations,
        token_usage: response.token_usage,
        is_mock: response.is_mock,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: "err-" + Date.now(),
        role: "assistant",
        content: "⚠️ " + (err.message || "Failed to generate answer. Please verify connection to the AI backend."),
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Chat Header */}
      <div className="h-12 border-b border-slate-200 px-4 flex items-center justify-between shrink-0 bg-slate-50/50">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-600" />
          <h3 className="text-xs font-semibold text-slate-800">
            {documentTitle ? `Grounded Q&A: ${documentTitle}` : "Document Intelligence Assistant"}
          </h3>
        </div>
        <Badge variant="outline" className="text-[10px]">
          Strict Grounding
        </Badge>
      </div>

      {/* Messages Thread */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12 px-4 space-y-4">
            <div className="w-10 h-10 rounded-full bg-indigo-50 text-indigo-600 mx-auto flex items-center justify-center">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-900">
                Ask anything about your document
              </h4>
              <p className="text-xs text-slate-500 mt-1 max-w-xs mx-auto">
                Answers are grounded strictly in the text with verified page citations.
              </p>
            </div>

            <div className="pt-2 flex flex-col gap-1.5 max-w-sm mx-auto">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider text-left pl-1">
                Suggested questions
              </span>
              {samplePrompts.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(prompt)}
                  className="text-left text-xs p-2.5 rounded-lg border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/50 text-slate-700 transition-all font-medium"
                >
                  "{prompt}"
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
            >
              <div
                className={`max-w-[88%] rounded-2xl p-4 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-indigo-600 text-white rounded-br-none shadow-sm"
                    : "bg-slate-50 border border-slate-200 text-slate-900 rounded-bl-none"
                }`}
              >
                {/* Answer text */}
                <div className="whitespace-pre-wrap">{msg.content}</div>

                {/* Citations Footer */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-200/80 space-y-1.5">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                      Sources & Page Citations:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {msg.citations.map((c) => (
                        <button
                          key={c.citation_id}
                          onClick={() => c.page_number && onCitationClick && onCitationClick(c.page_number)}
                          className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-white border border-slate-300 hover:border-indigo-400 hover:bg-indigo-50 text-xs font-medium text-slate-700 hover:text-indigo-700 transition-all shadow-xs"
                          title={`Click to jump to Page ${c.page_number || 1}\n\n"${c.snippet}"`}
                        >
                          <BookOpen className="w-3 h-3 text-indigo-600" />
                          <span>[{c.citation_id}] Page {c.page_number || 1}</span>
                          <ExternalLink className="w-2.5 h-2.5 text-slate-400" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Tokens and Model info */}
                {msg.token_usage && (
                  <div className="mt-2 text-[10px] text-slate-400 flex items-center justify-between">
                    <span>{msg.token_usage.total_tokens} tokens</span>
                    {msg.is_mock && <span className="font-semibold text-amber-600">Simulated Mock Engine</span>}
                  </div>
                )}
              </div>

              {msg.role === "assistant" && (
                <div className="flex items-center gap-2 mt-1 px-1">
                  <button
                    onClick={() => handleCopy(msg.content, msg.id)}
                    className="text-[11px] text-slate-400 hover:text-slate-600 flex items-center gap-1"
                  >
                    {copiedId === msg.id ? (
                      <>
                        <CheckCircle className="w-3 h-3 text-emerald-500" /> Copied
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" /> Copy
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex items-start">
            <div className="bg-slate-50 border border-slate-200 rounded-2xl rounded-bl-none p-4 text-xs text-slate-500 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-600 animate-ping" />
              Searching vector chunks & synthesizing grounded response...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="p-3 border-t border-slate-200 bg-slate-50/50">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask a question about this document..."
            disabled={isLoading}
            className="flex-1 bg-white border border-slate-300 rounded-xl px-4 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
          />
          <Button
            type="submit"
            disabled={!inputQuery.trim() || isLoading}
            size="icon"
            className="rounded-xl shrink-0"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
