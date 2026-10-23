interface ServiceCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

export function ServiceCard({ icon, title, description }: ServiceCardProps) {
  return (
    <div className="bg-[#022F32]/30 backdrop-blur-sm rounded-2xl border border-white/15 p-6 hover:border-[#19D8B0]/30 transition-colors">
      <div className="text-[#19D8B0] mb-4">{icon}</div>
      <h3 className="text-white font-semibold text-lg mb-2">{title}</h3>
      <p className="text-white/60 text-sm">{description}</p>
    </div>
  );
}
