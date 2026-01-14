import { Bot, ChevronDown, Search } from "lucide-react"
import { useEffect, useMemo, useState } from "react"

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import { type Agent, useAgentStore } from "@/stores/agentStore"

// Category icons mapping
const categoryIcons: Record<string, string> = {
  entity_resolution: "🏢",
  risk_evaluation: "📊",
  relationship_mining: "🔗",
  marketing: "💰",
  default: "🤖",
}

// Category labels mapping
const categoryLabels: Record<string, string> = {
  entity_resolution: "主体识别",
  risk_evaluation: "风险评估",
  relationship_mining: "关系挖掘",
  marketing: "营销拓客",
  default: "其他",
}

interface AgentsByCategory {
  [category: string]: Agent[]
}

export function AgentList() {
  const userAgents = useAgentStore((state) => state.userAgents)
  const selectAgent = useAgentStore((state) => state.selectAgent)
  const loadUserAgents = useAgentStore((state) => state.loadUserAgents)

  const [searchQuery, setSearchQuery] = useState("")
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set(["default"]),
  )

  useEffect(() => {
    loadUserAgents()
  }, [loadUserAgents])

  // Filter and group agents by category
  const { filteredAgents, agentsByCategory } = useMemo(() => {
    let filtered = userAgents

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = userAgents.filter(
        (agent) =>
          agent.name.toLowerCase().includes(query) ||
          (agent.description || "").toLowerCase().includes(query),
      )
    }

    // Group by category
    const grouped: AgentsByCategory = {}
    for (const agent of filtered) {
      const category = agent.category || "default"
      if (!grouped[category]) {
        grouped[category] = []
      }
      grouped[category].push(agent)
    }

    return { filteredAgents: filtered, agentsByCategory: grouped }
  }, [userAgents, searchQuery])

  const toggleCategory = (category: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev)
      if (next.has(category)) {
        next.delete(category)
      } else {
        next.add(category)
      }
      return next
    })
  }

  if (userAgents.length === 0) {
    return null
  }

  const categories = Object.keys(agentsByCategory).sort()

  return (
    <Collapsible defaultOpen className="mt-4">
      <CollapsibleTrigger className="flex items-center gap-2 w-full px-2 py-1.5 text-sm font-medium hover:bg-accent rounded-md">
        <Bot className="h-4 w-4" />
        <span>我的 Agent</span>
        {userAgents.length > 0 && (
          <span className="ml-auto text-xs text-muted-foreground">
            {userAgents.length}
          </span>
        )}
      </CollapsibleTrigger>
      <CollapsibleContent className="mt-1 space-y-1">
        {/* Search input */}
        {userAgents.length > 3 && (
          <div className="relative px-1 mb-2">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="搜索 Agent..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 pl-8 text-xs"
            />
          </div>
        )}

        {/* Grouped agent list */}
        {filteredAgents.length > 0 ? (
          categories.map((category) => (
            <div key={category} className="mb-1">
              {/* Category header (only show if multiple categories) */}
              {categories.length > 1 && (
                <button
                  type="button"
                  onClick={() => toggleCategory(category)}
                  className="flex items-center gap-1.5 w-full px-2 py-1 text-xs text-muted-foreground hover:text-foreground"
                >
                  <ChevronDown
                    className={cn(
                      "h-3 w-3 transition-transform",
                      !expandedCategories.has(category) && "-rotate-90",
                    )}
                  />
                  <span>
                    {categoryIcons[category] || categoryIcons.default}
                  </span>
                  <span>{categoryLabels[category] || category}</span>
                  <span className="ml-auto">
                    {agentsByCategory[category].length}
                  </span>
                </button>
              )}

              {/* Agents in category */}
              {(categories.length === 1 || expandedCategories.has(category)) &&
                agentsByCategory[category].map((agent) => (
                  <button
                    type="button"
                    key={agent.id}
                    onClick={() => selectAgent(agent)}
                    className="w-full text-left cursor-pointer p-2 rounded-md text-sm flex items-start gap-2 hover:bg-accent ml-2"
                  >
                    <span className="shrink-0">
                      {agent.icon || categoryIcons[category] || "🤖"}
                    </span>
                    <div className="min-w-0">
                      <div className="font-medium truncate">{agent.name}</div>
                      {agent.description && (
                        <div className="text-xs text-muted-foreground truncate">
                          {agent.description}
                        </div>
                      )}
                    </div>
                  </button>
                ))}
            </div>
          ))
        ) : (
          <div className="px-2 py-4 text-xs text-muted-foreground text-center">
            未找到匹配的 Agent
          </div>
        )}
      </CollapsibleContent>
    </Collapsible>
  )
}
