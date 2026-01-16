import {
  Check,
  MessageSquare,
  MoreVertical,
  Pencil,
  Pin,
  PinOff,
  Trash2,
  X,
} from "lucide-react"
import type React from "react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { SidebarMenuSubButton } from "@/components/ui/sidebar"
import { useConversations } from "@/hooks/useConversations"
import { cn } from "@/lib/utils"
import type { Conversation } from "@/stores/chatStore"

interface SidebarConversationItemProps {
  conversation: Conversation
  isActive: boolean
  onSelect: (id: string) => void
}

export function SidebarConversationItem({
  conversation,
  isActive,
  onSelect,
}: SidebarConversationItemProps) {
  const { deleteConversation, updateConversation } = useConversations()

  const [isEditing, setIsEditing] = useState(false)
  const [editTitle, setEditTitle] = useState("")

  const handleStartRename = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsEditing(true)
    setEditTitle(conversation.title || "New Conversation")
  }

  const handleSaveRename = async (e: React.MouseEvent) => {
    e.stopPropagation()
    await updateConversation(conversation.id, { title: editTitle })
    setIsEditing(false)
  }

  const handleCancelRename = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsEditing(false)
  }

  if (isEditing) {
    return (
      <div className="flex items-center gap-1 px-2 py-1">
        <Input
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          className="h-7 text-sm px-2"
          autoFocus
          onKeyDown={(e: React.KeyboardEvent) => {
            if (e.key === "Enter") handleSaveRename(e as any)
            if (e.key === "Escape") handleCancelRename(e as any)
            e.stopPropagation()
          }}
          onClick={(e) => e.stopPropagation()}
        />
        <Button
          size="icon"
          variant="ghost"
          className="h-7 w-7 shrink-0"
          onClick={handleSaveRename}
        >
          <Check className="h-4 w-4 text-green-500" />
        </Button>
        <Button
          size="icon"
          variant="ghost"
          className="h-7 w-7 shrink-0"
          onClick={handleCancelRename}
        >
          <X className="h-4 w-4 text-red-500" />
        </Button>
      </div>
    )
  }

  return (
    <div className="group/item relative flex items-center">
      <SidebarMenuSubButton
        onClick={() => onSelect(conversation.id)}
        isActive={isActive}
        className="text-sm pr-8 cursor-pointer" // Add padding for the menu button
      >
        <MessageSquare className="size-4 shrink-0" />
        <span
          className={cn(
            "truncate flex-1 block", // Ensure full width for text
            isActive && "font-semibold",
          )}
        >
          {conversation.title || "New Conversation"}
        </span>
        {conversation.isPinned && (
          <Pin className="size-3 ml-auto shrink-0 text-muted-foreground" />
        )}
      </SidebarMenuSubButton>

      {/* Actions Menu - Absolute positioned to appear on right */}
      <div className="absolute right-1 opacity-0 group-hover/item:opacity-100 transition-opacity flex items-center bg-sidebar-accent/10 sm:bg-transparent">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
              onClick={(e) => e.stopPropagation()}
            >
              <MoreVertical className="h-3 w-3" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem onClick={handleStartRename}>
              <Pencil className="h-4 w-4 mr-2" />
              Rename
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={async (e) => {
                e.stopPropagation()
                await updateConversation(conversation.id, {
                  is_pinned: !conversation.isPinned,
                })
              }}
            >
              {conversation.isPinned ? (
                <>
                  <PinOff className="h-4 w-4 mr-2" />
                  Unpin
                </>
              ) : (
                <>
                  <Pin className="h-4 w-4 mr-2" />
                  Pin
                </>
              )}
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-destructive focus:text-destructive"
              onClick={async (e) => {
                e.stopPropagation()
                await deleteConversation(conversation.id)
              }}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}
