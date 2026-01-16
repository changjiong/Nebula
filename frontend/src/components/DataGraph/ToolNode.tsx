import { Handle, Position } from "@xyflow/react"
import { Box } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ToolNodeProps {
  data: {
    label: string
    description?: string
  }
}

export function ToolNode({ data }: ToolNodeProps) {
  return (
    <div className="w-[250px]">
      <Handle type="target" position={Position.Left} />
      <Card className="border-purple-500 border-2">
        <CardHeader className="p-3 bg-purple-50/10">
          <CardTitle className="text-sm flex items-center gap-2">
            <Box className="w-4 h-4 text-purple-500" />
            {data.label}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-3 text-xs text-muted-foreground">
          {data.description || "No description"}
        </CardContent>
      </Card>
      <Handle type="source" position={Position.Right} />
    </div>
  )
}
