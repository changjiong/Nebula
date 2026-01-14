import { ChevronDown, History, MoreHorizontal, MessageSquare } from "lucide-react"
import { useState } from "react"
import { HistoryModal } from "@/components/Chat/HistoryModal"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubItem,
  SidebarMenuSubButton,
  useSidebar,
} from "@/components/ui/sidebar"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"

export function ConversationList() {
  const conversations = useChatStore((state) => state.conversations)
  const currentConversationId = useChatStore(
    (state) => state.currentConversationId,
  )
  const switchConversation = useChatStore((state) => state.switchConversation)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isOpen, setIsOpen] = useState(true)
  const { state } = useSidebar()
  const isCollapsed = state === "collapsed"

  if (conversations.length === 0) {
    return null
  }

  // Limit displayed items
  const MAX_ITEMS = 8
  const displayConversations = conversations.slice(0, MAX_ITEMS)
  const hasMore = conversations.length > MAX_ITEMS

  // When collapsed, show only the History icon as a group indicator
  if (isCollapsed) {
    return (
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton onClick={() => setIsModalOpen(true)} tooltip="History">
            <History className="size-4" />
          </SidebarMenuButton>
        </SidebarMenuItem>
        <HistoryModal open={isModalOpen} onOpenChange={setIsModalOpen} />
      </SidebarMenu>
    )
  }

  return (
    <>
      <SidebarMenu>
        <Collapsible open={isOpen} onOpenChange={setIsOpen} className="group/collapsible">
          <SidebarMenuItem>
            <CollapsibleTrigger asChild>
              <SidebarMenuButton tooltip="History">
                <History className="size-4" />
                <span>History</span>
                <ChevronDown className="ml-auto size-4 transition-transform group-data-[state=open]/collapsible:rotate-180" />
              </SidebarMenuButton>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <SidebarMenuSub>
                {displayConversations.map((conv) => (
                  <SidebarMenuSubItem key={conv.id}>
                    <SidebarMenuSubButton
                      onClick={() => {
                        console.log("Switching to conversation:", conv.id)
                        switchConversation(conv.id)
                      }}
                      isActive={currentConversationId === conv.id}
                      className="text-xs"
                    >
                      <MessageSquare className="size-3 shrink-0" />
                      <span
                        className={cn(
                          "truncate",
                          currentConversationId === conv.id && "font-semibold",
                        )}
                      >
                        {conv.title || "New Conversation"}
                      </span>
                    </SidebarMenuSubButton>
                  </SidebarMenuSubItem>
                ))}

                {hasMore && (
                  <SidebarMenuSubItem>
                    <SidebarMenuSubButton
                      onClick={() => setIsModalOpen(true)}
                      className="text-xs text-muted-foreground"
                    >
                      <MoreHorizontal className="size-3 shrink-0" />
                      <span>+{conversations.length - MAX_ITEMS} more</span>
                    </SidebarMenuSubButton>
                  </SidebarMenuSubItem>
                )}
              </SidebarMenuSub>
            </CollapsibleContent>
          </SidebarMenuItem>
        </Collapsible>
      </SidebarMenu>

      <HistoryModal open={isModalOpen} onOpenChange={setIsModalOpen} />
    </>
  )
}
