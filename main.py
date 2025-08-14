import asyncio
from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv

from config import BASE_URL, CSS_SELECTOR, REQUIRED_KEYS
from utils.data_utils import save_fellowships_to_csv  # change this import
from utils.scraper_utils import (
    fetch_and_process_page,
    get_browser_config,
    get_llm_strategy,
)

load_dotenv()


async def crawl_fellowships():
    """
    Main function to crawl cardiology fellowship data from the website.
    """
    # Initialize configurations
    browser_config = get_browser_config()
    llm_strategy = get_llm_strategy()
    session_id = "fellowship_crawl_session"

    # Initialize state variables
    page_number = 1
    all_fellowships = []  # rename variable
    seen_programs = set()  # rename variable

    # Start the web crawler context
    async with AsyncWebCrawler(config=browser_config) as crawler:
        while True:
            # Fetch and process data from the current page
            fellowships, no_results_found = await fetch_and_process_page(
                crawler,
                page_number,
                BASE_URL,
                CSS_SELECTOR,
                llm_strategy,
                session_id,
                REQUIRED_KEYS,
                seen_programs,
            )

            if no_results_found:
                print("No more fellowships found. Ending crawl.")
                break

            if not fellowships:
                print(f"No fellowships extracted from page {page_number}.")
                break

            # Add the fellowships from this page to the total list
            all_fellowships.extend(fellowships)
            page_number += 1

            # Pause between requests to be polite
            await asyncio.sleep(2)

    # Save the collected fellowships to a CSV file
    if all_fellowships:
        save_fellowships_to_csv(all_fellowships, "complete_fellowships.csv")
        print(f"Saved {len(all_fellowships)} fellowships to 'complete_fellowships.csv'.")
    else:
        print("No fellowships were found during the crawl.")

    # Display usage statistics for the LLM strategy
    llm_strategy.show_usage()


async def main():
    """
    Entry point of the script.
    """
    await crawl_fellowships()


if __name__ == "__main__":
    asyncio.run(main())
