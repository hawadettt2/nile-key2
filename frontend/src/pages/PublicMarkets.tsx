import StitchPage from '@/components/StitchPage';
import stitchMarkets from '../../stitch/markets/code.html?raw';

export function PublicMarkets() {
  return <StitchPage raw={stitchMarkets} />;
}

export default PublicMarkets;
