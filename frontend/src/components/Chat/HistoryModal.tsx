import { format } from "date-fns"
import { MessageSquare, Search, Trash2 } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
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

  const filteredConversations = conversations.filter((conv) =>
    (conv.title || "New Conversation")
      .toLowerCase()
      .includes(searchQuery.toLowerCase()),
  )

  const handleSelect = (id: string) => {
    switchConversation(id)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl h-[80vh] flex flex-col p-0 gap-0 overflow-hidden">
        <DialogHeader className="p-4 border-b">
          <DialogTitle>History</DialogTitle>
          <div className="relative mt-2">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search history..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8"
            />
          </div>
        </DialogHeader>
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-2">
            {filteredConversations.length === 0 ? (
              <div className="text-center text-muted-foreground py-8">
                No conversations found.
              </div>
            ) : (
              filteredConversations.map((conv) => (
                <HoverCard key={conv.id} openDelay={200}>
                  <HoverCardTrigger asChild>
                    <div
                      role="button"
                      onClick={() => handleSelect(conv.id)}
                      className="flex items-center justify-between p-3 rounded-lg border hover:bg-accent cursor-pointer group transition-colors"
                    >
                      <div className="flex items-center gap-3 overflow-hidden">
                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                          <MessageSquare className="h-4 w-4 text-primary" />
                        </div>
                        <div className="flex flex-col min-w-0">
                          <span className="font-medium truncate">
                            {conv.title || "New Conversation"}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {format(
                              new Date(conv.updatedAt),
                              "MMM d, yyyy h:mm a",
                            )}
                          </span>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteConversation(conv.id)
                        }}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </HoverCardTrigger>
                  <HoverCardContent side="right" align="start" className="w-80">
                    <div className="space-y-2">
                      <h4 className="text-sm font-semibold">Preview</h4>
                      {/* Ideally we would show the last message content here, but we might not have it in the summary list. warning: 'messages' might be loaded async. assuming we have title for now. */}
                      <p className="text-sm text-muted-foreground line-clamp-6">
                        {conv.title}
                        {/* Placeholder for content preview if available */}
                      </p>
                    </div>
                  </HoverCardContent>
                </HoverCard>
              ))
            )}
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
