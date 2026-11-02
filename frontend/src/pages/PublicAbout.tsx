import StitchPage from '@/components/StitchPage';
import stitchAbout from '../../stitch/about/code.html?raw';
import { aboutTranslations } from '@/locales/aboutTranslations';

export function PublicAbout() {
  return <StitchPage raw={stitchAbout} translations={aboutTranslations} />;
}

export default PublicAbout;
