from crawl4ai import LLMExtractionStrategy, LLMConfig

def test():
    strat = LLMExtractionStrategy(
        llm_config=LLMConfig(provider="groq/deepseek-r1-distill-llama-70b"),
        api_token="dummy_token",
        schema={},
        extraction_type="schema",
        instruction="Test",
        input_format="markdown",
        verbose=True,
    )
    print("Strategy created successfully")

if __name__ == "__main__":
    test()
