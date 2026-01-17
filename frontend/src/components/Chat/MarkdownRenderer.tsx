import { memo } from "react"
import ReactMarkdown from "react-markdown"
import { PrismLight as SyntaxHighlighter } from "react-syntax-highlighter"
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism"
import remarkGfm from "remark-gfm"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import "katex/dist/katex.min.css"

// Import specific languages to reduce bundle size if needed.
// For now, using PrismLight with default languages or importing common ones.
import ts from "react-syntax-highlighter/dist/esm/languages/prism/typescript"
import js from "react-syntax-highlighter/dist/esm/languages/prism/javascript"
import python from "react-syntax-highlighter/dist/esm/languages/prism/python"
import bash from "react-syntax-highlighter/dist/esm/languages/prism/bash"
import json from "react-syntax-highlighter/dist/esm/languages/prism/json"
import sql from "react-syntax-highlighter/dist/esm/languages/prism/sql"
import markdown from "react-syntax-highlighter/dist/esm/languages/prism/markdown"

SyntaxHighlighter.registerLanguage("typescript", ts)
SyntaxHighlighter.registerLanguage("javascript", js)
SyntaxHighlighter.registerLanguage("python", python)
SyntaxHighlighter.registerLanguage("bash", bash)
SyntaxHighlighter.registerLanguage("json", json)
SyntaxHighlighter.registerLanguage("sql", sql)
SyntaxHighlighter.registerLanguage("markdown", markdown)

interface MarkdownRendererProps {
    content: string
}

const MarkdownRenderer = memo(({ content }: MarkdownRendererProps) => {
    return (
        <div className="prose prose-neutral dark:prose-invert max-w-none
      prose-p:leading-relaxed prose-pre:p-0 prose-pre:bg-transparent
      prose-code:text-primary prose-code:bg-muted/50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-md prose-code:before:content-none prose-code:after:content-none
      prose-headings:font-semibold prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg
      prose-ul:my-2 prose-ol:my-2 prose-li:my-0.5
      prose-blockquote:border-l-4 prose-blockquote:border-primary/50 prose-blockquote:pl-4 prose-blockquote:italic
      prose-img:rounded-lg prose-img:shadow-md
    ">
            <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
                components={{
                    code({ node, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || "")
                        const isInline = !match

                        if (isInline) {
                            return (
                                <code className={className} {...props}>
                                    {children}
                                </code>
                            )
                        }

                        const { ref, ...rest } = props as any

                        return (
                            <div className="rounded-lg overflow-hidden border border-border/50 bg-[#282c34] my-4 shadow-sm">
                                <div className="flex items-center justify-between px-3 py-1.5 bg-muted/20 border-b border-border/50">
                                    <span className="text-xs font-medium text-muted-foreground uppercase">
                                        {match[1]}
                                    </span>
                                </div>
                                <SyntaxHighlighter
                                    style={oneDark as any}
                                    language={match[1]}
                                    PreTag="div"
                                    customStyle={{
                                        margin: 0,
                                        padding: "1rem",
                                        background: "transparent",
                                        fontSize: "0.875rem", // text-sm
                                        lineHeight: "1.5",
                                    }}
                                    wrapLines={true}
                                    wrapLongLines={true}
                                    {...(rest as any)}
                                >
                                    {String(children).replace(/\n$/, "")}
                                </SyntaxHighlighter>
                            </div>
                        )
                    },
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    )
})

MarkdownRenderer.displayName = "MarkdownRenderer"

export { MarkdownRenderer }
