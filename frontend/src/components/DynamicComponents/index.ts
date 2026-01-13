// Dynamic Components Registry
// Import all components
import { EntityCard } from "./EntityCard"
import { ScoreCard } from "./ScoreCard"
import { DataTable } from "./DataTable"
import { CandidateList } from "./CandidateList"
import { RelationGraph } from "./RelationGraph"
import { TreeView } from "./TreeView"
import { MarkdownContent } from "./MarkdownContent"
import { ActionButtons } from "./ActionButtons"
import { ComponentRenderer, registerComponent } from "./ComponentRenderer"

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
}

