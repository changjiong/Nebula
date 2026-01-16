/**
 * Manage Models Dialog
 * Allows users to select which models to enable from the available list
 * Similar to CherryStudio's model management dialog
 */

import {
  Check,
  ChevronDown,
  ChevronRight,
  Plus,
  RefreshCw,
  Search,
} from "lucide-react"
import { useMemo, useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"

// Model with enabled flag
export interface ModelItem {
  id: string
  name: string
  group?: string
  is_enabled: boolean
  is_custom?: boolean
}

interface ManageModelsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  providerName: string
  models: ModelItem[]
  onToggleModel: (modelId: string) => void
  onRefresh?: () => void
  isRefreshing?: boolean
  onSelectAll?: () => void
  onClearAll?: () => void
}

// Model categories for filter tabs (based on CherryStudio)
const CATEGORIES = [
  { id: "all", label: "全部" },
  { id: "reasoning", label: "推理" },
  { id: "vision", label: "视觉" },
  { id: "online", label: "联网" },
  { id: "free", label: "免费" },
  { id: "embedding", label: "嵌入" },
  { id: "rerank", label: "重排" },
  { id: "tool", label: "工具" },
] as const

export function ManageModelsDialog({
  open,
  onOpenChange,
  providerName,
  models,
  onToggleModel,
  onRefresh,
  isRefreshing = false,
  onSelectAll,
  onClearAll,
}: ManageModelsDialogProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(
    new Set(["all"]),
  )

  // Group models by prefix (e.g., qwen-coder, qwen-max, etc.)
  const groupedModels = useMemo(() => {
    const groups: Record<string, ModelItem[]> = {}

    models.forEach((model) => {
      const groupName = model.group || getModelGroup(model.id)
      if (!groups[groupName]) {
        groups[groupName] = []
      }
      groups[groupName].push(model)
    })

    return groups
  }, [models])

  // Filter models by search query
  const filteredGroups = useMemo(() => {
    if (!searchQuery) return groupedModels

    const filtered: Record<string, ModelItem[]> = {}
    Object.entries(groupedModels).forEach(([group, groupModels]) => {
      const matchingModels = groupModels.filter(
        (model) =>
          model.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          model.name.toLowerCase().includes(searchQuery.toLowerCase()),
      )
      if (matchingModels.length > 0) {
        filtered[group] = matchingModels
      }
    })
    return filtered
  }, [groupedModels, searchQuery])

  const toggleGroup = (group: string) => {
    setExpandedGroups((prev) => {
      const next = new Set(prev)
      if (next.has(group)) {
        next.delete(group)
      } else {
        next.add(group)
      }
      return next
    })
  }

  const enabledCount = models.filter((m) => m.is_enabled).length

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>{providerName} 模型</DialogTitle>
        </DialogHeader>

        {/* Search and Actions */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索模型 ID 或名称"
              className="pl-9"
              autoComplete="off"
            />
          </div>
          <Button
            variant="outline"
            size="icon"
            onClick={onRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw
              className={`size-4 ${isRefreshing ? "animate-spin" : ""}`}
            />
          </Button>
        </div>

        {/* Category Tabs */}
        <div className="flex gap-4 border-b overflow-x-auto pb-2">
          {CATEGORIES.map((cat) => (
            <button
              type="button"
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`text-sm whitespace-nowrap ${
                selectedCategory === cat.id
                  ? "text-primary font-medium"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Model List */}
        <ScrollArea className="h-[400px] pr-4">
          <div className="space-y-2">
            {Object.entries(filteredGroups).map(([group, groupModels]) => (
              <div key={group} className="space-y-1">
                {/* Group Header */}
                <button
                  type="button"
                  onClick={() => toggleGroup(group)}
                  className="flex items-center gap-2 w-full py-2 px-2 rounded-md bg-muted/50 hover:bg-muted"
                >
                  {expandedGroups.has(group) ? (
                    <ChevronDown className="size-4" />
                  ) : (
                    <ChevronRight className="size-4" />
                  )}
                  <span className="font-medium text-sm">{group}</span>
                  <span className="text-xs text-muted-foreground bg-primary/10 px-1.5 py-0.5 rounded">
                    {groupModels.filter((m) => m.is_enabled).length}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="ml-auto h-6"
                    onClick={(e) => {
                      e.stopPropagation()
                      // Add all models in group
                      groupModels.forEach((m) => {
                        if (!m.is_enabled) onToggleModel(m.id)
                      })
                    }}
                  >
                    <Plus className="size-3" />
                  </Button>
                </button>

                {/* Group Models */}
                {expandedGroups.has(group) && (
                  <div className="ml-6 space-y-1">
                    {groupModels.map((model) => (
                      <div
                        key={model.id}
                        className="flex items-center justify-between py-2 px-3 rounded-md hover:bg-muted/30"
                      >
                        <div className="flex items-center gap-2">
                          <div className="size-6 rounded bg-muted flex items-center justify-center text-xs font-medium">
                            {model.name.charAt(0).toUpperCase()}
                          </div>
                          <span className="text-sm">{model.name}</span>
                          {model.is_custom && (
                            <span className="text-xs text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
                              自定义
                            </span>
                          )}
                        </div>
                        <Button
                          variant={model.is_enabled ? "default" : "ghost"}
                          size="sm"
                          className="h-6 w-6 p-0"
                          onClick={() => onToggleModel(model.id)}
                        >
                          {model.is_enabled ? (
                            <Check className="size-3" />
                          ) : (
                            <Plus className="size-3" />
                          )}
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {Object.keys(filteredGroups).length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                {searchQuery ? "没有找到匹配的模型" : "暂无可用模型"}
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Footer */}
        <div className="flex justify-between items-center pt-2 border-t">
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              已选择 {enabledCount} / {models.length} 个模型
            </span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={onSelectAll}
                disabled={!onSelectAll}
              >
                全选
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={onClearAll}
                disabled={!onClearAll || enabledCount === 0}
              >
                清空
              </Button>
            </div>
          </div>
          <Button onClick={() => onOpenChange(false)}>完成</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

/**
 * Extract group name from model ID
 * e.g., "qwen-max-0428" -> "qwen-max"
 */
function getModelGroup(modelId: string): string {
  // Common patterns: name-variant-date, name-variant
  const parts = modelId.split("-")

  // If last part looks like a date, remove it
  if (parts.length > 2 && /^\d{4,}/.test(parts[parts.length - 1])) {
    parts.pop()
  }

  // Keep first 2 parts as group name, or all if less
  if (parts.length <= 2) {
    return modelId
  }

  return parts.slice(0, 2).join("-")
}
