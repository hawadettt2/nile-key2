import React from 'react';
import { submitContact } from '@/services/api';
import StitchPage from '@/components/StitchPage';
import stitchContact from '../../stitch/contact/code.html?raw';

export function PublicContact() {
  const onMount = React.useCallback((container: HTMLDivElement) => {
    const form = container.querySelector('form');
    if (!form) return;
    const handler = async (e: Event) => {
      e.preventDefault();
      const controls = Array.from(form.querySelectorAll('select, input, textarea'));
      // order: select(inquiry), name, email, phone, whatsapp, subject, message
      const getValue = (i: number) => (controls[i] as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement)?.value ?? '';
      const payload = {
        name: getValue(1),
        email: getValue(2),
        subject: getValue(5) || getValue(0),
        message: getValue(6),
      };
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

  return <StitchPage raw={stitchContact} onMount={onMount} />;
}

export default PublicContact;
