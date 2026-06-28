import * as React from "react"
import * as RechartsPrimitive from "recharts"
import { cn } from "@/lib/utils"
const THEMES = { light: "", dark: ".dark" } as const
type ChartConfig = Record<string, { label?: React.ReactNode; icon?: React.ComponentType; color?: string }>
const ChartContext = React.createContext<{ config: ChartConfig } | null>(null)
function useChart() { const context = React.useContext(ChartContext); if (!context) throw new Error("useChart must be used within a <ChartContainer />"); return context; }
function ChartContainer({ id, className, children, config, ...props }: React.ComponentProps<"div"> & { config: ChartConfig }) {
  const uniqueId = React.useId(); const chartId = `chart-${id || uniqueId.replace(/:/g, "")}`;
  return (
    <ChartContext.Provider value={{ config }}>
      <div data-chart={chartId} className={cn("flex aspect-video justify-center text-xs [&_.recharts-cartesian-axis-tick_text]:fill-muted-foreground [&_.recharts-cartesian-grid_line[stroke='#ccc']]:stroke-border/50 [&_.recharts-curve.recharts-tooltip-cursor]:stroke-border [&_.recharts-dot[stroke='#fff']]:stroke-transparent [&_.recharts-layer]:outline-none [&_.recharts-polar-grid_[stroke='#ccc']]:stroke-border [&_.recharts-radial-bar-background-sector]:fill-muted [&_.recharts-rectangle.recharts-tooltip-cursor]:fill-muted [&_.recharts-reference-line_[stroke='#ccc']]:stroke-border [&_.recharts-sector[stroke='#fff']]:stroke-transparent [&_.recharts-sector]:outline-none [&_.recharts-surface]:outline-none", className)} {...props}>
        <ChartStyle id={chartId} config={config} />
        <RechartsPrimitive.ResponsiveContainer width="100%" height="100%">{children}</RechartsPrimitive.ResponsiveContainer>
      </div>
    </ChartContext.Provider>
  )
}
function ChartStyle({ id, config }: { id: string; config: ChartConfig }) {
  const colorConfig = Object.entries(config).filter(([, c]) => c.color);
  if (!colorConfig.length) return null;
  return <style dangerouslySetInnerHTML={{ __html: Object.entries(THEMES).map(([theme, prefix]) => `${prefix} [data-chart=${id}] { ${colorConfig.map(([key, c]) => `--color-${key}: ${c.color};`).join(" ")} }`).join("\n") }} />
}
const ChartTooltip = RechartsPrimitive.Tooltip;
function ChartTooltipContent({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border bg-background px-3 py-2 shadow-sm">
      <p className="font-medium">{label}</p>
      {payload.map((entry: any, i: number) => (
        <div key={i} className="flex items-center gap-2 text-sm">
          <div className="size-2 rounded-full" style={{ background: entry.color }} />
          <span className="text-muted-foreground">{entry.name}:</span>
          <span className="font-medium">{entry.value}</span>
        </div>
      ))}
    </div>
  );
}
const ChartLegend = RechartsPrimitive.Legend;
export { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartStyle }
