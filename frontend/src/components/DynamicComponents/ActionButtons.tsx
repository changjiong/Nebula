/**
 * ActionButtons - Dynamic Action Button Group
 *
 * Renders a group of action buttons based on configuration.
 * Supports different action types: inject_to_system, export, navigate.
 */

import { Download, ExternalLink, MoreHorizontal, Upload } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface ActionConfig {
  type: "inject_to_system" | "export" | "navigate" | "custom"
  label: string
  icon?: string
  params?: Record<string, any>
  variant?: "default" | "secondary" | "outline" | "ghost"
  disabled?: boolean
}

interface ActionButtonsProps {
  data: {
    actions: ActionConfig[]
  }
  config?: {
    maxVisible?: number
    size?: "default" | "sm" | "lg"
    direction?: "row" | "column"
  }
  onAction?: (action: ActionConfig) => void
}

const iconMap: Record<string, React.ElementType> = {
  download: Download,
  export: Download,
  external: ExternalLink,
  upload: Upload,
  inject: Upload,
}

export function ActionButtons({ data, config, onAction }: ActionButtonsProps) {
  const maxVisible = config?.maxVisible ?? 3
  const size = config?.size ?? "default"
  const direction = config?.direction ?? "row"

  const handleAction = (action: ActionConfig) => {
    if (onAction) {
      onAction(action)
      return
    }

    // Default action handlers
    switch (action.type) {
      case "navigate":
        if (action.params?.url) {
          window.open(action.params.url, action.params?.target || "_self")
        }
        break
      case "export":
        console.log("Export action:", action.params)
        // TODO: Implement export logic
        break
      case "inject_to_system":
        console.log("Inject to system:", action.params)
        // TODO: Implement injection logic
        break
      default:
        console.log("Custom action:", action)
    }
  }

  if (!data?.actions?.length) {
    return null
  }

  const visibleActions = data.actions.slice(0, maxVisible)
  const hiddenActions = data.actions.slice(maxVisible)

  return (
    <div
      className={`flex gap-2 ${direction === "column" ? "flex-col" : "flex-row flex-wrap"}`}
    >
      {visibleActions.map((action, idx) => {
        const IconComponent = action.icon ? iconMap[action.icon] : null

        return (
          <Button
            key={idx}
            variant={action.variant || "default"}
            size={size}
            disabled={action.disabled}
            onClick={() => handleAction(action)}
          >
            {IconComponent && <IconComponent className="h-4 w-4 mr-2" />}
            {action.label}
          </Button>
        )
      })}

      {hiddenActions.length > 0 && (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size={size}>
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {hiddenActions.map((action, idx) => (
              <DropdownMenuItem
                key={idx}
                disabled={action.disabled}
                onClick={() => handleAction(action)}
              >
                {action.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      )}
    </div>
  )
}
