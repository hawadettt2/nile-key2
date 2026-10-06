import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

interface LanguageSwitcherProps {
  variant?: 'light' | 'dark' | 'header';
}

export function LanguageSwitcher({ variant = 'light' }: LanguageSwitcherProps) {
  const { i18n } = useTranslation();
  const toggleLanguage = () => {
    const newLang = i18n.language === 'ar' ? 'en' : 'ar';
    i18n.changeLanguage(newLang);
  };
  const isDark = variant === 'dark' || variant === 'header';
  return (
    <button
      type="button"
      onClick={toggleLanguage}
      aria-label={i18n.language === 'ar' ? 'Switch language to English' : 'تغيير اللغة إلى العربية'}
      className={variant === 'header'
        ? 'flex items-center gap-2 rounded-md px-2 py-1 text-xs font-semibold text-white transition-colors hover:bg-white/10'
        : `flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-medium transition-colors ${
            isDark
              ? 'border-white/20 bg-white/10 text-white hover:bg-white/20'
              : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
          }`}
    >
      {variant === 'header' ? <><span>{i18n.language === 'ar' ? 'EN' : 'AR'}</span><Globe size={14} /></> : <><Globe size={16} /><span>{i18n.language === 'ar' ? 'English' : 'العربية'}</span></>}
    </button>
  );
}
