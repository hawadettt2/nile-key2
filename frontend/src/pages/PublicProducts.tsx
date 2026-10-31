import StitchPage from '@/components/StitchPage';
import stitchProducts from '../../stitch/products/code.html?raw';

export function PublicProducts() {
  return <StitchPage raw={stitchProducts} />;
}

export default PublicProducts;
