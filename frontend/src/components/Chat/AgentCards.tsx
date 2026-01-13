import { Bot, Code2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"

// Mock data for initial dev
const MOCK_AGENTS = [
  {
    id: "1",
    name: "Research Agent",
    description: "Helps with data analysis and research.",
    icon: Bot,
    capabilities: ["Data Analysis", "Web Search"],
  },
  {
    id: "2",
    name: "Coding Agent",
    description: "Assists with code generation and debugging.",
    icon: Code2,
    capabilities: ["Python", "TypeScript", "Refactoring"],
  },
]

export function AgentCards() {
  const { currentAgentId, setCurrentAgentId } = useChatStore()

  return (
    <div className="grid grid-cols-2 gap-3">
      {MOCK_AGENTS.map((agent) => {
        const Icon = agent.icon
        return (
          <button
            key={agent.id}
            className={cn(
              "flex flex-col items-start gap-2 p-4 rounded-xl border text-left",
              "transition-all duration-200",
              "hover:border-primary hover:bg-muted/50 hover:shadow-sm",
              currentAgentId === agent.id
                ? "border-primary bg-primary/5"
                : "border-border/50",
            )}
            onClick={() => setCurrentAgentId(agent.id)}
          >
            <div className="flex items-center gap-2 w-full">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                <Icon className="w-4 h-4 text-primary" />
              </div>
              <span className="font-medium text-sm">{agent.name}</span>
            </div>
            <p className="text-xs text-muted-foreground leading-relaxed">
              {agent.description}
            </p>
          </button>
        )
      })}
    </div>
  )
}
