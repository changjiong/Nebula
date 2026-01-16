import { Handle, Position } from "@xyflow/react"
import { Database } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface TableNodeProps {
  data: {
    label: string
    fields: Array<{ name: string; type: string }>
  }
}

export function TableNode({ data }: TableNodeProps) {
  return (
    <div className="w-[200px]">
      <Handle type="target" position={Position.Left} />
      <Handle type="source" position={Position.Right} />

      <Card className="border-blue-500/50">
        <CardHeader className="p-3 bg-blue-50/10 border-b">
          <CardTitle className="text-sm flex items-center gap-2">
            <Database className="w-3 h-3 text-blue-500" />
            {data.label}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <ul className="text-xs">
            {data.fields.map((field, i) => (
              <li
                key={i}
                className="p-2 border-b last:border-0 flex justify-between"
              >
                <span>{field.name}</span>
                <span className="text-muted-foreground opacity-70">
                  {field.type}
                </span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
