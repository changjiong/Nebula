// Dynamic Components Registry
// Import all components
import { EntityCard } from "./EntityCard"
import { ScoreCard } from "./ScoreCard"
import { DataTable } from "./DataTable"
import { CandidateList } from "./CandidateList"
import { ComponentRenderer, registerComponent } from "./ComponentRenderer"

// Register all components
registerComponent("entity_card", EntityCard)
registerComponent("score_card", ScoreCard)
registerComponent("data_table", DataTable)
registerComponent("candidate_list", CandidateList)

// Export
export { ComponentRenderer, registerComponent }
export { EntityCard, ScoreCard, DataTable, CandidateList }
