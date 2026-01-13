import { SendIcon } from "lucide-react"
import { useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useChatStore } from "@/stores/chatStore"

export function InputBox() {
  const [input, setInput] = useState("")
  const { addMessage, isConnecting } = useChatStore()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = async (): Promise<void> => {
    if (!input.trim() || isConnecting) return

    const userMessage = {
      id: Date.now().toString(),
      role: "user" as const,
      content: input,
      timestamp: Date.now(),
    }

    addMessage(userMessage)
    setInput("")

    // Call the backend streaming endpoint
    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"
      const response = await fetch(`${apiUrl}/api/v1/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          role: "user",
          content: input,
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Handle SSE response
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let assistantMessage = ""

      if (reader) {
        // Create initial empty assistant message
        const assistantMessageId = (Date.now() + 1).toString()
        addMessage({
          id: assistantMessageId,
          role: "assistant",
          content: "",
          timestamp: Date.now(),
        })

        let buffer = ""
        const { updateMessage, addThinkingStep } = useChatStore.getState()

        // eslint-disable-next-line no-constant-condition
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split("\n")

          // Keep the last incomplete line in buffer
          buffer = lines.pop() || ""

          for (const line of lines) {
            if (!line.trim()) continue

            if (line.startsWith("data: ")) {
              const data = line.slice(6).trim()
              if (data === "[DONE]") break

              try {
                // Try to parse as JSON event
                const event = JSON.parse(data)

                if (event.type === "thinking") {
                  // Add or update thinking step
                  const step = event.data
                  addThinkingStep({
                    id: step.id,
                    title: step.title,
                    status: step.status,
                    content: step.content || "",
                    timestamp: step.timestamp,
                  })
                } else if (event.type === "message") {
                  // Accumulate message content
                  assistantMessage += event.data.content
                  updateMessage(assistantMessageId, assistantMessage)
                } else if (event.type === "error") {
                  // Handle error
                  console.error("Stream error:", event.data)
                  assistantMessage += `\n[错误: ${event.data.message}]`
                  updateMessage(assistantMessageId, assistantMessage)
                }
              } catch (e) {
                // Fallback: treat as plain text (backward compatibility)
                assistantMessage += data
                updateMessage(assistantMessageId, assistantMessage)
              }
            }
          }
        }
      }
    } catch (error) {
      console.error("Failed to send message:", error)
      addMessage({
        id: (Date.now() + 2).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: Date.now(),
      })
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value)
  }

  return (
    <div className="sticky bottom-0 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <div className="max-w-3xl mx-auto p-4">
        <div className="flex items-end gap-2 rounded-2xl border border-border/50 bg-background p-2 shadow-sm hover:border-border transition-colors">
          {/* Plus button (placeholder for attachments) */}
          <Button
            variant="ghost"
            size="icon"
            className="shrink-0 h-9 w-9 rounded-xl"
            disabled
            title="附件功能即将推出"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
          </Button>

          {/* Input area */}
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="我能为你做什么..."
            className="flex-1 min-h-[2.5rem] max-h-32 resize-none border-0 bg-transparent px-2 py-2 text-sm focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-muted-foreground/60"
            rows={1}
          />

          {/* Function buttons group */}
          <div className="flex items-center gap-1 shrink-0">
            {/* Image button (placeholder) */}
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9 rounded-xl"
              disabled
              title="图片功能即将推出"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </Button>

            {/* Send button */}
            <Button
              onClick={handleSubmit}
              disabled={!input.trim() || isConnecting}
              size="icon"
              className="h-9 w-9 rounded-xl"
            >
              <SendIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
