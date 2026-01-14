import { ChevronDown, ChevronUp, Loader2 } from "lucide-react"
import { useMemo, useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import type { ThinkingStep } from "@/stores/chatStore"
import { useChatStore } from "@/stores/chatStore"
import { TimelineGroup } from "../Timeline/TimelineGroup"
import { TimelineStep } from "../Timeline/TimelineStep"

interface ThinkingMessageProps {
  steps: ThinkingStep[]
  currentStep?: number
  totalSteps?: number
}

interface GroupedStep {
  type: "group" | "step"
  id: string
  title?: string // for group
  steps?: ThinkingStep[] // for group
  step?: ThinkingStep // for step
}

export function ThinkingMessage({
  steps,
  currentStep,
  totalSteps,
}: ThinkingMessageProps) {
  const { openCanvas } = useChatStore()
  const [isOpen, setIsOpen] = useState(true)

  // Group sequential steps
  const groupedSteps = useMemo(() => {
    const groups: GroupedStep[] = []
    let currentGroup: GroupedStep | null = null

    steps.forEach((step) => {
      if (step.group) {
        if (
          currentGroup &&
          currentGroup.type === "group" &&
          currentGroup.title === step.group
        ) {
          // Add to existing group
          currentGroup.steps!.push(step)
        } else {
          // Start new group
          currentGroup = {
            type: "group",
            id: `group-${step.group}-${step.id}`,
            title: step.group,
            steps: [step],
          }
          groups.push(currentGroup)
        }
      } else {
        // Standalone step
        currentGroup = null
        groups.push({
          type: "step",
          id: `step-${step.id}`,
          step,
        })
      }
    })

    return groups
  }, [steps])

  if (steps.length === 0) return null

  const completedSteps = steps.filter((s) => s.status === "completed").length
  const progressText = totalSteps
    ? `${currentStep || completedSteps}/${totalSteps}`
    : `${completedSteps}/${steps.length}`

  const isAllCompleted = completedSteps === steps.length

  // Auto-collapse when done (optional, can adjust behavior)
  // useEffect(() => {
  //   if (isAllCompleted) {
  //     setIsOpen(false)
  //   }
  // }, [isAllCompleted])

  return (
    <Collapsible
      open={isOpen}
      onOpenChange={setIsOpen}
      className="border rounded-lg bg-muted/20 overflow-hidden my-4 transition-all duration-200"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 md:p-4 bg-muted/40">
        <div className="flex items-center gap-3">
          {isAllCompleted ? (
            <div className="w-5 h-5 rounded-full bg-green-500/10 flex items-center justify-center">
              <div className="w-2.5 h-2.5 rounded-full bg-green-500" />
            </div>
          ) : (
            <Loader2 className="h-4 w-4 animate-spin text-orange-500" />
          )}
          <h4 className="font-medium text-sm">
            {isAllCompleted ? "已完成任务" : "执行任务中..."}
          </h4>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs font-normal">
            {progressText}
          </Badge>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
              {isOpen ? (
                <ChevronUp className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              )}
            </Button>
          </CollapsibleTrigger>
        </div>
      </div>

      <CollapsibleContent>
        <div className="p-3 md:p-4 pt-0 space-y-4 relative">
          {/* Vertical Line for the whole timeline */}
          <div className="absolute left-[27px] md:left-[31px] top-4 bottom-4 w-0.5 bg-border/50" />

          {groupedSteps.map((group) => {
            if (group.type === "group") {
              return (
                <TimelineGroup
                  key={group.id}
                  title={group.title!}
                  steps={group.steps!}
                  onOpenCanvas={openCanvas}
                />
              )
            }
            return (
              <TimelineStep
                key={group.id}
                step={group.step!}
                onOpenCanvas={openCanvas}
              />
            )
          })}
        </div>
      </CollapsibleContent>
    </Collapsible>
  )
}
