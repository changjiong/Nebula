/**
 * Add Custom Model Dialog
 * Allows users to add custom models with ID, name, and group
 * Similar to CherryStudio's add model dialog
 */

import { HelpCircle } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

export interface CustomModelData {
  id: string
  name: string
  group: string
}

interface AddCustomModelDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onAdd: (model: CustomModelData) => void
}

export function AddCustomModelDialog({
  open,
  onOpenChange,
  onAdd,
}: AddCustomModelDialogProps) {
  const [modelId, setModelId] = useState("")
  const [modelName, setModelName] = useState("")
  const [groupName, setGroupName] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!modelId.trim()) return

    onAdd({
      id: modelId.trim(),
      name: modelName.trim() || modelId.trim(),
      group: groupName.trim(),
    })

    // Reset form
    setModelId("")
    setModelName("")
    setGroupName("")
    onOpenChange(false)
  }

  const handleClose = (isOpen: boolean) => {
    if (!isOpen) {
      setModelId("")
      setModelName("")
      setGroupName("")
    }
    onOpenChange(isOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>添加模型</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Model ID */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor="model-id" className="flex items-center gap-1">
                <span className="text-destructive">*</span>
                模型 ID
              </Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="size-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>API 调用时使用的模型标识符</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <Input
              id="model-id"
              value={modelId}
              onChange={(e) => setModelId(e.target.value)}
              placeholder="必填 例如 gpt-3.5-turbo"
              required
            />
          </div>

          {/* Model Name */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor="model-name">模型名称</Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="size-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>显示名称，留空则使用模型 ID</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <Input
              id="model-name"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
              placeholder="例如 GPT-4"
            />
          </div>

          {/* Group Name */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Label htmlFor="group-name">分组名称</Label>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <HelpCircle className="size-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>用于模型列表分组显示</p>
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <Input
              id="group-name"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              placeholder="例如 ChatGPT"
            />
          </div>

          {/* Submit Button */}
          <div className="flex justify-end pt-2">
            <Button type="submit" disabled={!modelId.trim()}>
              添加模型
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
