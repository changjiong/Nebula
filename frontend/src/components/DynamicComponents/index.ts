// Dynamic Components Registry
// Import all components

import { ActionButtons } from "./ActionButtons"
import { CandidateList } from "./CandidateList"
import { ComponentRenderer, registerComponent } from "./ComponentRenderer"
import { DataTable } from "./DataTable"
import { EntityCard } from "./EntityCard"
import { MarkdownContent } from "./MarkdownContent"
import { RadarChart } from "./RadarChart"
import { RelationGraph } from "./RelationGraph"
import { ScoreCard } from "./ScoreCard"
import { TreeView } from "./TreeView"

// Register all components
registerComponent("entity_card", EntityCard)
registerComponent("customer_card", EntityCard) // Alias
registerComponent("score_card", ScoreCard)
registerComponent("summary_card", ScoreCard) // Alias
registerComponent("data_table", DataTable)
registerComponent("comparison_table", DataTable) // Alias
registerComponent("candidate_list", CandidateList)
registerComponent("relation_graph", RelationGraph)
registerComponent("tree_view", TreeView)
registerComponent("markdown_content", MarkdownContent)
registerComponent("action_buttons", ActionButtons)
registerComponent("radar_chart", RadarChart)

// Export
export { ComponentRenderer, registerComponent }
export {
  EntityCard,
  ScoreCard,
  DataTable,
  CandidateList,
  RelationGraph,
  TreeView,
  MarkdownContent,
  ActionButtons,
  RadarChart,
}
