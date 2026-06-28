import * as React from "react"
import * as ContextMenuPrimitive from "@radix-ui/react-context-menu"
import { Check, ChevronRight, Circle } from "lucide-react"
import { cn } from "@/lib/utils"
function ContextMenuSubTrigger({ className, inset, children, ...props }: React.ComponentProps<typeof ContextMenuPrimitive.SubTrigger> & { inset?: boolean }) {
  return (
    <ContextMenuPrimitive.SubTrigger data-slot="context-menu-sub-trigger" data-inset={inset} className={cn("focus:bg-accent focus:text-accent-foreground data-[state=open]:bg-accent data-[state=open]:text-accent-foreground flex cursor-default items-center rounded-sm px-2 py-1.5 text-sm outline-none select-none data-[inset]:pl-8", className)} {...props}>
      {children}<ChevronRight className="ml-auto size-4" />
    </ContextMenuPrimitive.SubTrigger>
  )
}
function ContextMenuSubContent({ className, ...props }: React.ComponentProps<typeof ContextMenuPrimitive.SubContent>) {
  return <ContextMenuPrimitive.SubContent data-slot="context-menu-sub-content" className={cn("bg-popover text-popover-foreground z-50 min-w-[8rem] overflow-hidden rounded-md border p-1 shadow-md", className)} {...props} />
}
function ContextMenuContent({ className, ...props }: React.ComponentProps<typeof ContextMenuPrimitive.Content>) {
  return (
    <ContextMenuPrimitive.Portal>
      <ContextMenuPrimitive.Content data-slot="context-menu-content" className={cn("bg-popover text-popover-foreground z-50 min-w-[8rem] overflow-hidden rounded-md border p-1 shadow-md animate-in fade-in-80", className)} {...props} />
    </ContextMenuPrimitive.Portal>
  )
}
function ContextMenuItem({ className, inset, ...props }: React.ComponentProps<typeof ContextMenuPrimitive.Item> & { inset?: boolean }) {
  return <ContextMenuPrimitive.Item data-slot="context-menu-item" data-inset={inset} className={cn("focus:bg-accent focus:text-accent-foreground relative flex cursor-default items-center rounded-sm px-2 py-1.5 text-sm outline-none select-none data-[inset]:pl-8", className)} {...props} />
}
function ContextMenuCheckboxItem({ className, children, checked, ...props }: React.ComponentProps<typeof ContextMenuPrimitive.CheckboxItem>) {
  return (
    <ContextMenuPrimitive.CheckboxItem data-slot="context-menu-checkbox-item" className={cn("relative flex cursor-default items-center rounded-sm py-1.5 pr-2 pl-8 text-sm outline-none select-none focus:bg-accent focus:text-accent-foreground", className)} checked={checked} {...props}>
      <span className="absolute left-2 flex size-3.5 items-center justify-center"><ContextMenuPrimitive.ItemIndicator><Check className="size-4" /></ContextMenuPrimitive.ItemIndicator></span>
      {children}
    </ContextMenuPrimitive.CheckboxItem>
  )
}
function ContextMenuRadioItem({ className, children, ...props }: React.ComponentProps<typeof ContextMenuPrimitive.RadioItem>) {
  return (
    <ContextMenuPrimitive.RadioItem data-slot="context-menu-radio-item" className={cn("relative flex cursor-default items-center rounded-sm py-1.5 pr-2 pl-8 text-sm outline-none select-none focus:bg-accent focus:text-accent-foreground", className)} {...props}>
      <span className="absolute left-2 flex size-3.5 items-center justify-center"><ContextMenuPrimitive.ItemIndicator><Circle className="size-2 fill-current" /></ContextMenuPrimitive.ItemIndicator></span>
      {children}
    </ContextMenuPrimitive.RadioItem>
  )
}
export { ContextMenuSubTrigger, ContextMenuSubContent, ContextMenuContent, ContextMenuItem, ContextMenuCheckboxItem, ContextMenuRadioItem }
