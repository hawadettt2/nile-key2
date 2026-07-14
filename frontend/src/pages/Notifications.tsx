import { useEffect, useState, useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { getAuditLogs } from '@/services/api';
import { Bell, Users, FileText, Truck, BookOpen, Settings, Inbox, CheckCheck, Filter } from 'lucide-react';

interface AuditLog {
  id: number;
  action: string;
  entity_type: string;
  entity_id?: number;
  details?: string;
  created_at: string;
}

type ReadFilter = 'all' | 'unread' | 'read';

const ENTITY_ICONS: Record<string, typeof Users> = {
  customer: Users,
  invoice: FileText,
  shipment: Truck,
  customs: BookOpen,
  document: BookOpen,
  resource: Settings,
};

export function Notifications() {
  const { t } = useTranslation();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [readIds, setReadIds] = useState<Set<number>>(new Set());
  const [readFilter, setReadFilter] = useState<ReadFilter>('all');
  const [entityFilter, setEntityFilter] = useState<string>('all');
  const [markingAllRead, setMarkingAllRead] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAuditLogs({ limit: 50 });
      setLogs(res.data || []);
      setReadFilter('all');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const entityTypes = useMemo(() =>
    Array.from(new Set(logs.map((l) => l.entity_type))).sort(),
    [logs]
  );

  const filtered = useMemo(() => {
    let result = logs;
    if (entityFilter !== 'all') {
      result = result.filter((l) => l.entity_type === entityFilter);
    }
    if (readFilter !== 'all') {
      const isRead = readFilter === 'read';
      result = result.filter((l) => readIds.has(l.id) === isRead);
    }
    return result;
  }, [logs, entityFilter, readFilter, readIds]);

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

  const handleMarkAllRead = useCallback(async () => {
    setMarkingAllRead(true);
    try {
      await load();
      setReadIds((prev) => {
        const next = new Set(prev);
        logs.forEach((l) => next.add(l.id));
        return next;
      });
    } catch {
      setReadIds((prev) => {
        const next = new Set(prev);
        logs.forEach((l) => next.add(l.id));
        return next;
      });
    } finally {
      setMarkingAllRead(false);
    }
  }, [load, logs]);

  const getEntityIcon = (entityType: string) => {
    const Icon = ENTITY_ICONS[entityType] || Bell;
    return <Icon size={16} className="text-slate-500" />;
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t('dashboard.notifications') || 'Notifications'}</h1>
          <p className="text-slate-500 text-sm mt-1">
            {unreadCount > 0
              ? `${unreadCount} unread notification${unreadCount !== 1 ? 's' : ''}`
              : 'All notifications read'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllRead}
              disabled={markingAllRead}
              className="flex items-center gap-1.5 text-sm text-emerald-600 hover:text-emerald-700 px-3 py-2 rounded-lg hover:bg-emerald-50 transition-colors disabled:opacity-50"
            >
              <CheckCheck size={16} />
              {t('notifications.markAllRead') || 'Mark all read'}
            </button>
          )}
          <button
            onClick={load}
            disabled={loading}
            className="text-sm text-slate-600 hover:text-slate-800 px-3 py-2 rounded-lg hover:bg-slate-100 transition-colors disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
      </div>

      {(entityTypes.length > 0 || !loading) && (
        <div className="flex items-center gap-2 mb-4">
          <div className="flex rounded-lg border border-slate-200 overflow-hidden">
            {(['all', 'unread', 'read'] as ReadFilter[]).map((f) => (
              <button
                key={f}
                onClick={() => setReadFilter(f)}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  readFilter === f
                    ? 'bg-emerald-600 text-white'
                    : 'bg-white text-slate-600 hover:bg-slate-50'
                }`}
              >
                {f === 'all' ? (t('notifications.all') || 'All') : f === 'unread' ? (t('notifications.unread') || 'Unread') : (t('notifications.read') || 'Read')}
              </button>
            ))}
          </div>
          {entityTypes.length > 0 && (
            <div className="relative">
              <select
                value={entityFilter}
                onChange={(e) => setEntityFilter(e.target.value)}
                className="appearance-none pl-9 pr-8 py-2 border border-slate-200 rounded-lg text-sm text-slate-700 bg-white hover:border-slate-300 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none cursor-pointer"
              >
                <option value="all">{t('notifications.allTypes') || 'All types'}</option>
                {entityTypes.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              <Filter size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            </div>
          )}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" />
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-700 rounded-xl p-4 text-sm">{error}</div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-xl p-8 shadow-sm border border-slate-100 text-center">
          {logs.length === 0 ? (
            <>
              <Inbox size={48} className="mx-auto text-slate-300 mb-4" />
              <p className="text-slate-500">{t('notifications.noNotifications') || 'No notifications yet'}</p>
            </>
          ) : (
            <>
              <Bell size={48} className="mx-auto text-slate-300 mb-4" />
              <p className="text-slate-500">
                {readFilter === 'read'
                  ? (t('notifications.noRead') || 'No read notifications')
                  : readFilter === 'unread'
                    ? (t('notifications.allRead') || 'All notifications have been read')
                    : (t('notifications.noNotifications') || 'No notifications match the current filter')}
              </p>
            </>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 divide-y divide-slate-100">
          {filtered.map((log) => {
            const isRead = readIds.has(log.id);
            return (
              <div
                key={log.id}
                onClick={() => handleItemClick(log.id)}
                className={`p-4 flex items-start gap-3 cursor-pointer transition-colors ${
                  isRead ? 'bg-white hover:bg-slate-50' : 'bg-blue-50/40 hover:bg-blue-50'
                }`}
              >
                <div className="p-2 rounded-lg bg-slate-100 mt-0.5 shrink-0">
                  {getEntityIcon(log.entity_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-slate-900 capitalize">{log.action}</span>
                    <div className="flex items-center gap-2">
                      {!isRead && (
                        <span className="w-2 h-2 rounded-full bg-blue-500 shrink-0" title="Unread" />
                      )}
                      <span className="text-xs text-slate-400 whitespace-nowrap">
                        {new Date(log.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-slate-600 capitalize">{log.entity_type}</span>
                    {log.entity_id && (
                      <span className="text-xs text-slate-400">#{log.entity_id}</span>
                    )}
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                      isRead ? 'bg-slate-100 text-slate-500' : 'bg-blue-100 text-blue-700'
                    }`}>
                      {isRead ? (t('notifications.read') || 'Read') : (t('notifications.unread') || 'Unread')}
                    </span>
                  </div>
                  {log.details && (
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">{log.details}</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
