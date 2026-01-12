import type { ReactNode } from "react"

interface ChatContainerProps {
  children: ReactNode
  rightPanel?: ReactNode
}

export function ChatContainer({ children, rightPanel }: ChatContainerProps) {
  return (
    <div className="flex h-full w-full overflow-hidden bg-background">
      <div className="flex-1 flex flex-col relative min-w-0">{children}</div>
      {rightPanel && (
        <div className="w-[400px] border-l bg-muted/30 hidden lg:flex flex-col">
          {rightPanel}
        </div>
      )}
    </div>
  )
}
