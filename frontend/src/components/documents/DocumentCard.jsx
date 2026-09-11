import React, { useState } from 'react';
import {
  FileText,
  CheckCircle2,
  Clock,
  Download,
  Trash2,
  RefreshCw,
  UploadCloud,
  Check,
  AlertCircle
} from 'lucide-react';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import Button from '../ui/Button';
import Modal from '../ui/Modal';
import { uploadDocument } from '../../services/api';

export function DocumentCard({ doc, onReplace, onView, onDelete }) {
  const isVerified = doc.verified || doc.status === 'Verified';

  return (
    <Card hoverEffect className="flex flex-col justify-between">
      <div>
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-btn flex items-center justify-center shrink-0 ${isVerified ? 'bg-gov-success-light text-gov-success' : 'bg-gov-warning-light text-gov-warning'
              }`}>
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-navy leading-tight">{doc.name}</h4>
              <span className="text-[10px] text-slate-400 block mt-0.5">{doc.type} · For scheme application use</span>
            </div>
          </div>
          <Badge variant={isVerified ? 'success' : 'warning'} size="sm" dot>
            {doc.status}
          </Badge>
        </div>

        <div className="text-[11px] text-slate-muted space-y-1 bg-slate-bg p-2.5 rounded-btn mb-4">
          <div className="flex justify-between">
            <span>Filename:</span>
            <span className="font-mono text-slate-700 truncate max-w-[140px]">{doc.filename}</span>
          </div>
          <div className="flex justify-between">
            <span>Uploaded:</span>
            <span className="text-slate-700">{doc.uploadDate}</span>
          </div>
          {doc.size && (
            <div className="flex justify-between">
              <span>File Size:</span>
              <span className="text-slate-700">{doc.size}</span>
            </div>
          )}
        </div>
      </div>

      <div className="pt-3 border-t border-slate-border flex items-center justify-between gap-2">
        <button
          onClick={() => onView && onView(doc)}
          className="text-xs font-semibold text-primary hover:text-primary-dark p-1"
        >
          View Preview
        </button>
        <div className="flex items-center gap-1">
          <Button variant="outline" size="sm" icon={RefreshCw} onClick={() => onReplace && onReplace(doc)}>Replace</Button>
          <Button variant="danger" size="sm" icon={Trash2} onClick={() => onDelete && onDelete(doc)}>Delete</Button>
        </div>
      </div>
    </Card>
  );
}

export function UploadModal({ isOpen, onClose, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successResult, setSuccessResult] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setSuccessResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }

    setIsUploading(true);
    setError(null);
    try {
      const res = await uploadDocument(file);
      setSuccessResult(res);
      if (onUploadSuccess) {
        onUploadSuccess({
          name: file.name.replace(/\.[^/.]+$/, "").replace(/_/g, " "),
          type: "Official Government Circular / Policy",
          filename: file.name,
          size: `${(file.size / (1024 * 1024)).toFixed(2)} MB`,
          uploadDate: new Date().toISOString().split('T')[0],
          status: "Pending Review",
          verified: false
        });
      }
    } catch (err) {
      setError(err.message || 'Upload and indexing failed.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setError(null);
    setSuccessResult(null);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Upload Scheme Application Document"
      subtitle="Upload only documents needed for your scheme application. Supported formats: .txt, .md, .pdf, .html (Max size 10MB)"
    >
      <div className="space-y-4">
        {successResult ? (
          <div className="p-4 rounded-card bg-gov-success-light border border-gov-success/20 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-gov-success text-white flex items-center justify-center mx-auto">
              <Check className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-navy">Document uploaded successfully</h4>
              <p className="text-xs text-slate-muted mt-1">
                Your document is available in your Documents section and can be reviewed by authorized administrators for scheme application processing. Generated {successResult.summary?.chunks || 0} knowledge-base chunks.
              </p>
            </div>
            <Button variant="primary" size="sm" onClick={handleClose} className="w-full">
              Done
            </Button>
          </div>
        ) : (
          <>
            <label className="border-2 border-dashed border-slate-border hover:border-primary/50 rounded-card p-6 flex flex-col items-center justify-center cursor-pointer transition-colors bg-slate-bg/50">
              <UploadCloud className="w-10 h-10 text-primary mb-2" />
              <span className="text-sm font-bold text-navy">
                {file ? file.name : "Click to browse or drag file here"}
              </span>
              <span className="text-xs text-slate-muted mt-1">
                {file ? `${(file.size / 1024).toFixed(1)} KB` : "Accepts .txt, .md, .pdf, .html files"}
              </span>
              <input
                type="file"
                className="hidden"
                accept=".txt,.md,.pdf,.html"
                onChange={handleFileChange}
              />
            </label>

            {error && (
              <div className="p-3 bg-gov-error-light border border-gov-error/20 text-gov-error text-xs rounded-btn flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="flex justify-end gap-3 pt-3 border-t border-slate-border">
              <Button variant="ghost" size="sm" onClick={handleClose}>
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                isLoading={isUploading}
                disabled={!file || isUploading}
                onClick={handleUpload}
              >
                Upload
              </Button>
            </div>
          </>
        )}
      </div>
    </Modal>
  );
}

export default DocumentCard;
