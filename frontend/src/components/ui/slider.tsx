import * as React from "react"
import * as SliderPrimitive from "@radix-ui/react-slider"
import { cn } from "@/lib/utils"
function Slider({ className, ...props }: React.ComponentProps<typeof SliderPrimitive.Root>) {
  return (
    <SliderPrimitive.Root data-slot="slider" className={cn("relative flex w-full touch-none select-none items-center", className)} {...props}>
      <SliderPrimitive.Track className="bg-secondary relative h-2 w-full grow overflow-hidden rounded-full">
        <SliderPrimitive.Range className="absolute h-full bg-primary" />
      </SliderPrimitive.Track>
      {props.value?.map((_, i) => (
        <SliderPrimitive.Thumb key={i} className="border-primary bg-background ring-offset-background focus-visible:ring-ring block size-5 rounded-full border-2 shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 disabled:pointer-events-none disabled:opacity-50" />
      ))}
    </SliderPrimitive.Root>
  )
}
export { Slider }
