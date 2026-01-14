import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"

interface CandidateListProps {
  data: {
    question: string
    options: Array<{
      id: string
      label: string
      description?: string
      [key: string]: any
    }>
  }
  config?: {
    onSelect?: (selected: string) => void
  }
}

export function CandidateList({ data, config }: CandidateListProps) {
  const [selected, setSelected] = useState<string>("")

  const handleConfirm = () => {
    if (selected && config?.onSelect) {
      config.onSelect(selected)
    }
  }

  return (
    <Card className="border-amber-200 bg-amber-50/50">
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          ⚠️ {data.question}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <RadioGroup value={selected} onValueChange={setSelected}>
          <div className="space-y-2">
            {data.options.map((option) => (
              <div
                key={option.id}
                className="flex items-start space-x-3 space-y-0 rounded-md border p-4 hover:bg-accent cursor-pointer"
              >
                <RadioGroupItem value={option.id} id={option.id} />
                <Label
                  htmlFor={option.id}
                  className="font-normal cursor-pointer flex-1"
                >
                  <div className="font-medium">{option.label}</div>
                  {option.description && (
                    <div className="text-sm text-muted-foreground mt-1">
                      {option.description}
                    </div>
                  )}
                </Label>
              </div>
            ))}
          </div>
        </RadioGroup>
        <div className="flex justify-end">
          <Button onClick={handleConfirm} disabled={!selected}>
            选择后继续
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
