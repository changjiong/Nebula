import { CheckCircle2, Circle, Loader2, XCircle } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import type { ThinkingStep } from "@/stores/chatStore"
import { ExecutionDetail } from "../ThinkingChain/ExecutionDetail"

interface ThinkingMessageProps {
  steps: ThinkingStep[]
  currentStep?: number
  totalSteps?: number
}

export function ThinkingMessage({
  steps,
  currentStep,
  totalSteps,
}: ThinkingMessageProps) {
  if (steps.length === 0) return null

  const completedSteps = steps.filter((s) => s.status === "completed").length
  const progressText = totalSteps
    ? `${currentStep || completedSteps}/${totalSteps}`
    : `${completedSteps}/${steps.length}`

  return (
    <div className="border rounded-lg p-3 md:p-4 my-2 bg-muted/30 space-y-2 md:space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
          <h4 className="font-medium text-sm">📋 任务进度</h4>
        </div>
        <Badge variant="outline" className="text-xs">
          {progressText}
        </Badge>
      </div>

      <Separator />

      {/* Steps */}
      <div className="space-y-3">
        {steps.map((step) => (
          <div key={step.id} className="flex flex-col gap-2">
            {/* Step Status */}
            <div className="flex items-center gap-2">
              {step.status === "pending" && (
                <Circle className="h-4 w-4 text-muted-foreground shrink-0" />
              )}
              {step.status === "in-progress" && (
                <Loader2 className="h-4 w-4 animate-spin text-blue-500 shrink-0" />
              )}
              {step.status === "completed" && (
                <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
              )}
              {step.status === "failed" && (
                <XCircle className="h-4 w-4 text-red-500 shrink-0" />
              )}

              <span className="text-sm font-medium leading-none flex-1">
                {step.title}
              </span>
            </div>

            {/* Execution Detail */}
            {step.content && (
              <div className="pl-6 border-l-2 border-muted ml-2">
                <ExecutionDetail content={step.content} />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
