import { Link as RouterLink } from "@tanstack/react-router"
import {
  BrainCircuit,
  Briefcase,
  Database,
  ListTodo,
  LogOut,
  Monitor,
  Moon,
  Settings,
  Sun,
  Wrench,
} from "lucide-react"

import { useTheme } from "@/components/theme-provider"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuPortal,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import { getInitials } from "@/utils"

export function User({ user }: { user: any }) {
  const { logout } = useAuth()
  const { isMobile, setOpenMobile } = useSidebar()
  const { setTheme, theme } = useTheme()

  if (!user) return null

  const handleMenuClick = () => {
    if (isMobile) {
      setOpenMobile(false)
    }
  }

  const handleLogout = async () => {
    logout()
  }

  const themeOptions = [
    { value: "light", label: "Light", icon: Sun },
    { value: "dark", label: "Dark", icon: Moon },
    { value: "system", label: "System", icon: Monitor },
  ]

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground justify-start"
              data-testid="user-menu"
              tooltip={user?.email}
            >
              <Avatar className="size-8 shrink-0">
                <AvatarImage
                  src={
                    user?.avatar_url
                      ? `${import.meta.env.VITE_API_URL}${user.avatar_url}`
                      : undefined
                  }
                  alt={user?.full_name || "User"}
                />
                <AvatarFallback className="bg-zinc-600 text-white text-xs">
                  {getInitials(user?.full_name || "User")}
                </AvatarFallback>
              </Avatar>
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-52 rounded-xl shadow-lg"
            side="top"
            align="start"
            sideOffset={8}
          >
            {/* Header: Avatar + Email */}
            <div className="flex items-center gap-3 p-3">
              <Avatar className="size-10">
                <AvatarImage
                  src={
                    user?.avatar_url
                      ? `${import.meta.env.VITE_API_URL}${user.avatar_url}`
                      : undefined
                  }
                  alt={user?.full_name || "User"}
                />
                <AvatarFallback className="bg-zinc-600 text-white">
                  {getInitials(user?.full_name || "User")}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user?.email}</p>
              </div>
            </div>

            <DropdownMenuSeparator />

            {/* Settings */}
            <RouterLink to="/settings" onClick={handleMenuClick}>
              <DropdownMenuItem className="cursor-pointer">
                <Settings className="mr-3 h-4 w-4" />
                Settings
              </DropdownMenuItem>
            </RouterLink>

            {/* Appearance - Sub-menu that opens to the RIGHT */}
            <DropdownMenuSub>
              <DropdownMenuSubTrigger className="cursor-pointer">
                <Monitor className="mr-3 h-4 w-4" />
                Appearance
              </DropdownMenuSubTrigger>
              <DropdownMenuPortal>
                <DropdownMenuSubContent>
                  {themeOptions.map((opt) => (
                    <DropdownMenuItem
                      key={opt.value}
                      onClick={() =>
                        setTheme(opt.value as "light" | "dark" | "system")
                      }
                      className="cursor-pointer"
                    >
                      <opt.icon className="mr-2 h-4 w-4" />
                      {opt.label}
                      {theme === opt.value && (
                        <span className="ml-auto text-primary">✓</span>
                      )}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuSubContent>
              </DropdownMenuPortal>
            </DropdownMenuSub>

            <DropdownMenuSeparator />

            {/* Navigation Links */}
            <RouterLink to="/agents" onClick={handleMenuClick}>
              <DropdownMenuItem className="cursor-pointer">
                <Briefcase className="mr-3 h-4 w-4" />
                Agents
              </DropdownMenuItem>
            </RouterLink>
            <RouterLink to="/tasks" onClick={handleMenuClick}>
              <DropdownMenuItem className="cursor-pointer">
                <ListTodo className="mr-3 h-4 w-4" />
                Tasks
              </DropdownMenuItem>
            </RouterLink>
            <RouterLink to="/data-standards" onClick={handleMenuClick}>
              <DropdownMenuItem className="cursor-pointer">
                <Database className="mr-3 h-4 w-4" />
                Data Standards
              </DropdownMenuItem>
            </RouterLink>
            <RouterLink to="/tools" onClick={handleMenuClick}>
              <DropdownMenuItem className="cursor-pointer">
                <Wrench className="mr-3 h-4 w-4" />
                Tools
              </DropdownMenuItem>
            </RouterLink>
            <RouterLink to="/skills" onClick={handleMenuClick}>
              <DropdownMenuItem className="cursor-pointer">
                <BrainCircuit className="mr-3 h-4 w-4" />
                Skills
              </DropdownMenuItem>
            </RouterLink>

            <DropdownMenuSeparator />

            {/* Logout */}
            <DropdownMenuItem
              onClick={handleLogout}
              className="cursor-pointer text-destructive focus:text-destructive"
            >
              <LogOut className="mr-3 h-4 w-4" />
              Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  )
}
