import React, { useEffect, useState } from 'react';
import {
  HelpCircle,
  Plus,
  MessageSquare,
  FileQuestion,
  FileCheck2,
  ShieldCheck,
  PhoneCall,
  Mail,
  ExternalLink
} from 'lucide-react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import Modal from '../../components/ui/Modal';
import { TicketTable, CreateTicketModal } from '../../components/helpdesk/TicketTable';
import { useAuth } from '../../context/AuthContext';
import { confirmTicketResolution, createTicket, getTickets } from '../../services/helpdeskService';

export function HelpdeskPage() {
  const { user } = useAuth();
  const [tickets, setTickets] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);

  const loadTickets = () => {
    setTickets(getTickets().filter((ticket) => ticket.citizenEmail === user?.email || ticket.citizenId === user?.id));
  };

  useEffect(() => {
    loadTickets();
    const refresh = () => loadTickets();
    window.addEventListener('storage', refresh);
    const interval = setInterval(refresh, 3000);
    return () => { window.removeEventListener('storage', refresh); clearInterval(interval); };
  }, [user?.email, user?.id]);

  const quickCategories = [
    { title: "Application Issues", desc: "Status delays, rejection queries & DBT tracking", icon: FileCheck2 },
    { title: "Document Issues", desc: "Aadhaar e-KYC mismatch & document re-upload", icon: FileQuestion },
    { title: "Eligibility Questions", desc: "Criteria clarification & income category doubts", icon: ShieldCheck },
    { title: "Technical Support", desc: "Login, OTP verification, or portal access glitches", icon: HelpCircle },
  ];

  const handleCreateTicket = (newTicket) => {
    createTicket({
      ...newTicket,
      citizenId: user?.id || '',
      citizenEmail: user?.email || '',
      citizen: user?.name || 'Citizen',
    });
    loadTickets();
  };

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy tracking-tight">
            How Can We Help You?
          </h1>
          <p className="text-xs sm:text-sm text-slate-muted mt-1">
            Citizen Grievance Redressal & Official Scheme Helpdesk Support
          </p>
        </div>
        <Button
          variant="primary"
          size="md"
          icon={Plus}
          onClick={() => setModalOpen(true)}
        >
          Create Support Ticket
        </Button>
      </div>

      {/* Quick Help Category Cards */}
      <div>
        <h2 className="text-sm font-bold text-navy uppercase tracking-wider mb-3">
          Frequently Assisted Categories
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickCategories.map((c, i) => (
            <Card
              key={i}
              hoverEffect
              onClick={() => setModalOpen(true)}
              className="space-y-2 cursor-pointer"
            >
              <div className="w-10 h-10 rounded-btn bg-primary-50 text-primary flex items-center justify-center border border-primary/20">
                <c.icon className="w-5 h-5" />
              </div>
              <h3 className="text-sm font-bold text-navy">{c.title}</h3>
              <p className="text-xs text-slate-muted leading-relaxed">{c.desc}</p>
            </Card>
          ))}
        </div>
      </div>

      {/* Direct Helpline Banner */}
      <div className="bg-navy text-white rounded-card p-6 flex flex-col md:flex-row items-center justify-between gap-4 shadow-subtle">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-btn bg-white/10 text-primary-light flex items-center justify-center shrink-0">
            <PhoneCall className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Need Immediate Assistance?</h3>
            <p className="text-xs text-slate-300 mt-0.5">
              Call the national citizen grievance toll-free helpline operating 24x7 in 12 languages.
            </p>
          </div>
        </div>
        <div className="text-right">
          <span className="text-xl font-black text-primary-light font-mono block">1800-111-565</span>
          <span className="text-[10px] text-slate-400">Toll Free &bull; Government of India</span>
        </div>
      </div>

      {/* Active Support Tickets Table */}
      <Card>
        <div className="flex items-center justify-between pb-4 border-b border-slate-border mb-4">
          <div>
            <h2 className="text-base font-bold text-navy">My Support & Grievance Tickets</h2>
            <p className="text-xs text-slate-muted">Track resolutions submitted for your citizen profile</p>
          </div>
          <Badge variant="primary" size="sm">
            {tickets.length} Tickets
          </Badge>
        </div>

        <TicketTable
          tickets={tickets}
          onViewTicket={(t) => setSelectedTicket(t)}
        />
      </Card>

      {/* Ticket Details View Modal */}
      {selectedTicket && <Modal isOpen={true} onClose={() => setSelectedTicket(null)} title={`Ticket ${selectedTicket.id}`} subtitle={`${selectedTicket.category} · Created ${selectedTicket.createdDate}`}>
        <div className="space-y-4 text-xs">
          <div><p className="font-bold text-navy">{selectedTicket.subject}</p><p className="mt-2 text-slate-600 whitespace-pre-wrap">{selectedTicket.description}</p></div>
          {selectedTicket.adminResponse && <div className="rounded-btn bg-primary-50 border border-primary/20 p-3"><p className="font-bold text-navy">Admin response</p><p className="mt-1 text-slate-700 whitespace-pre-wrap">{selectedTicket.adminResponse}</p></div>}
          {selectedTicket.status === 'Resolved' && <div className="border-t border-slate-border pt-4"><p className="font-bold text-navy mb-2">Has your problem been resolved?</p><div className="flex gap-2"><Button variant="success" size="sm" onClick={() => { confirmTicketResolution(selectedTicket.id, true); setSelectedTicket(null); loadTickets(); }}>Yes, mark resolved</Button><Button variant="outline" size="sm" onClick={() => { confirmTicketResolution(selectedTicket.id, false); setSelectedTicket(null); loadTickets(); }}>No, still need help</Button></div></div>}
          <div className="flex justify-end"><Button variant="ghost" size="sm" onClick={() => setSelectedTicket(null)}>Close</Button></div>
        </div>
      </Modal>}

      {/* Create Ticket Modal */}
      <CreateTicketModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleCreateTicket}
      />
    </div>
  );
}

export default HelpdeskPage;
