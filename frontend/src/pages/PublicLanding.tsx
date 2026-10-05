import { Fragment } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Factory,
  FileText,
  Ship,
  Truck,
  type LucideIcon,
} from 'lucide-react';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';

function WorldMapVisual({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 1000 500"
      className={className}
      aria-hidden="true"
      focusable="false"
      preserveAspectRatio="xMidYMid slice"
    >
      <g fill="currentColor">
        <path d="M50,110 L85,80 L150,55 L230,58 L285,80 L305,115 L285,145 L260,170 L245,205 L230,240 L215,265 L200,255 L195,225 L180,200 L150,180 L115,165 L80,145 L55,130 Z" />
        <path d="M315,40 L370,35 L390,60 L360,85 L325,75 Z" />
        <path d="M230,275 L270,262 L300,285 L305,325 L290,375 L265,425 L245,435 L228,395 L212,345 L212,305 Z" />
        <path d="M465,85 L515,62 L560,70 L585,95 L565,122 L535,135 L505,128 L478,112 Z" />
        <path d="M462,158 L528,148 L588,162 L615,198 L610,252 L578,305 L542,335 L508,325 L482,285 L458,232 L452,192 Z" />
        <path d="M588,68 L705,52 L825,68 L905,92 L925,128 L885,162 L845,182 L805,212 L775,245 L742,235 L722,205 L692,182 L652,162 L612,142 L590,112 Z" />
        <path d="M755,262 L815,255 L855,268 L845,285 L785,285 Z" />
        <path d="M798,318 L872,308 L912,330 L908,372 L862,392 L814,382 L794,352 Z" />
        <path d="M935,400 L955,395 L960,415 L940,420 Z" />
      </g>
      <g fill="none" stroke="#19D8B0" strokeWidth="2">
        <path d="M180,180 Q400,110 560,140" opacity="0.75" />
        <path d="M560,140 Q710,210 860,340" opacity="0.75" />
        <path d="M180,180 Q360,310 540,300" opacity="0.5" />
      </g>
      <g fill="#19D8B0">
        <circle cx="180" cy="180" r="5" />
        <circle cx="560" cy="140" r="5" />
        <circle cx="860" cy="340" r="5" />
        <circle cx="540" cy="300" r="4" />
      </g>
    </svg>
  );
}

