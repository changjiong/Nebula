import { CheckCircle2, ChevronDown, ChevronUp, Loader2, Search, Globe, FileText, Zap } from "lucide-react"
import { useMemo, useState } from "react"

import type { ThinkingStep } from "@/stores/chatStore"
import { useChatStore } from "@/stores/chatStore"
import { cn } from "@/lib/utils"

interface ThinkingMessageProps {
  steps: ThinkingStep[]
  currentStep?: number
  totalSteps?: number
}

interface GroupedStep {
  type: "group" | "step"
  id: string
  title?: string
  description?: string
  steps?: ThinkingStep[]
  step?: ThinkingStep
}

// 获取子项图标
const getSubItemIcon = (type: string, title: string) => {
  if (type === "search-result" || title.includes("搜索")) {
    return <Search className="w-3.5 h-3.5 text-muted-foreground" />
  }
  if (type === "api-call" || title.includes("浏览") || title.includes("访问")) {
    return <Globe className="w-3.5 h-3.5 text-muted-foreground" />
  }
  if (type === "file-operation" || title.includes("文件") || title.includes("创建") || title.includes("编辑")) {
    return <FileText className="w-3.5 h-3.5 text-muted-foreground" />
  }
  return <Zap className="w-3.5 h-3.5 text-muted-foreground" />
}

