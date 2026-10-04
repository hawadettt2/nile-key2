import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { PublicNavbar } from '@/components/public/PublicNavbar';
import { PublicFooter } from '@/components/public/PublicFooter';
import { ProductCard } from '@/components/public/ProductCard';
import { Button } from '@/components/ui/button';

export function PublicProducts() {
  const { t, i18n } = useTranslation();
  const isArabic = i18n.language === 'ar';

  const products = [
    {
      imageSrc: '/assets/products/vegetables.jpg',
      title: t('public.products.vegetablesTitle'),
      description: t('public.products.vegetablesDesc'),
      ctaText: t('public.products.ctaExplore'),
      ctaLink: '/contact',
    },
    {
      imageSrc: '/assets/products/fruits.jpg',
      title: t('public.products.fruitsTitle'),
      description: t('public.products.fruitsDesc'),
      ctaText: t('public.products.ctaExplore'),
      ctaLink: '/contact',
    },
    {
      imageSrc: '/assets/products/factory.jpg',
      title: t('public.products.factoryTitle'),
      description: t('public.products.factoryDesc'),
      ctaText: t('public.products.ctaCatalog'),
      ctaLink: '/contact',
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
              {t('public.products.title')}
            </h1>
            <p className="text-xl text-slate-300">
              {t('public.products.subtitle')}
            </p>
          </div>
        </section>

        {/* Products Grid */}
        <section className="py-20 bg-slate-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {products.map((product, index) => (
                <ProductCard
                  key={index}
                  imageSrc={product.imageSrc}
                  title={product.title}
                  description={product.description}
                  ctaText={product.ctaText}
                  ctaLink={product.ctaLink}
                />
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 bg-slate-800">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-white mb-8">
              {isArabic ? 'هل تريد معرفة المزيد عن منتجاتنا؟' : 'Want to know more about our products?'}
            </h2>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/contact">
                <Button size="lg" className="bg-emerald-600 hover:bg-emerald-700 text-white px-8">
                  {t('public.cta.contactUs')}
                </Button>
              </Link>
              <Link to="/services">
                <Button size="lg" variant="outline" className="border-white text-black hover:bg-white/10 hover:text-emerald-500 px-8">
                  {t('public.cta.learnMore')}
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
