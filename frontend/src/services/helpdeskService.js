const STORAGE_KEY = 'schemeassist_helpdesk_tickets';

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
    return updated.find((ticket) => ticket.id === ticketId) || null;
}

export function confirmTicketResolution(ticketId, resolved) {
    const updated = readTickets().map((ticket) => ticket.id === ticketId ? {
        ...ticket,
        status: resolved ? 'Closed' : 'Open',
        citizenConfirmed: resolved,
        lastUpdate: new Date().toISOString().split('T')[0],
    } : ticket);
    writeTickets(updated);
    return updated.find((ticket) => ticket.id === ticketId) || null;
}

export default { getTickets, createTicket, resolveTicket, confirmTicketResolution };
