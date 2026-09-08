import React, { useState } from 'react';
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
import { DocumentCard, UploadModal } from '../../components/documents/DocumentCard';
import { MOCK_DOCUMENTS } from '../../data/mockCitizenData';

export function DocumentsPage() {
  const [documents, setDocuments] = useState(MOCK_DOCUMENTS);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [previewDoc, setPreviewDoc] = useState(null);

  const totalCount = documents.length;
  const verifiedCount = documents.filter((d) => d.status === 'Verified' || d.verified).length;
  const pendingCount = totalCount - verifiedCount;

  const handleUploadSuccess = (newDoc) => {
    setDocuments((prev) => [newDoc, ...prev]);
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
            <p className="text-xs font-semibold text-slate-muted uppercase tracking-wider">Verified Documents</p>
            <h3 className="text-2xl font-black text-navy mt-0.5">{verifiedCount}</h3>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-card bg-gov-warning-light text-gov-warning border border-gov-warning/20 flex items-center justify-center shrink-0">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-muted uppercase tracking-wider">Pending Review</p>
            <h3 className="text-2xl font-black text-navy mt-0.5">{pendingCount}</h3>
          </div>
        </Card>
      </div>

      {/* Document Security Notice */}
      <div className="bg-primary-50/60 border border-primary/20 rounded-card p-4 flex items-center gap-3 text-xs text-primary">
        <ShieldCheck className="w-5 h-5 shrink-0" />
        <span>All uploaded documents are encrypted with AES-256 and integrated directly with Digilocker & state revenue databases.</span>
      </div>

      {/* Document Cards Grid */}
      <div>
        <h2 className="text-sm font-bold text-navy uppercase tracking-wider mb-4">
          Repository Certificates ({totalCount})
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.map((doc, idx) => (
            <DocumentCard
              key={doc.id || idx}
              doc={doc}
              onView={(d) => setPreviewDoc(d)}
              onReplace={(d) => setUploadModalOpen(true)}
            />
          ))}
        </div>
      </div>

      {/* Upload Modal connected to FastAPI /documents */}
      <UploadModal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
}

export default DocumentsPage;
