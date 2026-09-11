import React from 'react';
import {
  Bot,
  User,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  ShieldCheck,
  Gift,
  FileCheck2,
  ListOrdered,
  Sparkles,
} from 'lucide-react';
import Avatar from '../ui/Avatar';
import Badge from '../ui/Badge';
import SourceCitation from './SourceCitation';

export function ChatMessage({ message }) {
  const isUser = message.sender === 'user';
  const isError = message.isError;
  const isRefusal = message.status === 'refused_weak_context';

  const answerText = message.text || message.answer || '';
  const eligibility = message.eligibility || '';
  const benefits = message.benefits || '';
  const applicationProcess = Array.isArray(message.application_process) ? message.application_process : [];
  const documentsRequired = Array.isArray(message.documents_required) ? message.documents_required : [];
  const sources = Array.isArray(message.sources) ? message.sources : [];
  const answerMode = message.answer_mode || 'general_ai';

  return (
    <div className={`flex gap-3 my-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-btn bg-navy text-white flex items-center justify-center font-extrabold text-xs shrink-0 shadow-subtle mt-0.5">
          SA
        </div>
      )}

      <div
        className={`max-w-2xl rounded-card p-4 shadow-subtle ${isUser
            ? 'bg-primary text-white rounded-tr-none'
            : isError
              ? 'bg-red-50/80 border border-red-200 text-red-900 rounded-tl-none'
              : 'bg-white border border-slate-border text-slate-text rounded-tl-none'
          }`}
      >
        {/* Header tag for AI status */}
        {!isUser && !isError && (
          <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-border/50 text-[11px]">
            <span className="font-bold text-navy flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-primary" />
              SchemeAssist AI
            </span>
            {isRefusal ? (
              <Badge variant="warning" size="sm">
                Policy Refusal / Out of Scope
              </Badge>
            ) : answerMode === 'verified_rag' ? (
              <Badge variant="success" size="sm" dot>
                Verified Government Document
              </Badge>
            ) : (
              <Badge variant="warning" size="sm" dot>
                AI Generated Information
              </Badge>
            )}
          </div>
        )}

        {/* Error message card */}
        {isError && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-red-700 font-bold text-xs">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>Backend & OpenAI Service Notice</span>
            </div>
            <p className="text-xs text-red-800 leading-relaxed whitespace-pre-wrap font-medium">
              {message.text || 'An error occurred while contacting the live SchemeAssist backend.'}
            </p>
          </div>
        )}

        {/* AI Answer Text */}
        {!isError && (
          <div className={`text-xs md:text-sm leading-relaxed whitespace-pre-wrap ${isUser ? 'text-white font-medium' : 'text-slate-800 font-normal'}`}>
            {answerText}
          </div>
        )}

        {/* Structured Welfare Sections */}
        {!isUser && !isError && !isRefusal && (
          <div className="mt-3.5 space-y-3">
            {answerMode === 'general_ai' && (
              <p className="text-[11px] leading-relaxed text-amber-800 bg-amber-50 border border-amber-200 rounded-card px-3 py-2">
                This answer uses general scheme knowledge. Verify important details with the official government authority.
              </p>
            )}
            {/* 1. Eligibility Criteria */}
            {eligibility && (
              <div className="p-3 rounded-card bg-emerald-50/60 border border-emerald-200 text-xs">
                <div className="flex items-center gap-1.5 font-bold text-emerald-900 mb-1">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span>Eligibility Criteria</span>
                </div>
                <p className="text-slate-700 leading-relaxed pl-5">
                  {eligibility}
                </p>
              </div>
            )}

            {/* 2. Scheme Benefits */}
            {benefits && (
              <div className="p-3 rounded-card bg-amber-50/60 border border-amber-200 text-xs">
                <div className="flex items-center gap-1.5 font-bold text-amber-900 mb-1">
                  <Gift className="w-4 h-4 text-amber-600" />
                  <span>Scheme Benefits & Financial Assistance</span>
                </div>
                <p className="text-slate-700 leading-relaxed pl-5">
                  {benefits}
                </p>
              </div>
            )}

            {/* 3. Application Process */}
            {applicationProcess.length > 0 && (
              <div className="p-3 rounded-card bg-blue-50/50 border border-blue-200 text-xs">
                <div className="flex items-center gap-1.5 font-bold text-blue-900 mb-2">
                  <ListOrdered className="w-4 h-4 text-blue-600" />
                  <span>Application Process</span>
                </div>
                <ol className="space-y-1.5 pl-2">
                  {applicationProcess.map((step, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-slate-700">
                      <span className="w-4 h-4 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      <span className="leading-tight">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* 4. Required Documents */}
            {documentsRequired.length > 0 && (
              <div className="p-3 rounded-card bg-slate-50 border border-slate-200 text-xs">
                <div className="flex items-center gap-1.5 font-bold text-slate-800 mb-2">
                  <FileCheck2 className="w-4 h-4 text-primary" />
                  <span>Required Documents</span>
                </div>
                <div className="flex flex-wrap gap-1.5 pl-1">
                  {documentsRequired.map((doc, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white border border-slate-300 text-slate-700 text-[11px] font-medium shadow-xs"
                    >
                      <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
                      {doc}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* 5. Sources Citations Drawer */}
            {sources.length > 0 && (
              <SourceCitation sources={sources} />
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-btn bg-slate-200 text-slate-700 flex items-center justify-center font-bold text-xs shrink-0 shadow-subtle mt-0.5">
          You
        </div>
      )}
    </div>
  );
}

import { Paperclip, Mic, Send } from 'lucide-react';
import Button from '../ui/Button';

export function ChatInput({
  input,
  setInput,
  onSend,
  isLoading,
  onAttachment,
}) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSend(input.trim());
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative bg-white border border-slate-border rounded-card shadow-subtle p-2">
      <textarea
        rows={2}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about government schemes (e.g., 'What is the annual benefit of PM-KISAN?')..."
        disabled={isLoading}
        className="w-full text-xs md:text-sm text-slate-text placeholder:text-slate-400 resize-none focus:outline-none p-2 bg-transparent"
      />

      <div className="flex items-center justify-between pt-2 border-t border-slate-border/50 px-2">
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={onAttachment}
            title="Upload supporting document"
            className="p-1.5 rounded-btn text-slate-400 hover:text-navy hover:bg-slate-100 transition-colors"
          >
            <Paperclip className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => alert("Voice transcription input initialized.")}
            title="Voice input"
            className="p-1.5 rounded-btn text-slate-400 hover:text-primary hover:bg-slate-100 transition-colors"
          >
            <Mic className="w-4 h-4" />
          </button>
        </div>

        <Button
          type="submit"
          variant="primary"
          size="sm"
          isLoading={isLoading}
          disabled={!input.trim() || isLoading}
          icon={Send}
        >
          Send
        </Button>
      </div>
    </form>
  );
}

export default ChatMessage;
