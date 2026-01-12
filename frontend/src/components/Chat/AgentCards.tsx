import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { useChatStore } from "@/stores/chatStore"

// Mock data for initial dev
const MOCK_AGENTS = [
  {
    id: "1",
    name: "Research Agent",
    description: "Helps with data analysis and research.",
    capabilities: ["Data Analysis", "Web Search"],
  },
  {
    id: "2",
    name: "Coding Agent",
    description: "Assists with code generation and debugging.",
    capabilities: ["Python", "TypeScript", "Refactoring"],
  },
]

export function AgentCards() {
  const { currentAgentId, setCurrentAgentId } = useChatStore()

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4 max-w-3xl mx-auto">
      {MOCK_AGENTS.map((agent) => (
        <Card
          key={agent.id}
          className={cn(
            "cursor-pointer hover:border-primary transition-colors",
            currentAgentId === agent.id ? "border-primary bg-primary/5" : "",
          )}
          onClick={() => setCurrentAgentId(agent.id)}
        >
          <CardHeader>
            <CardTitle className="text-base">{agent.name}</CardTitle>
            <CardDescription className="text-xs">
              {agent.description}
            </CardDescription>
          </CardHeader>
        </Card>
      ))}
    </div>
  )
}
