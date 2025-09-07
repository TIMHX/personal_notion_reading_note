import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from logger_utils import setup_logger


class GeminiProcessor:
    def __init__(self, api_key, log_level_str: str = "WARNING"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-pro")

        self.logger = setup_logger(__name__, log_level_str)

    def summarize_text(self, text: str) -> str:
        prompt = f"""
        Please provide a detailed summary of the following document.
        Document:
        ---
        {text}
        ---
        Detailed Summary:
        """
        try:
            self.logger.debug(f"Sending summarization prompt to Gemini:\n{prompt}")
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            self.logger.error(f"Error summarizing text with Gemini: {e}")
            return "Error generating summary."


if __name__ == "__main__":
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    log_level_str = os.getenv("LOG_LEVEL", "WARNING").upper()

    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")

    gemini_processor = GeminiProcessor(gemini_api_key, log_level_str=log_level_str)

    sample_text_to_summarize = "This is a sample document about artificial intelligence. It discusses the history, key concepts, and future of AI."
    summary = gemini_processor.summarize_text(sample_text_to_summarize)
    gemini_processor.logger.info(f"Summary of sample text: {summary}")
