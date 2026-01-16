/**
 * MarkdownContent - Rich Text / Report Rendering
 *
 * Renders markdown content with support for common elements.
 */

import { FileText } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface MarkdownContentProps {
  data: {
    content: string
    title?: string
  }
  config?: {
    showTitle?: boolean
    maxHeight?: number
  }
}

// Simple markdown parser for basic formatting
function parseMarkdown(content: string): string {
  const html = content
    // Headers
    .replace(
      /^### (.*$)/gim,
      '<h3 class="text-lg font-semibold mt-4 mb-2">$1</h3>',
    )
    .replace(
      /^## (.*$)/gim,
      '<h2 class="text-xl font-semibold mt-5 mb-2">$1</h2>',
    )
    .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-6 mb-3">$1</h1>')
    // Bold
    .replace(/\*\*(.*?)\*\*/gim, "<strong>$1</strong>")
    // Italic
    .replace(/\*(.*?)\*/gim, "<em>$1</em>")
    // Code blocks
    .replace(
      /```([\s\S]*?)```/gim,
      '<pre class="bg-muted p-3 rounded-md overflow-x-auto my-2"><code>$1</code></pre>',
    )
    // Inline code
    .replace(
      /`(.*?)`/gim,
      '<code class="bg-muted px-1 py-0.5 rounded text-sm">$1</code>',
    )
    // Unordered lists
    .replace(/^\s*[-*+]\s(.*)$/gim, '<li class="ml-4">$1</li>')
    // Ordered lists
    .replace(/^\s*\d+\.\s(.*)$/gim, '<li class="ml-4 list-decimal">$1</li>')
    // Line breaks
    .replace(/\n\n/gim, '</p><p class="my-2">')
    .replace(/\n/gim, "<br />")
    // Links
    .replace(
      /\[([^\]]+)\]\(([^)]+)\)/gim,
      '<a href="$2" class="text-primary hover:underline" target="_blank" rel="noopener noreferrer">$1</a>',
    )

  return `<div class="prose dark:prose-invert max-w-none"><p class="my-2">${html}</p></div>`
}

export function MarkdownContent({ data, config }: MarkdownContentProps) {
  const showTitle = config?.showTitle ?? true
  const maxHeight = config?.maxHeight

  if (!data?.content) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-muted-foreground text-sm">暂无内容</p>
        </CardContent>
      </Card>
    )
  }

  const htmlContent = parseMarkdown(data.content)

  return (
    <Card>
      {showTitle && data.title && (
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            {data.title}
          </CardTitle>
        </CardHeader>
      )}
      <CardContent className={showTitle && data.title ? "pt-0" : "pt-6"}>
        <div
          className={maxHeight ? "overflow-y-auto" : ""}
          style={maxHeight ? { maxHeight: `${maxHeight}px` } : {}}
          // biome-ignore lint/security/noDangerouslySetInnerHtml: Renders markdown content
          dangerouslySetInnerHTML={{ __html: htmlContent }}
        />
      </CardContent>
    </Card>
  )
}
