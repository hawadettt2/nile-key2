import { Link } from 'react-router-dom';

interface ProductCardProps {
  imageSrc: string;
  title: string;
  description: string;
  ctaText: string;
  ctaLink: string;
}

export function ProductCard({ imageSrc, title, description, ctaText, ctaLink }: ProductCardProps) {
  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 overflow-hidden group">
      <div className="aspect-[4/3] overflow-hidden bg-slate-800">
        <img
          src={imageSrc}
          alt={title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
      </div>
      <div className="p-6">
        <h3 className="text-white font-semibold text-xl mb-2">{title}</h3>
        <p className="text-slate-400 text-sm mb-4">{description}</p>
        <Link to={ctaLink}>
          <button className="text-emerald-400 hover:text-emerald-300 text-sm font-medium transition-colors">
            {ctaText} →
          </button>
        </Link>
      </div>
    </div>
  );
}
