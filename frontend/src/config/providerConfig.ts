/**
 * Provider Configuration
 * Contains URLs and settings for each model provider
 * Based on CherryStudio's provider configuration pattern
 */

export interface ProviderConfig {
  /** Provider ID (matches provider_type) */
  id: string
  /** Display name */
  name: string
  /** Default API URL (OpenAI compatible) */
  apiUrl: string
  /** Anthropic compatible API URL (for providers that support it) */
  anthropicApiUrl?: string
  /** URL to get API key */
  apiKeyUrl?: string
  /** Documentation URL */
  docsUrl?: string
  /** Model list URL */
  modelsUrl?: string
  /** Official website */
  officialUrl?: string
  /** Whether this provider supports Anthropic API format */
  supportsAnthropicFormat?: boolean
}

/**
 * Provider configurations with URLs for documentation, API keys, etc.
 */
export const PROVIDER_CONFIGS: Record<string, ProviderConfig> = {
  openai: {
    id: "openai",
    name: "OpenAI",
    apiUrl: "https://api.openai.com/v1",
    apiKeyUrl: "https://platform.openai.com/api-keys",
    docsUrl: "https://platform.openai.com/docs",
    modelsUrl: "https://platform.openai.com/docs/models",
    officialUrl: "https://openai.com",
    supportsAnthropicFormat: false,
  },
  deepseek: {
    id: "deepseek",
    name: "DeepSeek",
    apiUrl: "https://api.deepseek.com/v1",
    anthropicApiUrl: "https://api.deepseek.com/anthropic",
    apiKeyUrl: "https://platform.deepseek.com/api_keys",
    docsUrl: "https://platform.deepseek.com/api-docs",
    modelsUrl:
      "https://platform.deepseek.com/api-docs/zh-cn/quick_start/pricing",
    officialUrl: "https://deepseek.com",
    supportsAnthropicFormat: true,
  },
  gemini: {
    id: "gemini",
    name: "Google Gemini",
    apiUrl: "https://generativelanguage.googleapis.com/v1beta",
    apiKeyUrl: "https://aistudio.google.com/app/apikey",
    docsUrl: "https://ai.google.dev/docs",
    modelsUrl: "https://ai.google.dev/gemini-api/docs/models/gemini",
    officialUrl: "https://ai.google.dev",
    supportsAnthropicFormat: false,
  },
  qwen: {
    id: "qwen",
    name: "阿里通义千问",
    apiUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1",
    anthropicApiUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1",
    apiKeyUrl: "https://dashscope.console.aliyun.com/apiKey",
    docsUrl: "https://help.aliyun.com/zh/dashscope/",
    modelsUrl: "https://help.aliyun.com/zh/model-studio/getting-started/models",
    officialUrl: "https://dashscope.aliyun.com",
    supportsAnthropicFormat: true,
  },
  anthropic: {
    id: "anthropic",
    name: "Anthropic Claude",
    apiUrl: "https://api.anthropic.com/v1",
    apiKeyUrl: "https://console.anthropic.com/settings/keys",
    docsUrl: "https://docs.anthropic.com",
    modelsUrl: "https://docs.anthropic.com/en/docs/about-claude/models",
    officialUrl: "https://anthropic.com",
    supportsAnthropicFormat: false,
  },
  moonshot: {
    id: "moonshot",
    name: "月之暗面 Kimi",
    apiUrl: "https://api.moonshot.cn/v1",
    anthropicApiUrl: "https://api.moonshot.cn/v1",
    apiKeyUrl: "https://platform.moonshot.cn/console/api-keys",
    docsUrl: "https://platform.moonshot.cn/docs",
    modelsUrl: "https://platform.moonshot.cn/docs/intro#主要模型",
    officialUrl: "https://moonshot.cn",
    supportsAnthropicFormat: true,
  },
  zhipu: {
    id: "zhipu",
    name: "智谱 GLM",
    apiUrl: "https://open.bigmodel.cn/api/paas/v4",
    anthropicApiUrl: "https://open.bigmodel.cn/api/anthropic",
    apiKeyUrl: "https://bigmodel.cn/usercenter/apikeys",
    docsUrl: "https://bigmodel.cn/dev/howuse/introduction",
    modelsUrl: "https://bigmodel.cn/dev/howuse/model",
    officialUrl: "https://bigmodel.cn",
    supportsAnthropicFormat: true,
  },
  baidu: {
    id: "baidu",
    name: "百度文心一言",
    apiUrl: "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop",
    apiKeyUrl:
      "https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application",
    docsUrl: "https://cloud.baidu.com/doc/WENXINWORKSHOP/index.html",
    modelsUrl: "https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu",
    officialUrl: "https://yiyan.baidu.com",
    supportsAnthropicFormat: false,
  },
}

/**
 * Get provider config by provider_type
 */
export function getProviderConfig(
  providerType: string,
): ProviderConfig | undefined {
  return PROVIDER_CONFIGS[providerType]
}

/**
 * Get API key URL for a provider
 */
export function getApiKeyUrl(providerType: string): string | undefined {
  return PROVIDER_CONFIGS[providerType]?.apiKeyUrl
}

/**
 * Get documentation URL for a provider
 */
export function getDocsUrl(providerType: string): string | undefined {
  return PROVIDER_CONFIGS[providerType]?.docsUrl
}

/**
 * Get models list URL for a provider
 */
export function getModelsUrl(providerType: string): string | undefined {
  return PROVIDER_CONFIGS[providerType]?.modelsUrl
}

/**
 * Check if provider supports Anthropic API format
 */
export function supportsAnthropicFormat(providerType: string): boolean {
  return PROVIDER_CONFIGS[providerType]?.supportsAnthropicFormat ?? false
}

/**
 * Get Anthropic API URL for a provider
 */
export function getAnthropicApiUrl(providerType: string): string | undefined {
  return PROVIDER_CONFIGS[providerType]?.anthropicApiUrl
}
