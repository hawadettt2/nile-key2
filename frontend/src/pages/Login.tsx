import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import StitchPage from '@/components/StitchPage';
import stitchLogin from '../../stitch/login/code.html?raw';

export function Login() {
  const navigate = useNavigate();
  const { login, clearError } = useAuthStore();

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
        navigate('/');
      } else {
        alert(useAuthStore.getState().error || 'فشل تسجيل الدخول. تحقق من البيانات.');
      }
    };
    form.addEventListener('submit', handler);
    return () => form.removeEventListener('submit', handler);
  }, [login, clearError, navigate]);

  return <StitchPage raw={stitchLogin} onMount={onMount} />;
}

export default Login;
