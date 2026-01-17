import {
  CheckCircle2,
  ChevronRight,
  Code,
  Database,
  FileText,
  Globe,
  Loader2,
  Search,
  ServerCog,
  Sparkles,
  Zap,
} from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import { cn } from "@/lib/utils"
import type { ThinkingStep } from "@/stores/chatStore"
import { useChatStore } from "@/stores/chatStore"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"

interface ThinkingMessageProps {
  steps: ThinkingStep[]
}

interface GroupedStep {
  type: "group" | "step"
  id: string
  title?: string
  description?: string
  steps?: ThinkingStep[]
  step?: ThinkingStep
}

// 获取子项图标 - Helper for icons
const getSubItemIcon = (type: string, title: string) => {
  const props = { className: "w-3.5 h-3.5" }

  switch (type) {
    case "search-result":
      return <Search {...props} />
    case "browse":
      return <Globe {...props} />
    case "file-operation":
      return <FileText {...props} />
    case "mcp-call":
      return <Database {...props} />
    case "code-execution":
      return <Code {...props} />
    case "api-call":
      return <ServerCog {...props} />
  }

  const titleLower = title.toLowerCase()
  if (titleLower.includes("搜索") || titleLower.includes("search"))
    return <Search {...props} />
  if (titleLower.includes("浏览") || titleLower.includes("visit") || titleLower.includes("browse"))
    return <Globe {...props} />
  if (titleLower.includes("文件") || titleLower.includes("file") || titleLower.includes("create") || titleLower.includes("edit"))
    return <FileText {...props} />
  if (titleLower.includes("mcp") || titleLower.includes("database"))
    return <Database {...props} />
  if (titleLower.includes("code") || titleLower.includes("run") || titleLower.includes("exec"))
    return <Code {...props} />

  return <Zap {...props} />
}

function ThinkingIcon({ isAnimating }: { isAnimating: boolean }) {
  return (
    <div className={cn("relative flex items-center justify-center p-0.5")}>
      <Sparkles
        className={cn(
          "w-4 h-4 transition-colors duration-500",
          isAnimating ? "text-amber-500/80 animate-pulse" : "text-muted-foreground/60"
        )}
      />
    </div>
  )
}

function StepItem({
  icon,
  title,
  subtitle,
  status,
  onClick,
  isInteractive,
}: {
  icon: React.ReactNode
  title: string
  subtitle?: string
  status?: "pending" | "in-progress" | "completed" | "failed" // simplified status
  onClick?: () => void
  isInteractive?: boolean
}) {
  return (
    <div
      onClick={onClick}
      onKeyDown={isInteractive ? (e) => (e.key === "Enter" || e.key === " ") && onClick?.() : undefined}
      role={isInteractive ? "button" : undefined}
      tabIndex={isInteractive ? 0 : undefined}
      className={cn(
        "flex items-start gap-3 py-1.5 px-2 -ml-2 rounded-md transition-colors text-sm group/item",
        isInteractive && "hover:bg-muted/50 cursor-pointer"
      )}
    >
      <div className="mt-0.5 text-muted-foreground/70 group-hover/item:text-foreground/80 transition-colors">
        {status === "in-progress" ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin text-primary" />
        ) : status === "completed" ? (
          <CheckCircle2 className="w-3.5 h-3.5 text-green-500/70" />
        ) : (
          icon
        )}
      </div>

      <div className="flex-1 min-w-0 grid gap-0.5">
        <div className={cn(
          "font-medium leading-none truncate",
          status === "in-progress" ? "text-foreground" : "text-muted-foreground/90"
        )}>
          {title}
        </div>
        {subtitle && (
          <div className="text-xs text-muted-foreground/60 whitespace-pre-wrap break-words font-mono">
            {subtitle}
          </div>
        )}
      </div>
    </div>
  )
}

