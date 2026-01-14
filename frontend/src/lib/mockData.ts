import type { ThinkingStep } from "@/stores/chatStore"
import { useChatStore } from "@/stores/chatStore"

export function injectMockData() {
  const store = useChatStore.getState()

  // Clear existing steps
  store.clearThinkingSteps()

  const mockSteps: ThinkingStep[] = [
    // Group 1: Research
    {
      id: "step-1",
      title: "开始研究用户需求",
      status: "completed",
      group: "开始研究",
      content: "分析用户关于 AIGC 落地应用的需求...",
      timestamp: Date.now() - 10000,
    },
    {
      id: "step-2",
      title: "搜索相关技术文档",
      status: "completed",
      group: "开始研究",
      content: "Found 20+ relevant articles",
      timestamp: Date.now() - 8000,
      isCollapsible: true,
      defaultExpanded: 2,
      subItems: [
        {
          id: "sub-1",
          type: "search-result",
          title: "AIGC 技术基础：从原理到应用原创",
          source: "developer.aliyun.com",
          previewable: true,
          content:
            "# AIGC 技术基础\n\n本文详细介绍了 AIGC 的基本原理，包括 Transformer 架构、扩散模型等核心技术。\n\n## 目录\n1. 核心架构\n2. 训练数据\n3. 应用场景\n\n(此处省略详细内容...)",
        },
        {
          id: "sub-2",
          type: "search-result",
          title: "AIGC 的局限性与挑战 - 阿里云开发者社区",
          source: "developer.aliyun.com",
          previewable: true,
          content:
            "# AIGC 的局限性\n\n虽然 AIGC 发展迅速，但仍面临诸如幻觉问题、版权争议等挑战。",
        },
        {
          id: "sub-3",
          type: "search-result",
          title: "畅聊未来 -- AIGC 的发展方向与趋势",
          source: "cloud.tencent.com",
          previewable: true,
          content: "腾讯云技术专家分享关于 AIGC 未来三年的发展预测。",
        },
      ],
    },

    // Group 2: Analysis (Standalone step in middle)
    {
      id: "step-3",
      title: "生成初步大纲",
      status: "completed",
      content: "根据搜索结果，生成了本次报告的初步大纲结构...",
      timestamp: Date.now() - 5000,
    },

    // Group 3: Reporting
    {
      id: "step-4",
      title: "撰写详细报告内容",
      status: "in-progress",
      group: "准备生成报告",
      content: "正在生成第一章...",
      timestamp: Date.now() - 2000,
      subItems: [
        {
          id: "sub-4",
          type: "file-operation",
          title: "写入文件 AIGC模型发展趋势与应用报告.md",
          previewable: true,
          content: "# AIGC模型发展趋势与应用报告\n\n## 摘要\n本报告旨在分析...",
        },
        {
          id: "sub-5",
          type: "api-call",
          title: "调用 GPT-4 模型优化内容",
          previewable: false,
        },
      ],
    },
  ]

  // Add steps sequentially
  mockSteps.forEach((step) => store.addThinkingStep(step))

  console.log("Mock data injected successfully")
}
