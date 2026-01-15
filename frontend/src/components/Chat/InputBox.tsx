import {
  ChevronDown,
  Image as ImageIcon,
  Paperclip,
  Plus,
  SendIcon,
  Square,
} from "lucide-react"
import { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Textarea } from "@/components/ui/textarea"
import { useConversations } from "@/hooks/useConversations"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"
import { useModelProviderStore, AvailableModel } from "@/stores/modelProviderStore"

// Fallback models when no providers configured
const FALLBACK_MODELS: AvailableModel[] = [
  { id: "deepseek-chat", name: "DeepSeek Chat", provider_id: "", provider_name: "DeepSeek", provider_type: "deepseek" },
]

export function InputBox() {
  const [input, setInput] = useState("")
  const { addMessage, isConnecting, setIsConnecting, currentConversationId } = useChatStore()
  const { createConversation, sendMessage } = useConversations()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Get models from provider store
  const { getEnabledModels, fetchProviders } = useModelProviderStore()
  const enabledModels = getEnabledModels()
  const models = enabledModels.length > 0 ? enabledModels : FALLBACK_MODELS
  const [selectedModel, setSelectedModel] = useState<AvailableModel>(models[0])

  // Fetch providers on mount
  useEffect(() => {
    fetchProviders()
  }, [fetchProviders])

  // Update selected model when models change
  useEffect(() => {
    if (models.length > 0 && !models.find((m) => m.id === selectedModel?.id)) {
      setSelectedModel(models[0])
    }
  }, [models, selectedModel])


  const handleSubmit = async (): Promise<void> => {
    if (!input.trim() || isConnecting) return

    const userInput = input
    setInput("")

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
    }

    setIsConnecting(true)

    try {
      // Ensure we have a conversation (create one if needed)
      let conversationId = currentConversationId
      if (!conversationId) {
        // Create conversation on server first
        const newConv = await createConversation(userInput.slice(0, 50))
        if (!newConv) {
          throw new Error("Failed to create conversation")
        }
        conversationId = newConv.id
      }

      // Save user message to server
      const savedUserMessage = await sendMessage(conversationId, "user", userInput)

      // Add to local state for immediate UI feedback
      const userMessage = {
        id: savedUserMessage?.id || Date.now().toString(),
        role: "user" as const,
        content: userInput,
        timestamp: Date.now(),
      }
      addMessage(userMessage)

      // Call the backend streaming endpoint
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"
      const response = await fetch(`${apiUrl}/api/v1/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({
          role: "user",
          content: userInput,
          model: selectedModel.id,
          provider_id: selectedModel.provider_id || null,
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
        const {
          updateMessageTransient,
          addThinkingStep,
          syncMessageToConversation,
        } = useChatStore.getState()

        // eslint-disable-next-line no-constant-condition
        while (true) {
          const { done, value } = await reader.read()
          if (done) {
            // Stream finished, sync and save to server
            syncMessageToConversation(assistantMessageId)
            // Save assistant message to server
            if (conversationId && assistantMessage) {
              await sendMessage(conversationId, "assistant", assistantMessage)
            }
            break
          }

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split("\n")

          // Keep the last incomplete line in buffer
          buffer = lines.pop() || ""

          for (const line of lines) {
            if (!line.trim()) continue

            if (line.startsWith("data: ")) {
              const data = line.slice(6).trim()
              if (data === "[DONE]") {
                syncMessageToConversation(assistantMessageId)
                // Save assistant message to server
                if (conversationId && assistantMessage) {
                  await sendMessage(conversationId, "assistant", assistantMessage)
                }
                break
              }

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
                  // Use transient update to avoid expensive persist on every chunk
                  updateMessageTransient(assistantMessageId, assistantMessage)
                } else if (event.type === "error") {
                  // Handle error
                  console.error("Stream error:", event.data)
                  assistantMessage += `\n[错误: ${event.data.message}]`
                  updateMessageTransient(assistantMessageId, assistantMessage)
                }
              } catch (_e) {
                // Fallback: treat as plain text (backward compatibility)
                assistantMessage += data
                updateMessageTransient(assistantMessageId, assistantMessage)
              }
            }
          }
        }
        // Ensure sync happens if loop exits for other reasons
        syncMessageToConversation(assistantMessageId)
      }
    } catch (error) {
      console.error("Failed to send message:", error)
      addMessage({
        id: (Date.now() + 2).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: Date.now(),
      })
    } finally {
      setIsConnecting(false)
    }
  }

  const handleStop = () => {
    // Placeholder for abort logic (needs AbortController impl)
    setIsConnecting(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleInputChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value)
    // Auto-resize
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }

  return (
    <div className="w-full relative">
      {" "}
      {/* Removed sticky positioning here, let parent handle layout */}
      <div className="flex flex-col gap-2 rounded-2xl border bg-background p-3 shadow-md focus-within:ring-1 focus-within:ring-ring transition-all">
        {/* Input Area */}
        <Textarea
          ref={textareaRef}
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything..."
          className="flex-1 min-h-[60px] max-h-[200px] resize-none border-0 bg-transparent px-2 py-2 text-base shadow-none focus-visible:ring-0 placeholder:text-muted-foreground/50"
          rows={1}
        />

        {/* Toolbar */}
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-2">
            {/* Attachment Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 text-muted-foreground hover:text-foreground"
                >
                  <Plus className="size-5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                <DropdownMenuItem>
                  <Paperclip className="mr-2 h-4 w-4" />
                  Upload File
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <ImageIcon className="mr-2 h-4 w-4" />
                  Upload Image
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Model Selector */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 text-xs font-medium text-muted-foreground hover:text-foreground gap-1 px-2"
                >
                  {selectedModel.name}
                  <ChevronDown className="size-3 opacity-50" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                {models.map((model) => (
                  <DropdownMenuItem
                    key={model.id}
                    onClick={() => setSelectedModel(model)}
                  >
                    <span>{model.name}</span>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <div className="flex items-center gap-2">
            {isConnecting ? (
              <Button
                onClick={handleStop}
                size="icon"
                className="h-8 w-8 rounded-full bg-foreground text-background hover:bg-foreground/90"
              >
                <Square className="size-3 fill-current" />
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                disabled={!input.trim()}
                size="icon"
                className={cn(
                  "h-8 w-8 rounded-full transition-all",
                  input.trim()
                    ? "bg-primary text-primary-foreground hover:bg-primary/90"
                    : "bg-muted text-muted-foreground hover:bg-muted/80",
                )}
              >
                <SendIcon className="size-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