// 单个分组任务卡片
function TaskGroup({
  title,
  description,
  steps,
  isCompleted,
  isInProgress,
}: {
  title: string
  description?: string
  steps: ThinkingStep[]
  isCompleted: boolean
  isInProgress: boolean
}) {
  const [isExpanded, setIsExpanded] = useState(true)
  const { openCanvas } = useChatStore()

  return (
    <div className="space-y-2">
      {/* 标题行 */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-start gap-2 w-full text-left group"
      >
        {/* 状态指示器 */}
        {isCompleted ? (
          <CheckCircle2 className="w-4 h-4 text-muted-foreground mt-0.5 shrink-0" />
        ) : isInProgress ? (
          <Loader2 className="w-4 h-4 animate-spin text-muted-foreground mt-0.5 shrink-0" />
        ) : (
          <div className="w-4 h-4 rounded-full border-2 border-muted-foreground/40 mt-0.5 shrink-0" />
        )}

        {/* 标题和描述 */}
        <div className="flex-1 min-w-0">
          <span className="text-sm font-medium text-foreground">{title}</span>
          {description && (
            <p className="text-sm text-muted-foreground mt-0.5 line-clamp-2">
              {description}
            </p>
          )}
        </div>

        {/* 展开/折叠箭头 */}
        <ChevronDown
          className={cn(
            "w-4 h-4 text-muted-foreground shrink-0 transition-transform mt-0.5",
            isExpanded && "rotate-180"
          )}
        />
      </button>

      {/* 子步骤列表 */}
      {isExpanded && steps.length > 0 && (
        <div className="ml-6 space-y-1.5">
          {steps.map((step) => (
            <div key={step.id}>
              {/* 主步骤 */}
              {step.content && (
                <div className="flex items-center gap-2 py-1.5 px-3 rounded-lg bg-muted/50 text-sm">
                  {getSubItemIcon("text", step.title)}
                  <span className="text-muted-foreground truncate">
                    {step.content}
                  </span>
                </div>
              )}

              {/* 子项列表 */}
              {step.subItems?.map((subItem) => (
                <div
                  key={subItem.id}
                  className={cn(
                    "flex items-center gap-2 py-1.5 px-3 rounded-lg bg-muted/50 text-sm mt-1.5",
                    subItem.previewable && "cursor-pointer hover:bg-muted/80 transition-colors"
                  )}
                  onClick={subItem.previewable ? () => openCanvas(subItem) : undefined}
                  onKeyDown={
                    subItem.previewable
                      ? (e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          openCanvas(subItem)
                        }
                      }
                      : undefined
                  }
                  role={subItem.previewable ? "button" : undefined}
                  tabIndex={subItem.previewable ? 0 : undefined}
                >
                  {subItem.icon ? (
                    <img src={subItem.icon} alt="" className="w-3.5 h-3.5 rounded-sm object-cover" />
                  ) : (
                    getSubItemIcon(subItem.type, subItem.title)
                  )}
                  <span className="text-muted-foreground truncate flex-1">
                    {subItem.title}
                  </span>
                  {subItem.source && (
                    <span className="text-xs text-muted-foreground/70 truncate max-w-[200px]">
                      {subItem.source}
                    </span>
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// 独立步骤（无分组）
function StandaloneStep({ step }: { step: ThinkingStep }) {
  const [isExpanded, setIsExpanded] = useState(true)
  const { openCanvas } = useChatStore()
  const hasContent = step.content || (step.subItems && step.subItems.length > 0)

  return (
    <div className="space-y-2">
      {/* 标题行 */}
      <button
        type="button"
        onClick={() => hasContent && setIsExpanded(!isExpanded)}
        className={cn(
          "flex items-start gap-2 w-full text-left",
          hasContent && "cursor-pointer"
        )}
      >
        {/* 状态指示器 */}
        {step.status === "completed" ? (
          <CheckCircle2 className="w-4 h-4 text-muted-foreground mt-0.5 shrink-0" />
        ) : step.status === "in-progress" ? (
          <Loader2 className="w-4 h-4 animate-spin text-muted-foreground mt-0.5 shrink-0" />
        ) : (
          <div className="w-4 h-4 rounded-full border-2 border-muted-foreground/40 mt-0.5 shrink-0" />
        )}

        {/* 标题 */}
        <span className="text-sm font-medium text-foreground flex-1">
          {step.title}
        </span>

        {/* 展开/折叠箭头 */}
        {hasContent && (
          <ChevronDown
            className={cn(
              "w-4 h-4 text-muted-foreground shrink-0 transition-transform mt-0.5",
              isExpanded && "rotate-180"
            )}
          />
        )}
      </button>

      {/* 内容 */}
      {isExpanded && hasContent && (
        <div className="ml-6 space-y-1.5">
          {step.content && (
            <div className="flex items-center gap-2 py-1.5 px-3 rounded-lg bg-muted/50 text-sm">
              {getSubItemIcon("text", step.title)}
              <span className="text-muted-foreground truncate">
                {step.content}
              </span>
            </div>
          )}

          {step.subItems?.map((subItem) => (
            <div
              key={subItem.id}
              className={cn(
                "flex items-center gap-2 py-1.5 px-3 rounded-lg bg-muted/50 text-sm",
                subItem.previewable && "cursor-pointer hover:bg-muted/80 transition-colors"
              )}
              onClick={subItem.previewable ? () => openCanvas(subItem) : undefined}
              onKeyDown={
                subItem.previewable
                  ? (e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      openCanvas(subItem)
                    }
                  }
                  : undefined
              }
              role={subItem.previewable ? "button" : undefined}
              tabIndex={subItem.previewable ? 0 : undefined}
            >
              {subItem.icon ? (
                <img src={subItem.icon} alt="" className="w-3.5 h-3.5 rounded-sm object-cover" />
              ) : (
                getSubItemIcon(subItem.type, subItem.title)
              )}
              <span className="text-muted-foreground truncate flex-1">
                {subItem.title}
              </span>
              {subItem.source && (
                <span className="text-xs text-muted-foreground/70 truncate max-w-[200px]">
                  {subItem.source}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export function ThinkingMessage({
  steps,
}: ThinkingMessageProps) {
  // 按分组组织步骤
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

  if (steps.length === 0) return null

  return (
    <div className="my-4 space-y-4">
      {groupedSteps.map((group) => {
        if (group.type === "group") {
          const allCompleted = group.steps!.every((s) => s.status === "completed")
          const anyInProgress = group.steps!.some((s) => s.status === "in-progress")

          return (
            <TaskGroup
              key={group.id}
              title={group.title!}
              description={group.description}
              steps={group.steps!}
              isCompleted={allCompleted}
              isInProgress={anyInProgress}
            />
          )
        }

        return <StandaloneStep key={group.id} step={group.step!} />
      })}
    </div>
  )
}