export function ThinkingMessage({ steps }: ThinkingMessageProps) {
  const [isOpen, setIsOpen] = useState(false)
  const isThinking = steps.some((s) => s.status === "in-progress")
  const { openCanvas } = useChatStore()

  // Auto-expand when thinking starts, but allow user to collapse
  // Auto-expand when thinking starts, and auto-collapse when done (Vercel style)
  useEffect(() => {
    if (isThinking) {
      if (!isOpen) setIsOpen(true)
    } else {
      // When thinking finishes, keep it open or let user decide
      // if (isOpen) setIsOpen(false) 
    }
  }, [isThinking])

  // Grouping Logic
  const groupedSteps = useMemo(() => {
    const groups: GroupedStep[] = []
    let currentGroup: GroupedStep | null = null

    steps.forEach((step) => {
      if (step.group) {
        if (
          currentGroup &&
          currentGroup.type === "group" &&
          currentGroup.title === step.group
        ) {
          currentGroup.steps!.push(step)
        } else {
          currentGroup = {
            type: "group",
            id: `group-${step.group}-${step.id}`,
            title: step.group,
            description: step.content,
            steps: [step],
          }
          groups.push(currentGroup)
        }
      } else {
        currentGroup = null
        groups.push({
          type: "step",
          id: `step-${step.id}`,
          step,
        })
      }
    })

    return groups
  }, [steps])

  const currentStatusText = useMemo(() => {
    if (!isThinking) return `Thought Process • ${steps.length} steps`

    // Find the last active step
    const activeStep = [...steps].reverse().find((s) => s.status === "in-progress")
    if (activeStep) return activeStep.title
    return "Thinking..."
  }, [isThinking, steps])

  if (steps.length === 0) return null

  return (
    <Collapsible
      open={isOpen}
      onOpenChange={setIsOpen}
      className="w-full my-4"
    >
      <CollapsibleTrigger asChild>
        <button
          type="button"
          className={cn(
            "flex items-center gap-2.5 w-full text-left group select-none py-1 rounded-md transition-colors",
            "hover:bg-muted/30"
          )}
        >
          <div className="flex items-center justify-center w-5 h-5">
            {isThinking ? (
              <Loader2 className="w-4 h-4 animate-spin text-amber-500/80" />
            ) : (
              <ThinkingIcon isAnimating={false} />
            )}
          </div>

          <span className={cn(
            "text-sm font-medium transition-colors",
            isThinking ? "text-foreground" : "text-muted-foreground"
          )}>
            {currentStatusText}
          </span>

          <ChevronRight
            className={cn(
              "w-4 h-4 text-muted-foreground/50 transition-all duration-200 ml-auto mr-1",
              isOpen && "rotate-90"
            )}
          />
        </button>
      </CollapsibleTrigger>

      <CollapsibleContent>
        <div className="relative mt-2 ml-2.5 pl-4 border-l-2 border-border/40 space-y-3 pb-2 animate-in slide-in-from-top-2 fade-in duration-200">
          {groupedSteps.map((group) => {
            if (group.type === "group") {
              // Render Group
              return (
                <div key={group.id} className="space-y-1.5">
                  <div className="text-xs font-semibold text-muted-foreground/70 uppercase tracking-wider mb-1">
                    {group.title}
                  </div>
                  {group.steps?.map(step => (
                    <div key={step.id}>
                      <StepItem
                        icon={getSubItemIcon("text", step.title)}
                        title={step.content || step.title}
                        status={step.status as any}
                      />
                      {step.subItems?.map(subItem => (
                        <div key={subItem.id} className="pl-4 mt-1 border-l border-border/30 ml-1">
                          <StepItem
                            icon={subItem.icon ? <img src={subItem.icon} className="w-3.5 h-3.5 rounded-sm" /> : getSubItemIcon(subItem.type, subItem.title)}
                            title={subItem.title}
                            subtitle={subItem.source}
                            isInteractive={!!subItem.previewable}
                            onClick={() => subItem.previewable && openCanvas(subItem)}
                          />
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              )
            }

            // Render Standalone Step
            const step = group.step!
            return (
              <div key={group.id} className="space-y-1">
                {/* If it has no content/subitems, maybe just a title line? */}
                <StepItem
                  icon={getSubItemIcon("text", step.title)}
                  title={step.title}
                  subtitle={step.content}
                  status={step.status as any}
                />
                {step.subItems?.map(subItem => (
                  <div key={subItem.id} className="pl-4 mt-1 border-l border-border/30 ml-1">
                    <StepItem
                      icon={subItem.icon ? <img src={subItem.icon} className="w-3.5 h-3.5 rounded-sm" /> : getSubItemIcon(subItem.type, subItem.title)}
                      title={subItem.title}
                      subtitle={subItem.source}
                      isInteractive={!!subItem.previewable}
                      onClick={() => subItem.previewable && openCanvas(subItem)}
                    />
                  </div>
                ))}
              </div>
            )
          })}
        </div>
      </CollapsibleContent>
    </Collapsible>
  )
}
