import { format } from "date-fns"
import {
  Check,
  MessageSquare,
  MoreVertical,
  Pencil,
  Pin,
  PinOff,
  Search,
  Trash2,
  X,
} from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useConversations } from "@/hooks/useConversations"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"

interface HistoryModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function HistoryModal({ open, onOpenChange }: HistoryModalProps) {
  const conversations = useChatStore((state) => state.conversations)
  const {
    deleteConversation,
    updateConversation,
    loadConversation,
  } = useConversations()
  const [searchQuery, setSearchQuery] = useState("")
  const [hoveredConversation, setHoveredConversation] = useState<string | null>(
    null,
  )
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState("")

  const filteredConversations = conversations.filter((conv) =>
    (conv.title || "New Conversation")
      .toLowerCase()
      .includes(searchQuery.toLowerCase()),
  )

  // Get the hovered conversation's details for preview
  const previewConversation = conversations.find(
    (c) => c.id === hoveredConversation,
  )

  const handleSelect = async (id: string) => {
    // Load full conversation from server
    await loadConversation(id)
    onOpenChange(false)
  }

  // Group conversations by date, separating pinned ones
  const pinnedConversations = filteredConversations.filter((c) => c.isPinned)
  const unpinnedConversations = filteredConversations.filter((c) => !c.isPinned)

