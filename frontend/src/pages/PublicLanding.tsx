import StitchPage from '@/components/StitchPage';
import stitchHome from '../../stitch/home/code.html?raw';
import { homeTranslations, homeAttrTranslations } from '@/locales/homeTranslations';

export function PublicLanding() {
  return <StitchPage raw={stitchHome} translations={homeTranslations} attrTranslations={homeAttrTranslations} />;
}

export default PublicLanding;
