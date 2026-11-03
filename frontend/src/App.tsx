import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Layout } from '@/components/layout/Layout';
const Login = lazy(() => import('@/pages/Login').then((m) => ({ default: m.Login })));
const PublicLanding = lazy(() => import('@/pages/PublicLanding').then((m) => ({ default: m.PublicLanding })));
const PublicAbout = lazy(() => import('@/pages/PublicAbout').then((m) => ({ default: m.PublicAbout })));
const PublicProducts = lazy(() => import('@/pages/PublicProducts').then((m) => ({ default: m.PublicProducts })));
const PublicServices = lazy(() => import('@/pages/PublicServices').then((m) => ({ default: m.PublicServices })));
const PublicMarkets = lazy(() => import('@/pages/PublicMarkets').then((m) => ({ default: m.PublicMarkets })));
const PublicContact = lazy(() => import('@/pages/PublicContact').then((m) => ({ default: m.PublicContact })));
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
import { ArchitectureExplorer } from '@/pages/ArchitectureExplorer';
import { Avatar } from '@/pages/Avatar';
import { PotentialCustomers } from '@/pages/PotentialCustomers';
import { useEffect } from 'react';
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
  useEffect(() => {
    if (shouldRedirectDEM) {
      toast({ title: 'Access Denied', description: 'You do not have permission to access this module.', variant: 'destructive' });
    }
  }, [shouldRedirectDEM, toast]);
  if (shouldRedirectDEM) {
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

function App() {
  const loadUser = useAuthStore((s) => s.loadUser);

  useEffect(() => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      loadUser();
    } else {
      useAuthStore.setState({ isLoading: false });
    }
  }, [loadUser]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Suspense fallback={null}><Login /></Suspense>} />
        <Route path="/" element={<Suspense fallback={null}><PublicLanding /></Suspense>} />
        <Route element={<PrivateRoute><Layout /></PrivateRoute>}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/suppliers" element={<Suppliers />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/shipments" element={<Shipments />} />
          <Route path="/invoices" element={<Invoices />} />
          <Route path="/customs" element={<Customs />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/resources" element={<Resources />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/avatar" element={<Avatar />} />
          <Route path="/digital-export-manager" element={<DEMLanding />} />
          <Route path="/digital-export-manager/sessions" element={<DEMSessions />} />
          <Route path="/digital-export-manager/sessions/:sessionId" element={<DEMSessionDetail />} />
          <Route path="/digital-export-manager/missions" element={<DEMMissions />} />
          <Route path="/digital-export-manager/missions/new" element={<DEMMissionComposer />} />
          <Route path="/digital-export-manager/missions/:missionId" element={<DEMMissionDetail />} />
          <Route path="/digital-export-manager/approvals" element={<DEMApprovals />} />
          <Route path="/digital-export-manager/tools" element={<DEMTools />} />
          <Route path="/knowledge-graph" element={<KnowledgeGraph />} />
          <Route path="/trade-intelligence" element={<TradeIntelligence />} />
          <Route path="/export-readiness" element={<ExportReadiness />} />
          <Route path="/architecture-explorer" element={<ArchitectureExplorer />} />
          <Route path="/potential-customers" element={<PotentialCustomers />} />
        </Route>
        <Route path="/about" element={<Suspense fallback={null}><PublicAbout /></Suspense>} />
        <Route path="/products" element={<Suspense fallback={null}><PublicProducts /></Suspense>} />
        <Route path="/services" element={<Suspense fallback={null}><PublicServices /></Suspense>} />
        <Route path="/markets" element={<Suspense fallback={null}><PublicMarkets /></Suspense>} />
        <Route path="/contact" element={<Suspense fallback={null}><PublicContact /></Suspense>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Toaster />
    </BrowserRouter>
  );
}

export default App;
