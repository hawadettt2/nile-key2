import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import StitchPage from '@/components/StitchPage';
import stitchLogin from '../../stitch/login/code.html?raw';
import { loginTranslations } from '@/locales/loginTranslations';

export function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, clearError, isAuthenticated } = useAuthStore();

  React.useEffect(() => {
    if (isAuthenticated) {
      const _st = location.state as { from?: { pathname?: string } } | null;
      const from = _st?.from?.pathname;
      navigate(from && from !== '/login' ? from : '/dashboard', { replace: true });
    }
  }, [isAuthenticated, location.state, navigate]);

  const onMount = React.useCallback((container: HTMLDivElement) => {
    const form = container.querySelector('form');
    if (!form) return;
    const handler = async (e: Event) => {
      e.preventDefault();
      clearError();
      const inputs = Array.from(form.querySelectorAll('input'));
      const username = (inputs[0] as HTMLInputElement)?.value ?? '';
      const password = (inputs[1] as HTMLInputElement)?.value ?? '';
      if (!username.trim() || !password.trim()) {
        alert('يرجى إدخال اسم المستخدم وكلمة المرور.');
        return;
      }
      await login(username, password);
      if (useAuthStore.getState().isAuthenticated) {
        const _st = location.state as { from?: { pathname?: string } } | null;
        const from = _st?.from?.pathname;
        navigate(from && from !== '/login' ? from : '/dashboard', { replace: true });
      } else {
        alert(useAuthStore.getState().error || 'فشل تسجيل الدخول. تحقق من البيانات.');
      }
    };
    form.addEventListener('submit', handler);
    return () => form.removeEventListener('submit', handler);
  }, [login, clearError, navigate, location.state]);

  return <StitchPage raw={stitchLogin} translations={loginTranslations} onMount={onMount} />;
}

export default Login;
