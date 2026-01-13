import { createFileRoute } from "@tanstack/react-router"

import { AgentCards } from "@/components/Chat/AgentCards"
import { InputBox } from "@/components/Chat/InputBox"
import { MessageList } from "@/components/Chat/MessageList"
import { useSSE } from "@/hooks/useSSE"
import { useChatStore } from "@/stores/chatStore"

export const Route = createFileRoute("/_layout/")(({
  component: ChatPage,
  head: () => ({
    meta: [
      {
        title: "对公业务智能助手 - Agent Portal",
      },
    ],
  }),
}))

function ChatPage(): React.JSX.Element {
  const { messages } = useChatStore()

  // Initialize SSE connection (currently disabled with null for dev/mock)
  useSSE(null)

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col justify-center items-center p-8">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            您好,我是对公业务智能助手
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            我能为您做什么？
          </p>
          <AgentCards />
        </div>
      ) : (
        <MessageList />
      )}
      <InputBox />
    </div>
  )
}
