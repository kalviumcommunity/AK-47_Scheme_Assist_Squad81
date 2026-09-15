const STORAGE_KEY = 'schemeassist_helpdesk_tickets';
import { recordActivity } from './activityLogService';

function readTickets() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch {
        return [];
    }
}

function writeTickets(tickets) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tickets));
    window.dispatchEvent(new StorageEvent('storage', { key: STORAGE_KEY }));
}

export function getTickets() {
    return readTickets();
}

export function createTicket(ticketData) {
    const ticket = {
        ...ticketData,
        id: `TKT-${Date.now().toString().slice(-8)}`,
        status: 'Open',
        createdDate: new Date().toISOString().split('T')[0],
        lastUpdate: new Date().toISOString().split('T')[0],
        adminResponse: '',
        citizenConfirmed: null,
    };
    writeTickets([ticket, ...readTickets()]);
        recordActivity({
            level: 'INFO',
            source: 'HELPDESK',
            message: `Helpdesk ticket created: ${ticket.id}`,
            details: `Subject: ${ticket.subject || 'Not provided'} | Citizen: ${ticket.citizenName || ticket.citizenEmail || 'Citizen'}`,
        });
    return ticket;
}

export function resolveTicket(ticketId, adminResponse = '') {
    const updated = readTickets().map((ticket) => ticket.id === ticketId ? {
        ...ticket,
        status: 'Resolved',
        adminResponse,
        lastUpdate: new Date().toISOString().split('T')[0],
    } : ticket);
    writeTickets(updated);
    const ticket = updated.find((item) => item.id === ticketId) || null;
    if (ticket) {
        recordActivity({
            level: 'SUCCESS',
            source: 'HELPDESK',
            message: `Helpdesk ticket resolved: ${ticketId}`,
            details: `Admin response: ${adminResponse || 'No response provided'}`,
        });
    }
    return ticket;
}

export function confirmTicketResolution(ticketId, resolved) {
    const updated = readTickets().map((ticket) => ticket.id === ticketId ? {
        ...ticket,
        status: resolved ? 'Closed' : 'Open',
        citizenConfirmed: resolved,
        lastUpdate: new Date().toISOString().split('T')[0],
    } : ticket);
    writeTickets(updated);
    const ticket = updated.find((item) => item.id === ticketId) || null;
    if (ticket) {
        recordActivity({
            level: resolved ? 'SUCCESS' : 'WARN',
            source: 'HELPDESK',
            message: `Citizen ${resolved ? 'confirmed' : 'reopened'} helpdesk ticket: ${ticketId}`,
            details: `Ticket status: ${ticket.status}`,
        });
    }
    return ticket;
}

export default { getTickets, createTicket, resolveTicket, confirmTicketResolution };
