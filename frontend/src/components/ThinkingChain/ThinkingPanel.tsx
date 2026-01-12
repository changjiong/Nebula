import { Separator } from "@/components/ui/separator"
import { useChatStore } from "@/stores/chatStore"
import { ExecutionDetail } from "./ExecutionDetail"
import { TaskProgress } from "./TaskProgress"

export function ThinkingPanel() {
  const { thinkingSteps } = useChatStore()

  if (thinkingSteps.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-muted-foreground text-sm p-4">
        No active tasks or thoughts.
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full p-4 space-y-4 overflow-y-auto">
      <h3 className="font-semibold text-lg">Agent Thinking Chain</h3>
      <Separator />

      <div className="space-y-6">
        {thinkingSteps.map((step) => (
          <div key={step.id} className="flex flex-col gap-2">
            <TaskProgress status={step.status} title={step.title} />
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
