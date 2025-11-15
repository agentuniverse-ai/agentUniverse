# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/22 10:00
# @Author  : wangyapei 
# @FileName: jina_ai_tool.py

from typing import Optional, Dict
import requests
import time
from pydantic import Field
from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.base.util.env_util import get_from_env
import html


jina_read_url = "https://r.jina.ai/"
jina_search_url = "https://s.jina.ai/"
jina_check_fact_url = "https://g.jina.ai/"


class JinaAITool(Tool):
    """Jina AI tool for webpage reading, search and fact checking.

    This tool uses Jina.ai's API for three main functionalities:
    1. Read: Extract content from web pages
    2. Search: Perform web searches and return structured results
    3. Check fact: Verify factual claims with references
    
    Note: 
        API key is not required for webpage reading, but required for search and fact checking.
        API key can be found at https://jina.ai/.
        
    Attributes:
        mode: Operation mode - 'read', 'search', or 'check_fact'
        timeout: Request timeout in seconds
        api_key: Jina API key from environment variable
        max_read_content_length: Maximum content length in characters
        remove_image: Whether to remove image descriptions from content
        headers: Additional HTTP headers
    """

    mode: str = "read"
    timeout: int = 30
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("JINA_API_KEY"))
    max_read_content_length: int = Field(10000, description="Maximum content length in characters")
    remove_image: bool = Field(True, description="Remove image from content")
    headers: Dict[str, str] = None
    def execute(self,
                input: str = None,
                mode: str = None,
                timeout: int = None,
                api_key: str = None,
                max_read_content_length: int = None,
                remove_image: bool = None,
                headers: Dict[str, str] = None
                ):
        """Execute Jina AI operation based on mode.
        
        Args:
            input: URL for read mode, query for search/check_fact modes
            mode: Operation mode - 'read', 'search', or 'check_fact'
            timeout: Request timeout in seconds
            api_key: Jina API key
            max_read_content_length: Maximum content length in characters
            remove_image: Whether to remove image descriptions
            headers: Additional HTTP headers
            
        Returns:
            str: Operation result or None if invalid input
        """
        if not input:
            return None
        
        # Update optional configurations if provided
        if mode:
            self.mode = mode
        if timeout:
            self.timeout = timeout
        if api_key:
            self.api_key = api_key
        if max_read_content_length:
            self.max_read_content_length = max_read_content_length
        if remove_image is not None:
            self.remove_image = remove_image
        if headers:
            self.headers = headers

        # Debug logging (commented out for production)
        # print(f"mode: {self.mode}, max_read_content_length: {self.max_read_content_length}, headers: {self.headers}")

        if self.mode == "read":
            if input.startswith("https://") or input.startswith("http://"):
                return self.read_url(url=html.unescape(input))
            else:
                return None
        elif self.mode == "search":
            return self.search_query(query=input)
        elif self.mode == "check_fact":
            return self.check_fact(query=input)
        else:
            return None

    def _make_api_request(self, url: str, timeout: int, error_prefix: str) -> Optional[dict]:
        """
        Unified method for handling API requests with retry logic.
        
        Args:
            url: The URL to request
            timeout: Request timeout in seconds
            error_prefix: Error message prefix for logging
            
        Returns:
            Optional[dict]: Response data, returns None if failed
        """
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(
                    url, 
                    headers=self._get_headers(), 
                    verify=False, 
                    timeout=timeout
                )
                response.raise_for_status()
                content = response.json()

                if content.get("code") != 200:
                    print(f"Request failed with status code {content.get('code')}")
                    return None
                    
                return content
                
            except requests.HTTPError as e:
                error_msg = (f"Access forbidden. Please check your API key and permissions. Error: {str(e)}" 
                           if e.response.status_code == 403 
                           else f"HTTP Error: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return error_msg
            except requests.Timeout:
                error_msg = f"{error_prefix}: Request timeout"
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return error_msg
            except Exception as e:
                error_msg = f"{error_prefix}: {str(e)}"
                return error_msg

    def read_url(self, url: str) -> str:
        """
        Read URL and return full webpage content.
        
        Args:
            url: URL to read
            
        Returns:
            str: Webpage content or error message
        """
        full_url = f"{jina_read_url}{url}"
        
        content = self._make_api_request(full_url, self.timeout, "Error reading URL")
        if isinstance(content, str):  # Error message
            return content
        if not content:
            return None     
        
        data = content.get("data", {})
        content_text = data.get("content", "").strip()
        
        if self.remove_image:
            content_text = self._remove_images(content_text)
        # Remove blank lines for cleaner output
        content_text = "\n".join(line for line in content_text.splitlines() if line.strip())
        return self._truncate_content(content_text)

    def search_query(self, query: str) -> str:
        """
        Execute search query and return json list string
        return example:
        [
            {
            "title": "About Jina AI",
            "description": "These photos include our former colleagues and interns—we appreciate every one of them. favorite · <strong>Founded</strong> in 2020, <strong>Jina</strong> <strong>AI</strong> is a leading search <strong>AI</strong> company.",
            "url": "https://jina.ai/about-us/",
            "content": "About Jina AI\n===============\n  \n\n[](https://jina.ai/)\n\n_search__reorder_\n\n[News](https://jina.ai/news)[Models](https://jina.ai/models)",
            "usage": {
                "tokens": 1758
                }
            },
            {
            "title": "Dr. Han Xiao, CEO and Founder of Jina AI",
            "description": "Our recent release of the jina-embeddings-v2, on <strong>October 26th</strong>, stands as a testament to Jina AI&#x27;s commitment to spearheading innovation in the AI realm. ",
            "url": "https://ai-berlin.com/blog/article/interview-with-dr-han-xiao-ceo-and-co-founder-of-jina-ai",
            "content": "Dr. Han Xiao, CEO and Founder of Jina AI | Artificial Intelligence in Berlin\n===============                \n\n[](https://ai-berlin.com/)",
            "usage": {
                "tokens": 9647
                }
            }
        ]
        """
        full_url = f"{jina_search_url}{query}"
        
        content = self._make_api_request(full_url, self.timeout, "Error executing search")
        if isinstance(content, str): 
            return content
        if not content:
            return None
            
        return str(content.get("data"))
    
    def check_fact(self, query: str) -> str:
        """
        Execute check fact query and return json string
        return example:
        {
            "factuality": 0,
            "result": false,
            "reason": "The statement is incorrect as it asserts that President Obama repealed the Smith-Mundt Act. However, the Smith-Mundt Modernization Act of 2012 did not repeal the original act. Instead, it lifted restrictions that prevented U.S. government-produced information from being disseminated to domestic audiences. The original act still exists, but its applicability has been changed. Multiple references confirm that the Smith-Mundt Act remains in effect, emphasizing that only certain restrictions were modified rather than a complete repeal.",
            "references": [
            {
                "url": "https://apnews.com/article/archive-fact-checking-7064410002",
                "keyQuote": "THE FACTS: A post circulating on Facebook with a photo of Obama falsely states he repealed a ban on government propaganda in the U.S. when he signed the National Defense Authorization Act in 2013. The amendment did not repeal the Smith-Mundt Act",
                "isSupportive": false
            },
            {
                "url": "https://en.wikipedia.org/wiki/Smith–Mundt_Act",
                "keyQuote": "The original version of the Act was amended by the Smith–Mundt Modernization Act of 2012 which allowed for materials produced by the State Department and the Broadcasting Board of Governors ...",
                "isSupportive": false
            }
            ],
            "usage": {
            "tokens": 11848
            }
        }
        """

        full_url = f"{jina_check_fact_url}{query}"
        # Fact checking is slower, so we use a longer timeout
        content = self._make_api_request(full_url, self.timeout * 3, "Error executing check fact")
        if isinstance(content, str): 
            return content
        if not content:
            return None
        return str(content.get("data"))

    def _remove_images(self, content: str) -> str:
        """
        Remove image descriptions from content.
        
        Args:
            content: Text content containing image descriptions
            
        Returns:
            str: Content with image descriptions removed
        """
        return "\n".join(
            line for line in content.split("\n") 
            if not line.startswith("![Image")
        ).rstrip()

    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers with API key and other configurations.
        
        Returns:
            Dict[str, str]: Headers dictionary containing Accept, X-Engine, X-Retain-Images 
            and optionally Authorization if API key is provided
        """
        headers = {
            "Accept": "application/json",
            "X-Engine": "direct",
            "X-Retain-Images": "none",
        }
        if self.headers:
            headers.update(self.headers)
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _truncate_content(self, content: str) -> str:
        """
        Truncate content to the maximum allowed length.
        
        Args:
            content: Original content text
            
        Returns:
            str: Truncated content with ellipsis if exceeds max length, otherwise original content
        """
        if len(content) > self.max_read_content_length:
            truncated = content[: self.max_read_content_length]
            return truncated + "... (Content truncated)"
        return content