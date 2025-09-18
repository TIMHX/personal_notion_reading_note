import os
from dotenv import load_dotenv
from logger_utils import setup_logger
import dspy
import yaml
from dspy_modules import ProcessDocument, ReadingNotes


class GeminiProcessor:
    def __init__(self, api_key, log_level_str: str = "WARNING"):
        self.logger = setup_logger(__name__, log_level_str)
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        max_tokens = config.get("max_tokens", 4000)  # Default to 4000 if not specified
        model_name = config.get(
            "model", "gemini/gemini-2.5-pro"
        )  # Default to "gemini/gemini-2.5-pro" if not specified
        self.dspy_lm = dspy.LM(model=model_name, api_key=api_key, max_tokens=max_tokens)
        dspy.configure(lm=self.dspy_lm)
        self.document_processor = ProcessDocument()

    def process_document(self, text: str) -> ReadingNotes:
        try:
            self.logger.debug("Sending document to dspy for processing.")
            response: ReadingNotes = self.document_processor(
                document_content=text
            ).processed_document
            self.logger.info(f"Received response from dspy: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Error processing document with dspy: {e}")
            return ReadingNotes(
                key_points=[],
                notes="Error generating notes.",
                summary="Error generating summary.",
            )


if __name__ == "__main__":
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    log_level_str = os.getenv("LOG_LEVEL", "WARNING").upper()

    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")

    sample_text_to_summarize = (
        "This is a slightly longer sample document about artificial intelligence. "
        "It discusses the history, key concepts, and future of AI, including machine learning, "
        "deep learning, and natural language processing. The document also touches upon "
        "the ethical considerations and societal impact of AI, such as job displacement "
        "and bias in algorithms. Furthermore, it explores the potential applications "
        "of AI in various industries like healthcare, finance, and transportation, "
        "highlighting both the opportunities and challenges that lie ahead."
    )

    gemini_processor = GeminiProcessor(gemini_api_key, log_level_str=log_level_str)
    processed_content = gemini_processor.process_document(sample_text_to_summarize)
    gemini_processor.logger.info(
        f"Processed content of sample text: {processed_content}"
    )
