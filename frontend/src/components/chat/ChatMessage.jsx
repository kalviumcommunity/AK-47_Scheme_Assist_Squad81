import React from 'react';
import { Bot, User, CheckCircle2, AlertCircle } from 'lucide-react';
import Avatar from '../ui/Avatar';
import Badge from '../ui/Badge';
import SourceCitation from './SourceCitation';

export function ChatMessage({ message }) {
  const isUser = message.sender === 'user';
  const isError = message.isError;
  const isRefusal = message.status === 'refused_weak_context';

  return (
    <div className={`flex gap-3 my-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-btn bg-navy text-white flex items-center justify-center font-extrabold text-xs shrink-0 shadow-subtle mt-0.5">
          SA
        </div>
      )}

      <div
        className={`max-w-2xl rounded-card p-4 shadow-subtle ${
          isUser
            ? 'bg-primary text-white rounded-tr-none'
            : isError
            ? 'bg-gov-error-light border border-gov-error/20 text-gov-error rounded-tl-none'
            : 'bg-white border border-slate-border text-slate-text rounded-tl-none'
        }`}
      >
        {/* Header tag for AI status */}
        {!isUser && !isError && (
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-border/50 text-[11px]">
            <span className="font-bold text-navy flex items-center gap-1.5">
              SchemeAssist AI
            </span>
            {isRefusal ? (
              <Badge variant="warning" size="sm">
                Policy Refusal / Out of Scope
              </Badge>
            ) : (
              <Badge variant="success" size="sm" dot>
                Grounded via ChromaDB
              </Badge>
            )}
          </div>
        )}

        {/* Message Body with clean paragraph & bullet formatting */}
        <div className={`text-xs md:text-sm leading-relaxed space-y-2 whitespace-pre-wrap ${isUser ? 'text-white' : 'text-slate-700'}`}>
          {message.text}
        </div>

        {/* Retrieved sources citations drawer */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <SourceCitation sources={message.sources} />
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
