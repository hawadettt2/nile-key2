interface ProductCardProps {
  imageSrc: string;
  title: string;
  description: string;
}

export function ProductCard({ imageSrc, title, description }: ProductCardProps) {
  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 overflow-hidden shadow-lg">
      <div className="aspect-[3/2] overflow-hidden bg-slate-800">
        <img
          src={imageSrc}
          alt={title}
          className="w-full h-full object-cover"
        />
      </div>
      <div className="p-6">
        <h3 className="text-lg font-semibold text-white mt-4">{title}</h3>
        <p className="text-sm text-slate-300 mt-2">{description}</p>
      </div>
    </div>
  );
}
