import React, { useEffect, useState } from 'react';
import Card from '../../components/ui/Card';
import Badge from '../../components/ui/Badge';
import Button from '../../components/ui/Button';
import Modal from '../../components/ui/Modal';
import { FolderOpen, FileCheck2, Search, RefreshCw, XCircle, CheckCircle2 } from 'lucide-react';
import { listUploadedDocuments } from '../../services/api';
import { UploadModal } from '../../components/documents/DocumentCard';
import { fetchDocumentFile, setDocumentReviewStatus } from '../../services/documentService';

export function AdminDocumentsPage() {
  const [search, setSearch] = useState('');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [preview, setPreview] = useState(null);
  const [previewError, setPreviewError] = useState(null);

  const loadDocuments = async () => {
    setLoading(true);
    try { const result = await listUploadedDocuments(); setDocuments(result.documents || []); setError(null); }
    catch (err) { setError(err.message || 'Unable to load documents.'); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadDocuments(); }, []);

  const filtered = documents.filter((document) => document.filename?.toLowerCase().includes(search.toLowerCase()));

  const handleReject = (filename) => {
    if (!window.confirm(`Reject ${filename}? The document will be marked as rejected for review.`)) return;
    setDocumentReviewStatus(filename, 'Rejected');
    setDocuments((previous) => previous.map((document) => document.filename === filename ? { ...document, status: 'Rejected' } : document));
  };

  const handleApprove = (filename) => {
    setDocumentReviewStatus(filename, 'Approved');
    setDocuments((previous) => previous.map((document) => document.filename === filename ? { ...document, status: 'Approved' } : document));
  };

  const handleView = async (document) => {
    setPreviewError(null);
    try {
      const file = await fetchDocumentFile(document.filename);
      const isText = /\.(txt|md|html?)$/i.test(document.filename);
      if (isText) {
        setPreview({ document, text: await file.text(), isText: true });
      } else {
        setPreview({ document, url: URL.createObjectURL(file), isText: false });
      }
    } catch (err) {
      setPreviewError(err.message || 'Unable to preview this document.');
    }
  };

  const closePreview = () => {
    if (preview?.url) URL.revokeObjectURL(preview.url);
    setPreview(null);
    setPreviewError(null);
  };

  const statusVariant = (status) => status === 'Rejected' ? 'danger' : status === 'Approved' ? 'success' : 'warning';

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <FolderOpen className="w-5 h-5 text-blue-600" />
            <h1 className="text-xl font-black text-slate-800">Citizen Document Verification Vault</h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">Uploaded knowledge-base documents and their indexing state.</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2"><Button variant="primary" size="sm" onClick={() => setUploadOpen(true)}>Upload document</Button><Badge variant="navy" size="sm">{documents.length} Documents</Badge><button onClick={loadDocuments} title="Refresh documents" className="p-2 rounded-btn text-slate-500 hover:bg-slate-100"><RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /></button></div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by citizen, document name, or scheme..."
            className="w-full pl-9 pr-4 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          />
        </div>
      </div>

      {error && <div className="p-3 rounded-card bg-gov-error-light border border-gov-error/20 text-xs text-gov-error">{error}</div>}

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3.5 px-4">File name</th><th className="py-3.5 px-4">Type</th><th className="py-3.5 px-4">Size</th><th className="py-3.5 px-4">Status</th><th className="py-3.5 px-4">Path</th><th className="py-3.5 px-4 text-right">Review</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              {!loading && filtered.map((doc) => (
                <tr key={doc.filename} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3.5 px-4 font-bold text-slate-900"><FileCheck2 className="w-3.5 h-3.5 text-blue-500 inline mr-1.5" />{doc.filename}</td>
                  <td className="py-3.5 px-4 text-slate-600">{doc.filename?.split('.').pop()?.toUpperCase()}</td>
                  <td className="py-3.5 px-4 text-slate-500">{(Number(doc.size_bytes || 0) / 1024).toFixed(1)} KB</td>
                  <td className="py-3.5 px-4">
                    <Badge variant={statusVariant(doc.status)} size="sm" dot>{doc.status || 'Pending Review'}</Badge>
                  </td>
                  <td className="py-3.5 px-4 text-slate-500 font-mono text-[10px]">{doc.path || '—'}</td>
                  <td className="py-3.5 px-4 text-right"><div className="flex items-center justify-end gap-2"><Button variant="outline" size="sm" onClick={() => handleView(doc)}>View</Button>{doc.status !== 'Approved' && doc.status !== 'Rejected' && <><Button variant="success" size="sm" icon={CheckCircle2} onClick={() => handleApprove(doc.filename)}>Approve</Button><Button variant="danger" size="sm" icon={XCircle} onClick={() => handleReject(doc.filename)}>Reject</Button></>}{doc.status === 'Approved' && <span className="text-[11px] text-gov-success font-semibold">Approved</span>}{doc.status === 'Rejected' && <span className="text-[11px] text-gov-error font-semibold">Rejected</span>}</div></td>
                </tr>
              ))}
              {!loading && filtered.length === 0 && <tr><td colSpan="6" className="py-10 text-center text-xs text-slate-500">No backend documents match this search.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
      <UploadModal isOpen={uploadOpen} onClose={() => setUploadOpen(false)} onUploadSuccess={loadDocuments} />
      <Modal isOpen={Boolean(preview || previewError)} onClose={closePreview} title={preview?.document?.filename || 'Document preview'} subtitle="Uploaded scheme application document" maxWidth="max-w-5xl">
        {previewError && <p className="text-xs text-gov-error">{previewError}</p>}
        {preview?.isText && <pre className="max-h-[65vh] overflow-auto whitespace-pre-wrap rounded-btn bg-slate-950 p-4 text-xs text-slate-100">{preview.text}</pre>}
        {preview && !preview.isText && <iframe title={`Preview of ${preview.document.filename}`} src={preview.url} className="h-[65vh] w-full rounded-btn border border-slate-border" />}
      </Modal>
    </div>
  );
}

export default AdminDocumentsPage;
