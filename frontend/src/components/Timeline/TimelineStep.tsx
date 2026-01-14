import {
  CheckCircle2,
  ChevronDown,
  Circle,
  Loader2,
  XCircle,
} from "lucide-react"
import { useState } from "react"

import { Badge } from "@/components/ui/badge"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { cn } from "@/lib/utils"
import type { StepSubItem, ThinkingStep } from "@/stores/chatStore"
import { TimelineSubItem } from "./TimelineSubItem"

interface TimelineStepProps {
  step: ThinkingStep
  onOpenCanvas?: (item: StepSubItem) => void
  className?: string
}

const statusIcons = {
  pending: <Circle className="h-4 w-4 text-muted-foreground shrink-0" />,
  "in-progress": (
    <Loader2 className="h-4 w-4 animate-spin text-orange-500 shrink-0" />
  ),
  completed: <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />,
  failed: <XCircle className="h-4 w-4 text-red-500 shrink-0" />,
}

export function TimelineStep({
  step,
  onOpenCanvas,
  className,
}: TimelineStepProps) {
  const defaultExpanded = step.defaultExpanded ?? 1
  const hasSubItems = step.subItems && step.subItems.length > 0
  const [isExpanded, setIsExpanded] = useState(true)
  const [showAllItems, setShowAllItems] = useState(false)

  // Determine which items to show
  const itemsToShow = showAllItems
    ? step.subItems || []
    : (step.subItems || []).slice(0, defaultExpanded)
  const hiddenCount = (step.subItems?.length || 0) - defaultExpanded

  return (
    <div className={cn("relative", className)}>
      {/* Step Header */}
      <div className="flex items-start gap-3">
        {/* Status Icon with Timeline Line */}
        <div className="relative flex flex-col items-center">
          {statusIcons[step.status]}
        </div>

        {/* Step Content */}
        <div className="flex-1 min-w-0 pb-4">
          {/* Title Row */}
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium leading-tight">
              {step.title}
            </span>
            {step.status === "in-progress" && (
              <Badge
                variant="outline"
                className="text-[10px] h-5 bg-orange-500/10 text-orange-600 border-orange-200"
              >
                进行中
              </Badge>
            )}
          </div>

          {/* Sub Items */}
          {hasSubItems && (
            <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
              <CollapsibleContent className="mt-3 space-y-2">
                {itemsToShow.map((subItem) => (
                  <TimelineSubItem
                    key={subItem.id}
                    item={subItem}
                    onClick={() => onOpenCanvas?.(subItem)}
                  />
                ))}

                {/* Show More Button */}
                {hiddenCount > 0 && !showAllItems && (
                  <button
                    type="button"
                    onClick={() => setShowAllItems(true)}
                    className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors py-1"
                  >
                    <ChevronDown className="h-3 w-3" />
                    <span>显示 {hiddenCount} 个更多</span>
                  </button>
                )}

                {/* Show Less Button */}
                {showAllItems && hiddenCount > 0 && (
                  <button
                    type="button"
                    onClick={() => setShowAllItems(false)}
                    className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors py-1"
                  >
                    <ChevronDown className="h-3 w-3 rotate-180" />
                    <span>收起</span>
                  </button>
                )}
              </CollapsibleContent>

              {/* Collapsible Trigger (if has many items) */}
              {step.isCollapsible &&
                step.subItems &&
                step.subItems.length > 0 && (
                  <CollapsibleTrigger asChild>
                    <button
                      type="button"
                      className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors mt-1"
                    >
                      <ChevronDown
                        className={cn(
                          "h-3 w-3 transition-transform",
                          isExpanded && "rotate-180",
                        )}
                      />
                      <span>{isExpanded ? "收起详情" : "展开详情"}</span>
                    </button>
                  </CollapsibleTrigger>
                )}
            </Collapsible>
          )}

          {/* Plain Content (for backward compatibility) */}
          {step.content && !hasSubItems && (
            <div className="mt-2 text-xs text-muted-foreground bg-muted/50 rounded-md p-3 font-mono whitespace-pre-wrap">
              {step.content}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