export function PublicLanding() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const journeySteps: { icon: LucideIcon; title: string }[] = [
    { icon: Factory, title: t('public.markets.step1Title') },
    { icon: CheckCircle, title: t('public.markets.step2Title') },
    { icon: FileText, title: t('public.markets.step3Title') },
    { icon: Truck, title: t('public.markets.step4Title') },
    { icon: Ship, title: t('public.markets.step5Title') },
  ];

  const products = [
    { gap: 'G4', title: t('public.products.vegetablesTitle'), description: t('public.products.vegetablesDesc') },
    { gap: 'G5', title: t('public.products.fruitsTitle'), description: t('public.products.fruitsDesc') },
    { gap: 'G6', title: t('public.products.factoryTitle'), description: t('public.products.factoryDesc') },
  ];

  const stats = [
    { value: '50+', label: t('public.markets.statCountries') },
    { value: '200+', label: t('public.markets.statPartners') },
    { value: '100%', label: t('public.markets.statQuality') },
  ];

  return (
    <div className="min-h-screen bg-[#022F32] text-white" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* ================= HERO (5.2) ================= */}
        <section className="relative h-[460px] md:h-[480px] lg:h-[600px] xl:h-[640px] w-full overflow-hidden bg-[#022F32]">
          {/* G1 Asset Gap: full-bleed photographic background (Egyptian landscape) — no clean atomic asset exists in the project */}
          <div className="absolute inset-0" data-asset-gap="G1" aria-hidden="true" />
          {/* Directional scrim for text readability (part of the reference composition) */}
          <div
            className="absolute inset-0 bg-gradient-to-r from-[rgba(2,47,50,0.9)] via-[rgba(2,47,50,0.5)] to-transparent rtl:bg-gradient-to-l"
            aria-hidden="true"
          />
          {/* G2 Asset Gap: Egyptian vegetables foreground layer — bottom/end */}
          <div className="absolute bottom-0 end-0 h-[55%] w-[38%]" data-asset-gap="G2" aria-hidden="true" />
          {/* Text block — start side in LTR (≈48% of container), vertically centered */}
          <div className="relative mx-auto flex h-full w-[min(92vw,1280px)] items-center">
            <div className="w-full lg:w-[48%] lg:max-w-[560px]">
              <div className="text-sm font-normal uppercase tracking-[0.14em] text-[#19D8B0]">
                {t('public.home.heroEyebrow')}
              </div>
              <h1 className="mt-4 text-5xl font-extrabold leading-[1.1] text-white lg:text-6xl">
                {t('public.home.heroTitle')}
              </h1>
              <div className="mt-3 text-base font-semibold text-white/90 lg:text-lg">
                {t('public.home.heroCorporateAr')}
              </div>
              <div className="mt-1 text-sm text-white/70 lg:text-base">
                {t('public.home.heroCorporateEn')}
              </div>
              <p className="mt-5 max-w-[520px] text-base leading-7 text-white/70">
                {t('public.home.heroDescription')}
              </p>
              <div className="mt-8 flex flex-col gap-4 sm:flex-row">
                <Link to="/services" className="w-full sm:w-auto">
                  <Button className="h-12 w-full rounded-full bg-[#19D8B0] px-8 text-base font-semibold text-[#022F32] hover:bg-[#19D8B0]/90 sm:w-auto">
                    {t('public.cta.getStarted')}
                  </Button>
                </Link>
                <Link to="/about" className="w-full sm:w-auto">
                  <Button
                    variant="outline"
                    className="h-12 w-full rounded-full border-white/40 bg-transparent px-8 text-base font-semibold text-white hover:bg-white/10 hover:text-white sm:w-auto"
                  >
                    {t('public.cta.learnMore')}
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* ================= OUR COMPANY (5.3) ================= */}
        <section className="w-full bg-[#043B3E]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14">
            <div className="grid items-center gap-12 lg:grid-cols-[48%_44%] lg:gap-16">
              {/* Text — left in LTR; on mobile the image comes first (order) */}
              <div className="order-2 lg:order-1">
                <div className="text-sm font-normal uppercase tracking-[0.14em] text-[#19D8B0]">
                  {t('public.home.ourCompanyEyebrow')}
                </div>
                <h2 className="mt-4 text-3xl font-bold leading-tight text-white lg:text-[34px]">
                  {t('public.home.ourCompanyTitle')}
                </h2>
                <p className="mt-4 max-w-xl text-base leading-7 text-white/70">
                  {t('public.home.ourCompanyText')}
                </p>
                <Link
                  to="/about"
                  className="mt-8 inline-block text-base font-semibold text-[#19D8B0] underline-offset-4 hover:underline"
                >
                  {t('public.cta.learnMore')}
                </Link>
              </div>
              {/* Image — right in LTR, aspect 4/3, offset teal backing */}
              <div className="relative order-1 lg:order-2">
                <div className="absolute -bottom-6 lg:-end-6 h-full w-full rounded-2xl bg-[#022F32]" aria-hidden="true" />
                {/* G3 Asset Gap: Egyptian visual (pyramids/Nile/sailboat) — atomic photograph, aspect 4/3 */}
                <div
                  className="relative aspect-[4/3] w-full rounded-2xl border border-white/10 bg-[#022F32]/70"
                  data-asset-gap="G3"
                />
              </div>
            </div>
          </div>
        </section>

        {/* ================= PREMIUM EGYPTIAN PRODUCTS (5.4) ================= */}
        <section className="w-full bg-[#043B3E]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14">
            <div className="flex flex-wrap items-end justify-between gap-6">
              <div>
                <div className="text-sm font-normal uppercase tracking-[0.14em] text-[#19D8B0]">
                  {t('public.home.productsEyebrow')}
                </div>
                <h2 className="mt-4 text-3xl font-bold leading-tight text-white lg:text-[34px]">
                  {t('public.home.productsTitle')}
                </h2>
              </div>
              <Link
                to="/products"
                className="text-base font-semibold text-[#19D8B0] underline-offset-4 hover:underline"
              >
                {t('public.home.viewAllProducts')}
              </Link>
            </div>
            <div className="mt-6 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {products.map((product) => (
                <div key={product.title} className="group mx-auto w-full max-w-[300px] xl:max-w-[330px]">
                  <div className="relative overflow-hidden rounded-xl border border-white/10">
                    {/* G4/G5/G6 Asset Gap: product photograph — top-heavy portrait (≈4/5) */}
                    <div className="aspect-[4/5] w-full bg-[#022F32]/70" data-asset-gap={product.gap} />
                    {/* Dark scrim behind the lower text (part of the reference composition) */}
                    <div
                      className="absolute inset-x-0 bottom-0 h-2/3 bg-gradient-to-t from-[rgba(2,47,50,0.85)] via-[rgba(2,47,50,0.4)] to-transparent"
                      aria-hidden="true"
                    />
                    <div className="absolute inset-x-0 bottom-0 p-5">
                      <h3 className="text-lg font-semibold text-white">{product.title}</h3>
                      <p className="mt-1 text-sm leading-6 text-white/60">{product.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ================= THE EXPORT JOURNEY (5.5) ================= */}
        <section className="w-full bg-[#022F32]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 md:py-20">
            <div className="max-w-2xl">
              <h2 className="text-3xl font-bold leading-tight text-white lg:text-[34px]">
                {t('public.home.journeyTitle')}
              </h2>
              <p className="mt-4 text-base leading-7 text-white/70">
                {t('public.home.journeyDescription')}
              </p>
            </div>

            {/* Desktop (lg+): 5 nodes horizontal with connector line + direction arrows */}
            <div className="mt-20 hidden items-start lg:flex" aria-label={t('public.home.journeyTitle')}>
              {journeySteps.map((step, index) => (
                <Fragment key={step.title}>
                  <div className="flex flex-col items-center text-center">
                    <div className="flex h-14 w-14 items-center justify-center rounded-full border border-white/15 bg-[#043B3E] text-[#19D8B0]">
                      <step.icon size={22} />
                    </div>
                    <h3 className="mt-4 max-w-[140px] text-sm font-semibold leading-5 text-white">
                      {step.title}
                    </h3>
                  </div>
                  {index < journeySteps.length - 1 && (
                    <div className="relative mt-[26.5px] h-[3px] flex-1 bg-white/15" aria-hidden="true">
                      <ChevronRight
                        className="absolute -top-[9px] left-1/2 -translate-x-1/2 text-[#19D8B0]"
                        size={18}
                      />
                    </div>
                  )}
                </Fragment>
              ))}
            </div>

            {/* Tablet & Mobile: vertical with connector line + direction arrows */}
            <div className="mt-16 flex flex-col lg:hidden" aria-label={t('public.home.journeyTitle')}>
              {journeySteps.map((step, index) => (
                <Fragment key={step.title}>
                  <div className="flex items-center gap-4">
                    <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full border border-white/15 bg-[#043B3E] text-[#19D8B0]">
                      <step.icon size={22} />
                    </div>
                    <h3 className="text-base font-semibold text-white">{step.title}</h3>
                  </div>
                  {index < journeySteps.length - 1 && (
                    <div className="relative ms-7 mt-2 h-10 w-[3px] bg-white/15" aria-hidden="true">
                      <ChevronDown
                        className="absolute -left-[7.5px] top-1/2 -translate-y-1/2 text-[#19D8B0]"
                        size={18}
                      />
                    </div>
                  )}
                </Fragment>
              ))}
            </div>
          </div>
        </section>

        {/* ================= DIGITAL PLATFORM (5.6) ================= */}
        <section className="w-full bg-[#043B3E]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14">
            <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
              {/* Visual LEFT (≈50–52%) — G7 execution path: laptop frame (CSS/HTML build) with a simplified interface/map visual inside. No fake data, no invented dashboard, no metrics. */}
              <div className="order-1">
                <div className="mx-auto max-w-[460px]">
                  <div className="rounded-2xl border border-white/15 bg-[#022F32] p-2.5">
                    <div className="relative aspect-[16/10] w-full overflow-hidden rounded-xl bg-[#043B3E]">
                      <WorldMapVisual className="absolute inset-0 h-full w-full text-white/20" />
                      <div
                        className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-[rgba(2,47,50,0.6)] to-transparent"
                        aria-hidden="true"
                      />
                    </div>
                  </div>
                  <div className="mx-auto h-2 w-2/3 rounded-b-lg bg-white/15" aria-hidden="true" />
                </div>
              </div>
              {/* Text RIGHT (≈48–50%) */}
              <div className="order-2">
                <div className="text-sm font-normal uppercase tracking-[0.14em] text-[#19D8B0]">
                  {t('public.home.platformEyebrow')}
                </div>
                <h2 className="mt-4 text-3xl font-bold leading-tight text-white lg:text-[34px]">
                  <span>{t('public.home.platformTitleLine1')}</span>
                  <br />
                  <span>{t('public.home.platformTitleLine2')}</span>
                </h2>
                <p className="mt-4 max-w-xl text-base leading-7 text-white/70">
                  {t('public.home.platformShortDesc')}
                </p>
                <Link
                  to="/services"
                  className="mt-8 inline-block text-base font-semibold text-[#19D8B0] underline-offset-4 hover:underline"
                >
                  {t('public.cta.learnMore')}
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* ================= OUR PRESENCE IN GLOBAL MARKETS (5.7) ================= */}
        <section className="relative w-full overflow-hidden bg-[#022F32]">
          {/* G8 execution path: simplified world map visual as the section background — low opacity, accent routes/nodes */}
          <div className="absolute inset-0" aria-hidden="true">
            <WorldMapVisual className="h-full w-full text-white/10" />
          </div>
          <div className="relative mx-auto w-[min(92vw,1280px)] py-14">
            <div className="max-w-2xl">
              <div className="text-sm font-normal uppercase tracking-[0.14em] text-[#19D8B0]">
                {t('public.home.marketsEyebrow')}
              </div>
              <h2 className="mt-4 text-3xl font-bold leading-tight text-white lg:text-[34px]">
                {t('public.home.marketsTitle')}
              </h2>
              <p className="mt-4 text-base leading-7 text-white/70">
                {t('public.home.marketsSubtitle')}
              </p>
            </div>
            <div className="mt-16 grid gap-8 sm:grid-cols-3">
              {stats.map((stat, index) => (
                <div key={stat.value} className={index > 0 ? 'border-s border-white/10 ps-8' : ''}>
                  <div className="text-3xl font-bold leading-tight text-[#19D8B0] lg:text-[36px]">
                    {stat.value}
                  </div>
                  <div className="mt-2 text-sm text-white/60">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ================= TRUSTED BY GLOBAL PARTNERS / LET'S GROW TOGETHER (5.8) ================= */}
        <section className="w-full">
          <div className="mx-auto w-[min(92vw,1280px)] grid lg:grid-cols-[51%_49%]">
            {/* LEFT (≈51%): light trust surface */}
            <div className="bg-[#F4F6F2]">
              <div className="flex min-h-[280px] flex-col justify-center px-6 py-14 lg:px-10">
                <h2 className="text-2xl font-bold leading-tight text-[#022F32] lg:text-3xl">
                  {t('public.home.trustedByTitle')}
                </h2>
                {/* G10 Asset Gap: official SGS / ISO / HACCP / GLOBALG.A.P. trust marks — require official assets from the project or an approved source. No text-as-logo, no invented SVG. Left empty intentionally. */}
                <div className="mt-10" data-asset-gap="G10" />
              </div>
            </div>
            {/* RIGHT (≈49%): dark image-based CTA panel */}
            <div className="relative overflow-hidden bg-[#022F32]">
              {/* G9 Asset Gap: trade/shipping/ship photograph */}
              <div className="absolute inset-0" data-asset-gap="G9" aria-hidden="true" />
              <div className="absolute inset-0 bg-[#022F32]/70" aria-hidden="true" />
              <div className="relative flex min-h-[280px] flex-col justify-center px-6 py-14 lg:px-10">
                <h2 className="text-2xl font-bold leading-tight text-white lg:text-3xl">
                  {t('public.home.trustedTitle')}
                </h2>
                <p className="mt-4 max-w-md text-base leading-7 text-white/70">
                  {t('public.home.trustedDescription')}
                </p>
                <div className="mt-8">
                  <Link to="/contact">
                    <Button className="h-12 rounded-full bg-[#19D8B0] px-8 text-base font-semibold text-[#022F32] hover:bg-[#19D8B0]/90">
                      {t('public.home.trustedCta')}
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
