import { SendIcon } from "lucide-react"
import { useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useChatStore } from "@/stores/chatStore"

export function InputBox() {
  const [input, setInput] = useState("")
  const { addMessage, isConnecting } = useChatStore()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = () => {
    if (!input.trim() || isConnecting) return

    addMessage({
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: Date.now(),
    })

    // TODO: Send to backend via API or triggering an event that useSSE might listen to (if bi-directional)
    // For now, we assume the backend interaction will happen separately or this is just UI.

    setInput("")
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
