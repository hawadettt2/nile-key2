import { useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import {
  listPotentialCustomerCountries,
  getPotentialCustomerFileContent,
  api,
  type PotentialCustomerCountry,
  type PotentialCustomerExcelContent,
} from '@/services/api';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  FolderOpen,
  FileSpreadsheet,
  ExternalLink,
  ChevronRight,
  Globe,
  Loader2,
  ArrowLeft,
  Search,
  Copy,
  CheckCircle,
  Phone,
  Mail,
  ChevronLeft,
  X,
  UserPlus,
} from 'lucide-react';

const ARABIC_HEADERS: Record<string, string> = {
  '#': '#',
  'Company Name': 'اسم الشركة',
  'Contact Person': 'جهة الاتصال',
  'Email': 'البريد الإلكتروني',
  'Phone': 'الهاتف',
  'Mobile': 'الجوال',
  'Website': 'الموقع الإلكتروني',
  'Address': 'العنوان',
  'City': 'المدينة',
  'Country': 'الدولة',
  'Product': 'المنتج',
  'HS Code': 'كود HS',
  'Quantity': 'الكمية',
  'Unit': 'الوحدة',
  'Status': 'الحالة',
  'Notes': 'ملاحظات',
  'Name': 'الاسم',
  'Description': 'الوصف',
  'Date': 'التاريخ',
  'Amount': 'المبلغ',
  'Currency': 'العملة',
  'Invoice No': 'رقم الفاتورة',
  'Reference': 'المرجع',
  'Shipment': 'الشحنة',
  'Tracking': 'التتبع',
  'Origin': 'المنشأ',
  'Destination': 'الوجهة',
  'Port': 'الميناء',
  'ETD': 'تاريخ المغادرة',
  'ETA': 'تاريخ الوصول',
  'Document': 'المستند',
  'Type': 'النوع',
  'Size': 'الحجم',
  'Created': 'تاريخ الإنشاء',
  'Modified': 'تاريخ التعديل',
  'Metric': 'المقياس',
  'Value': 'القيمة',
  'Period / Scope': 'الفترة / النطاق',
  'Source': 'المصدر',
  'Observed buyers': 'العملاء المشاهدون',
  'Active buyers': 'العملاء النشطون',
  'Import shipments': 'شحنات الاستيراد',
  'Global suppliers': 'الموردون العالميون',
  'Exporting countries': 'الدول المصدرة',
  'High activity buyers': 'العملاء عاليو النشاط',
  'Medium activity buyers': 'العملاء متوسطو النشاط',
  'Low activity buyers': 'العملاء ضعيفو النشاط',
  'New buyers': 'العملاء الجدد',
  'Interpretation Rule': 'قاعدة التفسير',
  'Meaning': 'المعنى',
  'Market universe': 'الكون السوقي',
  'Free extraction ceiling': 'سقف الاستخراج المجاني',
  'No false precision': 'لا دقة كاذبة',
  'No origin filter': 'لا فلتر للمنشأ',
  'Purpose': 'الغرض',
  'Rule': 'القاعدة',
  'Limitation': 'القيود',
  'Evidence': 'الأدلة',
  'Summary': 'الملخص',
  'Directory': 'الدليل',
  'Contacts': 'جهات الاتصال',
  'Company': 'الشركة',
  'Buyer': 'المشتري',
  'Seller': 'البائع',
  'Product Description': 'وصف المنتج',
  'Price': 'السعر',
  'Weight': 'الوزن',
  'Country of Origin': 'بلد المنشأ',
  'Port of Loading': 'ميناء الشحن',
  'Port of Discharge': 'ميناء التفريغ',
  'Incoterm': 'شروط البيع',
  'Payment Terms': 'شروط الدفع',
  'Delivery Terms': 'شروط التسليم',
  'Bank Name': 'اسم البنك',
  'Account Number': 'رقم الحساب',
  'SWIFT Code': 'رمز السويفت',
  'IBAN': 'آيبان',
  'VAT Number': 'الرقم الضريبي',
  'Tax ID': 'الرقم الضريبي',
  'Customs Code': 'الكود الجمركي',
  'HS Code Description': 'وصف كود HS',
  'Unit Price': 'سعر الوحدة',
  'Total Value': 'القيمة الإجمالية',
  'Freight': 'الشحن',
  'Insurance': 'التأمين',
  'Other Charges': 'رسوم أخرى',
  'Grand Total': 'الإجمالي الكلي',
  'Remarks': 'ملاحظات',
  'Status': 'الحالة',
  'Action': 'إجراء',
};

