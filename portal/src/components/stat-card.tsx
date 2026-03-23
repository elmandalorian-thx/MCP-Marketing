interface StatCardProps {
  icon: string;
  label: string;
  value: string | number;
  footer?: string;
  color?: "teal" | "green" | "amber" | "coral" | "blue";
}

const colors = {
  teal: { bg: "bg-[#51cbce]/10", text: "text-[#51cbce]" },
  green: { bg: "bg-[#6bd098]/10", text: "text-[#6bd098]" },
  amber: { bg: "bg-[#fcc468]/10", text: "text-[#e8a317]" },
  coral: { bg: "bg-[#f17e5d]/10", text: "text-[#f17e5d]" },
  blue: { bg: "bg-[#51bcda]/10", text: "text-[#51bcda]" },
};

export function StatCard({ icon, label, value, footer, color = "teal" }: StatCardProps) {
  const c = colors[color];
  return (
    <div className="card p-5 flex items-start gap-4">
      <div className={`w-12 h-12 rounded-xl ${c.bg} ${c.text} flex items-center justify-center text-xl flex-shrink-0`}>
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-[0.72rem] font-semibold text-[#9A9A9A] uppercase tracking-wider mb-1">
          {label}
        </div>
        <div className="text-2xl font-bold text-[#252422] leading-tight">
          {typeof value === "number" ? value.toLocaleString() : value}
        </div>
        {footer && (
          <div className="text-[0.7rem] text-[#9A9A9A] mt-1.5 truncate">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
