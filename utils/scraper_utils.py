import json
import os
from typing import List, Set, Tuple

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy,
    LLMConfig
)

from models.fellowship import Fellowship
from utils.data_utils import is_complete_fellowship, is_duplicate_fellowship


def get_browser_config() -> BrowserConfig:
    """
    Returns the browser configuration for the crawler.
    """
    return BrowserConfig(
        browser_type="chromium",
        headless=False,
        verbose=True,
    )


def get_llm_strategy() -> LLMExtractionStrategy:
    """
    Returns the configuration for the language model extraction strategy.
    """
    return LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="groq/deepseek-r1-distill-llama-70b",
            api_token=os.environ["GROQ_API_KEY"]
        ),
        schema=Fellowship.model_json_schema(),
        extraction_type="schema",
        extraction_scope="#content h2 + ul, #content h3, #content h3 + p",
        instruction="""
Extract each fellow from the HTML snippet:
- Name
- PGY level
- Medical school
Ignore everything else.
Return as a JSON array with keys: program_name, name, PGY, medical_school.
        """,
        input_format="html",
        verbose=True,
    )


async def check_no_results(
    crawler: AsyncWebCrawler,
    url: str,
    session_id: str,
) -> bool:
    """
    Checks if the "No Results Found" message is present on the page.
    """
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=session_id,
        ),
    )

    if result.success:
        if "No Results Found" in result.cleaned_html:
            return True
    else:
        print(f"Error fetching page for 'No Results Found' check: {result.error_message}")

    return False


async def fetch_and_process_page(
    crawler: AsyncWebCrawler,
    page_number: int,
    base_url: str,
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: List[str],
    seen_programs: Set[str],
) -> Tuple[List[dict], bool]:
    """
    Fetches and processes a single page of fellowship data.
    """
    url = f"{base_url}?page={page_number}"
    print(f"Loading page {page_number}...")

    no_results = await check_no_results(crawler, url, session_id)
    if no_results:
        return [], True

    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=llm_strategy,
            css_selector=css_selector,
            session_id=session_id,
        ),
    )

    if not (result.success and result.extracted_content):
        print(f"Error fetching page {page_number}: {result.error_message}")
        return [], False

    extracted_data = json.loads(result.extracted_content)
    if not extracted_data:
        print(f"No fellowships found on page {page_number}.")
        return [], False

    print("Extracted data:", extracted_data)

    complete_fellowships = []
    for fellowship in extracted_data:
        print("Processing fellowship:", fellowship)

        if fellowship.get("error") is False:
            fellowship.pop("error", None)

        if not is_complete_fellowship(fellowship, required_keys):
            continue

        if is_duplicate_fellowship(fellowship.get("program_name"), seen_programs):
            print(f"Duplicate fellowship '{fellowship.get('program_name')}' found. Skipping.")
            continue

        seen_programs.add(fellowship.get("program_name"))
        complete_fellowships.append(fellowship)

    if not complete_fellowships:
        print(f"No complete fellowships found on page {page_number}.")
        return [], False

    print(f"Extracted {len(complete_fellowships)} fellowships from page {page_number}.")
    return complete_fellowships, False
