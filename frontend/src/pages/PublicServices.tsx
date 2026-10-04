import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';
import { ServiceCard } from '@/components/public/ServiceCard';
import { Button } from '@/components/ui/button';
import { ArrowRight, Globe, Truck, Package, FileText, CheckCircle, Factory, Warehouse } from 'lucide-react';

export function PublicServices() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const services = [
    {
      icon: <Globe size={32} />,
      title: t('public.services.exportManagement'),
      description: t('public.services.exportManagementDesc'),
    },
    {
      icon: <Truck size={32} />,
      title: t('public.services.tradeServices'),
      description: t('public.services.tradeServicesDesc'),
    },
    {
      icon: <Package size={32} />,
      title: t('public.services.digitalPlatform'),
      description: t('public.services.digitalPlatformDesc'),
    },
    {
      icon: <Warehouse size={32} />,
      title: t('public.services.shipmentManagement'),
      description: t('public.services.shipmentManagementDesc'),
    },
    {
      icon: <FileText size={32} />,
      title: t('public.services.invoicingDocuments'),
      description: t('public.services.invoicingDocumentsDesc'),
    },
    {
      icon: <CheckCircle size={32} />,
      title: t('public.services.customsProcedures'),
      description: t('public.services.customsProceduresDesc'),
    },
    {
      icon: <Factory size={32} />,
      title: t('public.services.partnerNetwork'),
      description: t('public.services.partnerNetworkDesc'),
    },
  ];

  return (
    <div className="min-h-screen bg-slate-900" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Hero Section */}
        <section className="py-20 bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
              {t('public.services.title')}
            </h1>
            <p className="text-xl text-slate-300">
              {t('public.services.subtitle')}
            </p>
          </div>
        </section>

        {/* Services Grid */}
        <section className="py-20 bg-slate-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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

        {/* Why Choose Nile Key */}
        <section className="py-20 bg-slate-800 relative">
          <img
            src="/assets/services/services-bg.jpg"
            alt=""
            className="absolute inset-0 w-full h-full object-cover opacity-30"
            aria-hidden="true"
          />
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <h2 className="text-3xl font-bold text-emerald-400 mb-12 text-center">
              {t('public.services.whyChooseTitle')}
            </h2>
            <div className="space-y-8">
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8">
                <div className="flex items-start gap-4">
                  <div className="text-emerald-400 mt-1">
                    <CheckCircle size={24} />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-lg mb-2">
                      {isArabic ? 'منظومة متكاملة' : 'Integrated System'}
                    </h3>
                    <p className="text-slate-300">
                      {t('public.services.whyChooseP1')}
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8">
                <div className="flex items-start gap-4">
                  <div className="text-emerald-400 mt-1">
                    <CheckCircle size={24} />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-lg mb-2">
                      {isArabic ? 'التزام بالجودة' : 'Commitment to Quality'}
                    </h3>
                    <p className="text-slate-300">
                      {t('public.services.whyChooseP2')}
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8">
                <div className="flex items-start gap-4">
                  <div className="text-emerald-400 mt-1">
                    <CheckCircle size={24} />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-lg mb-2">
                      {isArabic ? 'فهم عميق للسوق' : 'Deep Market Understanding'}
                    </h3>
                    <p className="text-slate-300">
                      {t('public.services.whyChooseP3')}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-slate-900">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-white mb-8">
              {isArabic ? 'جاهز للبدء؟' : 'Ready to Get Started?'}
            </h2>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/contact">
                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-white px-8">
                  {t('public.cta.contactUs')}
                </Button>
              </Link>
              <Link to="/markets">
                <Button size="lg" variant="outline" className="border-white text-black hover:bg-white/10 hover:text-emerald-500 px-8">
                  {t('public.cta.learnMore')}
                  <ArrowRight size={20} className="ms-2" />
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
