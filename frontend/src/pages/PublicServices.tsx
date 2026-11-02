import StitchPage from '@/components/StitchPage';
import stitchServices from '../../stitch/services/code.html?raw';
import { servicesTranslations } from '@/locales/servicesTranslations';

export function PublicServices() {
  return <StitchPage raw={stitchServices} translations={servicesTranslations} />;
}

export default PublicServices;