const TEXTUAL_TRANSLATIONS: Record<string, string> = {
  'Purpose': 'الغرض',
  'Source': 'المصدر',
  'Interpretation': 'التفسير',
  'Limitation': 'القيود',
  'Rule': 'القاعدة',
  'Notes': 'ملاحظات',
  'Summary': 'الملخص',
  'Evidence': 'الأدلة',
  'Description': 'الوصف',
  'Name': 'الاسم',
  'Type': 'النوع',
  'Status': 'الحالة',
  'Date': 'التاريخ',
  'Amount': 'المبلغ',
  'Quantity': 'الكمية',
  'Unit': 'الوحدة',
  'Price': 'السعر',
  'Currency': 'العملة',
  'Country': 'الدولة',
  'City': 'المدينة',
  'Address': 'العنوان',
  'Phone': 'الهاتف',
  'Email': 'البريد الإلكتروني',
  'Website': 'الموقع الإلكتروني',
  'Contact': 'جهة الاتصال',
  'Reference': 'المرجع',
  'Tracking': 'التتبع',
  'Origin': 'المنشأ',
  'Destination': 'الوجهة',
  'Port': 'الميناء',
  'Document': 'المستند',
  'Created': 'تاريخ الإنشاء',
  'Modified': 'تاريخ التعديل',
  'Metric': 'المقياس',
  'Value': 'القيمة',
  'Period': 'الفترة',
  'Scope': 'النطاق',
  'Rule': 'القاعدة',
  'Meaning': 'المعنى',
  'Market universe': 'الكون السوقي',
  'Free extraction ceiling': 'سقف الاستخراج المجاني',
  'No false precision': 'لا دقة كاذبة',
  'No origin filter': 'لا فلتر للمنشأ',
  'Method And Sources': 'المنهج والمصادر',
  'Method': 'المنهج',
  'Sources': 'المصادر',
  'Raw Product Evidence': 'أدلة المنتج الخام',
  'Directory Additional': 'دليل إضافي',
  'Merged Leads': 'العملاء المدمجون',
  'Free Directory Contacts': 'جهات اتصال الدليل المجاني',
  'Volza Active Evidence': 'أدلة نشطة من Volza',
  'Market Overview': 'نظرة عامة على السوق',
  'Active buyers': 'العملاء النشطون',
  'Import shipments': 'شحنات الاستيراد',
  'Global suppliers': 'الموردون العالميون',
  'Exporting countries': 'الدول المصدرة',
  'High activity buyers': 'العملاء عاليو النشاط',
  'Medium activity buyers': 'العملاء متوسطو النشاط',
  'Low activity buyers': 'العملاء ضعيفو النشاط',
  'New buyers': 'العملاء الجدد',
  'Observed buyers': 'العملاء المشاهدون',
  'Last 3 years': 'آخر 3 سنوات',
  'Jul 2024–Jun 2025': 'يوليو 2024 - يونيو 2025',
  'Through Sep-2026': 'حتى سبتمبر 2026',
  'First shipment in last 12 months': 'أول شحنة في آخر 12 شهراً',
  '≥10 active months': '10 أشهر نشطة على الأقل',
  '5–9 active months': '5-9 أشهر نشطة',
  '<5 active months': 'أقل من 5 أشهر نشطة',
  'Blank means unavailable or not proven; masked numbers remain masked rather than guessed.': 'الفراغ يعني غير متاح أو غير مثبت؛ الأرقام المحجوبة تبقى محجوبة بدلاً من التخمين.',
  'The workbook contains only names/data actually visible in free/public pages or public directories found during research.': 'يحتوي الملف فقط على الأسماء/البيانات المرئية فعلياً في الصفحات المجانية/العامة أو الأدلة العامة الموجودة أثناء البحث.',
  'This research is the UAE market itself; no Egypt-origin filter was applied.': 'هذا البحث هو سوق الإمارات نفسه؛ لم يتم تطبيق فلتر للمنشأ المصري.',
  '8,868 observed buyers is the full observed Volza universe; 4,378 is the active base.': '8,868 عميل مشاهد هو الكون المرصود الكامل من Volza؛ 4,378 هو القاعدة النشطة.',
  'Extract the maximum buyer/shipment data that is actually visible on public Volza pages for Jordan fresh/mixed/vegetable demand.': 'استخراج أقصى قدر من بيانات المشترين/الشحنات المرئية فعلياً في الصفحات العامة لـ Volza لطلب الأردن من الخضار/الفاكهة المختلطة/الطازجة.',
  'Master public metric': 'المقياس العام الرئيسي',
  'Buyer observations': 'ملاحظات المشترين',
  'Critical limitation': 'القيود الحرجة',
  'Shipment rows': 'صفوف الشحنات',
  'What this file contains': 'ماذا يحتوي هذا الملف',
  'What this file does not contain': 'ماذا لا يحتوي هذا الملف',
  'Company profiles': 'ملفات الشركات',
  'Master active buyers': 'إجمالي المشترين النشطين',
  'Master total buyers': 'إجمالي المشترين',
  'Egypt rule': 'قاعدة مصر',
  'Source pages': 'صفحات المصادر',
  'Actual public buyer observations; may include same company across products.': 'ملاحظات مشترين عامة فعلية؛ قد تشمل نفس الشركة عبر منتجات مختلفة.',
  'The public page shows the 305 active-buyer count, but Volza gates the complete buyer directory and shipment details behind subscription.': 'تعرض الصفحة العامة عدد 305 مشترين نشطين، لكن Volza تحجب دليل المشترين الكامل وتفاصيل الشحنات خلف اشتراك.',
  'Actual unique public shipment examples captured from public pages.': 'أمثلة شحنات عامة فريدة تم التقاطها من الصفحات العامة.',
  'Actual public buyer observations + actual public shipment examples + current market metrics + two public company-profile records + source index.': 'ملاحظات مشترين عامة فعلية + أمثلة شحنات عامة فعلية + مقاييس السوق الحالية + سجلان لملفات شركات عامة + فهرس المصادر.',
  'Public company-profile records captured.': 'سجلات ملفات شركات عامة تم التقاطها.',
  'Invented or placeholder rows pretending to be the missing 305 buyer identities.': 'صفوف مخترعة أو نائبة pretend أنها هويات المشترين 305 المفقودة.',
  'No buyer is classified as an Egypt customer unless buyer-level Egypt-origin evidence is available.': 'لا يتم تصنيف أي مشترين كعملاء مصريين ما لم تتوفر أدلة على المنشأ المصري على مستوى المشترين.',
  'Public metric; full roster not exposed.': 'مقياس عام؛ القائمة الكاملة غير معروضة.',
  'Direct URLs preserved in workbook.': 'روابط مباشرة محفوظة في الملف.',
  'Dataset count': 'عدد مجموعات البيانات',
  'Jordan Fresh-Produce Buyer Extraction — Public Web Evidence': 'استخراج بيانات مشتري الخضار الطازجة الأردنية — أدلة ويب عامة',
  'Actual public buyer observations; may include same company across products.': 'ملاحظات مشترين عامة فعلية؛ قد تشمل نفس الشركة عبر منتجات مختلفة.',
  'README': 'التعريف',
  'Market_Metrics': 'مؤشرات السوق',
  'Buyer_Observations': 'ملاحظات المشترين',
  'Public_Shipments': 'الشحنات العامة',
  'Company_Profiles': 'ملفات الشركات',
  'Source_Pages': 'صفحات المصادر',
  'Research_Notes': 'ملاحظات البحث',
  'Market_Scope': 'نطاق السوق',
  'Broad_Category_Only': 'فئة واسعة فقط',
  'Conflicts_Exclusions': 'التعارضات والاستثناءات',
  'Initial_Contacts': 'جهات الاتصال الأولية',
  'Free_Contacts': 'جهات الاتصال المجانية',
  'Oman_Leads': 'عملاء عمان',
  'Market_Overview': 'نظرة عامة على السوق',
  'Active_Buyers': 'المشترين النشطين',
  'Import_Shipments': 'شحنات الاستيراد',
  'Global_Suppliers': 'الموردون العالميون',
  'Exporting_Countries': 'الدول المصدرة',
  'High_Activity_Buyers': 'المشترين عاليي النشاط',
  'Medium_Activity_Buyers': 'المشترين متوسطي النشاط',
  'Low_Activity_Buyers': 'المشترين ضعيفي النشاط',
  'New_Buyers': 'المشترين الجدد',
  'Observed_Buyers': 'المشترين المشاهدين',
  'Last_3_Years': 'آخر 3 سنوات',
  'Jul_2024_Jun_2025': 'يوليو 2024 - يونيو 2025',
  'Through_Sep_2026': 'حتى سبتمبر 2026',
  'First_Shipment_In_Last_12_Months': 'أول شحنة في آخر 12 شهراً',
  'Ge10_Active_Months': '10 أشهر نشطة على الأقل',
  'Ge5_Active_Months': '5-9 أشهر نشطة',
  'Lt5_Active_Months': 'أقل من 5 أشهر نشطة',
};

const TRANSLATION_CACHE = new Map<string, string>();
const IN_FLIGHT = new Map<string, Promise<string>>();

const CONCURRENCY = 2;
let activeCount = 0;
const pendingQueue: Array<{
  task: () => Promise<string>;
  resolve: (value: string) => void;
  reject: (reason?: any) => void;
}> = [];

function enqueueTranslation(task: () => Promise<string>): Promise<string> {
  return new Promise<string>((resolve, reject) => {
    pendingQueue.push({ task, resolve, reject });
    drainQueue();
  });
}

function drainQueue() {
  while (activeCount < CONCURRENCY && pendingQueue.length > 0) {
    const item = pendingQueue.shift()!;
    activeCount++;
    item.task().then(item.resolve).catch(item.reject).finally(() => {
      activeCount--;
      drainQueue();
    });
  }
}

