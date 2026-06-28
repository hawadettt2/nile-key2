import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '@/store/authStore';
import { LogIn, UserPlus, AlertCircle } from 'lucide-react';
import { LanguageSwitcher } from '@/components/layout/LanguageSwitcher';

export function Login() {
  const { t } = useTranslation();
  const { login, register, error, clearError } = useAuthStore();
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ username: '', password: '', email: '', full_name: '', phone: '', company: '' });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    if (isRegister) { await register(form); if (!error) setIsRegister(false); }
    else { await login(form.username, form.password); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900 p-4">
      <div className="absolute top-4 right-4"><LanguageSwitcher /></div>
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <span className="text-white text-2xl font-bold">NK</span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900">{t('app.name')}</h1>
            <p className="text-slate-500 text-sm mt-1">{t('app.tagline')}</p>
          </div>
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700 text-sm">
              <AlertCircle size={16} />{error}
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('auth.username')}</label>
              <input type="text" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">{t('auth.password')}</label>
              <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none" required />
            </div>
            {isRegister && (
              <>
                <div><label className="block text-sm font-medium text-slate-700 mb-1">{t('auth.email')}</label>
                  <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
                    className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none" required /></div>
                <div><label className="block text-sm font-medium text-slate-700 mb-1">{t('auth.fullName')}</label>
                  <input type="text" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                    className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500 outline-none" required /></div>
              </>
            )}
            <button type="submit" className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2.5 rounded-lg flex items-center justify-center gap-2 transition-colors">
              {isRegister ? <UserPlus size={18} /> : <LogIn size={18} />}
              {isRegister ? t('auth.register') : t('auth.login')}
            </button>
          </form>
          <div className="mt-6 text-center">
            <button onClick={() => { setIsRegister(!isRegister); clearError(); }}
              className="text-emerald-600 hover:text-emerald-700 text-sm font-medium">
              {isRegister ? t('auth.hasAccount') : t('auth.noAccount')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
