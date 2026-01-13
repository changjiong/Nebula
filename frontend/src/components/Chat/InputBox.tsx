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

        // eslint-disable-next-line no-constant-condition
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split("\n")

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6).trim()
              if (data === "[DONE]") break

              assistantMessage += data + " "

              // Update the assistant message with accumulated content
              if (assistantMessage.trim()) {
                const { updateMessage } = useChatStore.getState()
                updateMessage(assistantMessageId, assistantMessage.trim())
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

  return (
    <div className="p-4 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-3xl mx-auto relative flex gap-2 items-end">
        <Textarea
          ref={textareaRef}
          value={input}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
            setInput(e.target.value)
          }
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          className="min-h-[50px] max-h-[200px] resize-none pr-12"
          rows={1}
        />
        <Button
          size="icon"
          onClick={handleSubmit}
          disabled={!input.trim() || isConnecting}
          className="absolute right-2 bottom-2 h-8 w-8"
        >
          <SendIcon className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
