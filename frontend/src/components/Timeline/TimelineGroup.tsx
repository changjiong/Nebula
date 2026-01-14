import { cn } from "@/lib/utils"
import type { StepSubItem, ThinkingStep } from "@/stores/chatStore"
import { TimelineStep } from "./TimelineStep"

interface TimelineGroupProps {
  title: string
  steps: ThinkingStep[]
  onOpenCanvas?: (item: StepSubItem) => void
  className?: string
}

export function TimelineGroup({
  title,
  steps,
  onOpenCanvas,
  className,
}: TimelineGroupProps) {
  if (steps.length === 0) return null

  return (
    <div className={cn("relative", className)}>
      {/* Group Header */}
      <div className="flex items-center gap-2 mb-3">
        <div className="w-1 h-4 rounded-full bg-orange-500" />
        <h4 className="text-sm font-semibold text-foreground">{title}</h4>
      </div>

      {/* Timeline Items */}
      <div className="relative pl-4 border-l-2 border-muted ml-0.5">
        {steps.map((step, index) => (
          <TimelineStep
            key={step.id}
            step={step}
            onOpenCanvas={onOpenCanvas}
            className={cn(
              index !== steps.length - 1 && "border-b border-border/30 mb-3",
            )}
          />
        ))}
      </div>
    </div>
  )
}
