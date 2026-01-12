import { CheckCircle2, Circle, Loader2, XCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface TaskProgressProps {
  status: "pending" | "in-progress" | "completed" | "failed"
  title: string
}

export function TaskProgress({ status, title }: TaskProgressProps) {
  return (
    <div className="flex items-center gap-2 py-2">
      {status === "pending" && (
        <Circle className="h-4 w-4 text-muted-foreground" />
      )}
      {status === "in-progress" && (
        <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      )}
      {status === "completed" && (
        <CheckCircle2 className="h-4 w-4 text-green-500" />
      )}
      {status === "failed" && <XCircle className="h-4 w-4 text-red-500" />}

      <span className="text-sm font-medium leading-none">{title}</span>

      <div className="ml-auto">
        <Badge
          variant={status === "completed" ? "default" : "outline"}
          className="text-[10px] h-5"
        >
          {status}
        </Badge>
      </div>
    </div>
  )
}
