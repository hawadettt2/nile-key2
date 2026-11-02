// Auto-generated login page translations (Arabic -> English)
export const loginTranslations: Record<string, string> = {
  "Nile Key - منصة مفتاح النيل": "Nile Key - Nile Key Platform",
  "© 2025 مفتاح النيل للاستثمار والتجارة الدولية (ذ.م.م). جميع الحقوق محفوظة.": "© 2025 Nile Key for Investment and International Trade LLC. All rights reserved.",
  "إنشاء حساب جديد": "Create new account",
  "اتصل بنا": "Contact Us",
  "اسم المستخدم": "Username",
  "الأسواق": "Markets",
  "الخدمات": "Services",
  "الرئيسية": "Home",
  "المنتجات": "Products",
  "المنصة الرقمية للتصدير": "Digital Export Platform",
  "تسجيل الدخول": "Sign In",
  "حساب جديد": "New account",
  "كلمة المرور": "Password",
  "ليس لديك حساب؟": "Don't have an account?",
  "مفتاح النيل": "Nile Key",
  "من نحن": "About Us",
  "نسيت كلمة المرور؟": "Forgot password?",
};

export function normalizeLoginText(s: string): string {
  const t = document.createElement('textarea');
  t.innerHTML = s;
  return t.value.replace(/\u00A0/g, ' ').replace(/\s+/g, ' ').trim();
}