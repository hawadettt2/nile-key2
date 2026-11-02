import StitchPage from '@/components/StitchPage';
import stitchProducts from '../../stitch/products/code.html?raw';
import { productsTranslations } from '@/locales/productsTranslations';

export function PublicProducts() {
  return <StitchPage raw={stitchProducts} translations={productsTranslations} />;
}

export default PublicProducts;
