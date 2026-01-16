import {
  getYear,
  isAfter,
  isToday,
  isYesterday,
  startOfDay,
  subDays,
} from "date-fns"
import type { Conversation } from "@/stores/chatStore"

export type DateGroup = {
  title: string
  conversations: Conversation[]
}

export function groupConversationsByDate(
  conversations: Conversation[],
): DateGroup[] {
  const groups: Record<string, Conversation[]> = {
    Today: [],
    Yesterday: [],
    "Previous 7 Days": [],
    "Previous 30 Days": [],
  }

  // Dynamic year groups
  const yearGroups: Record<string, Conversation[]> = {}

  const now = new Date()
  const todayStart = startOfDay(now)
  const sevenDaysAgo = subDays(todayStart, 7)
  const thirtyDaysAgo = subDays(todayStart, 30)

  // Sort conversations by updatedAt desc
  const sorted = [...conversations].sort((a, b) => {
    const timeA = new Date(a.updatedAt).getTime()
    const timeB = new Date(b.updatedAt).getTime()
    return timeB - timeA
  })

  sorted.forEach((conv) => {
    const date = new Date(conv.updatedAt)

    if (isToday(date)) {
      groups.Today.push(conv)
    } else if (isYesterday(date)) {
      groups.Yesterday.push(conv)
    } else if (isAfter(date, sevenDaysAgo)) {
      groups["Previous 7 Days"].push(conv)
    } else if (isAfter(date, thirtyDaysAgo)) {
      groups["Previous 30 Days"].push(conv)
    } else {
      const year = getYear(date).toString()
      if (!yearGroups[year]) {
        yearGroups[year] = []
      }
      yearGroups[year].push(conv)
    }
  })

  const result: DateGroup[] = []

  // Add predefined groups if they have items
  if (groups.Today.length > 0)
    result.push({ title: "Today", conversations: groups.Today })
  if (groups.Yesterday.length > 0)
    result.push({ title: "Yesterday", conversations: groups.Yesterday })
  if (groups["Previous 7 Days"].length > 0)
    result.push({
      title: "Previous 7 Days",
      conversations: groups["Previous 7 Days"],
    })
  if (groups["Previous 30 Days"].length > 0)
    result.push({
      title: "Previous 30 Days",
      conversations: groups["Previous 30 Days"],
    }) // Fixed title to match key

  // Add year groups, sorted by year desc
  Object.keys(yearGroups)
    .sort((a, b) => parseInt(b, 10) - parseInt(a, 10))
    .forEach((year) => {
      result.push({ title: year, conversations: yearGroups[year] })
    })

  return result
}
