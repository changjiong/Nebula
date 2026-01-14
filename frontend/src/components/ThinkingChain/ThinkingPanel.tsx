import { Separator } from "@/components/ui/separator"
import { useChatStore } from "@/stores/chatStore"
import { ExecutionDetail } from "./ExecutionDetail"
import { TaskProgress } from "./TaskProgress"

export function ThinkingPanel() {
  const { thinkingSteps } = useChatStore()

  if (thinkingSteps.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-center p-6 space-y-4">
        <div className="rounded-full bg-primary/10 p-4">
          <svg
            className="h-12 w-12 text-primary"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            role="img"
          >
            <title>Thinking Process</title>
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
            />
          </svg>
        </div>
        <div className="space-y-2">
          <h3 className="font-semibold text-lg">Agent Thinking Chain</h3>
          <p className="text-sm text-muted-foreground max-w-[200px]">
            Task execution progress will appear here in real-time
          </p>
        </div>
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
