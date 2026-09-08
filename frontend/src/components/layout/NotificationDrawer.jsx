import React, { useState } from 'react';
import { X, CheckCheck, Bell, ExternalLink, Sparkles, FileText, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { MOCK_NOTIFICATIONS } from '../../data/mockCitizenData';
import Badge from '../ui/Badge';

export function NotificationDrawer({ isOpen, onClose }) {
  const [notifications, setNotifications] = useState(MOCK_NOTIFICATIONS);
  const navigate = useNavigate();

  if (!isOpen) return null;

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, unread: false })));
  };

  const handleClick = (item) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === item.id ? { ...n, unread: false } : n))
    );
    if (item.link) {
      navigate(item.link);
      onClose();
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'scheme':
        return <Sparkles className="w-4 h-4 text-primary" />;
      case 'application':
        return <FileText className="w-4 h-4 text-gov-warning" />;
      case 'document':
      case 'benefit':
        return <CheckCircle2 className="w-4 h-4 text-gov-success" />;
      default:
        return <Bell className="w-4 h-4 text-slate-400" />;
    }
  };

  const unreadCount = notifications.filter((n) => n.unread).length;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-navy/40 backdrop-blur-xs">
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-sm md:max-w-md bg-white border-l border-slate-border shadow-modal flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-slate-border flex items-center justify-between bg-slate-50/70">
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-navy">Notifications</h3>
              {unreadCount > 0 && (
                <Badge variant="primary" size="sm">
                  {unreadCount} New
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-primary hover:text-primary-dark font-medium flex items-center gap-1 p-1"
                >
                  <CheckCheck className="w-3.5 h-3.5" />
                  <span>Mark all read</span>
                </button>
              )}
              <button
                onClick={onClose}
                className="p-1 rounded-btn text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto divide-y divide-slate-100 p-2 space-y-1">
            {notifications.length === 0 ? (
              <div className="py-12 text-center text-slate-muted text-xs">
                No notifications right now.
              </div>
            ) : (
              notifications.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleClick(item)}
                  className={`p-3.5 rounded-card cursor-pointer transition-all hover:bg-slate-50 relative flex items-start gap-3 ${
                    item.unread ? 'bg-primary-50/30' : ''
                  }`}
                >
                  <div className="p-2 rounded-btn bg-white border border-slate-border shrink-0 mt-0.5 shadow-subtle">
                    {getIcon(item.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-1">
                      <h4 className="text-xs font-bold text-navy truncate">{item.title}</h4>
                      <span className="text-[10px] text-slate-400 shrink-0">{item.time}</span>
                    </div>
                    <p className="text-xs text-slate-muted mt-1 leading-relaxed">
                      {item.message}
                    </p>
                  </div>
                  {item.unread && (
                    <span className="w-2 h-2 rounded-full bg-primary mt-1.5 shrink-0" />
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default NotificationDrawer;
