import { createFileRoute } from "@tanstack/react-router"
import { AgentCards } from "@/components/Chat/AgentCards"
import { ChatContainer } from "@/components/Chat/ChatContainer"
import { InputBox } from "@/components/Chat/InputBox"
import { MessageList } from "@/components/Chat/MessageList"
import { ThinkingPanel } from "@/components/ThinkingChain/ThinkingPanel"
import { useSSE } from "@/hooks/useSSE"
import { useChatStore } from "@/stores/chatStore"

// @ts-expect-error
export const Route = createFileRoute("/_layout/chat")({
  component: ChatPage,
})

function ChatPage() {
  // Use a hardcoded URL for now or enviroment variable.
  // In a real app, this might be dynamic based on session.
  // Assuming backend runs on same host/port during dev proxy or a known URL.
  // For now, let's assume we might get a conversation ID and connect to it.
  const { messages } = useChatStore()

  // Example SSE connection. In a real scenario, we might connect only when a session starts.
  // For demo purposes, we connect to a mock endpoint or a real one if available.
  // Passing null initially to not auto-connect until we have a proper endpoint logic.
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
