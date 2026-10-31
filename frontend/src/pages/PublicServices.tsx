import StitchPage from '@/components/StitchPage';
import stitchServices from '../../stitch/services/code.html?raw';

export function PublicServices() {
  return <StitchPage raw={stitchServices} />;
}

export default PublicServices;
