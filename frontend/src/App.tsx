import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Login } from '@/pages/Login';
import { PublicLanding } from '@/pages/PublicLanding';
import { PublicAbout } from '@/pages/PublicAbout';
import { PublicProducts } from '@/pages/PublicProducts';
import { PublicServices } from '@/pages/PublicServices';
import { PublicMarkets } from '@/pages/PublicMarkets';
import { PublicContact } from '@/pages/PublicContact';
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
    }
  }, [loadUser]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<PublicLanding />} />
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
        <Route path="/suppliers" element={<PrivateRoute><Suppliers /></PrivateRoute>} />
        <Route path="/customers" element={<PrivateRoute><Customers /></PrivateRoute>} />
        <Route path="/shipments" element={<PrivateRoute><Shipments /></PrivateRoute>} />
        <Route path="/invoices" element={<PrivateRoute><Invoices /></PrivateRoute>} />
        <Route path="/customs" element={<PrivateRoute><Customs /></PrivateRoute>} />
        <Route path="/documents" element={<PrivateRoute><Documents /></PrivateRoute>} />
        <Route path="/resources" element={<PrivateRoute><Resources /></PrivateRoute>} />
        <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
        <Route path="/notifications" element={<PrivateRoute><Notifications /></PrivateRoute>} />
        <Route path="/avatar" element={<PrivateRoute><Avatar /></PrivateRoute>} />
        <Route path="/digital-export-manager" element={<PrivateRoute><DEMLanding /></PrivateRoute>} />
        <Route path="/digital-export-manager/sessions" element={<PrivateRoute><DEMSessions /></PrivateRoute>} />
        <Route path="/digital-export-manager/sessions/:sessionId" element={<PrivateRoute><DEMSessionDetail /></PrivateRoute>} />
        <Route path="/digital-export-manager/missions" element={<PrivateRoute><DEMMissions /></PrivateRoute>} />
        <Route path="/digital-export-manager/missions/new" element={<PrivateRoute><DEMMissionComposer /></PrivateRoute>} />
        <Route path="/digital-export-manager/missions/:missionId" element={<PrivateRoute><DEMMissionDetail /></PrivateRoute>} />
        <Route path="/digital-export-manager/approvals" element={<PrivateRoute><DEMApprovals /></PrivateRoute>} />
        <Route path="/digital-export-manager/tools" element={<PrivateRoute><DEMTools /></PrivateRoute>} />
        <Route path="/knowledge-graph" element={<PrivateRoute><KnowledgeGraph /></PrivateRoute>} />
        <Route path="/trade-intelligence" element={<PrivateRoute><TradeIntelligence /></PrivateRoute>} />
        <Route path="/export-readiness" element={<PrivateRoute><ExportReadiness /></PrivateRoute>} />
        <Route path="/architecture-explorer" element={<PrivateRoute><ArchitectureExplorer /></PrivateRoute>} />
        <Route path="/potential-customers" element={<PrivateRoute><PotentialCustomers /></PrivateRoute>} />
        <Route path="/about" element={<PublicAbout />} />
        <Route path="/products" element={<PublicProducts />} />
        <Route path="/services" element={<PublicServices />} />
        <Route path="/markets" element={<PublicMarkets />} />
        <Route path="/contact" element={<PublicContact />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Toaster />
    </BrowserRouter>
  );
}

export default App;
