import asyncio
import logging
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, ConfigDict
from tenacity import retry, stop_after_attempt, wait_exponential
from duckduckgo_search import DDGS

from app.tools.base import BaseTool, ToolResult

logger = logging.getLogger(__name__)

class SearchResult(BaseModel):
    """Represents a single search result."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    position: int = Field(description="Position in search results")
    url: str = Field(description="URL of the search result")
    title: str = Field(default="", description="Title of the search result")
    description: str = Field(default="", description="Description or snippet of the search result")
    raw_content: Optional[str] = Field(default=None, description="Raw content from the search result page")

    def __str__(self) -> str:
        return f"{self.title} ({self.url})"

class SearchResponse(ToolResult):
    """Structured response from the web search tool."""
    query: str = Field(description="The search query executed")
    results: List[SearchResult] = Field(default_factory=list, description="List of search results")

    def __str__(self):
        if self.error:
            return f"Error: {self.error}"
        
        result_text = [f"Search results for '{self.query}':"]
        for i, result in enumerate(self.results, 1):
            title = result.title.strip() or "No title"
            result_text.append(f"\n{i}. {title}")
            result_text.append(f"   URL: {result.url}")
            if result.description.strip():
                result_text.append(f"   Description: {result.description}")
            if result.raw_content:
                content_preview = result.raw_content[:500].replace("\n", " ").strip()
                if len(result.raw_content) > 500:
                    content_preview += "..."
                result_text.append(f"   Content: {content_preview}")
        return "\n".join(result_text)

class WebContentFetcher:
    """Utility class for fetching web content."""

    @staticmethod
    def fetch_content(url: str, timeout: int = 10) -> Optional[str]:
        """Fetch and extract the main content from a webpage."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch content from {url}: HTTP {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()
            
            text = soup.get_text(separator="\n", strip=True)
            text = " ".join(text.split())
            return text[:10000] if text else None
        except Exception as e:
            logger.warning(f"Error fetching content from {url}: {e}")
            return None

class WebSearch(BaseTool):
    """Search the web for information using DuckDuckGo."""

    name: str = "web_search"
    description: str = """Search the web for real-time information about any topic.
    Returns comprehensive search results with URLs, titles, and descriptions.
    Can also fetch page content."""
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "(required) The search query.",
            },
            "num_results": {
                "type": "integer",
                "description": "(optional) Number of results to return. Default is 5.",
                "default": 5,
            },
            "fetch_content": {
                "type": "boolean",
                "description": "(optional) Whether to fetch full content from result pages. Default is false.",
                "default": False,
            },
        },
        "required": ["query"],
    }

    async def execute(
        self,
        query: str,
        num_results: int = 5,
        fetch_content: bool = False,
        **kwargs
    ) -> SearchResponse:
        """Execute a Web search."""
        try:
            # Run blocking search in a thread
            results = await asyncio.to_thread(self._search, query, num_results)
            
            structured_results = []
            for i, r in enumerate(results):
                structured_results.append(SearchResult(
                    position=i + 1,
                    url=r.get("href", ""),
                    title=r.get("title", ""),
                    description=r.get("body", "")
                ))

            if fetch_content and structured_results:
                await self._fetch_content_for_results(structured_results)

            return SearchResponse(
                output=str(SearchResponse(query=query, results=structured_results)), # Pre-calculate string output for ToolResult
                query=query,
                results=structured_results
            )

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return SearchResponse(query=query, error=str(e), results=[])

    def _search(self, query: str, max_results: int) -> List[Dict]:
        """Perform actual search using DuckDuckGo."""
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results, backend="lite"))

    async def _fetch_content_for_results(self, results: List[SearchResult]):
        """Fetch content for results in parallel."""
        fetcher = WebContentFetcher()
        
        async def fetch_one(result):
            if result.url:
                content = await asyncio.to_thread(fetcher.fetch_content, result.url)
                if content:
                    result.raw_content = content
        
        await asyncio.gather(*(fetch_one(r) for r in results))
