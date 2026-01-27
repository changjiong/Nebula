import { Bot } from "lucide-react"
import { useEffect, useRef } from "react"
import { useChatStore } from "@/stores/chatStore"
import { ContentCanvas } from "../Timeline/ContentCanvas"
import { MarkdownRenderer } from "./MarkdownRenderer"
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
    thinkingStepsCount: thinkingSteps.length,
  })

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 md:px-4 md:py-6 space-y-5 md:space-y-6">
      {messages.map((message, index) => {
        // Determine which thinking steps to show for this assistant message
        // Priority: persisted steps on message > global state (for live streaming)
        const stepsToShow =
          message.role === "assistant" && index === lastAssistantIndex
            ? message.thinkingSteps && message.thinkingSteps.length > 0
              ? message.thinkingSteps
              : thinkingSteps
            : message.thinkingSteps

        return (
          <div key={message.id}>
            {/* Show thinking steps before assistant message */}
            {message.role === "assistant" &&
              stepsToShow &&
              stepsToShow.length > 0 && (
                <div className="w-full max-w-5xl mx-auto mb-2">
                  <ThinkingMessage steps={stepsToShow} />
                </div>
              )}

            {/* Message */}
            {message.role === "user" ? (
              // User message: Right side bubble
              <div className="flex w-full justify-end max-w-5xl mx-auto">
                <div className="px-4 py-2.5 rounded-2xl max-w-[80%] bg-secondary text-secondary-foreground border border-border/50">
                  <p className="m-0 text-sm leading-relaxed whitespace-pre-wrap">
                    {message.content}
                  </p>
                  <span className="text-[10px] opacity-60 mt-1.5 block text-right">
                    {new Date(message.timestamp).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
              </div>
            ) : (
              // Assistant message: Document style with avatar
              <div className="w-full max-w-5xl mx-auto">
                <div className="flex items-start gap-3">
                  {/* Avatar */}
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                    <Bot className="w-5 h-5" />
                  </div>
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    {/* Header */}
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="text-sm font-medium text-foreground">
                        Assistant
                      </span>
                      <span className="text-[10px] text-muted-foreground">
                        {new Date(message.timestamp).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                    </div>
                    {/* Markdown Body */}
                    <div className="min-w-0">
                      <MarkdownRenderer content={message.content} />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )
      })}

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
