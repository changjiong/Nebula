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
import { useSSE } from "@/hooks/useSSE"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"
import {
  type AvailableModel,
  useModelProviderStore,
} from "@/stores/modelProviderStore"

// Fallback models when no providers configured
const FALLBACK_MODELS: AvailableModel[] = [
  {
    id: "deepseek-chat",
    name: "DeepSeek Chat",
    provider_id: "",
    provider_name: "DeepSeek",
    provider_type: "deepseek",
  },
]

export function InputBox() {
  const [input, setInput] = useState("")
  const { addMessage, isConnecting, setIsConnecting, currentConversationId } =
    useChatStore()
  const { createConversation, sendMessage } = useConversations()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Get models from provider store
  const { getEnabledModels, fetchProviders, selectedModelId, selectModel } =
    useModelProviderStore()
  const enabledModels = getEnabledModels()
  const models = enabledModels.length > 0 ? enabledModels : FALLBACK_MODELS

  // Derive selected model from store, or fallback to first available
  const selectedModel =
    models.find((m) => m.id === selectedModelId) || models[0]

  // Fetch providers on mount
  useEffect(() => {
    fetchProviders()
  }, [fetchProviders])

  // Sync initial selection if needed
  useEffect(() => {
    if (!selectedModelId && models.length > 0) {
      selectModel(models[0].id)
    }
  }, [models, selectedModelId, selectModel])

  const { streamMessage, isStreaming, abort } = useSSE()

  // Update store connecting state based on local hook state
  useEffect(() => {
    setIsConnecting(isStreaming)
  }, [isStreaming, setIsConnecting])

  const handleSubmit = async (): Promise<void> => {
    if (!input.trim() || isConnecting) return

    const userInput = input
    setInput("")

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
    }

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
      const savedUserMessage = await sendMessage(
        conversationId,
        "user",
        userInput,
      )

      // Add to local state for immediate UI feedback
      const userMessage = {
        id: savedUserMessage?.id || Date.now().toString(),
        role: "user" as const,
        content: userInput,
        timestamp: Date.now(),
      }
      addMessage(userMessage)

      // Call the streaming hook
      const result = await streamMessage({
        content: userInput,
        model: selectedModel.id,
        provider_id: selectedModel.provider_id,
        conversation_id: conversationId,
      })

      // Save assistant message to server after stream completes
      if (conversationId && result?.content) {
        await sendMessage(conversationId, "assistant", result.content)
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

  const handleStop = () => {
    abort()
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
      <div className="flex flex-col gap-2 rounded-2xl border bg-background p-3 shadow-md focus-within:ring-1 focus-within:ring-ring transition-all w-full max-w-5xl mx-auto">
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
                    onClick={() => selectModel(model.id)}
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
