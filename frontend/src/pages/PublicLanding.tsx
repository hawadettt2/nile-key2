import { Fragment } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  ArrowLeft,
  ArrowRight,
  BarChart3,
  CreditCard,
  Factory,
  Globe,
  Layers,
  Package,
  Ship,
  Truck,
  Users,
  type LucideIcon,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';

type HomeFeature = {
  icon: LucideIcon;
  title: string;
  description: string;
};

function PlatformMockup() {
  return (
    <div className="relative mx-auto w-full max-w-[430px]" aria-hidden="true" dir="ltr">
      <div className="relative z-10 mx-auto w-[86%] rounded-t-[18px] border-[5px] border-[#073c39] bg-[#072d2d] p-2 shadow-[0_18px_50px_rgba(0,0,0,0.3)]">
        <div className="aspect-[2.5/1] overflow-hidden rounded-t-[9px] bg-[#f4f8f4] p-2 sm:p-3">
          <div className="flex h-full gap-2">
            <div className="flex w-[15%] flex-col items-center gap-2 rounded-md bg-[#073c39] py-2">
              <span className="h-4 w-4 rounded bg-[#19d8a8]" />
              <span className="mt-2 h-2 w-7/12 rounded bg-white/35" />
              <span className="h-2 w-7/12 rounded bg-white/20" />
              <span className="h-2 w-7/12 rounded bg-white/20" />
              <span className="h-2 w-7/12 rounded bg-white/20" />
              <span className="mt-auto h-5 w-5 rounded-full bg-[#19d8a8]/70" />
            </div>
            <div className="grid min-w-0 flex-1 grid-rows-[auto_1fr_0.8fr] gap-2">
              <div className="flex items-center justify-between rounded-md bg-white px-2 py-1.5 shadow-sm">
                <span className="h-2 w-1/3 rounded bg-[#0a514a]/70" />
                <span className="h-4 w-4 rounded-full bg-[#d9efe4]" />
              </div>
              <div className="grid min-h-0 grid-cols-2 gap-2">
                <div className="rounded-md bg-white p-2 shadow-sm">
                  <span className="block h-2 w-2/3 rounded bg-[#0a514a]/50" />
                  <div className="mt-2 flex h-[72%] items-end gap-1 border-b border-l border-[#d9e4df] px-1">
                    {[32, 50, 38, 72, 58, 88, 66].map((height, index) => (
                      <span
                        key={index}
                        className="flex-1 rounded-t-sm bg-[#19b78e]"
                        style={{ height: `${height}%` }}
                      />
                    ))}
                  </div>
                </div>
                <div className="relative overflow-hidden rounded-md bg-[#e3f2e9] p-2">
                  <span className="relative z-10 block h-2 w-1/2 rounded bg-[#0a514a]/50" />
                  <svg viewBox="0 0 160 90" className="absolute inset-0 h-full w-full p-2 text-[#0b7b69]">
                    <path d="M12 32 24 20l15 3 8 10-7 8-12-2-8 7-10-4zm43-10 12-7 16 4 4 10-9 7-13-3-6 7-8-6zm8 29 14-5 12 8-2 12-13 7-11-9zm27-29 19-5 20 8-3 10-17 6-13-7z" fill="currentColor" opacity=".32" />
                    <path d="M25 34Q76 5 112 31T137 58M25 34Q64 60 85 59" fill="none" stroke="currentColor" strokeWidth="1.6" />
                    <circle cx="25" cy="34" r="3" fill="#19b78e" />
                    <circle cx="112" cy="31" r="3" fill="#19b78e" />
                    <circle cx="137" cy="58" r="3" fill="#19b78e" />
                  </svg>
                </div>
              </div>
              <div className="grid min-h-0 grid-cols-3 gap-2">
                {[0, 1, 2].map((item) => (
                  <div key={item} className="rounded-md bg-white p-2 shadow-sm">
                    <span className="block h-2 w-2/3 rounded bg-[#0a514a]/40" />
                    <span className="mt-2 block h-2 w-full rounded bg-[#dcebe2]" />
                    <span className="mt-1 block h-2 w-4/5 rounded bg-[#dcebe2]" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        <span className="absolute left-1/2 top-0 h-1 w-1 -translate-x-1/2 rounded-full bg-white/25" />
      </div>
      <div className="mx-auto h-3 w-[94%] rounded-b-xl bg-gradient-to-b from-[#78918c] to-[#294a45]" />
      <div className="mx-auto h-2 w-[30%] rounded-b-lg bg-[#25423e]" />

      <div className="absolute -bottom-1 right-0 z-20 w-[17%] min-w-[64px] max-w-[92px] rounded-[18px] border-[4px] border-[#083d39] bg-[#072d2d] p-1.5 shadow-xl">
        <div className="relative aspect-[0.48/1] overflow-hidden rounded-[12px] bg-[#f4f8f4] p-1.5">
          <span className="mx-auto block h-1 w-1/3 rounded-full bg-[#0a514a]/25" />
          <span className="mt-2 block h-2 w-4/5 rounded bg-[#0a514a]/50" />
          <div className="mt-2 rounded bg-[#e3f2e9] p-1.5">
            <span className="block h-1 w-2/3 rounded bg-[#0a514a]/40" />
            <div className="mt-1 flex h-8 items-end gap-0.5">
              {[30, 55, 40, 78, 62].map((height, index) => (
                <span key={index} className="flex-1 rounded-t-sm bg-[#19b78e]" style={{ height: `${height}%` }} />
              ))}
            </div>
          </div>
          <span className="mt-2 block h-7 rounded bg-[#dcebe2]" />
          <span className="mt-1 block h-7 rounded bg-[#dcebe2]" />
        </div>
      </div>
    </div>
  );
}

function FeatureTile({ icon: Icon, title, description }: HomeFeature) {
  return (
    <article className="flex min-h-[78px] items-center gap-3 rounded-xl border border-[#0c6558]/60 bg-[#032f30]/30 px-3 py-3 sm:gap-4 sm:px-5">
      <Icon className="h-7 w-7 shrink-0 text-[#4ee58e]" strokeWidth={1.8} aria-hidden="true" />
      <div className="min-w-0">
        <h3 className="text-sm font-bold leading-5 text-white sm:text-base">{title}</h3>
        <p className="mt-1 text-xs leading-5 text-white/65 sm:text-[13px]">{description}</p>
      </div>
    </article>
  );
}

function HeroTradeArtwork() {
  return (
    <div className="absolute inset-0 overflow-hidden" aria-hidden="true">
      <div className="absolute inset-0 bg-[#022f30]" />
      <img
        src="/assets/home/hero-port-said.jpg"
        alt=""
        className="absolute bottom-0 left-[23%] h-[84%] w-[48%] object-cover object-center opacity-80"
        style={{ maskImage: 'linear-gradient(90deg, transparent 0%, #000 13%, #000 83%, transparent 100%)' }}
      />
      <img
        src="/assets/home/hero-pyramids.jpg"
        alt=""
        className="absolute bottom-0 left-0 h-[92%] w-[42%] object-cover object-[62%_center]"
        style={{ maskImage: 'linear-gradient(90deg, #000 0%, #000 68%, transparent 100%)' }}
      />
      <img
        src="/assets/home/hero-produce.jpg"
        alt=""
        className="absolute bottom-0 left-0 h-[40%] w-[34%] object-cover object-center"
        style={{ maskImage: 'linear-gradient(0deg, #000 0%, #000 72%, transparent 100%)' }}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-[#022f30]/50 via-transparent to-[#022f30]/10" />
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#022f30]/25 to-[#022f30]" />
      <svg
        viewBox="0 0 640 300"
        className="absolute left-[9%] top-[10%] h-[68%] w-[50%] text-[#47cb9b]/35"
        preserveAspectRatio="xMidYMid meet"
      >
        <g fill="currentColor" opacity=".46">
          <path d="m38 78 24-17 46-9 31 11 8 18-14 13-19 2-10 17-20-2-13 19-17-8-9-24-17-7z" />
          <path d="m108 145 26-5 20 15-4 27-16 28-12 35-13-7-10-33-8-26z" />
          <path d="m281 78 23-14 27 4 8 12-17 12-26-3z" />
          <path d="m289 112 36-8 31 14 5 22-17 22-6 37-19 27-15-10-5-33-16-22-8-26z" />
          <path d="m354 73 46-17 68 8 57 21 25 20-22 17-35-3-26 18-40-1-19-21-34-3-23-17z" />
          <path d="m445 191 28-4 23 12-2 19-33 7-24-13z" />
        </g>
        <g fill="none" stroke="currentColor" strokeWidth="1.7">
          <path d="M93 107Q215 8 331 98T509 124" />
          <path d="M93 107Q234 204 350 134T509 124" />
          <path d="M151 74Q302 216 454 106" />
        </g>
        <g fill="#72e5ac">
          <circle cx="93" cy="107" r="4" />
          <circle cx="331" cy="98" r="4" />
          <circle cx="509" cy="124" r="4" />
          <circle cx="350" cy="134" r="3" />
        </g>
      </svg>
      <div className="absolute left-[24%] top-[19%] h-24 w-24 rounded-full bg-[#e3b95e]/25 blur-3xl" />
      <div className="absolute inset-y-0 right-0 w-[55%] bg-gradient-to-l from-[#022f30] via-[#022f30]/90 to-transparent" />
    </div>
  );
}

function ExportJourneyArtwork() {
  return (
    <div className="absolute inset-0 overflow-hidden" aria-hidden="true">
      <img
        src="/assets/home/export-journey-panorama.jpg"
        alt=""
        className="absolute inset-y-0 left-0 h-full w-[56%] object-cover object-[49%_56%]"
        style={{ maskImage: 'linear-gradient(90deg, #000 0%, #000 52%, transparent 100%)' }}
      />
      <img
        src="/assets/home/company-cargo-ship.jpg"
        alt=""
        className="absolute bottom-0 left-[24%] h-[87%] w-[48%] object-cover object-[50%_60%]"
        style={{ maskImage: 'linear-gradient(90deg, transparent 0%, #000 15%, #000 74%, transparent 100%)' }}
      />
      <img
        src="/assets/home/hero-produce.jpg"
        alt=""
        className="absolute bottom-0 left-0 h-[52%] w-[29%] object-cover object-[48%_67%]"
        style={{ maskImage: 'linear-gradient(0deg, #000 0%, #000 68%, transparent 100%)' }}
      />
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#f4f5ef]/50 to-[#f4f5ef]/95" />
      <div className="absolute inset-0 bg-gradient-to-t from-[#f4f5ef]/30 via-transparent to-[#f4f5ef]/10" />
    </div>
  );
}

export function PublicLanding() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language.startsWith('ar');
  const direction = isArabic ? 'rtl' : 'ltr';
  const JourneyArrow = isArabic ? ArrowLeft : ArrowRight;

  const companyHighlights = [
    { icon: Factory, title: t('public.home.companyPillar1') },
    { icon: Truck, title: t('public.home.companyPillar2') },
    { icon: Layers, title: t('public.home.companyPillar3') },
  ];

  const journeySteps = [
    { icon: Factory, title: t('public.home.journeyStep1') },
    { icon: Ship, title: t('public.home.journeyStep2') },
    { icon: Truck, title: t('public.home.journeyStep3') },
    { icon: Globe, title: t('public.home.journeyStep4') },
  ];

  const features: HomeFeature[] = [
    { icon: CreditCard, title: t('public.home.featurePaymentsTitle'), description: t('public.home.featurePaymentsDescription') },
    { icon: Truck, title: t('public.home.featureShipmentsTitle'), description: t('public.home.featureShipmentsDescription') },
    { icon: Users, title: t('public.home.featureCustomersTitle'), description: t('public.home.featureCustomersDescription') },
    { icon: Globe, title: t('public.home.featureMarketsTitle'), description: t('public.home.featureMarketsDescription') },
    { icon: Package, title: t('public.home.featureProductsTitle'), description: t('public.home.featureProductsDescription') },
    { icon: BarChart3, title: t('public.home.featureReportsTitle'), description: t('public.home.featureReportsDescription') },
  ];

  return (
    <div className="relative min-h-screen bg-[#022f30] text-white" dir={direction}>
      <PublicNavbar overlay />

      <main>
        <section className="relative isolate min-h-[480px] overflow-hidden bg-[#022f30] lg:min-h-[400px]">
          <HeroTradeArtwork />
          <div className="relative mx-auto grid min-h-[480px] w-[min(90vw,1280px)] items-center pt-16 lg:min-h-[400px] lg:grid-cols-2 lg:pt-16" dir="ltr">
            <div className="hidden lg:block" aria-hidden="true" />
            <div className={`max-w-[610px] py-10 ${isArabic ? 'text-right' : 'text-left'}`} dir={direction}>
              <h1 className="text-2xl font-extrabold leading-[1.45] text-white sm:text-3xl lg:text-[32px]">
                {isArabic ? t('public.home.heroCorporateAr') : t('public.home.heroCorporateEn')}
              </h1>
              <p className="mt-1 text-sm font-semibold text-white/90 sm:text-base lg:text-lg" dir="ltr">
                {isArabic ? t('public.home.heroCorporateEn') : t('public.home.heroCorporateAr')}
              </p>
              <p className="mt-5 text-lg font-extrabold leading-8 text-[#4ee58e] sm:text-xl lg:text-[22px]">
                {t('public.home.heroMessage')}
              </p>
              <p className="mt-3 text-sm leading-6 text-white/85 sm:text-[15px] sm:leading-7">
                {t('public.home.heroDescription')}
              </p>
              <div className={`mt-6 flex flex-wrap gap-3 ${isArabic ? 'justify-end' : 'justify-start'}`} dir="ltr">
                <Button asChild className="h-10 min-w-32 rounded-lg bg-white px-5 font-bold text-[#073a3a] hover:bg-white/90">
                  <Link to="/login" dir={direction}>
                    {t('public.cta.createAccount')}
                  </Link>
                </Button>
                <Button asChild className="h-10 min-w-32 rounded-lg bg-gradient-to-r from-[#19b86f] to-[#4ee58e] px-5 font-bold text-[#063934] hover:brightness-105">
                  <Link to="/login" dir={direction}>
                    {t('public.cta.signIn')}
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        <section className="border-t border-[#19b86f]/60 bg-[#003735]">
          <div className="mx-auto grid w-[min(84vw,1160px)] gap-8 py-10 lg:min-h-[244px] lg:grid-cols-[1fr_0.92fr] lg:items-center lg:gap-14 lg:py-7" dir="ltr">
            <div dir={direction} className={isArabic ? 'text-right' : 'text-left'}>
              <p className="text-sm font-semibold tracking-wide text-[#4ee58e]">{t('public.home.ourCompanyEyebrow')}</p>
              <h2 className="mt-2 text-2xl font-extrabold leading-tight text-white sm:text-[28px]">
                {t('public.home.ourCompanyTitle')}
              </h2>
              <p className="mt-3 max-w-[580px] text-sm leading-6 text-white/75 sm:text-[15px] sm:leading-7">
                {t('public.home.ourCompanyText')}
              </p>
              <div className="mt-5 grid grid-cols-3 divide-x divide-[#19b86f]/35" dir="ltr">
                {companyHighlights.map(({ icon: Icon, title }) => (
                  <div key={title} className="px-2 text-center" dir={direction}>
                    <Icon className="mx-auto h-6 w-6 text-[#4ee58e]" strokeWidth={1.8} aria-hidden="true" />
                    <p className="mt-2 text-xs font-semibold leading-5 text-white/90 sm:text-sm">{title}</p>
                  </div>
                ))}
              </div>
            </div>
            <figure className="relative mx-auto w-full max-w-[460px] lg:my-3">
              <div className="absolute -bottom-3 -left-3 h-full w-full rounded-lg border-l-[3px] border-b-[3px] border-[#19b86f]" aria-hidden="true" />
              <img
                src="/assets/home/company-cargo-ship.jpg"
                alt={t('public.home.companyImageAlt')}
                className="relative aspect-[2/1] w-full rounded-lg object-cover"
                loading="lazy"
              />
            </figure>
          </div>
        </section>

        <section className="relative isolate overflow-hidden bg-[#f2f4ed] text-[#073a3a]">
          <ExportJourneyArtwork />
          <div className="relative mx-auto grid w-[min(88vw,1200px)] gap-6 py-9 lg:min-h-[254px] lg:grid-cols-[0.72fr_1fr] lg:items-center lg:gap-8 lg:py-7" dir="ltr">
            <div className="hidden lg:block" aria-hidden="true" />
            <div dir={direction} className={isArabic ? 'text-right' : 'text-left'}>
              <p className="text-xs font-bold tracking-wide text-[#13955e]">{t('public.home.journeyTitle')}</p>
              <h2 className="mt-1 text-xl font-extrabold leading-tight sm:text-2xl">{t('public.home.journeyHeadline')}</h2>
              <p className="mt-2 text-xs leading-5 text-[#183d39]/90 sm:text-sm sm:leading-6">{t('public.home.journeyDescription')}</p>
              <div className="mt-5 hidden items-start lg:flex" dir={direction}>
                {journeySteps.map(({ icon: Icon, title }, index) => (
                  <Fragment key={title}>
                    <div className="flex w-[22%] shrink-0 flex-col items-center text-center">
                      <span className="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-[#26ad69] to-[#159b65] text-white shadow-sm">
                        <Icon className="h-5 w-5" strokeWidth={1.8} aria-hidden="true" />
                      </span>
                      <span className="mt-2 max-w-[110px] text-[11px] font-bold leading-4 text-[#073a3a]">{title}</span>
                    </div>
                    {index < journeySteps.length - 1 && (
                      <div className="relative mt-5 h-px min-w-4 flex-1 bg-[#1ba46b]/60" aria-hidden="true">
                        <JourneyArrow className="absolute -top-[7px] left-1/2 h-4 w-4 -translate-x-1/2 text-[#20a96d]" strokeWidth={1.8} />
                      </div>
                    )}
                  </Fragment>
                ))}
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3 lg:hidden" dir={direction}>
                {journeySteps.map(({ icon: Icon, title }) => (
                  <div key={title} className="flex items-center gap-2 rounded-full bg-white/75 px-3 py-2 shadow-sm">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[#20a96d] text-white">
                      <Icon className="h-4 w-4" aria-hidden="true" />
                    </span>
                    <span className="text-xs font-bold leading-4">{title}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="bg-[#022f30]">
          <div className="mx-auto w-[min(84vw,1160px)] py-5">
            <div className="grid items-center gap-8 lg:grid-cols-[0.95fr_1.05fr] lg:gap-12" dir="ltr">
              <div dir={direction} className={isArabic ? 'text-right' : 'text-left'}>
                <p className="text-sm font-semibold tracking-wide text-[#4ee58e]">{t('public.home.platformEyebrow')}</p>
                <h2 className="mt-2 text-2xl font-extrabold leading-tight text-white sm:text-[28px]">
                  <span>{t('public.home.platformTitleLine1')}</span>
                  <br />
                  <span>{t('public.home.platformTitleLine2')}</span>
                </h2>
                <p className="mt-3 max-w-[540px] text-sm leading-6 text-white/70 sm:text-[15px] sm:leading-7">
                  {t('public.home.platformDescription')}
                </p>
              </div>
              <PlatformMockup />
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-3" dir={direction}>
              {features.map((feature) => <FeatureTile key={feature.title} {...feature} />)}
            </div>
          </div>
        </section>

        <section className="relative isolate flex min-h-[144px] items-center justify-center overflow-hidden bg-[#c8e0b0] px-5 py-6 text-center sm:min-h-[152px]">
          <img
            src="/assets/home/global-trade-cta.jpg"
            alt=""
            aria-hidden="true"
            className="absolute inset-0 h-full w-full object-cover object-bottom"
            loading="lazy"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-[#cde5ae]/60 via-[#e4efcf]/78 to-[#bdd99d]/55" aria-hidden="true" />
          <div className="relative max-w-3xl text-[#064039]" dir={direction}>
            <h2 className="text-2xl font-extrabold leading-tight sm:text-3xl">{t('public.home.closingTitle')}</h2>
            <p className="mt-2 text-xs font-semibold text-[#0b463e]/85 sm:text-sm">{t('public.home.closingDescription')}</p>
            <Button asChild className="mt-4 h-9 rounded-full bg-[#073a3a] px-6 text-xs font-bold text-white hover:bg-[#0b514b]">
              <Link to="/contact">
                {t('public.home.closingCta')}
                {isArabic ? <ArrowLeft className="ms-2 h-4 w-4" aria-hidden="true" /> : <ArrowRight className="ms-2 h-4 w-4" aria-hidden="true" />}
              </Link>
            </Button>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
