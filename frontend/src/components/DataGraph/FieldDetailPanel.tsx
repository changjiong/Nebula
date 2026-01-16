interface FieldDetail {
  id: string
  name: string
  display_name: string
  type: string
  description?: string
  is_primary_key?: boolean
  sample_values?: string[]
  table_name: string
  table_display_name: string
}

interface FieldDetailPanelProps {
  field: FieldDetail | null
  onClose: () => void
}

export function FieldDetailPanel({ field, onClose }: FieldDetailPanelProps) {
  if (!field) return null

  return (
    <div className="absolute top-4 right-4 w-80 bg-card border border-border shadow-lg rounded-lg z-10 flex flex-col overflow-hidden animate-in slide-in-from-right-10 fade-in duration-200">
      <div className="px-4 py-3 border-b border-border flex justify-between items-start bg-muted/30">
        <div>
          <h3 className="font-semibold text-sm">字段详情</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            {field.table_display_name} ({field.table_name})
          </p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="text-muted-foreground hover:text-foreground"
        >
          ✕
        </button>
      </div>

      <div className="p-4 space-y-4 text-sm max-h-[calc(100vh-200px)] overflow-y-auto">
        <div>
          <span className="text-xs font-medium text-muted-foreground block mb-1">
            字段名
          </span>
          <div className="font-mono bg-muted/50 px-2 py-1 rounded inline-flex items-center gap-2">
            {field.name}
            {field.is_primary_key && (
              <span className="text-[10px] bg-yellow-100 text-yellow-700 px-1 rounded border border-yellow-200">
                PK
              </span>
            )}
          </div>
        </div>

        <div>
          <span className="text-xs font-medium text-muted-foreground block mb-1">
            显示名
          </span>
          <div className="">{field.display_name}</div>
        </div>

        <div>
          <span className="text-xs font-medium text-muted-foreground block mb-1">
            类型
          </span>
          <div className="font-mono text-xs">{field.type}</div>
        </div>

        <div>
          <span className="text-xs font-medium text-muted-foreground block mb-1">
            描述
          </span>
          <div className="text-muted-foreground bg-muted/20 p-2 rounded">
            {field.description || "暂无描述"}
          </div>
        </div>

        {field.sample_values && field.sample_values.length > 0 && (
          <div>
            <span className="text-xs font-medium text-muted-foreground block mb-1">
              示例值
            </span>
            <div className="flex flex-wrap gap-1">
              {field.sample_values.map((val, idx) => (
                <span
                  key={idx}
                  className="bg-secondary px-1.5 py-0.5 rounded text-xs font-mono text-secondary-foreground"
                >
                  {val}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
