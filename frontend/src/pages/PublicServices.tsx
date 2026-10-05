import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';
import { ServiceCard } from '@/components/public/ServiceCard';
import { Button } from '@/components/ui/button';
import {
  ClipboardCheck,
  FileText,
  Handshake,
  LayoutDashboard,
  Network,
  Truck,
  Workflow,
} from 'lucide-react';

export function PublicServices() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const services = [
    {
      icon: <Workflow size={32} />,
      title: t('public.services.exportManagement'),
      description: t('public.services.exportManagementDesc'),
    },
    {
      icon: <Handshake size={32} />,
      title: t('public.services.tradeServices'),
      description: t('public.services.tradeServicesDesc'),
    },
    {
      icon: <LayoutDashboard size={32} />,
      title: t('public.services.digitalPlatform'),
      description: t('public.services.digitalPlatformDesc'),
    },
    {
      icon: <Truck size={32} />,
      title: t('public.services.shipmentManagement'),
      description: t('public.services.shipmentManagementDesc'),
    },
    {
      icon: <FileText size={32} />,
      title: t('public.services.invoicingDocuments'),
      description: t('public.services.invoicingDocumentsDesc'),
    },
    {
      icon: <ClipboardCheck size={32} />,
      title: t('public.services.customsProcedures'),
      description: t('public.services.customsProceduresDesc'),
    },
    {
      icon: <Network size={32} />,
      title: t('public.services.partnerNetwork'),
      description: t('public.services.partnerNetworkDesc'),
    },
  ];

  return (
    <div className="min-h-screen bg-[#022F32] text-white" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Hero Section */}
        <section className="w-full bg-[#022F32]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 text-center md:py-20">
            <h1 className="text-3xl font-bold text-white lg:text-[34px]">{t('public.services.title')}</h1>
            <p className="mt-3 text-base text-white/70">{t('public.services.subtitle')}</p>
          </div>
        </section>

        {/* Services Grid */}
        <section className="w-full bg-[#043B3E]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 md:py-20">
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {services.map((service, index) => (
                <ServiceCard
                  key={index}
                  icon={service.icon}
                  title={service.title}
                  description={service.description}
                />
              ))}
            </div>
          </div>
        </section>

        {/* Why Choose Nile Key — solid dark surface (services-bg.jpg is a forbidden composite screenshot) */}
        <section className="w-full bg-[#022F32]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 md:py-20">
            <h2 className="text-3xl font-bold text-white lg:text-[34px]">
              {t('public.services.whyChooseTitle')}
            </h2>
            <div className="mt-12 grid gap-8 md:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div className="flex items-start gap-4">
                  <div className="text-[#19D8B0] mt-1">
                    <ClipboardCheck size={24} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {isArabic ? 'منظومة متكاملة' : 'Integrated System'}
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-white/60">{t('public.services.whyChooseP1')}</p>
                  </div>
                </div>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div className="flex items-start gap-4">
                  <div className="text-[#19D8B0] mt-1">
                    <ClipboardCheck size={24} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {isArabic ? 'الالتزام بالجودة' : 'Commitment to Quality'}
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-white/60">{t('public.services.whyChooseP2')}</p>
                  </div>
                </div>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div className="flex items-start gap-4">
                  <div className="text-[#19D8B0] mt-1">
                    <ClipboardCheck size={24} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {isArabic ? 'فهم عميق للسوق' : 'Deep Market Understanding'}
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-white/60">{t('public.services.whyChooseP3')}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="w-full bg-[#043B3E]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 text-center md:py-20">
            <h2 className="text-3xl font-bold text-white lg:text-[34px]">
              {isArabic ? 'جاهز للبدء؟' : 'Ready to Get Started?'}
            </h2>
            <div className="mt-8 flex justify-center">
              <Link to="/contact">
                <Button className="h-12 rounded-full bg-[#19D8B0] px-8 text-base font-semibold text-[#022F32] hover:bg-[#19D8B0]/90">
                  {t('public.cta.contactUs')}
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
