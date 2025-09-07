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
        content_to_process: str,  # Changed from content_blocks to raw text
        subject_id: str,
        assignment_id: str,
        key_points: list = None,
        notes: str = None,
        summary: str = None,
    ) -> dict:
        create_page_url = "https://api.notion.com/v1/pages"
        current_date = datetime.now().isoformat()

        children_blocks = []

        # Add Key Points as bulleted list
        if key_points:
            children_blocks.append(
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "Key Points"}}
                        ]
                    },
                }
            )
            for point in key_points:
                children_blocks.append(
                    {
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": point}}]
                        },
                    }
                )

        # Add Notes as paragraph
        if notes:
            children_blocks.append(
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "Notes"}}]
                    },
                }
            )
            for paragraph in notes.split("\n"):
                if paragraph.strip():
                    children_blocks.append(
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {"type": "text", "text": {"content": paragraph}}
                                ]
                            },
                        }
                    )

        # Add Summary as paragraph
        if summary:
            children_blocks.append(
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": "Summary"}}]
                    },
                }
            )
            for paragraph in summary.split("\n"):
                if paragraph.strip():
                    children_blocks.append(
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {"type": "text", "text": {"content": paragraph}}
                                ]
                            },
                        }
                    )

        # Process original content_to_process for paragraphs and headers
        if content_to_process:
            children_blocks.append(
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "Original Content"}}
                        ]
                    },
                }
            )
            for line in content_to_process.split("\n"):
                if line.strip():
                    if line.startswith("### "):
                        children_blocks.append(self._create_heading_block(line[4:], 3))
                    elif line.startswith("## "):
                        children_blocks.append(self._create_heading_block(line[3:], 2))
                    elif line.startswith("# "):
                        children_blocks.append(self._create_heading_block(line[2:], 1))
                    else:
                        # Split paragraph content into chunks of 2000 characters
                        chunks = [line[i : i + 2000] for i in range(0, len(line), 2000)]
                        for chunk in chunks:
                            children_blocks.append(
                                {
                                    "object": "block",
                                    "type": "paragraph",
                                    "paragraph": {
                                        "rich_text": [
                                            {"type": "text", "text": {"content": chunk}}
                                        ]
                                    },
                                }
                            )

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

    def _append_block_children(self, block_id: str, children: list) -> dict:
        append_block_children_url = (
            f"https://api.notion.com/v1/blocks/{block_id}/children"
        )
        data = {"children": children}
        try:
            response = requests.patch(
                append_block_children_url, headers=self.headers, json=data
            )
            response.raise_for_status()
            self.logger.info(f"Successfully appended blocks to {block_id}")
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error appending blocks to {block_id}: {e}")
            if response is not None:
                self.logger.error(f"Notion API response: {response.text}")
            return {"error": str(e)}


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
