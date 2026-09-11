import React, { useEffect, useState } from 'react';
import {
  FolderLock,
  UploadCloud,
  FileCheck2,
  Clock,
  ShieldCheck,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';
import Modal from '../../components/ui/Modal';
import { DocumentCard, UploadModal } from '../../components/documents/DocumentCard';
import { listUploadedDocuments } from '../../services/api';
import { deleteDocumentFile, fetchDocumentFile } from '../../services/documentService';

function normalizeDocument(document) {
  const filename = document.filename || document.name || 'Unnamed document';
  return {
    ...document,
    id: filename,
    name: filename.replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' '),
    filename,
    type: filename.split('.').pop()?.toUpperCase() || 'FILE',
    size: `${(Number(document.size_bytes || 0) / (1024 * 1024)).toFixed(2)} MB`,
    uploadDate: document.upload_date || 'Available in backend',
    status: document.status || 'Pending Review',
  };
}

export function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [preview, setPreview] = useState(null);
  const [previewError, setPreviewError] = useState(null);

  const loadDocuments = async () => {
    setIsLoading(true);
    try {
      const result = await listUploadedDocuments();
      setDocuments((result.documents || []).map(normalizeDocument));
      setError(null);
    } catch (err) {
      setError(err.message || 'Unable to load your documents.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
    const refresh = () => loadDocuments();
    window.addEventListener('storage', refresh);
    const interval = setInterval(refresh, 3000);
    return () => {
      window.removeEventListener('storage', refresh);
      clearInterval(interval);
    };
  }, []);

  const totalCount = documents.length;
  const approvedCount = documents.filter((d) => d.status === 'Approved').length;
  const rejectedCount = documents.filter((d) => d.status === 'Rejected').length;

  const handleUploadSuccess = (newDoc) => {
    loadDocuments();
  };

  const handleView = async (document) => {
    setPreviewError(null);
    try {
      const file = await fetchDocumentFile(document.filename);
      const isText = /\.(txt|md|html?)$/i.test(document.filename);
      setPreview({
        document,
        isText,
        ...(isText ? { text: await file.text() } : { url: URL.createObjectURL(file) }),
      });
    } catch (err) {
      setPreviewError(err.message || 'Unable to preview this document.');
    }
  };

  const handleDelete = async (document) => {
    if (!window.confirm(`Delete ${document.filename}? This removes the file and its indexed knowledge-base chunks.`)) return;
    try {
      await deleteDocumentFile(document.filename);
      await loadDocuments();
    } catch (err) {
      setError(err.message || 'Unable to delete this document.');
    }
  };

  const closePreview = () => {
    if (preview?.url) URL.revokeObjectURL(preview.url);
    setPreview(null);
    setPreviewError(null);
  };

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy tracking-tight">
            My Documents
          </h1>
          <p className="text-xs sm:text-sm text-slate-muted mt-1">
            Manage, verify, and store certificates for instant welfare scheme attestation.
          </p>
        </div>
        <Button
          variant="primary"
          size="md"
          icon={UploadCloud}
          onClick={() => setUploadModalOpen(true)}
        >
          Upload New Document
        </Button>
      </div>

      <div className="bg-primary-50/70 border border-primary/20 rounded-card p-4 flex items-start gap-3 text-xs text-primary">
        <ShieldCheck className="w-5 h-5 shrink-0 mt-0.5" />
        <div>
          <p className="font-bold text-navy">Your documents are for scheme applications</p>
          <p className="mt-1 leading-relaxed">Upload only the documents needed to apply for a government scheme. Your uploaded documents are stored in the SchemeAssist knowledge base and are visible to authorized administrators for application review.</p>
        </div>
      </div>

      {/* Document Summary Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-card bg-navy/10 text-navy border border-navy/20 flex items-center justify-center shrink-0">
            <FolderLock className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-muted uppercase tracking-wider">Total Documents</p>
            <h3 className="text-2xl font-black text-navy mt-0.5">{totalCount}</h3>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-card bg-gov-success-light text-gov-success border border-gov-success/20 flex items-center justify-center shrink-0">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-muted uppercase tracking-wider">Approved Documents</p>
            <h3 className="text-2xl font-black text-navy mt-0.5">{approvedCount}</h3>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-card bg-gov-warning-light text-gov-warning border border-gov-warning/20 flex items-center justify-center shrink-0">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-muted uppercase tracking-wider">Rejected Documents</p>
            <h3 className="text-2xl font-black text-navy mt-0.5">{rejectedCount}</h3>
          </div>
        </Card>
      </div>

      {/* Document Security Notice */}
      <div className="bg-primary-50/60 border border-primary/20 rounded-card p-4 flex items-center gap-3 text-xs text-primary">
        <ShieldCheck className="w-5 h-5 shrink-0" />
        <span>Documents are sent to the SchemeAssist knowledge base for processing. Do not upload information that is not required for your scheme question.</span>
      </div>

      {error && <div className="p-3 rounded-card bg-gov-error-light border border-gov-error/20 text-xs text-gov-error">{error}</div>}

      {/* Document Cards Grid */}
      <div>
        <h2 className="text-sm font-bold text-navy uppercase tracking-wider mb-1">
          Scheme Application Documents ({totalCount})
        </h2>
        <p className="text-xs text-slate-muted mb-4">Documents uploaded here can be reviewed by authorized administrators when processing applications.</p>
        {isLoading ? <div className="py-10 text-center text-xs text-slate-muted">Loading documents from SchemeAssist...</div> : documents.length === 0 ? <div className="py-10 text-center text-xs text-slate-muted">No documents have been uploaded yet.</div> : <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.map((doc, idx) => (
            <DocumentCard
              key={doc.id || idx}
              doc={doc}
              onView={handleView}
              onDelete={handleDelete}
              onReplace={(d) => setUploadModalOpen(true)}
            />
          ))}
        </div>}
      </div>

      {/* Upload Modal connected to FastAPI /documents */}
      <UploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
      <Modal isOpen={Boolean(preview || previewError)} onClose={closePreview} title={preview?.document?.filename || 'Document preview'} subtitle="Your uploaded scheme application document" maxWidth="max-w-5xl">
        {previewError && <p className="text-xs text-gov-error">{previewError}</p>}
        {preview?.isText && <pre className="max-h-[65vh] overflow-auto whitespace-pre-wrap rounded-btn bg-slate-950 p-4 text-xs text-slate-100">{preview.text}</pre>}
        {preview && !preview.isText && <iframe title={`Preview of ${preview.document.filename}`} src={preview.url} className="h-[65vh] w-full rounded-btn border border-slate-border" />}
      </Modal>
    </div>
  );
}

export default DocumentsPage;
