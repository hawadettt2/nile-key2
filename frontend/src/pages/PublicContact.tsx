import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';
import { Button } from '@/components/ui/button';
import { submitContact } from '@/services/api';
import { Globe } from 'lucide-react';

type FormStatus = 'idle' | 'submitting' | 'success' | 'error';

export function PublicContact() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });
  const [status, setStatus] = useState<FormStatus>('idle');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = isArabic ? 'الاسم الكامل مطلوب' : 'Full name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = isArabic ? 'البريد الإلكتروني مطلوب' : 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = isArabic ? 'البريد الإلكتروني غير صحيح' : 'Email is invalid';
    }

    if (!formData.subject.trim()) {
      newErrors.subject = isArabic ? 'الموضوع مطلوب' : 'Subject is required';
    }

    if (!formData.message.trim()) {
      newErrors.message = isArabic ? 'الرسالة مطلوبة' : 'Message is required';
    } else if (formData.message.trim().length < 10) {
      newErrors.message = isArabic ? 'الرسالة قصيرة جداً' : 'Message is too short';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // G12 RESOLVED: wired to the existing approved endpoint POST /contact
  // (backend/app/routers/contact.py:18, mounted in backend/main.py:659)
  // via submitContact (frontend/src/services/api.ts:289-290). No new backend created.
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    setStatus('submitting');
    try {
      await submitContact(formData);
      setStatus('success');
      setFormData({ name: '', email: '', subject: '', message: '' });
      setErrors({});
    } catch {
      setStatus('error');
    }
  };

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData((prev) => ({ ...prev, [field]: e.target.value }));
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  return (
    <div className="min-h-screen bg-[#022F32] text-white" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Hero Section */}
        <section className="w-full bg-[#022F32]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 text-center md:py-20">
            <h1 className="text-3xl font-bold text-white lg:text-[34px]">{t('public.contact.title')}</h1>
            <p className="mt-3 text-base text-white/70">{t('public.contact.subtitle')}</p>
          </div>
        </section>

        {/* Contact Section */}
        <section className="w-full bg-[#043B3E]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 md:py-20">
            <div className="grid gap-12 lg:grid-cols-3">
              {/* Contact Info — only data existing in the project (location: Egypt). Fake email/phone removed. */}
              <div className="lg:col-span-1">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                  <div className="flex items-start gap-4">
                    <div className="text-[#19D8B0] mt-1">
                      <Globe size={24} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white">{t('public.contact.locationTitle')}</h3>
                      <p className="mt-1 text-sm text-white/60">{t('public.contact.locationText')}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Contact Form */}
              <div className="lg:col-span-2">
                {status === 'success' ? (
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-8">
                    <h3 className="text-2xl font-bold text-[#19D8B0]">{t('public.contact.successTitle')}</h3>
                    <p className="mt-4 text-base leading-7 text-white/70">{t('public.contact.successText')}</p>
                    <Button
                      onClick={() => setStatus('idle')}
                      className="mt-6 rounded-full bg-[#19D8B0] px-8 text-base font-semibold text-[#022F32] hover:bg-[#19D8B0]/90"
                    >
                      {isArabic ? 'إرسال رسالة أخرى' : 'Send Another Message'}
                    </Button>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="rounded-2xl border border-white/10 bg-white/5 p-8">
                    <div className="space-y-6">
                      <div>
                        <label className="block font-medium text-white mb-2">
                          {t('public.contact.nameLabel')} <span className="text-red-400">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.name}
                          onChange={handleChange('name')}
                          placeholder={t('public.contact.namePlaceholder')}
                          className={`w-full rounded-xl border bg-[#022F32] px-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-[#19D8B0] ${
                            errors.name ? 'border-red-400' : 'border-white/10'
                          }`}
                        />
                        {errors.name && <p className="mt-1 text-sm text-red-400">{errors.name}</p>}
                      </div>

                      <div>
                        <label className="block font-medium text-white mb-2">
                          {t('public.contact.emailLabel')} <span className="text-red-400">*</span>
                        </label>
                        <input
                          type="email"
                          value={formData.email}
                          onChange={handleChange('email')}
                          placeholder={t('public.contact.emailPlaceholder')}
                          className={`w-full rounded-xl border bg-[#022F32] px-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-[#19D8B0] ${
                            errors.email ? 'border-red-400' : 'border-white/10'
                          }`}
                        />
                        {errors.email && <p className="mt-1 text-sm text-red-400">{errors.email}</p>}
                      </div>

                      <div>
                        <label className="block font-medium text-white mb-2">
                          {t('public.contact.subjectLabel')} <span className="text-red-400">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.subject}
                          onChange={handleChange('subject')}
                          placeholder={t('public.contact.subjectPlaceholder')}
                          className={`w-full rounded-xl border bg-[#022F32] px-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-[#19D8B0] ${
                            errors.subject ? 'border-red-400' : 'border-white/10'
                          }`}
                        />
                        {errors.subject && <p className="mt-1 text-sm text-red-400">{errors.subject}</p>}
                      </div>

                      <div>
                        <label className="block font-medium text-white mb-2">
                          {t('public.contact.messageLabel')} <span className="text-red-400">*</span>
                        </label>
                        <textarea
                          value={formData.message}
                          onChange={handleChange('message')}
                          placeholder={t('public.contact.messagePlaceholder')}
                          rows={6}
                          className={`w-full rounded-xl border bg-[#022F32] px-4 py-3 text-white placeholder:text-white/40 focus:outline-none focus:border-[#19D8B0] resize-vertical ${
                            errors.message ? 'border-red-400' : 'border-white/10'
                          }`}
                        />
                        {errors.message && <p className="mt-1 text-sm text-red-400">{errors.message}</p>}
                      </div>

                      <Button
                        type="submit"
                        disabled={status === 'submitting'}
                        className="w-full rounded-full bg-[#19D8B0] py-3 text-lg font-semibold text-[#022F32] hover:bg-[#19D8B0]/90"
                      >
                        {status === 'submitting' ? t('public.contact.sendingButton') : t('public.contact.sendButton')}
                      </Button>

                      {status === 'error' && (
                        <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4">
                          <p className="text-sm text-red-400">{t('public.contact.errorText')}</p>
                        </div>
                      )}
                    </div>
                  </form>
                )}
              </div>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
