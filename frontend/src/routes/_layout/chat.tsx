import { createFileRoute } from "@tanstack/react-router"
import { AgentCards } from "@/components/Chat/AgentCards"
import { ChatContainer } from "@/components/Chat/ChatContainer"
import { InputBox } from "@/components/Chat/InputBox"
import { MessageList } from "@/components/Chat/MessageList"
import { ThinkingPanel } from "@/components/ThinkingChain/ThinkingPanel"
import { useSSE } from "@/hooks/useSSE"
import { useChatStore } from "@/stores/chatStore"

export const Route = createFileRoute("/_layout/chat")({
  component: ChatPage,
})

function ChatPage(): React.JSX.Element {
  const { messages } = useChatStore()

  // Initialize SSE connection (currently disabled with null for dev/mock)
  useSSE(null)

  return (
    <ChatContainer rightPanel={<ThinkingPanel />}>
      <div className="flex flex-col h-full">
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col justify-center items-center p-8">
            <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              What can I help you with?
            </h1>
            <AgentCards />
          </div>
        ) : (
          <MessageList />
        )}
        <InputBox />
      </div>
    </ChatContainer>
  )
}
