import StitchPage from '@/components/StitchPage';
import stitchMarkets from '../../stitch/markets/code.html?raw';
import { marketsTranslations } from '@/locales/marketsTranslations';

export function PublicMarkets() {
  return <StitchPage raw={stitchMarkets} translations={marketsTranslations} />;
}

export default PublicMarkets;
