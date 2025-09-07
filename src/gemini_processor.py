import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from logger_utils import setup_logger


class GeminiProcessor:
    def __init__(self, api_key, prompt_content: str, log_level_str: str = "WARNING"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-pro")
        self.prompt_content = prompt_content
        self.logger = setup_logger(__name__, log_level_str)

    def process_document(self, text: str) -> dict:
        prompt = f"{self.prompt_content}\n\nFile:\n---\n{text}\n---"
        try:
            self.logger.debug(
                f"Sending document processing prompt to Gemini:\n{prompt}"
            )
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            self.logger.info(f"Received response from Gemini: {response_text}")

            key_points = []
            notes = ""
            summary = ""

            parts = response_text.split("### ")
            self.logger.info(parts)
            for i, part in enumerate(parts):
                if part.startswith("@Key Points"):
                    # Ensure there is a next part before accessing parts[i + 1]
                    kp_content = parts[i].strip()
                    key_points = [
                        item.strip().replace("- ", "")
                        for item in kp_content.split("\n")
                        if item.strip().startswith("-")
                    ]
                elif part.startswith("@Notes"):
                    notes = parts[i].strip().replace("@Notes", "")
                elif part.startswith("@Summary"):
                    summary = parts[i].strip().replace("@Summary", "")
            self.logger.info(f"Extracted Key Points: {key_points}")
            self.logger.info(f"Extracted Notes: {notes}")
            self.logger.info(f"Extracted Summary: {summary}")

            return {"key_points": key_points, "notes": notes, "summary": summary}
        except Exception as e:
            self.logger.error(f"Error processing document with Gemini: {e}")
            return {
                "key_points": [],
                "notes": "Error generating notes.",
                "summary": "Error generating summary.",
            }


default_reading_prompt = """
Please perform an in-depth analysis of the following textbook document and provide the following content. Ensure that each section is detailed, clear, and includes as much key information and detail as possible.
  1. Key Points: Directly and comprehensively list all core information from the document. Please focus on extracting and explaining key concepts, important definitions, core principles, and key terminology, especially content that is highlighted in the original text (e.g., in bold). Each point should be independent, clear, and contain sufficient context or explanation, rather than being a mere list of single words, presented as a bulleted list with no sub bullet
  2. Notes: Provide a detailed elaboration and supplement to the key information. In this section, please explain the logical relationships, hierarchical structure, and interconnections among the various key points. Provide a more in-depth explanation of important theories or models, and describe their practical applications or significance. This section should serve as a deeper dive and extension of the "Key Points," not as personal reflection, presented in paragraph form.
  3. Summary: Provide a comprehensive and detailed summary of the document's content. This summary must cover all the information listed in the "Key Points" and be organized according to the logical sequence of the original text. Please ensure the summary is of sufficient length to completely reproduce the core content of the document, including major theories, the evidence or examples that support them, and the final conclusions drawn. The summary should strive for completeness of content and accuracy of information, avoiding the omission of any critical details, presented in paragraph form.

Please ensure the output is formatted as follows, using clear headings to separate each section:

### @Key Points
  - [Key Point 1]
  - [Key Point 2]
  - [Key Point 3]

### @Notes
[Provide a detailed elaboration here on the logical relationships, hierarchical structure, and interconnections between the key points, as well as a deeper explanation of key theories.]

### @Summary
[Provide a detailed, comprehensive, and well-structured paragraph-style summary here, ensuring all key information is covered with completeness and accuracy.]
"""

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

    gemini_processor = GeminiProcessor(
        gemini_api_key, default_reading_prompt, log_level_str=log_level_str
    )
    processed_content = gemini_processor.process_document(sample_text_to_summarize)
    gemini_processor.logger.info(
        f"Processed content of sample text: {processed_content}"
    )
