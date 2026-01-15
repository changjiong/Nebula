import { useEffect, useRef } from "react"
import ReactMarkdown from "react-markdown"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"
import { ContentCanvas } from "../Timeline/ContentCanvas"
import { ThinkingMessage } from "./ThinkingMessage"

export function MessageList() {
  const { messages } = useChatStore()
  const thinkingSteps = useChatStore((state) => state.thinkingSteps)
  // Canvas state
  const canvasContent = useChatStore((state) => state.canvasContent)
  const isCanvasOpen = useChatStore((state) => state.isCanvasOpen)
  const closeCanvas = useChatStore((state) => state.closeCanvas)

  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [])

  // Find the last assistant message to insert thinking before it
  const lastAssistantIndex = messages
    .map((m, i) => (m.role === "assistant" ? i : -1))
    .filter((i) => i !== -1)
    .pop()

  console.log("MessageList render:", {
    msgCount: messages.length,
    lastAssistantIndex,
    thinkingStepsCount: thinkingSteps.length
  })

  return (
    <div className="flex-1 overflow-y-auto px-3 py-4 md:px-6 md:py-6 space-y-4 md:space-y-6">
      {messages.map((message, index) => (
        <div key={message.id}>
          {/* Show thinking steps before the last assistant message */}
          {index === lastAssistantIndex &&
            thinkingSteps.length > 0 && (
              <div className="max-w-3xl mx-auto mb-6">
                <ThinkingMessage steps={thinkingSteps} />
              </div>
            )}

          {/* Message */}
          <div
            className={cn(
              "flex max-w-3xl mx-auto",
              message.role === "user" ? "justify-end" : "justify-start",
            )}
          >
            <div
              className={cn(
                "rounded-2xl px-3 py-2 max-w-[80%]",
                message.role === "user"
                  ? "bg-secondary text-secondary-foreground border border-border/50"
                  : "bg-muted",
              )}
            >
              <div className="prose dark:prose-invert prose-sm max-w-none">
                {message.role === "user" ? (
                  <p className="m-0">{message.content}</p>
                ) : (
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                )}
              </div>
              <span className="text-[10px] opacity-70 mt-2 block">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        </div>
      ))}

      <div ref={bottomRef} />

      {/* Right-side Content Canvas */}
      <ContentCanvas
        item={canvasContent}
        isOpen={isCanvasOpen}
        onClose={closeCanvas}
      />
    </div>
  )
}
