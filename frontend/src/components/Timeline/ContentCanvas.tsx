import { Check, Copy, ExternalLink, FileText, X } from "lucide-react"
import { useState } from "react"
import ReactMarkdown from "react-markdown"

import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import type { StepSubItem } from "@/stores/chatStore"

interface ContentCanvasProps {
  item: StepSubItem | null
  isOpen: boolean
  onClose: () => void
  className?: string
}

export function ContentCanvas({
  item,
  isOpen,
  onClose,
  className,
}: ContentCanvasProps) {
  const [copied, setCopied] = useState(false)

  if (!isOpen || !item) return null

  const handleCopy = async () => {
    if (item.content) {
      await navigator.clipboard.writeText(item.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <>
      {/* Backdrop */}
      <button
        type="button"
        className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm animate-in fade-in duration-200"
        onClick={onClose}
        aria-label="Close canvas"
      />

      {/* Canvas Panel */}
      <div
        className={cn(
          "fixed inset-y-0 right-0 z-50 w-full max-w-xl",
          "bg-background border-l shadow-2xl",
          "animate-in slide-in-from-right duration-300",
          className,
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-3 min-w-0">
            <div className="shrink-0 w-8 h-8 rounded-lg bg-muted flex items-center justify-center">
              {item.icon ? (
                <img
                  src={item.icon}
                  alt=""
                  className="w-5 h-5 rounded object-cover"
                />
              ) : (
                <FileText className="w-4 h-4 text-muted-foreground" />
              )}
            </div>
            <div className="min-w-0">
              <h3 className="font-semibold text-sm truncate">{item.title}</h3>
              {item.source && (
                <a
                  href={`https://${item.source}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 transition-colors"
                >
                  {item.source}
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            {item.content && (
              <Button
                variant="ghost"
                size="icon"
                onClick={handleCopy}
                className="h-8 w-8"
              >
                {copied ? (
                  <Check className="h-4 w-4 text-green-500" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="h-8 w-8"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Content */}
        <ScrollArea className="h-[calc(100vh-73px)]">
          <div className="p-6">
            {item.content ? (
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown>{item.content}</ReactMarkdown>
              </div>
            ) : (
              <div className="text-center text-muted-foreground py-12">
                <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>没有可展示的内容</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>
    </>
  )
}
