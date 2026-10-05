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
    },
    {
      imageSrc: '/assets/products/fruits.jpg',
      title: t('public.products.fruitsTitle'),
      description: t('public.products.fruitsDesc'),
    },
    {
      imageSrc: '/assets/products/factory.jpg',
      title: t('public.products.factoryTitle'),
      description: t('public.products.factoryDesc'),
    },
  ];

  return (
    <div className="min-h-screen bg-slate-900" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Hero Section */}
        <section className="bg-[#002f32] py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-4xl font-bold text-white mb-4">{t('public.products.title')}</h1>
            <p className="text-base text-slate-300">{t('public.products.subtitle')}</p>
          </div>
        </section>

        {/* Products Grid */}
        <section className="bg-slate-900 py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {products.map((product, index) => (
                <ProductCard
                  key={index}
                  imageSrc={product.imageSrc}
                  title={product.title}
                  description={product.description}
                />
              ))}
            </div>
            <div className="mt-12 text-center">
              <Link to="/contact">
                <Button className="bg-emerald-600 hover:bg-emerald-700 text-white px-8">{t('public.products.ctaCatalog')}</Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <PublicFooter />
    </div>
  );
}
