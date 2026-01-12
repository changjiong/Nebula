import { ScrollArea } from "@/components/ui/scroll-area"

interface ExecutionDetailProps {
  content: string
}

export function ExecutionDetail({ content }: ExecutionDetailProps) {
  if (!content) return null

  return (
    <ScrollArea className="h-full max-h-[200px] w-full rounded-md border p-4 bg-muted/50 mt-2">
      <pre className="text-xs font-mono whitespace-pre-wrap break-words text-muted-foreground">
        {content}
      </pre>
    </ScrollArea>
  )
}
