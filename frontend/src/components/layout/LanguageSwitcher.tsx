import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';

interface LanguageSwitcherProps {
  variant?: 'light' | 'dark';
}

export function LanguageSwitcher({ variant = 'light' }: LanguageSwitcherProps) {
  const { i18n } = useTranslation();
  const toggleLanguage = () => {
    const newLang = i18n.language === 'ar' ? 'en' : 'ar';
    i18n.changeLanguage(newLang);
  };
  const isDark = variant === 'dark';
  return (
    <button
      onClick={toggleLanguage}
      className={`flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-medium transition-colors ${
        isDark
          ? 'border-white/20 bg-white/10 text-white hover:bg-white/20'
          : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
      }`}
    >
      <Globe size={16} />
      <span>{i18n.language === 'ar' ? 'English' : 'العربية'}</span>
    </button>
  );
}
