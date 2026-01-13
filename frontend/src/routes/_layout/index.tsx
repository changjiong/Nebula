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

function ChatPage(): React.JSX.Element {
  const { messages } = useChatStore()

  // Initialize SSE connection (currently disabled with null for dev/mock)
  useSSE(null)

  if (messages.length === 0) {
    // Empty state: centered layout with input in middle
    return (
      <div className="flex flex-col h-full items-center justify-center p-8">
        <div className="w-full max-w-2xl">
          <h1 className="text-3xl font-semibold text-center mb-2">
            我能为你做什么？
          </h1>
          <p className="text-muted-foreground text-center mb-8">
            选择一个功能开始，或直接输入
          </p>

          {/* Input box in center for empty state */}
          <div className="mb-12">
            <InputBox />
          </div>

          {/* Agent cards below */}
          <AgentCards />
        </div>
      </div>
    )
  }

  // Conversation state: standard layout with input at bottom
  return (
    <div className="flex flex-col h-full">
      <MessageList />
      <InputBox />
    </div>
  )
}
