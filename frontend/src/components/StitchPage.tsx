import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { extractStitch } from '@/lib/stitch';
import { normalizeHomeText } from '@/locales/homeTranslations';

interface StitchPageProps {
  raw: string;
  onMount?: (container: HTMLDivElement) => (() => void) | void;
  translations?: Record<string, string>;
  attrTranslations?: Record<string, Record<string, string>>;
}

const isLanguageButton = (btn: HTMLButtonElement): boolean => {
  const label = (btn.getAttribute('aria-label') || '').toLowerCase();
  const text = (btn.textContent || '').trim();
  return (
    label.includes('switch language') ||
    label.includes('language') ||
    text === 'EN' ||
    text === 'AR' ||
    text === 'English' ||
    text === 'العربية'
  );
};

const applyLanguageToDocument = (lng: string) => {
  document.documentElement.lang = lng;
  document.documentElement.dir = lng === 'ar' ? 'rtl' : 'ltr';
};

const applyLanguageToButtons = (container: HTMLDivElement | null, lng: string) => {
  if (!container) return;
  const buttons = Array.from(container.querySelectorAll('button')) as HTMLButtonElement[];
  buttons.forEach((btn) => {
    if (!isLanguageButton(btn)) return;
    const isAr = lng === 'ar';
    btn.textContent = isAr ? 'EN' : 'AR';
    btn.setAttribute('aria-label', isAr ? 'Switch language to English' : 'تغيير اللغة إلى العربية');
  });
};

const applyTextTranslations = (
  container: HTMLDivElement | null,
  lng: string,
  dict: Record<string, string> | undefined,
  origMap: WeakMap<Text, string>
) => {
  if (!container || !dict) return;
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null);
  let node: Text | null;
  while ((node = walker.nextNode() as Text | null)) {
    const original = origMap.get(node);
    const current = node.nodeValue || '';
    if (lng === 'en') {
      if (original === undefined) origMap.set(node, current);
      const key = normalizeHomeText(current);
      if (dict[key] !== undefined) {
        node.nodeValue = dict[key];
      }
    } else {
      if (original !== undefined) {
        node.nodeValue = original;
      }
    }
  }
};

const applyAttrTranslations = (
  container: HTMLDivElement | null,
  lng: string,
  attrDict: Record<string, Record<string, string>> | undefined
) => {
  if (!container || !attrDict) return;
  Object.keys(attrDict).forEach((attr) => {
    const map = attrDict[attr];
    const els = Array.from(container.querySelectorAll(`[${attr}]`)) as HTMLElement[];
    els.forEach((el) => {
      const val = el.getAttribute(attr);
      if (!val) return;
      const normVal = normalizeHomeText(val);
      const origKey = `data-orig-${attr}`;
      if (!el.getAttribute(origKey)) el.setAttribute(origKey, val);
      const original = el.getAttribute(origKey) || val;
      if (lng === 'en') {
        const entry = Object.keys(map).find((k) => normalizeHomeText(k) === normVal);
        if (entry) el.setAttribute(attr, map[entry]);
      } else {
        el.setAttribute(attr, original);
      }
    });
  });
};

const StitchPage: React.FC<StitchPageProps> = ({ raw, onMount, translations, attrTranslations }) => {
  const ref = React.useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { i18n } = useTranslation();
  const { css, html } = React.useMemo(() => extractStitch(raw), [raw]);
  const origMapRef = React.useRef<WeakMap<Text, string>>(new WeakMap());

  React.useEffect(() => {
    applyLanguageToDocument(i18n.language);
    const handler = (lng: string) => {
      applyLanguageToDocument(lng);
      applyLanguageToButtons(ref.current, lng);
      applyTextTranslations(ref.current, lng, translations, origMapRef.current);
      applyAttrTranslations(ref.current, lng, attrTranslations);
    };
    i18n.on('languageChanged', handler);
    applyLanguageToButtons(ref.current, i18n.language);
    applyTextTranslations(ref.current, i18n.language, translations, origMapRef.current);
    applyAttrTranslations(ref.current, i18n.language, attrTranslations);
    return () => {
      i18n.off('languageChanged', handler);
    };
  }, [i18n, translations, attrTranslations]);

  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const cleanups: Array<() => void> = [];

    applyLanguageToButtons(el, i18n.language);
    applyTextTranslations(el, i18n.language, translations, origMapRef.current);
    applyAttrTranslations(el, i18n.language, attrTranslations);

    const clickHandler = (e: MouseEvent) => {
      const target = e.target as HTMLElement | null;
      const anchor = target?.closest('a') as HTMLAnchorElement | null;
      if (!anchor) return;
      const href = anchor.getAttribute('href');
      if (!href || !href.startsWith('/') || href.startsWith('//')) return;
      e.preventDefault();
      navigate(href);
    };
    el.addEventListener('click', clickHandler);
    cleanups.push(() => el.removeEventListener('click', clickHandler));

    const langButtons = Array.from(el.querySelectorAll('button')) as HTMLButtonElement[];
    langButtons.forEach((btn) => {
      if (!isLanguageButton(btn)) return;
      const handler = (e: Event) => {
        e.preventDefault();
        e.stopPropagation();
        const newLang = i18n.language === 'ar' ? 'en' : 'ar';
        i18n.changeLanguage(newLang);
      };
      btn.addEventListener('click', handler);
      cleanups.push(() => btn.removeEventListener('click', handler));
    });

    if (onMount) {
      const cleanup = onMount(el);
      if (typeof cleanup === 'function') cleanups.push(cleanup);
    }
    return () => cleanups.forEach((c) => c());
  }, [onMount, html, navigate, i18n, translations, attrTranslations]);

  return (
    <>
      {css ? <style dangerouslySetInnerHTML={{ __html: css }} /> : null}
      <div ref={ref} dangerouslySetInnerHTML={{ __html: html }} />
    </>
  );
};

export default StitchPage;