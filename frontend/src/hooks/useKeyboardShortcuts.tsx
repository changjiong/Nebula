/**
 * useKeyboardShortcuts - Global Keyboard Shortcuts Hook
 *
 * Provides keyboard shortcuts for common actions:
 * - Ctrl/Cmd + N: New conversation
 * - Ctrl/Cmd + K: Focus search (future)
 * - Escape: Close modals/panels
 */

import { useEffect } from "react"
import { useChatStore } from "@/stores/chatStore"

interface ShortcutConfig {
  key: string
  ctrl?: boolean
  meta?: boolean
  shift?: boolean
  action: () => void
  description: string
}

export function useKeyboardShortcuts() {
  const createNewConversation = useChatStore(
    (state) => state.createNewConversation,
  )

  useEffect(() => {
    const shortcuts: ShortcutConfig[] = [
      {
        key: "n",
        ctrl: true,
        action: () => {
          createNewConversation()
        },
        description: "New conversation",
      },
      {
        key: "n",
        meta: true, // For Mac
        action: () => {
          createNewConversation()
        },
        description: "New conversation (Mac)",
      },
    ]

    const handleKeyDown = (e: KeyboardEvent) => {
      // Skip if user is typing in an input or textarea
      const target = e.target as HTMLElement
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable
      ) {
        return
      }

      for (const shortcut of shortcuts) {
        const ctrlMatch = shortcut.ctrl ? e.ctrlKey : !e.ctrlKey
        const metaMatch = shortcut.meta ? e.metaKey : !e.metaKey
        const shiftMatch = shortcut.shift ? e.shiftKey : !e.shiftKey
        const keyMatch = e.key.toLowerCase() === shortcut.key.toLowerCase()

        // Allow either Ctrl or Meta for cross-platform support
        const modifierMatch =
          shortcut.ctrl || shortcut.meta
            ? (shortcut.ctrl && e.ctrlKey) || (shortcut.meta && e.metaKey)
            : ctrlMatch && metaMatch

        if (keyMatch && modifierMatch && shiftMatch) {
          e.preventDefault()
          shortcut.action()
          return
        }
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [createNewConversation])
}

/**
 * KeyboardShortcutsProvider - Component wrapper for keyboard shortcuts
 * Use this in your app layout to enable global shortcuts
 */
export function KeyboardShortcutsProvider({
  children,
}: {
  children: React.ReactNode
}) {
  useKeyboardShortcuts()
  return <>{children}</>
}
