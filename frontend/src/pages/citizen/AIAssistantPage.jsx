import React, { useState, useRef, useEffect } from 'react';
import { RefreshCw, FolderLock } from 'lucide-react';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';
import { ChatMessage, ChatInput } from '../../components/chat/ChatMessage';
import { SuggestedQuestions } from '../../components/chat/SourceCitation';
import { UploadModal } from '../../components/documents/DocumentCard';
import { chatWithSchemeAssist, getSystemHealth } from '../../services/api';
import { recordActivity } from '../../services/activityLogService';

export function AIAssistantPage() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'assistant',
      text: `Hello! 👋\n\nI am your SchemeAssist AI, connected live to official government welfare scheme circulars.\n\nI can help you:\n• Check eligibility criteria & income limits (PM-KISAN, Ayushman Bharat, etc.)\n• Understand financial benefits, subsidies, and payment schedules\n• View required documents & certificates\n• Step-by-step application guidance directly grounded in government circulars`,
      sources: []
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [backendHealth, setBackendHealth] = useState(null);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const requestInFlightRef = useRef(false);

  useEffect(() => {
    // Check backend health
    getSystemHealth()
      .then((health) => setBackendHealth(health))
      .catch((err) => setBackendHealth({ status: 'offline', error: err.message }));
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (queryText) => {
    const text = (queryText || input).trim();
    if (!text || isLoading || requestInFlightRef.current) return;

    requestInFlightRef.current = true;

    // Add user message
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatWithSchemeAssist(text);
      const assistantMsg = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: response.answer || "I could not find this information in the available scheme documents.",
        answer: response.answer || "",
        eligibility: response.eligibility || "",
        benefits: response.benefits || "",
        application_process: response.application_process || [],
        documents_required: response.documents_required || [],
        sources: response.sources || [],
        answer_mode: response.answer_mode || 'general_ai',
        status: response.status || 'answered'
      };
      recordActivity({
        level: response.status === 'answered' ? 'SUCCESS' : 'WARN',
        source: 'AI',
        message: `User asked: ${text}`,
        details: `User query:\n${text}\n\nAI response:\n${response.answer || 'No answer returned.'}\n\nAnswer mode: ${response.answer_mode || 'general_ai'}\nSources: ${(response.sources || []).map((source) => source.source || source.scheme || 'Unknown').join(', ') || 'None'}`,
      });
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: `${err.message || 'Error communicating with the SchemeAssist backend service.'}`,
        isError: true,
        sources: []
      };
      recordActivity({
        level: 'ERROR',
        source: 'AI',
        message: `AI request failed for user query: ${text}`,
        details: `User query:\n${text}\n\nError:\n${err.message || 'Unknown AI service error.'}`,
      });
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      requestInFlightRef.current = false;
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-8.5rem)] animate-fadeIn">
      {/* Header Banner */}
      <div className="bg-white border border-slate-border rounded-t-card p-4 shadow-subtle flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-btn bg-navy text-white flex items-center justify-center font-extrabold text-sm shadow-subtle">
            SA
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-extrabold text-navy leading-none">SchemeAssist AI</h2>
              <Badge variant={backendHealth?.status === 'healthy' ? 'success' : 'warning'} size="sm" dot>
                {backendHealth?.status === 'healthy' ? 'AI service online' : 'AI service unavailable'}
              </Badge>
            </div>
            <p className="text-xs text-slate-muted mt-1 leading-none">
              Your Government Scheme Assistant &bull; Knowledge Base: {backendHealth?.indexed_chunks || 26} Chunks Indexed
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={FolderLock}
            onClick={() => setUploadModalOpen(true)}
            className="hidden sm:inline-flex"
          >
            Ingest Document
          </Button>
          <Button
            variant="ghost"
            size="sm"
            icon={RefreshCw}
            onClick={() => {
              setMessages([messages[0]]);
            }}
            title="Reset Chat"
          >
            Reset
          </Button>
        </div>
      </div>

      {/* Chat Messages Stream */}
      <div className="flex-1 overflow-y-auto bg-slate-bg/50 border-x border-slate-border p-4 md:p-6 space-y-2">
        {messages.map((m) => (
          <ChatMessage key={m.id} message={m} />
        ))}

        {isLoading && (
          <div className="flex items-center gap-3 my-4">
            <div className="w-8 h-8 rounded-btn bg-navy text-white flex items-center justify-center font-bold text-xs shrink-0">
              SA
            </div>
            <div className="p-4 rounded-card bg-white border border-slate-border text-xs text-slate-500 shadow-subtle flex items-center gap-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
              <span>Synthesizing grounded answer from official scheme gazettes...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions & Input Bar */}
      <div className="bg-white border border-slate-border rounded-b-card p-3 shadow-subtle space-y-3 shrink-0">
        <SuggestedQuestions onSelect={handleSend} disabled={isLoading} />

        <ChatInput
          input={input}
          setInput={setInput}
          onSend={handleSend}
          isLoading={isLoading}
          onAttachment={() => setUploadModalOpen(true)}
        />
      </div>

      {/* Ingest Document Modal */}
      <UploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUploadSuccess={(doc) => {
          // Recheck health
          getSystemHealth().then((h) => setBackendHealth(h));
        }}
      />
    </div>
  );
}

export default AIAssistantPage;
