import { createFileRoute } from "@tanstack/react-router"

import { AgentCards } from "@/components/Chat/AgentCards"
import { InputBox } from "@/components/Chat/InputBox"
import { MessageList } from "@/components/Chat/MessageList"
import { useSSE } from "@/hooks/useSSE"
import { useChatStore } from "@/stores/chatStore"

export const Route = createFileRoute("/_layout/")({
  component: ChatPage,
  head: () => ({
    meta: [
      {
        title: "对公业务智能助手 - Agent Portal",
      },
    ],
  }),
})

// ... imports unchanged

function ChatPage(): React.JSX.Element {
  const { messages } = useChatStore()

  // Initialize SSE connection (currently disabled with null for dev/mock)
  useSSE(null)

  if (messages.length === 0) {
    // New Task View: Centered, clean, "Grok-style"
    return (
      <div className="flex flex-col h-full items-center justify-center p-4 md:p-8">
        <div className="w-full max-w-3xl flex flex-col gap-8 animated-in fade-in duration-500 slide-in-from-bottom-4">
          <div className="text-center space-y-2">
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
              What can I help you with?
            </h1>
          </div>

          {/* Input Box */}
          <div className="w-full">
            <InputBox />
          </div>

          {/* Agent/Suggestions Cards */}
          <div className="w-full">
            <AgentCards />
          </div>
        </div>
      </div>
    )
  }

  // Active Conversation: Message list with pinned bottom input
  return (
    <div className="flex flex-col h-full relative">
      <div className="flex-1 overflow-hidden">
        <MessageList />
      </div>
      <div className="p-4 pt-0 mx-auto w-full max-w-3xl">
        <InputBox />
      </div>
    </div>
  )
}
