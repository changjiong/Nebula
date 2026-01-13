import { Briefcase, Users } from "lucide-react"

import { SidebarAppearance } from "@/components/Common/Appearance"
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
    <Sidebar>
      <SidebarHeader className="border-b">
        <div className="flex items-center gap-2 px-4 py-3">
          <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-sm">A</span>
          </div>
          <span className="font-semibold text-lg">ADTEC</span>
        </div>
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
