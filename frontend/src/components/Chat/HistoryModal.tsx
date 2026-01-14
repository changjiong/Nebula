import { format } from "date-fns"
import { MessageSquare, Pencil, Search, Trash2 } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"

interface HistoryModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function HistoryModal({ open, onOpenChange }: HistoryModalProps) {
  const conversations = useChatStore((state) => state.conversations)
  const switchConversation = useChatStore((state) => state.switchConversation)
  const deleteConversation = useChatStore((state) => state.deleteConversation)
  const [searchQuery, setSearchQuery] = useState("")
  const [hoveredConversation, setHoveredConversation] = useState<string | null>(null)

  const filteredConversations = conversations.filter((conv) =>
    (conv.title || "New Conversation")
      .toLowerCase()
      .includes(searchQuery.toLowerCase()),
  )

  // Get the hovered conversation's details for preview
  const previewConversation = conversations.find(c => c.id === hoveredConversation)

  const handleSelect = (id: string) => {
    switchConversation(id)
    onOpenChange(false)
  }

  // Group conversations by date
  const groupedConversations = filteredConversations.reduce<Record<string, typeof filteredConversations>>((acc, conv) => {
    const date = new Date(conv.updatedAt)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    let label: string
    if (date.toDateString() === today.toDateString()) {
      label = "Today"
    } else if (date.toDateString() === yesterday.toDateString()) {
      label = "Yesterday"
    } else if (date > new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)) {
      label = "Last 7 Days"
    } else {
      label = format(date, "MMM yyyy")
    }

    if (!acc[label]) acc[label] = []
    acc[label].push(conv)
    return acc
  }, {})

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl h-[80vh] flex flex-col p-0 gap-0 overflow-hidden">
        {/* Search Header */}
        <DialogHeader className="p-4 border-b shrink-0">
          <DialogTitle className="sr-only">Search History</DialogTitle>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 h-10"
              autoFocus
            />
          </div>
        </DialogHeader>

        {/* Split Panel: List Left, Preview Right */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left: Conversation List */}
          <div className="w-1/2 border-r flex flex-col">
            <ScrollArea className="flex-1">
              <div className="p-2">
                {filteredConversations.length === 0 ? (
                  <div className="text-center text-muted-foreground py-12">
                    No conversations found.
                  </div>
                ) : (
                  Object.entries(groupedConversations).map(([label, convs]) => (
                    <div key={label} className="mb-4">
                      <div className="px-2 py-1 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        {label}
                      </div>
                      {convs.map((conv) => (
                        <div
                          key={conv.id}
                          role="button"
                          onClick={() => handleSelect(conv.id)}
                          onMouseEnter={() => setHoveredConversation(conv.id)}
                          className={cn(
                            "group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors",
                            hoveredConversation === conv.id
                              ? "bg-accent"
                              : "hover:bg-accent/50"
                          )}
                        >
                          <div className="flex items-center gap-3 min-w-0 flex-1">
                            <MessageSquare className="h-4 w-4 text-muted-foreground shrink-0" />
                            <div className="min-w-0 flex-1">
                              <div className="text-sm font-medium truncate">
                                {conv.title || "New Conversation"}
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {format(new Date(conv.updatedAt), "MMM d")}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7"
                              onClick={(e) => {
                                e.stopPropagation()
                                // Edit functionality placeholder
                              }}
                            >
                              <Pencil className="h-3 w-3" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7 text-destructive hover:text-destructive"
                              onClick={(e) => {
                                e.stopPropagation()
                                deleteConversation(conv.id)
                              }}
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  ))
                )}
              </div>
            </ScrollArea>
          </div>

          {/* Right: Conversation Preview */}
          <div className="w-1/2 flex flex-col bg-muted/30">
            {previewConversation ? (
              <>
                <div className="p-4 border-b bg-background">
                  <h3 className="font-semibold truncate">
                    {previewConversation.title || "New Conversation"}
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    {format(new Date(previewConversation.updatedAt), "MMMM d, yyyy 'at' h:mm a")}
                  </p>
                </div>
                <ScrollArea className="flex-1 p-4">
                  {previewConversation.messages && previewConversation.messages.length > 0 ? (
                    <div className="space-y-4">
                      {previewConversation.messages.slice(0, 10).map((msg, idx) => (
                        <div key={idx} className={cn(
                          "p-3 rounded-lg text-sm",
                          msg.role === "user"
                            ? "bg-primary/10 ml-4"
                            : "bg-background mr-4"
                        )}>
                          <div className="text-xs font-medium text-muted-foreground mb-1">
                            {msg.role === "user" ? "You" : "Assistant"}
                          </div>
                          <div className="line-clamp-4 whitespace-pre-wrap">
                            {msg.content}
                          </div>
                        </div>
                      ))}
                      {previewConversation.messages.length > 10 && (
                        <div className="text-center text-xs text-muted-foreground">
                          + {previewConversation.messages.length - 10} more messages
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center text-muted-foreground py-12">
                      No messages yet.
                    </div>
                  )}
                </ScrollArea>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-20" />
                  <p>Hover over a conversation to preview</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
