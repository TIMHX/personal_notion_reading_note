import requests
import json
import os
from datetime import datetime  # Import datetime
from dotenv import load_dotenv
from logger_utils import setup_logger
from gemini_processor import GeminiProcessor


class NotionClient:
    def __init__(
        self,
        api_key,
        database_id,
        reading_template_id: str = None,
        log_level_str: str = "WARNING",
    ):
        self.api_key = api_key
        self.database_id = database_id
        self.reading_template_id = reading_template_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        self.logger = setup_logger(__name__, log_level_str)

    def create_reading_page(
        self,
        title: str,
        subject_id: str,
        assignment_id: str,
        key_points: list = None,
        notes: str = None,
        summary: str = None,
    ) -> dict:
        create_page_url = "https://api.notion.com/v1/pages"
        current_date = datetime.now().isoformat()

        column_list_children = []

        # Column 1: Key Points
        column_1_blocks = []
        if key_points:
            column_1_blocks.append(
                {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "Key Points"}}
                        ]
                    },
                }
            )
            for point in key_points:
                column_1_blocks.append(
                    {
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": point}}]
                        },
                    }
                )
        column_list_children.append(
            {
                "object": "block",
                "type": "column",
                "column": {"children": column_1_blocks},
            }
        )

        # Column 2: Summary and Notes
        column_2_blocks = []
        if summary:
            column_2_blocks.append(
                {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": "Summary"}}]
                    },
                }
            )
            column_2_blocks.extend(self._split_text_into_blocks(summary, "paragraph"))
        if notes:
            column_2_blocks.append(
                {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": "Notes"}}]
                    },
                }
            )
            column_2_blocks.extend(self._split_text_into_blocks(notes, "paragraph"))
        column_list_children.append(
            {
                "object": "block",
                "type": "column",
                "column": {"children": column_2_blocks},
            }
        )

        # Main children blocks for the page
        children_blocks = [
            {
                "object": "block",
                "type": "column_list",
                "column_list": {"children": column_list_children},
            }
        ]

        properties = {
            "notes": {"title": [{"text": {"content": title}}]},
            "review level": {"select": {"name": "📖 reading"}},
            "day": {"date": {"start": current_date}},
        }

        # Add subject and assignment if provided as IDs
        if subject_id:
            properties["subject"] = {"relation": [{"id": subject_id}]}
        if assignment_id:
            properties["assignments"] = {"relation": [{"id": assignment_id}]}

        data = {
            "parent": {"database_id": self.database_id},
            "icon": {
                "type": "external",
                "external": {"url": "https://www.notion.so/icons/book_open_brown.svg"},
            },  # Set the page icon to an external SVG
            "properties": properties,
            "children": children_blocks,
        }
        try:
            response = requests.post(create_page_url, headers=self.headers, json=data)
            response.raise_for_status()
            page_id = response.json().get("id")
            self.logger.info(
                f"Successfully created Notion page: {title} with ID: {page_id}"
            )
            return {"page_id": page_id}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error creating Notion page: {e}")
            if response is not None:
                self.logger.error(f"Notion API response: {response.text}")
            return {"error": str(e)}

    def _create_heading_block(self, content: str, level: int) -> dict:
        heading_type = f"heading_{level}"
        return {
            "object": "block",
            "type": heading_type,
            heading_type: {
                "rich_text": [{"type": "text", "text": {"content": content}}]
            },
        }

    def _split_text_into_blocks(
        self, text: str, block_type: str = "paragraph", max_block_length: int = 2000
    ) -> list:
        blocks = []
        current_block_paragraphs = []  # Store paragraphs for the current block

        # Split text by actual newlines
        paragraphs = text.split("\n")

        for paragraph in paragraphs:
            if not paragraph.strip():
                continue

            # If a single paragraph is too long, split it into smaller chunks
            if len(paragraph) > max_block_length:
                # Flush any existing content before adding chunks of a very long paragraph
                if current_block_paragraphs:
                    blocks.append(
                        self._create_block_with_rich_text(
                            block_type, "\n".join(current_block_paragraphs)
                        )
                    )
                    current_block_paragraphs = []

                # Split the long paragraph into chunks and add them as individual blocks
                for i in range(0, len(paragraph), max_block_length):
                    chunk = paragraph[i : i + max_block_length]
                    blocks.append(self._create_block_with_rich_text(block_type, chunk))
                continue  # Move to the next paragraph

            # Calculate the length if the current paragraph were added to the current block
            # Account for the newline character that will be added if there are multiple paragraphs
            potential_block_content = "\n".join(current_block_paragraphs + [paragraph])

            # If adding this paragraph makes the current block too long,
            # flush the current block and start a new one
            if (
                len(potential_block_content) > max_block_length
                and current_block_paragraphs
            ):
                blocks.append(
                    self._create_block_with_rich_text(
                        block_type, "\n".join(current_block_paragraphs)
                    )
                )
                current_block_paragraphs = [
                    paragraph
                ]  # Start new block with current paragraph
            else:
                current_block_paragraphs.append(paragraph)

        # Add any remaining content in current_block_paragraphs
        if current_block_paragraphs:
            blocks.append(
                self._create_block_with_rich_text(
                    block_type, "\n".join(current_block_paragraphs)
                )
            )

        return blocks

    def _create_block_with_rich_text(self, block_type: str, content: str) -> dict:
        return {
            "object": "block",
            "type": block_type,
            block_type: {"rich_text": [{"type": "text", "text": {"content": content}}]},
        }


if __name__ == "__main__":
    load_dotenv()
    notion_api_key = os.getenv("NOTION_API_KEY")
    notion_database_id = os.getenv("NOTION_DATABASE_ID")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    log_level_str = os.getenv("LOG_LEVEL", "WARNING").upper()

    if not notion_api_key or not notion_database_id or not gemini_api_key:
        raise ValueError(
            "NOTION_API_KEY, NOTION_DATABASE_ID, and GEMINI_API_KEY must be set in .env file"
        )

    # Instantiate NotionClient with the determined log level
    notion_client = NotionClient(
        notion_api_key,
        notion_database_id,
        log_level_str=log_level_str,
    )
    gemini_processor = GeminiProcessor(
        gemini_api_key, log_level_str=log_level_str
    )  # Pass log level to GeminiProcessor as well

    notion_client.logger.info("Logging reading summary...")
