import { useEffect, useState, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { getAuditLogs } from '@/services/api';
import { Bell, Users, FileText, Truck, BookOpen, Settings, Inbox } from 'lucide-react';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { useTranslation } from 'react-i18next';

interface AuditLog {
  id: number;
  action: string;
  entity_type: string;
  entity_id?: number;
  details?: string;
  created_at: string;
}

const ENTITY_ICONS: Record<string, typeof Users> = {
  customer: Users,
  invoice: FileText,
  shipment: Truck,
  customs: BookOpen,
  document: BookOpen,
  resource: Settings,
};

export function NotificationBell() {
  const { t } = useTranslation();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [readIds, setReadIds] = useState<Set<number>>(new Set());

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getAuditLogs({ limit: 10 });
      setLogs(res.data || []);
    } catch {
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (open) load();
  }, [open, load]);

  const unreadCount = useMemo(() =>
    logs.filter((l) => !readIds.has(l.id)).length,
    [logs, readIds]
  );

  const handleItemClick = useCallback((id: number) => {
    setReadIds((prev) => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
  }, []);

  const getEntityIcon = (entityType: string) => {
    const Icon = ENTITY_ICONS[entityType] || Bell;
    return <Icon size={14} className="text-slate-500" />;
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button className="relative p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors">
          <Bell size={20} />
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-xs font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="end">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
          <span className="text-sm font-semibold text-slate-900">{t('dashboard.notifications') || 'Notifications'}</span>
          <Link
            to="/notifications"
            onClick={() => setOpen(false)}
            className="text-xs text-emerald-600 hover:text-emerald-700 font-medium"
          >
            View all
          </Link>
        </div>
        <div className="max-h-80 overflow-y-auto">
          {loading ? (
            <div className="flex justify-center py-6">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-600" />
            </div>
          ) : logs.length === 0 ? (
            <div className="flex flex-col items-center py-6 text-slate-500">
              <Inbox size={32} className="mb-2 text-slate-300" />
              <p className="text-sm">{t('notifications.noNotifications') || 'No notifications yet'}</p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {logs.map((log) => {
                const isRead = readIds.has(log.id);
                const Icon = ENTITY_ICONS[log.entity_type] || Bell;
                return (
                  <Link
                    key={log.id}
                    to="/notifications"
                    onClick={() => handleItemClick(log.id)}
                    className={`flex items-start gap-3 px-4 py-3 hover:bg-slate-50 transition-colors block ${
                      isRead ? 'bg-white' : 'bg-blue-50/40'
                    }`}
                  >
                    <div className="p-1.5 rounded-md bg-slate-100 mt-0.5 shrink-0">
                      <Icon size={14} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm font-medium text-slate-900 capitalize truncate">{log.action}</span>
                        {!isRead && (
                          <span className="w-1.5 h-1.5 rounded-full bg-blue-500 shrink-0 mt-1.5" />
                        )}
                      </div>
                      <p className="text-xs text-slate-500 capitalize truncate">
                        {log.entity_type}
                        {log.entity_id ? ` #${log.entity_id}` : ''}
                      </p>
                      {log.details && (
                        <p className="text-xs text-slate-400 mt-0.5 line-clamp-1">{log.details}</p>
                      )}
                      <span className="text-xs text-slate-400 mt-1 block">{formatTime(log.created_at)}</span>
                    </div>
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
