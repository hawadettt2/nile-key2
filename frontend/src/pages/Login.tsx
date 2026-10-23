import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '@/store/authStore';
import { LogIn, UserPlus, AlertCircle, AlertTriangle } from 'lucide-react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';

export function Login() {
  const { t } = useTranslation();
  const { login, register, error, clearError } = useAuthStore();
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ username: '', password: '', email: '', full_name: '', phone: '', company: '' });
  const [showWarning, setShowWarning] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    if (isRegister) {
      setShowWarning(true);
      await register(form);
      if (!error) {
        setIsRegister(false);
        setShowWarning(false);
        setPendingApproval(true);
      }
    } else {
      setShowWarning(false);
      setPendingApproval(false);
      await login(form.username, form.password);
      if (useAuthStore.getState().isAuthenticated) navigate('/');
    }
  };

  const handleToggleMode = () => {
    setIsRegister(!isRegister);
    clearError();
    setShowWarning(!isRegister);
  };

  return (
    <div className="min-h-screen bg-[#022F32]">
      <PublicNavbar />
      <main className="flex-1 flex justify-center px-4 relative overflow-hidden items-center py-10">
        <div className="absolute -top-40 right-1/4 w-96 h-96 bg-[#19D8B0]/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-40 left-1/4 w-96 h-96 bg-[#0ca55f]/10 rounded-full blur-3xl pointer-events-none" />
        <div className="w-full max-w-md relative mx-auto mb-2">
          <div aria-hidden="true" className="absolute inset-0 rounded-2xl bg-[#19D8B0] z-0 pointer-events-none" style={{ transform: 'translate(-8px, 8px)', WebkitTransform: 'translate(-8px, 8px)' }} />
          <div className="relative z-10 bg-[#043B3E] border border-white/10 rounded-2xl p-8">
            <div className="text-center mb-8">
              <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-[#22BD75] to-[#0CA55F] mb-4">
                <span className="text-sm font-extrabold text-white">NK</span>
              </div>
              <h1 className="text-2xl font-bold text-white">{t('app.name')}</h1>
              <p className="text-white/70 text-sm mt-1">{t('app.tagline')}</p>
            </div>
            {error && (
              <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 p-3 flex items-center gap-2 text-red-400 text-sm">
                <AlertCircle size={16} />{error}
              </div>
            )}
            {isRegister && showWarning && !pendingApproval && (
              <Alert variant="warning" className="mb-4">
                <AlertTriangle size={16} />
                <AlertTitle>Registration notice</AlertTitle>
                <AlertDescription>New accounts require company approval before access is granted.</AlertDescription>
              </Alert>
            )}
            {pendingApproval && (
              <Alert variant="default" className="mb-4">
                <AlertTitle>{t('auth.register')} - Pending Approval</AlertTitle>
                <AlertDescription>Your account has been submitted for approval. You will be able to log in once an administrator approves your registration.</AlertDescription>
              </Alert>
            )}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white mb-1">{t('auth.username')} <span className="text-red-400 ml-1">*</span></label>
                <input type="text" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-[#022F32] text-white placeholder:text-white/40 focus:outline-none focus:border-[#19D8B0]" required />
              </div>
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-sm font-medium text-white/90 text-right">{t('auth.password')} <span className="text-red-400 ml-1">*</span></label>
                  <Link to="/forgot-password" className="text-xs text-[#19D8B0] hover:text-[#4ee58e] transition-colors">
                    {t('auth.forgotPassword')}
                  </Link>
                </div>
                <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-[#022F32] text-white placeholder:text-white/40 focus:outline-none focus:border-[#19D8B0] focus:ring-2 focus:ring-[#19D8B0]/20 transition-colors text-right" required />
              </div>
              {isRegister && (
                <>
                  <div><label className="block text-sm font-medium text-white mb-1">{t('auth.email')} <span className="text-red-400 ml-1">*</span></label>
                    <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
                      className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-[#022F32] text-white placeholder:text-white/40 focus:outline-none focus:border-[#19D8B0]" required /></div>
                  <div><label className="block text-sm font-medium text-white mb-1">{t('auth.fullName')} <span className="text-red-400 ml-1">*</span></label>
                    <input type="text" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                      className="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-[#022F32] text-white placeholder:text-white/40 focus:outline-none focus:border-[#19D8B0]" required /></div>
                </>
              )}
              <button type="submit" className="w-full bg-[#19D8B0] hover:bg-[#19D8B0]/90 text-[#022F32] font-semibold py-2.5 rounded-full flex items-center justify-center gap-2 transition-colors">
                {isRegister ? <UserPlus size={18} /> : <LogIn size={18} />}
                {isRegister ? t('auth.register') : t('auth.login')}
              </button>
            </form>
            <div className="mt-6 text-center">
              <button onClick={handleToggleMode}
                className="text-[#19D8B0] hover:text-[#19D8B0]/90 text-sm font-medium">
                {isRegister ? t('auth.hasAccount') : t('auth.noAccount')}
              </button>
            </div>
          </div>
        </div>
      </main>
      <PublicFooter />
    </div>
  );
}
