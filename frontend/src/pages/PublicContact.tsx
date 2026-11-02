import React from 'react';
import { submitContact } from '@/services/api';
import StitchPage from '@/components/StitchPage';
import stitchContact from '../../stitch/contact/code.html?raw';
import { contactTranslations } from '@/locales/contactTranslations';

export function PublicContact() {
  const onMount = React.useCallback((container: HTMLDivElement) => {
    const form = container.querySelector('form');
    if (!form) return;
    const handler = async (e: Event) => {
      e.preventDefault();
      const controls = Array.from(form.querySelectorAll('select, input, textarea'));
      // order: select(inquiry), name, email, phone, whatsapp, subject, message
      const getValue = (i: number) => (controls[i] as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement)?.value ?? '';
      const name = getValue(1).trim();
      const email = getValue(2).trim();
      const subject = getValue(5).trim() || getValue(0);
      const message = getValue(6).trim();
      if (!name || !email || !message) {
        alert('يرجى ملء الحقول المطلوبة (الاسم، البريد، الرسالة).');
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        alert('البريد الإلكتروني غير صحيح.');
        return;
      }
      const payload = { name, email, subject, message };
      try {
        await submitContact(payload);
        alert('تم إرسال رسالتك بنجاح.');
        form.reset();
      } catch {
        alert('فشل إرسال الرسالة. حاول مرة أخرى.');
      }
    };
    form.addEventListener('submit', handler);
    return () => form.removeEventListener('submit', handler);
  }, []);

  return <StitchPage raw={stitchContact} translations={contactTranslations} onMount={onMount} />;
}

export default PublicContact;
