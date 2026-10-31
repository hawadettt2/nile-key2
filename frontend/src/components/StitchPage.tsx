import React from 'react';
import { useNavigate } from 'react-router-dom';
import { extractStitch } from '@/lib/stitch';

interface StitchPageProps {
  raw: string;
  onMount?: (container: HTMLDivElement) => (() => void) | void;
}

const StitchPage: React.FC<StitchPageProps> = ({ raw, onMount }) => {
  const ref = React.useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { css, html } = React.useMemo(() => extractStitch(raw), [raw]);

  React.useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const cleanups: Array<() => void> = [];

    // SPA navigation: intercept internal <a href="/..."> clicks
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

    if (onMount) {
      const cleanup = onMount(el);
      if (typeof cleanup === 'function') cleanups.push(cleanup);
    }
    return () => cleanups.forEach((c) => c());
  }, [onMount, html, navigate]);

  return (
    <>
      {css ? <style dangerouslySetInnerHTML={{ __html: css }} /> : null}
      <div ref={ref} dangerouslySetInnerHTML={{ __html: html }} />
    </>
  );
};

export default StitchPage;
