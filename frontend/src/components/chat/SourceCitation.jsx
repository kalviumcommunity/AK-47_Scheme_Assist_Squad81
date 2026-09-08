import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronUp, Sparkles, ExternalLink } from 'lucide-react';
import Badge from '../ui/Badge';

export function SourceCitation({ sources = [] }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-slate-border">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full text-xs font-semibold text-slate-muted hover:text-navy transition-colors py-1"
      >
        <div className="flex items-center gap-1.5">
          <FileText className="w-3.5 h-3.5 text-primary" />
          <span>Retrieved Official Sources ({sources.length})</span>
        </div>
        {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
      </button>

      {isOpen && (
        <div className="mt-2 space-y-2 animate-fadeIn">
          {sources.map((src, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-btn bg-slate-50 border border-slate-border flex items-center justify-between gap-3 text-xs"
            >
              <div className="flex items-center gap-2 overflow-hidden">
                <span className="w-5 h-5 rounded bg-white border border-slate-border flex items-center justify-center text-[10px] font-bold text-slate-500 shrink-0">
                  {idx + 1}
                </span>
                <div className="truncate">
                  <span className="font-semibold text-navy truncate block">
                    {src.source}
                  </span>
                  {src.chunk_id && (
                    <span className="text-[10px] text-slate-400 font-mono">
                      {src.chunk_id}
                    </span>
                  )}
                </div>
              </div>

              {src.score !== undefined && src.score !== null && (
                <Badge variant="primary" size="sm" className="shrink-0 font-mono">
                  Relevance: {Number(src.score).toFixed(4)}
                </Badge>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function SuggestedQuestions({ onSelect, disabled = false }) {
  const questions = [
    "What schemes am I eligible for?",
    "How do I apply for PM-KISAN?",
    "What documents do I need for Ayushman Bharat?",
    "Show welfare benefits for smallholder farmers."
  ];

  return (
    <div className="flex flex-wrap gap-2 pt-2">
      {questions.map((q, idx) => (
        <button
          key={idx}
          onClick={() => !disabled && onSelect(q)}
          disabled={disabled}
          className="text-xs px-3 py-1.5 rounded-btn bg-white hover:bg-slate-50 text-slate-700 border border-slate-border hover:border-primary/40 font-medium transition-all shadow-subtle flex items-center gap-1.5 active:scale-95 disabled:opacity-50"
        >
          <Sparkles className="w-3 h-3 text-primary" />
          <span>{q}</span>
        </button>
      ))}
    </div>
  );
}

export default SourceCitation;
