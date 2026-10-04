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
    <div className="min-h-screen bg-slate-900" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Hero Section */}
        <section className="py-20 bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
              {t('public.contact.title')}
            </h1>
            <p className="text-xl text-slate-300">
              {t('public.contact.subtitle')}
            </p>
          </div>
        </section>

        {/* Contact Section */}
        <section className="py-20 bg-slate-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
              {/* Contact Info */}
              <div className="lg:col-span-1">
                <div className="space-y-6">
                  <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6">
                    <div className="flex items-start gap-4">
                      <div className="text-emerald-400 mt-1">
                        <Globe size={24} />
                      </div>
                      <div>
                        <h3 className="text-white font-semibold mb-1">{t('public.contact.locationTitle')}</h3>
                        <p className="text-slate-400">{t('public.contact.locationText')}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Contact Form */}
              <div className="lg:col-span-2">
                {status === 'success' ? (
                  <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8">
                    <h3 className="text-2xl font-bold text-emerald-400 mb-4">{t('public.contact.successTitle')}</h3>
                    <p className="text-slate-300 mb-6">{t('public.contact.successText')}</p>
                    <Button
                      onClick={() => setStatus('idle')}
                      className="bg-emerald-600 hover:bg-emerald-700 text-white"
                    >
                      {isArabic ? 'إرسال رسالة أخرى' : 'Send Another Message'}
                    </Button>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8">
                    <div className="space-y-6">
                      <div>
                        <label className="block text-white font-medium mb-2">
                          {t('public.contact.nameLabel')} <span className="text-red-400">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.name}
                          onChange={handleChange('name')}
                          placeholder={t('public.contact.namePlaceholder')}
                          className={`w-full px-4 py-3 bg-slate-800 border ${errors.name ? 'border-red-400' : 'border-white/10'} rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500`}
                        />
                        {errors.name && <p className="text-red-400 text-sm mt-1">{errors.name}</p>}
                      </div>

                      <div>
                        <label className="block text-white font-medium mb-2">
                          {t('public.contact.emailLabel')} <span className="text-red-400">*</span>
                        </label>
                        <input
                          type="email"
                          value={formData.email}
                          onChange={handleChange('email')}
                          placeholder={t('public.contact.emailPlaceholder')}
                          className={`w-full px-4 py-3 bg-slate-800 border ${errors.email ? 'border-red-400' : 'border-white/10'} rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500`}
                        />
                        {errors.email && <p className="text-red-400 text-sm mt-1">{errors.email}</p>}
                      </div>

                      <div>
                        <label className="block text-white font-medium mb-2">
                          {t('public.contact.subjectLabel')} <span className="text-red-400">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.subject}
                          onChange={handleChange('subject')}
                          placeholder={t('public.contact.subjectPlaceholder')}
                          className={`w-full px-4 py-3 bg-slate-800 border ${errors.subject ? 'border-red-400' : 'border-white/10'} rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500`}
                        />
                        {errors.subject && <p className="text-red-400 text-sm mt-1">{errors.subject}</p>}
                      </div>

                      <div>
                        <label className="block text-white font-medium mb-2">
                          {t('public.contact.messageLabel')} <span className="text-red-400">*</span>
                        </label>
                        <textarea
                          value={formData.message}
                          onChange={handleChange('message')}
                          placeholder={t('public.contact.messagePlaceholder')}
                          rows={6}
                          className={`w-full px-4 py-3 bg-slate-800 border ${errors.message ? 'border-red-400' : 'border-white/10'} rounded-xl text-white placeholder:text-slate-500 focus:outline-none focus:border-emerald-500 resize-vertical`}
                        />
                        {errors.message && <p className="text-red-400 text-sm mt-1">{errors.message}</p>}
                      </div>

                      <Button
                        type="submit"
                        disabled={status === 'submitting'}
                        className="w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3 text-lg"
                      >
                        {status === 'submitting' ? t('public.contact.sendingButton') : t('public.contact.sendButton')}
                      </Button>

                      {status === 'error' && (
                        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                          <p className="text-red-400 text-sm">{t('public.contact.errorText')}</p>
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