async function translateToArabic(text: string): Promise<string> {
  const trimmed = String(text).trim();
  if (!trimmed) return text;

  const cacheKey = trimmed.toLowerCase();
  if (TRANSLATION_CACHE.has(cacheKey)) return TRANSLATION_CACHE.get(cacheKey)!;

  const cellStr = String(text);
  const isLink = /^https?:\/\//i.test(cellStr);
  const isEmail = /^[^\s]+@[^\s]+\.[^\s]+$/.test(cellStr);
  const isPhone = /^\+?\d[\d\s\-()]{7,}$/.test(trimmed);
  if (isLink || isEmail || isPhone) return cellStr;
  if (/^[\d\s.,:\-+%$/]+$/.test(trimmed)) return cellStr;
  if (/^[A-Z0-9\-]{3,}$/i.test(trimmed) && trimmed === trimmed.toUpperCase()) return cellStr;

  if (TEXTUAL_TRANSLATIONS[trimmed]) {
    TRANSLATION_CACHE.set(cacheKey, TEXTUAL_TRANSLATIONS[trimmed]);
    return TEXTUAL_TRANSLATIONS[trimmed];
  }

  if (IN_FLIGHT.has(cacheKey)) {
    return IN_FLIGHT.get(cacheKey)!;
  }

  if (TRANSLATION_CACHE.size > 500) TRANSLATION_CACHE.clear();

  const task = async (): Promise<string> => {
    try {
      const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ar&dt=t&q=${encodeURIComponent(trimmed)}`;
      const response = await fetch(url, { headers: { Accept: 'application/json' } });
      if (response.ok) {
        const data = await response.json();
        const translated = data[0]?.map((item: any) => item[0]).join('') || trimmed;
        const final = translated || trimmed;
        TRANSLATION_CACHE.set(cacheKey, final);
        return final;
      }
    } catch {
      // ignore translation failures
    }
    return trimmed;
  };

  const promise = enqueueTranslation(task);
  IN_FLIGHT.set(cacheKey, promise);
  try {
    return await promise;
  } finally {
    IN_FLIGHT.delete(cacheKey);
  }
}

function shouldTranslate(value: string): boolean {
  if (!value) return false;
  const trimmed = String(value).trim();
  if (!trimmed) return false;
  if (/^[\d\s.,:\-+%$/]+$/.test(trimmed)) return false;
  if (/^https?:\/\//i.test(trimmed)) return false;
  if (/^[^\s]+@[^\s]+\.[^\s]+$/.test(trimmed)) return false;
  if (/^\+?\d[\d\s\-()]{7,}$/.test(trimmed)) return false;
  if (/^[A-Z0-9\-]{3,}$/i.test(trimmed) && trimmed === trimmed.toUpperCase()) return false;
  return true;
}

function translateHeader(header: string): string {
  const normalized = String(header).trim();
  if (ARABIC_HEADERS[normalized]) return ARABIC_HEADERS[normalized];
  if (!shouldTranslate(normalized)) return normalized;
  return normalized;
}

function translateCellValue(value: string): string {
  if (!value && value !== '') return value;
  const normalized = String(value).trim();
  if (!normalized) return value;

  const cellStr = String(value);
  const isLink = /^https?:\/\//i.test(cellStr);
  const isEmail = /^[^\s]+@[^\s]+\.[^\s]+$/.test(cellStr);
  const isPhone = /^\+?\d[\d\s\-()]{7,}$/.test(normalized);
  if (isLink || isEmail || isPhone) return cellStr;
  if (/^[\d\s.,:\-+%$/]+$/.test(normalized)) return cellStr;
  if (/^[A-Z0-9\-]{3,}$/i.test(normalized) && normalized === normalized.toUpperCase()) return cellStr;

  if (TEXTUAL_TRANSLATIONS[normalized]) return TEXTUAL_TRANSLATIONS[normalized];
  if (ARABIC_HEADERS[normalized]) return ARABIC_HEADERS[normalized];

  return normalized;
}

function translateSheetName(name: string): string {
  if (!name) return name;
  const normalized = name.trim();
  if (ARABIC_HEADERS[normalized]) return ARABIC_HEADERS[normalized];
  if (TEXTUAL_TRANSLATIONS[normalized]) return TEXTUAL_TRANSLATIONS[normalized];
  if (TRANSLATION_CACHE.has(normalized)) return TRANSLATION_CACHE.get(normalized)!;
  return name;
}

async function translateCellValueAsync(value: string): Promise<string> {
  if (!value && value !== '') return value;
  const normalized = String(value).trim();
  if (!normalized) return value;

  const cellStr = String(value);
  const isLink = /^https?:\/\//i.test(cellStr);
  const isEmail = /^[^\s]+@[^\s]+\.[^\s]+$/.test(cellStr);
  const isPhone = /^\+?\d[\d\s\-()]{7,}$/.test(normalized);
  if (isLink || isEmail || isPhone) return cellStr;
  if (/^[\d\s.,:\-+%$/]+$/.test(normalized)) return cellStr;
  if (/^[A-Z0-9\-]{3,}$/i.test(normalized) && normalized === normalized.toUpperCase()) return cellStr;

  if (TEXTUAL_TRANSLATIONS[normalized]) return TEXTUAL_TRANSLATIONS[normalized];
  if (ARABIC_HEADERS[normalized]) return ARABIC_HEADERS[normalized];

  return translateToArabic(normalized);
}

function formatBytes(bytes?: number): string {
  if (!bytes) return '-';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value?: string): string {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString('en-GB', { year: 'numeric', month: 'short', day: 'numeric' });
}

const FIELD_ALIASES: Record<string, string[]> = {
  company: [
    'Company',
    'Company Name',
    'Buyer',
    'Buyer Name',
    'Firm',
    'Organization',
    'Name',
    'الشركة',
    'اسم الشركة',
    'المشتري',
    'اسم المشتري',
    'المنشأة',
    'اسم المنشأة',
  ],
  mobile: [
    'Mobile',
    'Phone',
    'Public Phone-Mobile',
    'Cell',
    'Telephone',
    'Tel',
    'الجوال',
    'الموبايل',
    'هاتف',
    'هاتف عمومي/جوال',
    'رقم الجوال',
    'رقم الموبايل',
    'الهاتف',
    'الهاتف العمومي',
    'تليفون',
    'Mobile No.',
    'Mobile Number',
    'Phone No.',
    'Phone Number',
    'Cell No.',
    'Tel No.',
  ],
  email: [
    'Email',
    'E-mail',
    'Email Address',
    'E mail',
    'البريد الإلكتروني',
    'الإيميل',
    'البريد',
    'عنوان البريد',
    'بريد',
    'Email ID',
    'E-mail Address',
    'Email Address',
    'E mail Address',
    'Email Address',
  ],
  address: [
    'Address',
    'Location',
    'Office Address',
    'Plant Address',
    'العنوان',
    'الموقع',
    'موقع',
    'العنوان التجاري',
    'العنوان الرئيسي',
    'المقر',
    'Address Line',
    'Mailing Address',
    'Street Address',
    'Address ID',
  ],
  whatsApp: [
    'WhatsApp',
    'Whatsapp',
    'WhatsApp Number',
    'WA',
    'واتساب',
    'رقم واتساب',
    'الواتساب',
    'WhatsApp Contact',
    'WhatsApp ID',
    'واتساب رقم',
  ],
  website: [
    'Website',
    'URL',
    'Web',
    'Site',
    'Homepage',
    'الموقع الإلكتروني',
    'الموقع',
    'رابط الموقع',
    'الصفحة الرئيسية',
    'الرابط',
    'Website Link',
    'Site URL',
    'Web URL',
    'Homepage Link',
    'Website URL',
  ],
};

const PLACEHOLDER_VALUES = new Set(['-', 'n/a', 'na', 'not available', 'none', 'nil', '']);

function normalizeColumnName(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[\s_\-/]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function aliasMatchesColumn(alias: string, columnName: string): boolean {
  const normalizedAlias = normalizeColumnName(alias);
  const normalizedColumn = normalizeColumnName(columnName);

  if (normalizedColumn === normalizedAlias) return true;

  const aliasWithSpace = normalizedAlias + ' ';
  if (normalizedColumn.startsWith(aliasWithSpace)) return true;

  return false;
}

function hasRealValue(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  const str = String(value).trim();
  return !PLACEHOLDER_VALUES.has(str.toLowerCase());
}

type SmartFilterKey = keyof typeof FIELD_ALIASES;

type SmartFilters = Record<SmartFilterKey, boolean>;

function rowMatchesSmartFilter(row: Record<string, string>, filters: SmartFilters): boolean {
  const activeFilters = Object.entries(filters).filter(([, active]) => active) as [SmartFilterKey, boolean][];
  if (activeFilters.length === 0) return true;

  return activeFilters.every(([field]) => {
    const aliases = FIELD_ALIASES[field];
    if (!aliases || aliases.length === 0) return true;

    const matchedKeys = Object.keys(row).filter((k) =>
      aliases.some((a) => aliasMatchesColumn(a, k))
    );

    if (matchedKeys.length === 0) return false;
    return matchedKeys.some((key) => hasRealValue(row[key]));
  });
}

function detectHeaderRow(rows: Record<string, string>[]): { index: number; row: Record<string, string> } | null {
  if (!rows.length) return null;

  const allAliases = Object.values(FIELD_ALIASES).flatMap((aliases) => aliases);

  const searchLimit = Math.min(rows.length, 30);
  let bestIndex = -1;
  let bestScore = -1;

  for (let i = 0; i < searchLimit; i++) {
    const row = rows[i];
    let score = 0;

    Object.values(row).forEach((value) => {
      const str = String(value ?? '').trim();
      if (!str) return;
      const matched = allAliases.some((alias) => aliasMatchesColumn(alias, str));
      if (matched) {
        score++;
      }
    });

    if (score > bestScore) {
      bestScore = score;
      bestIndex = i;
    }
  }

  if (bestIndex >= 0 && bestScore > 0) {
    return { index: bestIndex, row: rows[bestIndex] };
  }
  return null;
}

const COUNTRY_ALIASES: Record<string, string> = {
  'الإمارات': 'UAE',
  'السعودية': 'KSA',
  'قطر': 'Qatar',
  'الكويت': 'Kuwait',
  'البحرين': 'Bahrain',
  'عمان': 'Oman',
  'العراق': 'Iraq',
  'الأردن': 'Jordan',
  'لبنان': 'Lebanon',
  'مصر': 'Egypt',
};

const getCanonicalCountry = (country: string | null | undefined): string | undefined => {
  if (!country) return undefined;
  const trimmed = country.trim();
  return COUNTRY_ALIASES[trimmed] || trimmed;
};

const SMART_FILTER_LABELS: Record<SmartFilterKey, string> = {
  company: 'اسم الشركة',
  mobile: 'الموبايل',
  email: 'البريد الإلكتروني',
  address: 'العنوان',
  whatsApp: 'WhatsApp',
  website: 'الموقع الإلكتروني',
};

type ViewMode = 'countries' | 'country-detail' | 'file-content';

export function PotentialCustomers() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [view, setView] = useState<ViewMode>('countries');
  const [countries, setCountries] = useState<PotentialCustomerCountry[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<PotentialCustomerCountry | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openFileId, setOpenFileId] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<PotentialCustomerCountry['files'][number] | null>(null);
  const [excelContent, setExcelContent] = useState<PotentialCustomerExcelContent | null>(null);
  const [activeSheet, setActiveSheet] = useState<string | null>(null);
  const [contentLoading, setContentLoading] = useState<boolean>(false);
  const [contentError, setContentError] = useState<string | null>(null);
  const [translatedRows, setTranslatedRows] = useState<Record<string, string>[]>([]);
  const [isTranslating, setIsTranslating] = useState(false);
  const [arabicMode, setArabicMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sheetTranslations, setSheetTranslations] = useState<Record<string, string>>({});
  const [smartFilterOpen, setSmartFilterOpen] = useState(false);
  const [smartFilters, setSmartFilters] = useState<SmartFilters>({
    company: false,
    mobile: false,
    email: false,
    address: false,
    whatsApp: false,
    website: false,
  });
    const [selectedDisplayIndex, setSelectedDisplayIndex] = useState<number | null>(null);
    const [copiedField, setCopiedField] = useState<string | null>(null);
    const [modalIsCustomerAdded, setModalIsCustomerAdded] = useState(false);

  const loadCountries = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listPotentialCustomerCountries();
      setCountries(res.data.countries || []);
      if (res.data.error) {
        setError(res.data.error);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load potential customers.');
      setCountries([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCountries();
  }, []);

  useEffect(() => {
    if (selectedDisplayIndex === null) {
      setModalIsCustomerAdded(false);
    }
  }, [selectedDisplayIndex]);

  const openCountry = async (country: PotentialCustomerCountry) => {
    setSelectedCountry(country);
    setView('country-detail');
    setOpenFileId(null);
  };

  const backToCountries = () => {
    setView('countries');
    setSelectedCountry(null);
    setOpenFileId(null);
    setSelectedFile(null);
    setExcelContent(null);
    setActiveSheet(null);
    setContentError(null);
    setTranslatedRows([]);
    setIsTranslating(false);
    setSheetTranslations({});
    setSmartFilterOpen(false);
    setSmartFilters({
      company: false,
      mobile: false,
      email: false,
      address: false,
      whatsApp: false,
      website: false,
    });
    setSelectedDisplayIndex(null);
  };

  const checkCustomerAdded = async (companyName?: string | null) => {
    const trimmedName = companyName?.trim();
    if (!trimmedName) return false;
    try {
      const res = await api.get('/api/v1/customers/check-source', { params: { company_name: trimmedName } });
      return res.data?.exists === true;
    } catch (error) {
      console.error('checkCustomerAdded failed:', error);
      return false;
    }
  };

  const displayRows = useMemo(() => {
    if (!excelContent || !excelContent.rows?.length) return [];

    const useTranslated = arabicMode && !isTranslating && translatedRows && translatedRows.length === excelContent.rows.length;
    const sourceRows = useTranslated ? translatedRows : excelContent.rows;

    const detectedHeader = detectHeaderRow(excelContent.rows);
    const headerRow = detectedHeader?.row || excelContent.rows[0] || {};
    const headerRowIndex = detectedHeader?.index ?? 0;

    const columnNameMap: Record<string, string> = {};
    Object.entries(headerRow).forEach(([key, value]) => {
      columnNameMap[key] = String(value ?? '');
    });

    const mapRowKeys = (row: Record<string, string>) => {
      const keys = Object.keys(row);
      const allNumeric = keys.length > 0 && keys.every((k) => /^\d+$/.test(k));
      if (allNumeric) {
        const mapped: Record<string, string> = {};
        Object.entries(row).forEach(([key, value]) => {
          mapped[columnNameMap[key] || key] = value;
        });
        return mapped;
      }

      const numericKeys = keys.filter((k) => /^\d+$/.test(k));
      if (numericKeys.length === 0) return row;

      const mapped: Record<string, string> = {};
      Object.entries(row).forEach(([key, value]) => {
        if (key === '__excel_row__') {
          mapped[key] = value;
          return;
        }
        mapped[columnNameMap[key] || key] = value;
      });
      return mapped;
    };

    let result = sourceRows;

    const activeFilters = Object.entries(smartFilters).filter(([, active]) => active) as [SmartFilterKey, boolean][];
    if (activeFilters.length > 0 && sourceRows.length === excelContent.rows.length) {
      const dataStartIndex = detectedHeader ? headerRowIndex + 1 : 1;
      const dataRows = sourceRows.slice(dataStartIndex);
      result = dataRows.filter((row, i) => {
        const originalRow = excelContent.rows[dataStartIndex + i];
        const mappedRow = mapRowKeys(originalRow);
        return rowMatchesSmartFilter(mappedRow, Object.fromEntries(activeFilters) as SmartFilters);
      });
    }

    if (searchQuery) {
      result = result.filter((row) => {
        const cells = Object.values(row);
        return cells.some((cell) => String(cell).toLowerCase().includes(searchQuery.toLowerCase()));
      });
    }

    const headerRowString = JSON.stringify(headerRow);
    result = result.filter((row) => JSON.stringify(row) !== headerRowString);

    const companyAliases = FIELD_ALIASES.company.map((a) => normalizeColumnName(a));
    const mobileAliases = FIELD_ALIASES.mobile.map((a) => normalizeColumnName(a));
    const whatsAppAliases = FIELD_ALIASES.whatsApp.map((a) => normalizeColumnName(a));

    const enriched = result.map((row, idx) => {
      const mapped = mapRowKeys(row);
      const companyKey = Object.keys(mapped).find((k) => companyAliases.includes(normalizeColumnName(k)));
      const mobileKey = Object.keys(mapped).find((k) => mobileAliases.includes(normalizeColumnName(k)));
      const whatsAppKey = Object.keys(mapped).find((k) => whatsAppAliases.includes(normalizeColumnName(k)));
      const companyValue = companyKey ? String(mapped[companyKey] ?? '').trim() : '';
      const mobileValue = mobileKey ? String(mapped[mobileKey] ?? '').trim() : '';
      const whatsAppValue = whatsAppKey ? String(mapped[whatsAppKey] ?? '').trim() : '';
      const contactReady = !!companyValue && (hasRealValue(mobileValue) || hasRealValue(whatsAppValue));
      return { row, contactReady, originalIndex: idx, companyValue };
    });

    enriched.sort((a, b) => {
      if (a.contactReady && !b.contactReady) return -1;
      if (!a.contactReady && b.contactReady) return 1;
      return a.originalIndex - b.originalIndex;
    });

    return enriched;
  }, [excelContent, arabicMode, isTranslating, translatedRows, smartFilters, searchQuery]);

  const loadFileContent = async (file: PotentialCustomerCountry['files'][number]) => {
    setSelectedFile(file);
    setContentLoading(true);
    setContentError(null);
    setExcelContent(null);
    setActiveSheet(null);
    try {
      const res = await getPotentialCustomerFileContent(file.id);
      const data = res.data;
      setExcelContent(data);
      setActiveSheet(data.active_sheet || data.sheets[0]?.name || null);
    } catch (err: any) {
      setContentError(err?.response?.data?.detail || 'Failed to load Excel content.');
    } finally {
      setContentLoading(false);
    }
  };

  useEffect(() => {
    if (!selectedFile?.id || !activeSheet) return;

    const loadSheetContent = async () => {
      setContentLoading(true);
      setContentError(null);
      try {
        const res = await getPotentialCustomerFileContent(selectedFile.id, activeSheet);
        const data = res.data;
        setExcelContent(data);
      } catch (err: any) {
        setContentError(err?.response?.data?.detail || 'Failed to load Excel content.');
      } finally {
        setContentLoading(false);
      }
    };

    loadSheetContent();
  }, [selectedFile?.id, activeSheet]);

  useEffect(() => {
    if (selectedDisplayIndex === null || !displayRows[selectedDisplayIndex]) return;

    const item = displayRows[selectedDisplayIndex];

    const mapped = item.row;
    const detectedHeader = excelContent ? detectHeaderRow(excelContent.rows) : null;
    const headerRow = detectedHeader?.row || excelContent?.rows?.[0] || {};
    const columnNameMap: Record<string, string> = {};
    Object.entries(headerRow).forEach(([key, value]) => {
      columnNameMap[key] = String(value ?? '');
    });
    const mapRowKeys = (row: Record<string, string>) => {
      const keys = Object.keys(row);
      const allNumeric = keys.length > 0 && keys.every((k) => /^\d+$/.test(k));
      if (allNumeric) {
        const mapped: Record<string, string> = {};
        Object.entries(row).forEach(([key, value]) => {
          mapped[columnNameMap[key] || key] = value;
        });
        return mapped;
      }

      const numericKeys = keys.filter((k) => /^\d+$/.test(k));
      if (numericKeys.length === 0) return row;

      const mapped: Record<string, string> = {};
      Object.entries(row).forEach(([key, value]) => {
        if (key === '__excel_row__') {
          mapped[key] = value;
          return;
        }
        mapped[columnNameMap[key] || key] = value;
      });
      return mapped;
    };
    const mappedRow = mapRowKeys(mapped);

    const companyAliases = FIELD_ALIASES.company.map((a) => normalizeColumnName(a));
    const companyKey = Object.keys(mappedRow).find((k) => companyAliases.includes(normalizeColumnName(k)));
    const companyValue = companyKey ? String(mappedRow[companyKey] ?? '').trim() : '';

    checkCustomerAdded(companyValue || undefined).then((exists) => {
      setModalIsCustomerAdded(exists);
    });
  }, [selectedDisplayIndex, displayRows, excelContent, selectedCountry]);

  useEffect(() => {
    if (!excelContent || !arabicMode) {
      setTranslatedRows([]);
      return;
    }

    const translateAll = async () => {
      setIsTranslating(true);
      try {
        const translated = await Promise.all(
          excelContent.rows.map(async (row) => {
            const newRow: Record<string, string> = {};
            for (const [key, value] of Object.entries(row)) {
              if (key === '__excel_row__') {
                newRow[key] = value;
                continue;
              }
              newRow[key] = await translateCellValueAsync(value);
            }
            return newRow;
          })
        );
        setTranslatedRows(translated);
      } catch (error) {
        console.error('Translation error:', error);
      } finally {
        setIsTranslating(false);
      }
    };

    translateAll();
  }, [excelContent, arabicMode, activeSheet]);

  useEffect(() => {
    if (!excelContent || !arabicMode) {
      setSheetTranslations({});
      return;
    }

    const translateSheetNames = async () => {
      const next: Record<string, string> = {};
      for (const sheet of excelContent.sheets) {
        const normalized = sheet.name.trim();
        if (!normalized) continue;
        if (ARABIC_HEADERS[normalized] || TEXTUAL_TRANSLATIONS[normalized]) {
          next[sheet.name] = ARABIC_HEADERS[normalized] || TEXTUAL_TRANSLATIONS[normalized];
          continue;
        }
        if (TRANSLATION_CACHE.has(normalized)) {
          next[sheet.name] = TRANSLATION_CACHE.get(normalized)!;
          continue;
        }
        if (!shouldTranslate(normalized)) {
          next[sheet.name] = sheet.name;
          continue;
        }

        try {
          const translated = await translateToArabic(normalized);
          if (translated && translated !== normalized) {
            TRANSLATION_CACHE.set(normalized, translated);
            next[sheet.name] = translated;
          } else {
            next[sheet.name] = sheet.name;
          }
        } catch {
          next[sheet.name] = sheet.name;
        }
      }
      setSheetTranslations(next);
    };

    translateSheetNames();
  }, [excelContent, arabicMode]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex items-center gap-2 text-slate-500">
          <Loader2 className="animate-spin" size={20} />
          <span>{t('common.loading') || 'Loading...'}</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div dir={i18n.language === 'ar' ? 'rtl' : 'ltr'} className="max-w-3xl mx-auto mt-10">
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-6 text-sm">
          <h2 className="text-lg font-semibold mb-2">Potential Customers data unavailable</h2>
          <p className="mb-2">Real data import from Google Drive is required to use this page.</p>
          <p className="mb-2">Error: {error}</p>
          <p className="text-xs text-red-600">
            To enable real data import, provide Google Drive credentials via one of:
            <br />- GOOGLE_SERVICE_ACCOUNT_JSON environment variable
            <br />- GOOGLE_OAUTH_CREDENTIALS_JSON environment variable
            <br />Then run: python scripts/import_google_drive.py
          </p>
        </div>
      </div>
    );
  }

  if (view === 'country-detail' && selectedCountry) {
    return (
      <div dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}>
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={backToCountries}
            className="inline-flex items-center gap-1 text-sm text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-3 py-2 rounded-lg transition-colors"
          >
            <ArrowLeft size={16} />
            {t('common.back') || 'Back'}
          </button>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{selectedCountry.name}</h1>
            <p className="text-sm text-slate-500">
              {selectedCountry.file_count} {t('common.files') || 'files'}
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {selectedCountry.files.map((file) => (
            <div
              key={file.id}
              className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden"
            >
              <div className="flex items-center justify-between p-4">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-emerald-50 rounded-lg">
                    <FileSpreadsheet className="text-emerald-600" size={22} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">{file.name}</h3>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-1">
                      {file.source && (
                        <span className="inline-flex items-center gap-1">
                          <Globe size={12} /> {file.source}
                        </span>
                      )}
                      {file.sheet_count != null && (
                        <span>{file.sheet_count} sheets</span>
                      )}
                      {file.row_count != null && (
                        <span>{file.row_count.toLocaleString()} rows</span>
                      )}
                      <span>{formatBytes(file.size_bytes)}</span>
                      <span>Modified: {formatDate(file.modified_time)}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setOpenFileId(openFileId === file.id ? null : file.id)}
                    className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-2 rounded-lg transition-colors"
                  >
                    {openFileId === file.id ? 'Hide Details' : 'Details'}
                  </button>
                  <button
                    onClick={() => loadFileContent(file)}
                    className="text-xs bg-emerald-50 hover:bg-emerald-100 text-emerald-700 px-3 py-2 rounded-lg transition-colors"
                  >
                    Open
                  </button>
                  {file.view_url && (
                    <a
                      href={file.view_url}
                      target="_blank"
                      rel="noreferrer noopener"
                      className="inline-flex items-center gap-1 text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 px-3 py-2 rounded-lg transition-colors"
                    >
                      <ExternalLink size={14} />
                      Drive
                    </a>
                  )}
                </div>
              </div>

              {openFileId === file.id && (
                <div className="border-t border-slate-100 bg-slate-50 p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-slate-500">File ID: </span>
                      <span className="font-mono text-slate-700">{file.id}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Source: </span>
                      <span className="text-slate-700">{file.source || '-'}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Sheets: </span>
                      <span className="text-slate-700">{file.sheet_count ?? '-'}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Rows: </span>
                      <span className="text-slate-700">{file.row_count?.toLocaleString() || '-'}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Size: </span>
                      <span className="text-slate-700">{formatBytes(file.size_bytes)}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Created: </span>
                      <span className="text-slate-700">{formatDate(file.created_time)}</span>
                    </div>
                    <div className="md:col-span-2">
                      <span className="text-slate-500">Modified: </span>
                      <span className="text-slate-700">{formatDate(file.modified_time)}</span>
                    </div>
                  </div>
                  {file.view_url && (
                    <div className="mt-4">
                      <a
                        href={file.view_url}
                        target="_blank"
                        rel="noreferrer noopener"
                        className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                      >
                        <ExternalLink size={16} />
                        Open in Google Drive
                      </a>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}

          {selectedCountry.files.length === 0 && (
            <div className="bg-white rounded-xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
              {t('common.noData') || 'No files found for this country.'}
            </div>
          )}

          {contentError && (
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 text-sm">
              {contentError}
            </div>
          )}

          {contentLoading && (
            <div className="flex items-center justify-center py-12 text-sm text-slate-500">
              <Loader2 className="animate-spin mr-2" size={18} />
              Loading Excel content...
            </div>
          )}

          {!contentLoading && excelContent && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-visible">
              <div className="p-4 border-b border-slate-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-900">{selectedFile?.name || excelContent.file_name}</h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {selectedCountry?.name} • {excelContent.sheets.length} sheets • {displayRows.length} / {excelContent.rows.length} rows
                      {arabicMode && <span className="mr-2 text-amber-600">• ترجمة آلية</span>}
                    </p>
                  </div>
                </div>
              </div>

              <div className="border-b border-slate-200 bg-white">
                <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-thin">
                  {excelContent.sheets.map((sheet) => (
                    <button
                      key={sheet.name}
                      onClick={() => setActiveSheet(sheet.name)}
                      className={`text-xs px-3 py-1.5 rounded-md border transition-colors whitespace-nowrap ${
                        activeSheet === sheet.name
                          ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                          : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50 hover:border-slate-400'
                      }`}
                    >
                      {arabicMode ? (sheetTranslations[sheet.name] || sheet.name) : sheet.name}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between gap-2 p-3 border-b border-slate-100 bg-slate-50/60">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setArabicMode(false)}
                    className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                      !arabicMode ? 'bg-slate-900 text-white border-slate-900' : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-100'
                    }`}
                  >
                    عرض الأصل
                  </button>
                  <button
                    onClick={() => setArabicMode(true)}
                    className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                      arabicMode ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-100'
                    }`}
                  >
                    🌐 عرض بالعربية
                  </button>
                </div>
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="بحث..."
                      className="pl-8 pr-3 py-1.5 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 outline-none"
                    />
                  </div>
                  <div className="relative">
                    <button
                      onClick={() => setSmartFilterOpen((prev) => !prev)}
                      className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                        smartFilterOpen
                          ? 'bg-emerald-600 text-white border-emerald-600'
                          : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-100'
                      }`}
                    >
                      🎯 فلترة ذكية
                    </button>
                    {smartFilterOpen && (
                      <div className="absolute top-full mt-2 right-0 bg-white border border-slate-200 rounded-xl shadow-lg p-4 z-50 min-w-[240px]">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-xs font-semibold text-slate-900">شروط الفلترة</span>
                        <button
                          onClick={() =>
                            setSmartFilters({
                              company: false,
                              mobile: false,
                              email: false,
                              address: false,
                              whatsApp: false,
                              website: false,
                            })
                          }
                          className="text-xs text-red-600 hover:text-red-700"
                        >
                          إعادة تعيين
                        </button>
                      </div>
                      <div className="space-y-2">
                        {(Object.keys(FIELD_ALIASES) as SmartFilterKey[]).map((field) => (
                          <label key={field} className="flex items-center gap-2 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={smartFilters[field]}
                              onChange={(e) =>
                                setSmartFilters((prev) => ({
                                  ...prev,
                                  [field]: e.target.checked,
                                }))
                              }
                              className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                            />
                            <span className="text-xs text-slate-700">{SMART_FILTER_LABELS[field]}</span>
                          </label>
                        ))}
                      </div>
                      <div className="mt-3 pt-3 border-t border-slate-100 text-xs text-slate-500">
                        النتائج: <span className="font-semibold text-slate-900">{displayRows.length}</span> من {excelContent?.rows.length || 0}
                      </div>
                    </div>
                  )}
                  </div>
                  {selectedFile?.view_url && (
                    <a
                      href={selectedFile.view_url}
                      target="_blank"
                      rel="noreferrer noopener"
                      className="inline-flex items-center gap-1 text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg transition-colors"
                    >
                      <ExternalLink size={14} />
                      فتح في Google Drive
                    </a>
                  )}
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-semibold text-slate-500 uppercase whitespace-nowrap sticky left-0 bg-slate-50 z-10 border-b border-slate-200">#</th>
                      {activeSheet &&
                        (() => {
                          const detectedHeader = detectHeaderRow(excelContent.rows);
                          const headerRow = detectedHeader?.row || excelContent.rows[0] || {};
                          const cols = Object.keys(headerRow);
                          return cols.map((col) => (
                            <th key={col} className="px-3 py-2 text-left text-xs font-semibold text-slate-500 uppercase whitespace-nowrap border-b border-slate-200">
                              {arabicMode ? translateHeader(col) : col}
                            </th>
                          ));
                        })()}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {displayRows.map((item, idx) => {
                      const row = item.row;
                      const cells = Object.values(row);
                      const isSelected = selectedDisplayIndex === idx;
                      return (
                        <tr
                          key={item.originalIndex}
                          className={`hover:bg-slate-50 cursor-pointer ${isSelected ? 'bg-blue-50' : ''} ${item.contactReady ? 'border-l-4 border-l-emerald-500' : ''}`}
                          onClick={() => setSelectedDisplayIndex(isSelected ? null : idx)}
                        >
                          <td className="px-3 py-2 text-xs text-slate-500 whitespace-nowrap sticky left-0 bg-white z-10 border-b border-slate-100">
                            <div className="flex items-center gap-2">
                              {item.contactReady && <CheckCircle className="text-emerald-600" size={16} />}
                              {idx + 1}
                            </div>
                          </td>
                          {cells.map((cell, cellIdx) => {
                            const cellStr = String(cell ?? '');
                            const isLink = /^https?:\/\//i.test(cellStr);
                            const isEmail = /^[^\s]+@[^\s]+\.[^\s]+$/.test(cellStr);
                            const isPhone = /^\+?\d[\d\s\-()]{7,}$/.test(cellStr.trim());
                            const displayValue = arabicMode ? translateCellValue(cellStr) : cellStr;
                            return (
                              <td key={cellIdx} className="px-3 py-2 text-xs text-slate-700 whitespace-nowrap max-w-[320px] truncate border-b border-slate-100">
                                {isEmail ? (
                                  <a href={`mailto:${cellStr}`} className="text-blue-600 hover:underline">{displayValue}</a>
                                ) : isLink ? (
                                  <a href={cellStr} target="_blank" rel="noreferrer noopener" className="text-blue-600 hover:underline">{displayValue}</a>
                                ) : isPhone ? (
                                  <a href={`tel:${cellStr}`} className="text-blue-600 hover:underline">{displayValue}</a>
                                ) : (
                                  displayValue
                                )}
                              </td>
                            );
                          })}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              <Dialog open={selectedDisplayIndex !== null} onOpenChange={(open) => { if (!open) setSelectedDisplayIndex(null); }}>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                  {selectedDisplayIndex !== null && displayRows[selectedDisplayIndex] && (() => {
                    const selected = displayRows[selectedDisplayIndex];
                    const mapped = selected.row;

                    const detectedHeader = excelContent ? detectHeaderRow(excelContent.rows) : null;
                    const headerRow = detectedHeader?.row || excelContent?.rows?.[0] || {};
                    const columnNameMap: Record<string, string> = {};
                    Object.entries(headerRow).forEach(([key, value]) => {
                      columnNameMap[key] = String(value ?? '');
                    });
                    const mapRowKeys = (row: Record<string, string>) => {
                      const keys = Object.keys(row);
                      const allNumeric = keys.length > 0 && keys.every((k) => /^\d+$/.test(k));
                      if (allNumeric) {
                        const mapped: Record<string, string> = {};
                        Object.entries(row).forEach(([key, value]) => {
                          mapped[columnNameMap[key] || key] = value;
                        });
                        return mapped;
                      }

                      const numericKeys = keys.filter((k) => /^\d+$/.test(k));
                      if (numericKeys.length === 0) return row;

                      const mapped: Record<string, string> = {};
                      Object.entries(row).forEach(([key, value]) => {
                        if (key === '__excel_row__') {
                          mapped[key] = value;
                          return;
                        }
                        mapped[columnNameMap[key] || key] = value;
                      });
                      return mapped;
                    };
                    const mappedRow = mapRowKeys(mapped);

                    const companyAliases = FIELD_ALIASES.company.map((a) => normalizeColumnName(a));
                    const mobileAliases = FIELD_ALIASES.mobile.map((a) => normalizeColumnName(a));
                    const whatsAppAliases = FIELD_ALIASES.whatsApp.map((a) => normalizeColumnName(a));
                    const emailAliases = FIELD_ALIASES.email.map((a) => normalizeColumnName(a));
                    const addressAliases = FIELD_ALIASES.address.map((a) => normalizeColumnName(a));
                    const websiteAliases = FIELD_ALIASES.website.map((a) => normalizeColumnName(a));
                    const companyKey = Object.keys(mappedRow).find((k) => companyAliases.includes(normalizeColumnName(k)));
                    const mobileKey = Object.keys(mappedRow).find((k) => mobileAliases.includes(normalizeColumnName(k)));
                    const whatsAppKey = Object.keys(mappedRow).find((k) => whatsAppAliases.includes(normalizeColumnName(k)));
                    const emailKey = Object.keys(mappedRow).find((k) => emailAliases.includes(normalizeColumnName(k)));
                    const addressKey = Object.keys(mappedRow).find((k) => addressAliases.includes(normalizeColumnName(k)));
                    const websiteKey = Object.keys(mappedRow).find((k) => websiteAliases.includes(normalizeColumnName(k)));
                     const companyValue = companyKey ? (String(mappedRow[companyKey] ?? '').trim() || '—') : '—';
                     const mobileValue = mobileKey ? (String(mappedRow[mobileKey] ?? '').trim() || '—') : '—';
                     const whatsAppValue = whatsAppKey ? (String(mappedRow[whatsAppKey] ?? '').trim() || '—') : '—';
                     const emailValue = emailKey ? (String(mappedRow[emailKey] ?? '').trim() || '—') : '—';
                     const addressValue = addressKey ? (String(mappedRow[addressKey] ?? '').trim() || '—') : '—';
                     const websiteValue = websiteKey ? (String(mappedRow[websiteKey] ?? '').trim() || '—') : '—';
                     const contactReady = selected.contactReady;

                     const contactFieldKeys = new Set([companyKey, mobileKey, whatsAppKey, emailKey, addressKey, websiteKey].filter(Boolean));
                     const allRowFields = Object.entries(mappedRow)
                       .map(([key, value]) => ({ key, value: String(value ?? '').trim() || '—' }));

                     const contactFields = [
                       { label: 'اسم الشركة', value: companyValue, key: companyKey },
                       { label: 'الموبايل', value: mobileValue, key: mobileKey },
                       { label: 'WhatsApp', value: whatsAppValue, key: whatsAppKey },
                       { label: 'البريد الإلكتروني', value: emailValue, key: emailKey },
                       { label: 'العنوان', value: addressValue, key: addressKey },
                       { label: 'الموقع الإلكتروني', value: websiteValue, key: websiteKey },
                     ];

                     const otherFields = allRowFields.filter((field) => !contactFieldKeys.has(field.key));

                     const handleCopy = async (value: string, fieldKey: string) => {
                       if (!value || value === '—') return;
                       await navigator.clipboard.writeText(value);
                       setCopiedField(fieldKey);
                       setTimeout(() => setCopiedField(null), 1500);
                     };

                    const handlePrev = () => {
                      if (selectedDisplayIndex !== null && selectedDisplayIndex > 0) {
                        setSelectedDisplayIndex(selectedDisplayIndex - 1);
                      }
                    };

                    const handleNext = () => {
                      if (selectedDisplayIndex !== null && selectedDisplayIndex < displayRows.length - 1) {
                        setSelectedDisplayIndex(selectedDisplayIndex + 1);
                      }
                    };

                    return (
                      <>
                         <DialogHeader>
                           <div className="flex items-center justify-between">
                             <div className="flex items-center gap-3">
                               <DialogTitle className="text-lg font-semibold text-slate-900">{companyValue}</DialogTitle>
                               {contactReady ? (
                                 <span className="inline-flex items-center gap-1 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-full px-2 py-0.5">
                                   <CheckCircle size={14} />
                                   جاهز للتواصل
                                 </span>
                               ) : (
                                 <span className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-full px-2 py-0.5">
                                   بيانات غير مكتملة للتواصل
                                 </span>
                               )}
                             </div>
                               <div className="flex items-center gap-2">
                                      <button
                                        onClick={() => {
                                          const excelRow = (mappedRow as any)?.__excel_row__;
                                          const safeForm: Record<string, string> = {
                                            name: companyValue !== '—' ? companyValue : '',
                                            name_en: companyValue !== '—' ? companyValue : '',
                                            contact_person: '',
                                            job_title: '',
                                            email: emailValue !== '—' ? emailValue : '',
                                            phone: mobileValue !== '—' ? mobileValue : '',
                                            mobile: mobileValue !== '—' ? mobileValue : '',
                                            whatsapp: whatsAppValue !== '—' ? whatsAppValue : '',
                                            website: websiteValue !== '—' ? websiteValue : '',
                                            address: addressValue !== '—' ? addressValue : '',
                                            city: '',
                                            country: selectedCountry?.name || '',
                                            tax_id: '',
                                            import_license: '',
                                            commercial_registration: '',
                                            category: '',
                                            crm_status: 'prospect',
                                            verification_status: 'unverified',
                                            activity_status: 'unknown',
                                            notes: '',
                                            source_url: '',
                                          };
                                          try {
                                            sessionStorage.setItem('potentialCustomerForm', JSON.stringify(safeForm));
                                            sessionStorage.setItem('potentialCustomerSourceRow', JSON.stringify(mappedRow));
                                            if (excelRow) {
                                              sessionStorage.setItem('potentialCustomerExcelRow', String(excelRow));
                                            }
                                            if (selectedFile?.id) {
                                              sessionStorage.setItem('potentialCustomerFileId', selectedFile.id);
                                            }
                                            if (activeSheet) {
                                              sessionStorage.setItem('potentialCustomerSheetName', activeSheet);
                                            }
                                          } catch {
                                            // ignore storage failure
                                          }
                                          navigate('/customers');
                                        }}
                                        disabled={modalIsCustomerAdded}
                                        className={modalIsCustomerAdded ? 'inline-flex items-center gap-1 text-xs bg-amber-100 text-amber-700 border border-amber-200 px-3 py-1.5 rounded-lg cursor-not-allowed opacity-100' : 'inline-flex items-center gap-1 text-xs bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-lg transition-colors'}
                                        type="button"
                                      >
                                        <UserPlus size={14} />
                                        {modalIsCustomerAdded ? 'تمت إضافة العميل' : 'إضافة عميل'}
                                      </button>
                               <span className="text-xs text-slate-500">
                                 {selectedDisplayIndex + 1} / {displayRows.length}
                               </span>
                              <button
                                onClick={handlePrev}
                                disabled={selectedDisplayIndex === 0}
                                className="p-1.5 rounded-md border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                type="button"
                                aria-label="Previous"
                              >
                                <ChevronLeft size={16} />
                              </button>
                              <button
                                onClick={handleNext}
                                disabled={selectedDisplayIndex === displayRows.length - 1}
                                className="p-1.5 rounded-md border border-slate-200 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                type="button"
                                aria-label="Next"
                              >
                                <ChevronRight size={16} />
                              </button>
                            </div>
                          </div>
                        </DialogHeader>
                        <DialogDescription className="text-slate-500">
                          جميع البيانات المتاحة للشركة
                        </DialogDescription>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                          {contactFields.map((field) => {
                            const isContact = contactFieldKeys.has(field.key);
                            const isCopied = copiedField === field.key;
                            const isEmpty = field.value === '—';
                            return (
                              <div key={field.label} className={`rounded-lg border bg-white p-3 ${isContact ? 'border-emerald-200' : 'border-slate-200'}`}>
                                <div className={`text-xs font-semibold mb-1 ${isContact ? 'text-emerald-700' : 'text-slate-500'}`}>{field.label}</div>
                                <div className="flex items-center justify-between gap-2">
                                  <div className={`text-sm break-all flex-1 ${isEmpty ? 'text-slate-400' : 'text-slate-900'}`} title={field.value}>{field.value}</div>
                                  {!isEmpty && (
                                    <button
                                      onClick={() => handleCopy(field.value, field.key)}
                                      className={`shrink-0 inline-flex items-center gap-1 text-xs border rounded-md px-2 py-1 transition-colors ${isCopied ? 'text-emerald-700 border-emerald-300 bg-emerald-50' : 'text-slate-500 border-slate-200 bg-white hover:text-emerald-700 hover:border-emerald-300'}`}
                                      type="button"
                                    >
                                      {isCopied ? <CheckCircle size={12} /> : <Copy size={12} />}
                                      {isCopied ? 'تم النسخ' : 'نسخ'}
                                    </button>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                          {otherFields.map((field) => {
                            const isCopied = copiedField === field.key;
                            const isEmpty = field.value === '—';
                            return (
                              <div key={field.key} className="rounded-lg border border-slate-200 bg-white p-3">
                                <div className="text-xs font-semibold text-slate-500 mb-1">{field.key}</div>
                                <div className="flex items-center justify-between gap-2">
                                  <div className={`text-sm break-all flex-1 ${isEmpty ? 'text-slate-400' : 'text-slate-900'}`} title={field.value}>{field.value}</div>
                                  {!isEmpty && (
                                    <button
                                      onClick={() => handleCopy(field.value, field.key)}
                                      className={`shrink-0 inline-flex items-center gap-1 text-xs border rounded-md px-2 py-1 transition-colors ${isCopied ? 'text-emerald-700 border-emerald-300 bg-emerald-50' : 'text-slate-500 border-slate-200 bg-white hover:text-emerald-700 hover:border-emerald-300'}`}
                                      type="button"
                                    >
                                      {isCopied ? <CheckCircle size={12} /> : <Copy size={12} />}
                                      {isCopied ? 'تم النسخ' : 'نسخ'}
                                    </button>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>

                        <div className="mt-4 flex justify-end">
                          <button
                            onClick={() => setSelectedDisplayIndex(null)}
                            className="text-xs text-slate-500 hover:text-slate-700 border border-slate-200 rounded-md px-3 py-1.5"
                            type="button"
                          >
                            إغلاق
                          </button>
                        </div>
                      </>
                    );
                  })()}
                </DialogContent>
              </Dialog>
              <div className="p-3 text-xs text-slate-500 border-t border-slate-100">
                {displayRows.length} / {excelContent.rows.length} rows • {excelContent.sheets.length} sheets • sheet: {arabicMode ? (sheetTranslations[activeSheet || ''] || activeSheet || '-') : (activeSheet || '-')}
                {arabicMode && <span className="mr-2 text-amber-600">• ترجمة آلية</span>}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div dir={i18n.language === 'ar' ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Potential Customers</h1>
          <p className="text-sm text-slate-500">
            {countries.length} {t('common.countries') || 'countries'} · {countries.reduce((sum, c) => sum + c.file_count, 0)} files
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {countries.map((country) => (
          <button
            key={country.id}
            onClick={() => openCountry(country)}
            className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 text-left hover:border-blue-300 hover:shadow-md transition-all group"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
                  <FolderOpen className="text-blue-600" size={22} />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">{country.name}</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {country.file_count} {country.file_count === 1 ? 'file' : 'files'}
                  </p>
                </div>
              </div>
              <ChevronRight className="text-slate-400 group-hover:text-blue-500 transition-colors" size={18} />
            </div>
          </button>
        ))}
      </div>

      {countries.length === 0 && (
        <div className="bg-white rounded-xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
          {t('common.noData') || 'No countries found.'}
        </div>
      )}
    </div>
  );
}
