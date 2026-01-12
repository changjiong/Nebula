import { useEffect, useRef } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"

export function MessageList() {
  const { messages } = useChatStore()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [])

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-6">
      {messages.map((message) => (
        <div
          key={message.id}
          className={cn(
            "flex gap-4 max-w-3xl mx-auto",
            message.role === "user" ? "flex-row-reverse" : "flex-row",
          )}
        >
          <Avatar className="w-8 h-8">
            <AvatarImage
              src={
                message.role === "user"
                  ? "/user-avatar.png"
                  : "/agent-avatar.png"
              }
            />
            <AvatarFallback>
              {message.role === "user" ? "U" : "A"}
            </AvatarFallback>
          </Avatar>

          <div
            className={cn(
              "rounded-lg p-4 max-w-[80%]",
              message.role === "user"
                ? "bg-primary text-primary-foreground"
                : "bg-muted",
            )}
          >
            <div className="prose dark:prose-invert text-sm">
              {message.content}
            </div>
            <span className="text-[10px] opacity-70 mt-2 block">
              {new Date(message.timestamp).toLocaleTimeString()}
            </span>
          </div>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
