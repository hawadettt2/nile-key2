interface MarketStepCardProps {
  stepNumber: number;
  icon: React.ReactNode;
  title: string;
  description: string;
}

export function MarketStepCard({ stepNumber, icon, title, description }: MarketStepCardProps) {
  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-6 hover:border-emerald-500/30 transition-colors relative">
      <div className="absolute top-4 right-4 text-emerald-500/30 text-4xl font-bold">
        {String(stepNumber).padStart(2, '0')}
      </div>
      <div className="text-emerald-400 mb-4">{icon}</div>
      <h3 className="text-white font-semibold text-lg mb-2">{title}</h3>
      <p className="text-slate-400 text-sm">{description}</p>
    </div>
  );
}
