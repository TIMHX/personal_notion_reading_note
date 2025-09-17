import dspy
import os
from dotenv import load_dotenv
from logger_utils import setup_logger
from src.models import ReadingData
from src.dspy_modules import ReadingModule
from pydantic import ValidationError


class GeminiProcessor:
    def __init__(self, api_key: str, log_level_str: str = "WARNING"):
        self.logger = setup_logger(__name__, log_level_str)
        try:
            self.llm = dspy.Google(model="gemini-2.5-pro", api_key=api_key)
            dspy.settings.configure(lm=self.llm)
            self.reading_module = ReadingModule()
        except Exception as e:
            self.logger.error(f"Failed to initialize dspy or Google LLM: {e}")
            raise

    def process_document(self, text: str) -> ReadingData:
        try:
            self.logger.debug("Processing document with DSPy ReadingModule.")
            result = self.reading_module(document=text)
            reading_data = result.reading_data

            # The output from the LM is a string representation of the Pydantic model,
            # so we need to parse it.
            if isinstance(reading_data, str):
                # Extract the JSON part from the string
                try:
                    import json
                    # A simple way to find the JSON object
                    json_str = reading_data[reading_data.find('{'):reading_data.rfind('}')+1]
                    data_dict = json.loads(json_str)
                    validated_data = ReadingData.model_validate(data_dict)
                    return validated_data
                except (json.JSONDecodeError, ValidationError) as e:
                    self.logger.error(f"Error parsing or validating reading data: {e}")
                    # Attempt to parse manually if JSON fails
                    return self._parse_manual_string(reading_data)


            if not isinstance(reading_data, ReadingData):
                 raise TypeError(f"Expected ReadingData, but got {type(reading_data)}")

            self.logger.info(f"Successfully processed document and got ReadingData.")
            return reading_data

        except (Exception, ValidationError) as e:
            self.logger.error(f"Error processing document with DSPy: {e}")
            return ReadingData(
                key_points=[],
                notes="Error generating notes.",
                summary="Error generating summary.",
            )

    def _parse_manual_string(self, data_str: str) -> ReadingData:
        try:
            key_points = []
            notes = ""
            summary = ""

            # Example parsing logic, this might need to be very robust
            if "key_points=" in data_str:
                kp_str = data_str.split("key_points=[")[1].split("]")[0]
                if kp_str:
                    key_points = [item.strip().strip("'\"") for item in kp_str.split(",")]

            if "notes='" in data_str:
                notes = data_str.split("notes='")[1].split("'")[0]

            if "summary='" in data_str:
                summary = data_str.split("summary='")[1].split("'")[0]

            return ReadingData(key_points=key_points, notes=notes, summary=summary)
        except Exception as e:
            self.logger.error(f"Manual parsing failed: {e}")
            return ReadingData(
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
