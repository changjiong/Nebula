import { Briefcase, Users } from "lucide-react"

import { SidebarAppearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { AgentList } from "./AgentList"
import { ConversationList } from "./ConversationList"
import { type Item, Main } from "./Main"
import { NewConversationButton } from "./NewConversationButton"
import { User } from "./User"

const baseItems: Item[] = [
  { icon: Briefcase, title: "Agents", path: "/agents" },
  { icon: Users, title: "Tasks", path: "/tasks" },
]

export function AppSidebar(): React.JSX.Element {
  const { user: currentUser } = useAuth()

  const items = currentUser?.is_superuser
    ? [...baseItems, { icon: Users, title: "Admin", path: "/admin" }]
    : baseItems

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center">
        <Logo variant="responsive" />
      </SidebarHeader>
      <SidebarContent className="px-2">
        {/* New Conversation Button */}
        <NewConversationButton />

        {/* Agent List */}
        <AgentList />

        {/* Conversation History */}
        <ConversationList />

        {/* Management Navigation */}
        <SidebarGroup className="mt-auto">
          <SidebarGroupLabel>管理</SidebarGroupLabel>
          <SidebarGroupContent>
            <Main items={items} />
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarAppearance />
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
