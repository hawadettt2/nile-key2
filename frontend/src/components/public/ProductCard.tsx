interface ProductCardProps {
  imageSrc?: string;
  assetGap?: string;
  title: string;
  description: string;
}

export function ProductCard({ imageSrc, assetGap, title, description }: ProductCardProps) {
  return (
    <div className="overflow-hidden rounded-xl border border-white/10 bg-white/5">
      <div className="relative">
        {imageSrc ? (
          <div className="aspect-[4/5] w-full overflow-hidden">
            <img src={imageSrc} alt={title} className="h-full w-full object-cover" />
          </div>
        ) : (
          <div className="aspect-[4/5] w-full bg-[#022F32]/70" data-asset-gap={assetGap} />
        )}
        <div
          className="absolute inset-x-0 bottom-0 h-2/3 bg-gradient-to-t from-[rgba(2,47,50,0.85)] via-[rgba(2,47,50,0.4)] to-transparent"
          aria-hidden="true"
        />
        <div className="absolute inset-x-0 bottom-0 p-5">
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          <p className="mt-1 text-sm leading-6 text-white/60">{description}</p>
        </div>
      </div>
    </div>
  );
}
