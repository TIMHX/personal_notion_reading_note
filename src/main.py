import os
from datetime import datetime
from gemini_processor import GeminiProcessor
from notion_client import NotionClient
from dotenv import load_dotenv
from logger_utils import setup_logger
import yaml  # Import yaml
from pypdf import PdfReader  # Import PdfReader
import glob  # Import glob
from pathlib import Path  # Import Path


def main():
    load_dotenv()
    log_level_str = os.getenv("LOG_LEVEL", "WARNING").upper()
    logger = setup_logger(__name__, log_level_str)

    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    notion_api_key = os.environ.get("NOTION_API_KEY")
    notion_database_id = os.environ.get("NOTION_DATABASE_ID")

    if not all(
        [
            gemini_api_key,
            notion_api_key,
            notion_database_id,
        ]
    ):
        logger.error(
            "One or more environment variables (GEMINI_API_KEY, NOTION_API_KEY, NOTION_DATABASE_ID) are not set."
        )
        return

    gemini_processor = GeminiProcessor(gemini_api_key, log_level_str=log_level_str)

    # Load config.yaml
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        subject_id = config.get("subject_id")
        assignment_id = config.get("assignments_id")
        reading_template_id = config.get("reading_template_id")
    except FileNotFoundError:
        logger.error(
            "config.yaml not found. Please create it with subject_id and assignments_id."
        )
        return
    except yaml.YAMLError as e:
        logger.error(f"Error reading config.yaml: {e}")
        return

    notion_client = NotionClient(
        notion_api_key,
        notion_database_id,
        reading_template_id=reading_template_id,
        log_level_str=log_level_str,
    )

    # Process PDF files in the 'readings' directory
    readings_dir = config.get("reading_folder")
    pdf_files = glob.glob(os.path.join(readings_dir, "*.pdf"))

    if not pdf_files:
        logger.info(f"No PDF files found in the '{readings_dir}' directory.")
        return

    for pdf_file in pdf_files:
        logger.info(f"Processing PDF file: {pdf_file}")
        try:
            reader = PdfReader(pdf_file)
            pdf_content = ""
            for page in reader.pages:
                pdf_content += page.extract_text()

            summary = gemini_processor.summarize_text(pdf_content)

            file_name = Path(pdf_file).stem
            title = f"Reading Summary: {file_name}"
            content_blocks = [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": summary,
                                },
                            }
                        ]
                    },
                }
            ]

            notion_client.create_reading_page(
                title, content_blocks, subject_id, assignment_id
            )
            logger.info(f"Created Notion page for {file_name}")

        except Exception as e:
            logger.error(f"Error processing {pdf_file}: {e}")


if __name__ == "__main__":
    main()
