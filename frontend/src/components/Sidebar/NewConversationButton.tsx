import { useNavigate } from "@tanstack/react-router"
import { Home, Search } from "lucide-react"
import { useState } from "react"

import { HistoryModal } from "@/components/Chat/HistoryModal"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { useChatStore } from "@/stores/chatStore"

export function NewConversationButton() {
  const resetToHome = useChatStore((state) => state.resetToHome)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const navigate = useNavigate()

  const handleHomeClick = () => {
    resetToHome()
    navigate({ to: "/" })
  }

  return (
    <>
      <SidebarMenu>
        {/* Home - creates new conversation */}
        <SidebarMenuItem>
          <SidebarMenuButton onClick={handleHomeClick} tooltip="Home">
            <Home className="size-4" />
            <span>Home</span>
          </SidebarMenuButton>
        </SidebarMenuItem>

        {/* Search - opens history modal */}
        <SidebarMenuItem>
          <SidebarMenuButton
            onClick={() => setIsModalOpen(true)}
            tooltip="Search"
          >
            <Search className="size-4" />
            <span>Search</span>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>

      <HistoryModal open={isModalOpen} onOpenChange={setIsModalOpen} />
    </>
  )
}
