"use client";

import { useState, useEffect, useRef } from "react";

const API_BASE = process.env.NEXT_PUBLIC_RAG_API_URL || "http://localhost:8000";

// Core RAG API query function as specified in the assignment contract
async function askQuestion(question) {
  const response = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || "RAG API request failed");
  }

  return response.json();
}

// Answer and Sources Component displaying verified sources alongside the answer
function AnswerSources({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <section className="sources-container" aria-label="Retrieved sources">
      <div className="sources-title">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
        Retrieved Grounding Sources ({sources.length})
      </div>
      <ul className="sources-list">
        {sources.map((source, index) => (
          <li key={index} className="source-item">
            <div className="source-meta">
              <span className="source-file">{source.source}</span>
              {source.chunk_id && <span className="source-chunk-id">({source.chunk_id})</span>}
            </div>
            {source.score !== null && source.score !== undefined && (
              <span className="source-score-badge">Relevance: {source.score}</span>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastQuestion, setLastQuestion] = useState("");
  const [health, setHealth] = useState({ status: "connecting", indexed_chunks: 0 });
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);

  const chatBottomRef = useRef(null);

  // Poll system health
  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (!res.ok) throw new Error("Health check failed");
      const data = await res.json();
      setHealth(data);
    } catch {
      setHealth({ status: "offline", indexed_chunks: 0 });
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Handle question submission with loading and error states
  async function handleSubmit(questionText) {
    const q = (questionText || inputValue).trim();
    if (!q || loading) return;

    setLoading(true);
    setError(null);
    setLastQuestion(q);
    setInputValue("");

    // Append user message
    setMessages((prev) => [
      ...prev,
      { role: "user", content: q, id: "u_" + Date.now() },
    ]);

    try {
      const result = await askQuestion(q);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources || [],
          status: result.status || "answered",
          id: "a_" + Date.now(),
        },
      ]);
    } catch (err) {
      setError(err.message || "Could not get an answer. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  // Preset query handler
  function handlePresetClick(presetText) {
    handleSubmit(presetText);
  }

  // Clear chat handler
  function handleClearChat() {
    setMessages([]);
    setError(null);
  }

  // Document upload handler
  async function handleDocumentUpload() {
    if (!uploadFile || uploadLoading) return;
    setUploadLoading(true);
    setUploadStatus("Uploading, chunking, embedding, and indexing into ChromaDB...");

    const formData = new FormData();
    formData.append("file", uploadFile);

    try {
      const res = await fetch(`${API_BASE}/documents`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Upload failed with status ${res.status}`);
      }

      const data = await res.json();
      setUploadStatus(
        `✓ Indexed '${data.filename}': ${data.summary.chunks} chunks created (${data.summary.indexed} indexed).`
      );
      setTimeout(() => {
        setUploadModalOpen(false);
        setUploadFile(null);
        setUploadStatus(null);
        checkHealth();
      }, 2000);
    } catch (err) {
      setUploadStatus(`Error: ${err.message}`);
    } finally {
      setUploadLoading(false);
    }
  }

  return (
    <>
      {/* Header */}
      <header className="header">
        <div className="brand">
          <div className="brand-icon" id="brandLogo">SA</div>
          <div className="brand-info">
            <h1 id="brandTitle">SchemeAssist</h1>
            <p id="brandSubtitle">Citizen Welfare RAG Query UI & Citation Inspector</p>
          </div>
        </div>

        <div className="header-actions">
          <div className="status-badge" id="backendHealthBadge" title="Live RAG Backend Health">
            <div className={`status-dot ${health.status !== "healthy" ? "offline" : ""}`} id="statusDot"></div>
            <span id="statusLabel">
              {health.status === "healthy" ? `Online • ${health.indexed_chunks} chunks` : "API Offline"}
            </span>
          </div>

          <button className="btn-header" id="uploadBtn" onClick={() => setUploadModalOpen(true)}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            Upload Document
          </button>

          <button className="btn-header" id="clearBtn" onClick={handleClearChat}>Clear</button>
        </div>
      </header>

      {/* Main Container */}
      <main className="main-container" id="mainSection">
        {/* Welcome Hero (visible before questions are asked) */}
        {messages.length === 0 && (
          <section className="hero-card" id="welcomeHero">
            <h2>Grounded Welfare Scheme Assistant</h2>
            <p>
              Ask any question about subsidies, eligibility criteria, documentation, or coverage for Indian welfare
              policies. Answers are strictly grounded in official circulars and backed by transparent source citations.
            </p>

            <div className="chips-title">Suggested Questions</div>
            <div className="chips-grid" id="presetChips">
              <button
                className="chip-btn"
                id="presetPmkisan"
                onClick={() => handlePresetClick("What is the annual financial assistance provided under PM-KISAN?")}
              >
                🌾 PM-KISAN Installments
              </button>
              <button
                className="chip-btn"
                id="presetAyushman"
                onClick={() => handlePresetClick("What hospitalisation cover is provided under Ayushman Bharat PM-JAY?")}
              >
                🏥 Ayushman Bharat PM-JAY
              </button>
              <button
                className="chip-btn"
                id="presetPmay"
                onClick={() => handlePresetClick("What interest subsidy is offered under PMAY Credit Linked Subsidy Scheme?")}
              >
                🏠 PMAY Housing Subsidy
              </button>
              <button
                className="chip-btn"
                id="presetPension"
                onClick={() => handlePresetClick("What are the age and assistance criteria under the senior citizen pension scheme?")}
              >
                👵 Senior Citizen Pension
              </button>
              <button
                className="chip-btn"
                id="presetVishwakarma"
                onClick={() => handlePresetClick("What toolkit incentive and collateral-free loan support is provided under PM Vishwakarma Scheme?")}
              >
                🔨 PM Vishwakarma Benefits
              </button>
            </div>
          </section>
        )}

        {/* Chat Thread */}
        <div className="chat-thread" id="chatThread">
          {messages.map((msg) => {
            const isUser = msg.role === "user";
            const isRefusal = msg.status && msg.status.startsWith("refused");

            return (
              <div key={msg.id} className={`message-item ${isUser ? "user" : "assistant"} ${isRefusal ? "refusal" : ""}`}>
                {!isUser && <div className="message-avatar">SA</div>}

                <div className="message-content">
                  <div className="bubble">
                    {!isUser && (
                      <div className={`badge-status ${isRefusal ? "refused" : "answered"}`}>
                        {isRefusal ? `⚠️ Notice: Refusal (${msg.status})` : "✓ Grounded Answer"}
                      </div>
                    )}

                    <div className="message-text">{msg.content}</div>

                    {!isUser && msg.sources && msg.sources.length > 0 && (
                      <AnswerSources sources={msg.sources} />
                    )}
                  </div>
                </div>

                {isUser && <div className="message-avatar" title="You">U</div>}
              </div>
            );
          })}

          {/* Loading Indicator */}
          {loading && (
            <div className="message-item assistant" id="loadingIndicator">
              <div className="message-avatar">SA</div>
              <div className="message-content">
                <div className="bubble">
                  <div className="loading-box">
                    <div className="spinner-icon"></div>
                    <span>Searching vector database & synthesizing grounded answer...</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Error Banner */}
          {error && (
            <div className="error-banner" id="errorBanner">
              <span><strong>Error:</strong> {error}</span>
              <button className="btn-retry" id="btnRetry" onClick={() => handleSubmit(lastQuestion)}>Retry</button>
            </div>
          )}

          <div ref={chatBottomRef} />
        </div>
      </main>

      {/* Sticky Bottom Floating Input Dock */}
      <div className="input-dock">
        <div className="input-wrapper">
          <form
            className="input-form"
            id="chatForm"
            onSubmit={(e) => {
              e.preventDefault();
              handleSubmit();
            }}
          >
            <input
              type="text"
              className="chat-input"
              id="questionInput"
              placeholder="Ask a question about government welfare schemes..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={loading}
              autoComplete="off"
            />
            <button
              type="submit"
              className="btn-send"
              id="submitQuestionBtn"
              disabled={loading || !inputValue.trim()}
              aria-label="Send question"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </form>
        </div>
      </div>

      {/* Document Upload Modal */}
      {uploadModalOpen && (
        <div className="modal-overlay" id="uploadModalDialog">
          <div className="modal-box">
            <h3>Upload Policy Document</h3>
            <p>
              Upload a new welfare policy document (.md, .txt, .pdf, .html). It will be cleaned, chunked, embedded, and
              indexed into the ChromaDB vector database at runtime without restarting.
            </p>

            <div
              className="dropzone-area"
              id="modalDropzone"
              onClick={() => document.getElementById("fileChooser").click()}
            >
              <input
                type="file"
                id="fileChooser"
                accept=".md,.txt,.pdf,.html"
                style={{ display: "none" }}
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setUploadFile(e.target.files[0]);
                  }
                }}
              />
              <p>
                {uploadFile
                  ? `Selected: ${uploadFile.name} (${(uploadFile.size / 1024).toFixed(1)} KB)`
                  : "Click to select or drop policy document here"}
              </p>
              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Supported: .md, .txt, .pdf, .html (Max 10MB)
              </span>
            </div>

            {uploadStatus && (
              <div
                id="modalUploadStatus"
                style={{
                  fontSize: "0.82rem",
                  marginBottom: "1rem",
                  color: uploadStatus.startsWith("✓") ? "#34d399" : uploadStatus.startsWith("Error") ? "#f87171" : "#a5b4fc",
                }}
              >
                {uploadStatus}
              </div>
            )}

            <div className="modal-footer">
              <button
                className="btn-modal-cancel"
                id="btnCancelUpload"
                onClick={() => {
                  setUploadModalOpen(false);
                  setUploadFile(null);
                  setUploadStatus(null);
                }}
                disabled={uploadLoading}
              >
                Cancel
              </button>
              <button
                className="btn-modal-submit"
                id="btnConfirmUpload"
                onClick={handleDocumentUpload}
                disabled={!uploadFile || uploadLoading}
              >
                {uploadLoading ? "Indexing..." : "Upload & Index"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
