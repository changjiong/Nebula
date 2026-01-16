import {
  Code,
  Database,
  ExternalLink,
  FileText,
  Globe,
  Search,
  ServerCog,
} from "lucide-react"

import { cn } from "@/lib/utils"
import type { StepSubItem } from "@/stores/chatStore"

interface TimelineSubItemProps {
  item: StepSubItem
  onClick?: () => void
  className?: string
}

// Manus-style icon mapping
const typeIcons = {
  "search-result": Search,
  "file-operation": FileText,
  "api-call": ServerCog,
  browse: Globe,
  "mcp-call": Database,
  "code-execution": Code,
  text: FileText,
}

export function TimelineSubItem({
  item,
  onClick,
  className,
}: TimelineSubItemProps) {
  const IconComponent = typeIcons[item.type] || FileText

  return (
    <div
      className={cn(
        "group flex items-start gap-3 p-2.5 rounded-lg bg-muted/40 border border-transparent",
        "relative", // Ensure positioning context
        className,
      )}
    >
      {/* Interactive Overlay or Container */}
      {item.previewable ? (
        <button
          type="button"
          onClick={onClick}
          className={cn(
            "absolute inset-0 w-full h-full rounded-lg cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/20",
            "hover:bg-muted/80 hover:border-border/50 transition-all duration-200",
          )}
          aria-label={`View details for ${item.title}`}
        />
      ) : null}

      {/* Icon */}
      <div className="shrink-0 w-5 h-5 rounded flex items-center justify-center bg-background border z-10 pointer-events-none">
        {item.icon ? (
          <img
            src={item.icon}
            alt=""
            className="w-4 h-4 rounded-sm object-cover"
          />
        ) : (
          <IconComponent className="w-3 h-3 text-muted-foreground" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 z-10 pointer-events-none">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium truncate">{item.title}</span>
          {item.previewable && (
            <ExternalLink className="w-3 h-3 text-muted-foreground opacity-0 group-hover:opacity-100 shrink-0 transition-opacity" />
          )}
        </div>
        {item.source && (
          <span className="text-xs text-muted-foreground truncate block">
            {item.source}
          </span>
        )}
      </div>
    </div>
  )
}
