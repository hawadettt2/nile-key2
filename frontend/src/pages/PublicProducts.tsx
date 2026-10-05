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
    { assetGap: 'G4', title: t('public.products.vegetablesTitle'), description: t('public.products.vegetablesDesc') },
    { assetGap: 'G5', title: t('public.products.fruitsTitle'), description: t('public.products.fruitsDesc') },
    { assetGap: 'G6', title: t('public.products.factoryTitle'), description: t('public.products.factoryDesc') },
  ];

  return (
    <div className="min-h-screen bg-[#022F32] text-white" dir={isArabic ? 'rtl' : 'ltr'}>
      <PublicNavbar />

      <main>
        {/* Hero Section */}
        <section className="w-full bg-[#022F32]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 text-center md:py-20">
            <h1 className="text-3xl font-bold text-white lg:text-[34px]">{t('public.products.title')}</h1>
            <p className="mt-3 text-base text-white/70">{t('public.products.subtitle')}</p>
          </div>
        </section>

        {/* Products Grid — G4/G5/G6 Asset Gaps: no clean product photographs exist in the project */}
        <section className="w-full bg-[#043B3E]">
          <div className="mx-auto w-[min(92vw,1280px)] py-14 md:py-20">
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {products.map((product) => (
                <ProductCard
                  key={product.title}
                  assetGap={product.assetGap}
                  title={product.title}
                  description={product.description}
                />
              ))}
            </div>
            <div className="mt-12 text-center">
              <Link to="/contact">
                <Button className="h-12 rounded-full bg-[#19D8B0] px-8 text-base font-semibold text-[#022F32] hover:bg-[#19D8B0]/90">
                  {t('public.products.ctaCatalog')}
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
