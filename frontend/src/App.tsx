import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Layout } from '@/components/layout/Layout';
import { Login } from '@/pages/Login';
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

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600" />
      </div>
    );
  }
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<PrivateRoute><Layout /></PrivateRoute>}>
          <Route index element={<Dashboard />} />
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
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
