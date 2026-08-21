import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Layout } from '@/components/layout/Layout';
import { Login } from '@/pages/Login';
import { PublicLanding } from '@/pages/PublicLanding';
import { Dashboard } from '@/pages/Dashboard';
import { Suppliers } from '@/pages/Suppliers';
import { Customers } from '@/pages/Customers';
import { Shipments } from '@/pages/Shipments';
import { Invoices } from '@/pages/Invoices';
import { Customs } from '@/pages/Customs';
import { Documents } from '@/pages/Documents';
import { Resources } from '@/pages/Resources';
import { Profile } from '@/pages/Profile';
import { Notifications } from '@/pages/Notifications';
import { DEMLanding } from '@/pages/DEMLanding';
import { DEMSessions } from '@/pages/DEMSessions';
import { DEMSessionDetail } from '@/pages/DEMSessionDetail';
import { DEMMissions } from '@/pages/DEMMissions';
import { DEMMissionDetail } from '@/pages/DEMMissionDetail';
import { DEMMissionComposer } from '@/pages/DEMMissionComposer';
import { DEMApprovals } from '@/pages/DEMApprovals';
import { DEMTools } from '@/pages/DEMTools';
import { KnowledgeGraph } from '@/pages/KnowledgeGraph';
import { TradeIntelligence } from '@/pages/TradeIntelligence';
import { ExportReadiness } from '@/pages/ExportReadiness';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';
import { useToast } from '@/hooks/use-toast';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const user = useAuthStore((s) => s.user);
  const location = useLocation();
  const { toast } = useToast();
  const INTERNAL_ROLES = ['owner', 'manager', 'sales', 'admin_staff', 'accountant', 'logistics'];
  const DEM_PATHS = ['/digital-export-manager', '/knowledge-graph', '/trade-intelligence'];
  const isDEMRoute = DEM_PATHS.some(path => location.pathname === path || location.pathname.startsWith(path + '/'));
  const shouldRedirectDEM = isDEMRoute && user && !INTERNAL_ROLES.includes(user.role);
  if (shouldRedirectDEM) {
    useEffect(() => {
      toast({ title: 'Access Denied', description: 'You do not have permission to access this module.', variant: 'destructive' });
    }, [toast]);
    return <Navigate to="/" replace />;
  }
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600" />
      </div>
    );
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function RoleRedirect() {
  const user = useAuthStore((s) => s.user);
  const navigate = useNavigate();
  const location = useLocation();
  useEffect(() => {
    if (!user) return;
    const role = user.role;
    let target = '/dashboard';
    if (['owner', 'manager'].includes(role)) target = '/digital-export-manager';
    else if (role === 'sales') target = '/customers';
    else if (role === 'admin_staff') target = '/documents';
    else if (role === 'accountant') target = '/invoices';
    else if (role === 'logistics') target = '/shipments';
    else if (['supplier', 'customer'].includes(role)) target = '/profile';
    if (location.pathname === '/') navigate(target, { replace: true });
  }, [user, navigate, location.pathname]);
  return null;
}

function App() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={isAuthenticated ? <PrivateRoute><Layout /></PrivateRoute> : <PublicLanding />}>
          <Route index element={<RoleRedirect />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="suppliers" element={<Suppliers />} />
          <Route path="customers" element={<Customers />} />
          <Route path="shipments" element={<Shipments />} />
          <Route path="invoices" element={<Invoices />} />
          <Route path="customs" element={<Customs />} />
          <Route path="documents" element={<Documents />} />
          <Route path="resources" element={<Resources />} />
          <Route path="profile" element={<Profile />} />
          <Route path="notifications" element={<Notifications />} />
          <Route path="digital-export-manager" element={<DEMLanding />} />
          <Route path="digital-export-manager/sessions" element={<DEMSessions />} />
          <Route path="digital-export-manager/sessions/:sessionId" element={<DEMSessionDetail />} />
          <Route path="digital-export-manager/missions" element={<DEMMissions />} />
          <Route path="digital-export-manager/missions/new" element={<DEMMissionComposer />} />
          <Route path="digital-export-manager/missions/:missionId" element={<DEMMissionDetail />} />
          <Route path="digital-export-manager/approvals" element={<DEMApprovals />} />
          <Route path="digital-export-manager/tools" element={<DEMTools />} />
          <Route path="knowledge-graph" element={<KnowledgeGraph />} />
          <Route path="trade-intelligence" element={<TradeIntelligence />} />
          <Route path="export-readiness" element={<ExportReadiness />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Toaster />
    </BrowserRouter>
  );
}

export default App;
