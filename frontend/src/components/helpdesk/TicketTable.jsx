import React, { useState } from 'react';
import { Plus, MessageSquare, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import Button from '../ui/Button';
import Modal from '../ui/Modal';
import Input from '../ui/Input';
import Select from '../ui/Select';
import Textarea from '../ui/Textarea';

export function TicketTable({ tickets = [], onViewTicket }) {
  const getStatusBadge = (status) => {
    switch (status) {
      case 'Resolved':
      case 'Closed':
        return <Badge variant="success" size="sm" dot>{status}</Badge>;
      case 'In Progress':
        return <Badge variant="primary" size="sm" dot>{status}</Badge>;
      default:
        return <Badge variant="warning" size="sm" dot>{status}</Badge>;
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-xs text-slate-text border-collapse">
        <thead>
          <tr className="border-b border-slate-border bg-slate-bg/70 text-slate-muted font-bold uppercase tracking-wider text-[10px]">
            <th className="py-3 px-4">Ticket ID</th>
            <th className="py-3 px-4">Subject</th>
            <th className="py-3 px-4">Category</th>
            <th className="py-3 px-4">Status</th>
            <th className="py-3 px-4">Created Date</th>
            <th className="py-3 px-4 text-right">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {tickets.map((t) => (
            <tr key={t.id} className="hover:bg-slate-50 transition-colors">
              <td className="py-3.5 px-4 font-bold font-mono text-navy">{t.id}</td>
              <td className="py-3.5 px-4 font-semibold text-slate-text max-w-xs truncate">{t.subject}</td>
              <td className="py-3.5 px-4 text-slate-500">{t.category}</td>
              <td className="py-3.5 px-4">{getStatusBadge(t.status)}</td>
              <td className="py-3.5 px-4 text-slate-500">{t.createdDate}</td>
              <td className="py-3.5 px-4 text-right">
                <button
                  onClick={() => onViewTicket && onViewTicket(t)}
                  className="text-primary font-bold hover:underline"
                >
                  View Details
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function CreateTicketModal({ isOpen, onClose, onSubmit }) {
  const [subject, setSubject] = useState('');
  const [category, setCategory] = useState('Application Issues');
  const [description, setDescription] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!subject.trim() || !description.trim()) return;

    onSubmit({
      id: `TCK-${Math.floor(1000 + Math.random() * 9000)}`,
      subject,
      category,
      description,
      status: 'Open',
      createdDate: new Date().toISOString().split('T')[0],
      lastUpdate: new Date().toISOString().split('T')[0],
    });
    setSubject('');
    setDescription('');
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create Support Ticket"
      subtitle="Our citizen grievance cell responds within 24 business hours"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Subject"
          placeholder="Brief summary of the issue..."
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          required
        />

        <Select
          label="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          options={[
            'Application Issues',
            'Document Issues',
            'Eligibility Questions',
            'Account Issues',
            'Technical Support'
          ]}
        />

        <Textarea
          label="Detailed Description"
          placeholder="Please describe the challenge you encountered, including scheme name or application ID if applicable..."
          rows={4}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        />

        <div className="flex justify-end gap-3 pt-3 border-t border-slate-border">
          <Button variant="ghost" size="sm" onClick={onClose} type="button">
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit">
            Submit Grievance Ticket
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default TicketTable;