  const groupedConversations = unpinnedConversations.reduce<
    Record<string, typeof filteredConversations>
  >((acc, conv) => {
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

  const handleStartRename = (
    e: React.MouseEvent,
    id: string,
    currentTitle: string,
  ) => {
    e.stopPropagation()
    setEditingId(id)
    setEditTitle(currentTitle || "New Conversation")
  }

  const handleSaveRename = async (e: React.MouseEvent) => {
    e.stopPropagation()
    if (editingId) {
      await updateConversation(editingId, { title: editTitle })
      setEditingId(null)
    }
  }

  const handleCancelRename = (e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingId(null)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-full max-w-[90vw] md:max-w-[calc(75vw-12rem)] h-[80vh] flex flex-col p-0 gap-0 overflow-hidden [&>button]:hidden">
        {/* Search Header */}
        <DialogHeader className="p-4 border-b shrink-0">
          <DialogTitle className="sr-only">Search History</DialogTitle>
          <div className="relative">
            <Input
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pr-10 h-10"
              autoFocus
            />
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
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
                  <>
                    {/* Pinned Conversations */}
                    {pinnedConversations.length > 0 && (
                      <div className="mb-4">
                        <div className="px-2 py-1 text-xs font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-1">
                          <Pin className="h-3 w-3" /> Pinned
                        </div>
                        {pinnedConversations.map((conv) => (
                          // biome-ignore lint/a11y/useSemanticElements: simpler styling with div
                          <div
                            key={conv.id}
                            role="button"
                            tabIndex={0}
                            onClick={() => handleSelect(conv.id)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter" || e.key === " ") {
                                e.preventDefault()
                                handleSelect(conv.id)
                              }
                            }}
                            onMouseEnter={() => setHoveredConversation(conv.id)}
                            onMouseLeave={() => setHoveredConversation(null)}
                            className={cn(
                              "group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
                              hoveredConversation === conv.id
                                ? "bg-accent"
                                : "hover:bg-accent/50",
                            )}
                          >
                            <div className="flex items-center gap-3 min-w-0 flex-1">
                              <MessageSquare className="h-4 w-4 text-muted-foreground shrink-0" />
                              {editingId === conv.id ? (
                                // biome-ignore lint/a11y/noStaticElementInteractions: pure wrapper for stopping propagation
                                <div
                                  className="flex items-center gap-1 flex-1 min-w-0"
                                  onClick={(e) => e.stopPropagation()}
                                  onKeyDown={(e) => e.stopPropagation()}
                                >
                                  <Input
                                    value={editTitle}
                                    onChange={(e) =>
                                      setEditTitle(e.target.value)
                                    }
                                    className="h-7 text-sm"
                                    autoFocus
                                    onKeyDown={(e) => {
                                      if (e.key === "Enter")
                                        handleSaveRename(e as any)
                                      if (e.key === "Escape")
                                        handleCancelRename(e as any)
                                    }}
                                  />
                                  <Button
                                    size="icon"
                                    variant="ghost"
                                    className="h-7 w-7"
                                    onClick={handleSaveRename}
                                  >
                                    <Check className="h-4 w-4 text-green-500" />
                                  </Button>
                                  <Button
                                    size="icon"
                                    variant="ghost"
                                    className="h-7 w-7"
                                    onClick={handleCancelRename}
                                  >
                                    <X className="h-4 w-4 text-red-500" />
                                  </Button>
                                </div>
                              ) : (
                                <div className="min-w-0 flex-1">
                                  <div className="text-sm font-medium truncate">
                                    {conv.title || "New Conversation"}
                                  </div>
                                  <div className="text-xs text-muted-foreground">
                                    {format(new Date(conv.updatedAt), "MMM d")}
                                  </div>
                                </div>
                              )}
                            </div>

                            {editingId !== conv.id && (
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity data-[state=open]:opacity-100"
                                    onClick={(e) => e.stopPropagation()}
                                  >
                                    <MoreVertical className="h-4 w-4" />
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuItem
                                    onClick={(e) =>
                                      handleStartRename(e, conv.id, conv.title)
                                    }
                                  >
                                    <Pencil className="h-4 w-4 mr-2" />
                                    Rename
                                  </DropdownMenuItem>
                                  <DropdownMenuItem
                                    onClick={async (e) => {
                                      e.stopPropagation()
                                      await updateConversation(conv.id, { is_pinned: false })
                                    }}
                                  >
                                    <PinOff className="h-4 w-4 mr-2" />
                                    Unpin
                                  </DropdownMenuItem>
                                  <DropdownMenuItem
                                    className="text-destructive focus:text-destructive"
                                    onClick={async (e) => {
                                      e.stopPropagation()
                                      await deleteConversation(conv.id)
                                    }}
                                  >
                                    <Trash2 className="h-4 w-4 mr-2" />
                                    Delete
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Regular Conversations */}
                    {Object.entries(groupedConversations).map(
                      ([label, convs]) => (
                        <div key={label} className="mb-4">
                          <div className="px-2 py-1 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                            {label}
                          </div>
                          {convs.map((conv) => (
                            // biome-ignore lint/a11y/useSemanticElements: simpler styling with div
                            <div
                              key={conv.id}
                              role="button"
                              tabIndex={0}
                              onClick={() => handleSelect(conv.id)}
                              onKeyDown={(e) => {
                                if (e.key === "Enter" || e.key === " ") {
                                  e.preventDefault()
                                  handleSelect(conv.id)
                                }
                              }}
                              onMouseEnter={() =>
                                setHoveredConversation(conv.id)
                              }
                              onMouseLeave={() => setHoveredConversation(null)}
                              className={cn(
                                "group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
                                hoveredConversation === conv.id
                                  ? "bg-accent"
                                  : "hover:bg-accent/50",
                              )}
                            >
                              <div className="flex items-center gap-3 min-w-0 flex-1">
                                <MessageSquare className="h-4 w-4 text-muted-foreground shrink-0" />
                                {editingId === conv.id ? (
                                  // biome-ignore lint/a11y/noStaticElementInteractions: pure wrapper for stopping propagation
                                  <div
                                    className="flex items-center gap-1 flex-1 min-w-0"
                                    onClick={(e) => e.stopPropagation()}
                                    onKeyDown={(e) => e.stopPropagation()}
                                  >
                                    <Input
                                      value={editTitle}
                                      onChange={(e) =>
                                        setEditTitle(e.target.value)
                                      }
                                      className="h-7 text-sm"
                                      autoFocus
                                      onKeyDown={(e) => {
                                        if (e.key === "Enter")
                                          handleSaveRename(e as any)
                                        if (e.key === "Escape")
                                          handleCancelRename(e as any)
                                      }}
                                    />
                                    <Button
                                      size="icon"
                                      variant="ghost"
                                      className="h-7 w-7"
                                      onClick={handleSaveRename}
                                    >
                                      <Check className="h-4 w-4 text-green-500" />
                                    </Button>
                                    <Button
                                      size="icon"
                                      variant="ghost"
                                      className="h-7 w-7"
                                      onClick={handleCancelRename}
                                    >
                                      <X className="h-4 w-4 text-red-500" />
                                    </Button>
                                  </div>
                                ) : (
                                  <div className="min-w-0 flex-1">
                                    <div className="text-sm font-medium truncate">
                                      {conv.title || "New Conversation"}
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                      {format(
                                        new Date(conv.updatedAt),
                                        "MMM d",
                                      )}
                                    </div>
                                  </div>
                                )}
                              </div>

                              {editingId !== conv.id && (
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button
                                      variant="ghost"
                                      size="icon"
                                      className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity data-[state=open]:opacity-100"
                                      onClick={(e) => e.stopPropagation()}
                                    >
                                      <MoreVertical className="h-4 w-4" />
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent align="end">
                                    <DropdownMenuItem
                                      onClick={(e) =>
                                        handleStartRename(
                                          e,
                                          conv.id,
                                          conv.title,
                                        )
                                      }
                                    >
                                      <Pencil className="h-4 w-4 mr-2" />
                                      Rename
                                    </DropdownMenuItem>
                                    <DropdownMenuItem
                                      onClick={async (e) => {
                                        e.stopPropagation()
                                        await updateConversation(conv.id, { is_pinned: true })
                                      }}
                                    >
                                      <Pin className="h-4 w-4 mr-2" />
                                      Pin
                                    </DropdownMenuItem>
                                    <DropdownMenuItem
                                      className="text-destructive focus:text-destructive"
                                      onClick={async (e) => {
                                        e.stopPropagation()
                                        await deleteConversation(conv.id)
                                      }}
                                    >
                                      <Trash2 className="h-4 w-4 mr-2" />
                                      Delete
                                    </DropdownMenuItem>
                                  </DropdownMenuContent>
                                </DropdownMenu>
                              )}
                            </div>
                          ))}
                        </div>
                      ),
                    )}
                  </>
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
                    {format(
                      new Date(previewConversation.updatedAt),
                      "MMMM d, yyyy 'at' h:mm a",
                    )}
                  </p>
                </div>
                <ScrollArea className="flex-1 p-4">
                  {previewConversation.messages &&
                    previewConversation.messages.length > 0 ? (
                    <div className="space-y-4">
                      {previewConversation.messages
                        .slice(0, 10)
                        .map((msg, idx) => (
                          <div
                            key={idx}
                            className={cn(
                              "px-3 py-2 rounded-2xl text-sm",
                              msg.role === "user"
                                ? "bg-secondary text-secondary-foreground border border-border/50 ml-4"
                                : "bg-background mr-4",
                            )}
                          >
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
                          + {previewConversation.messages.length - 10} more
                          messages
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
