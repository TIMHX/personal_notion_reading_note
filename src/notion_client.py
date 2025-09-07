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
        content_blocks: list,
        subject_id: str,
        assignment_id: str,
    ) -> dict:
        create_page_url = "https://api.notion.com/v1/pages"
        current_date = datetime.now().isoformat()

        # Truncate content blocks to fit Notion's 2000 character limit for rich_text content
        processed_content_blocks = []
        for block in content_blocks:
            if "paragraph" in block and "rich_text" in block["paragraph"]:
                for text_obj in block["paragraph"]["rich_text"]:
                    if "text" in text_obj and "content" in text_obj["text"]:
                        original_content = text_obj["text"]["content"]
                        # Split content into chunks of 2000 characters
                        chunks = [
                            original_content[i : i + 2000]
                            for i in range(0, len(original_content), 2000)
                        ]
                        for chunk in chunks:
                            processed_content_blocks.append(
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
            else:
                processed_content_blocks.append(block)

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

        if self.reading_template_id:
            # First, create the page without children, applying the template
            create_page_data = {
                "parent": {
                    "type": "database_id",
                    "database_id": self.database_id,
                    "template_id": self.reading_template_id,
                },
                "properties": {
                    "title": [{"text": {"content": title}}],
                },
            }
            try:
                response = requests.post(
                    create_page_url, headers=self.headers, json=create_page_data
                )
                response.raise_for_status()
                page_id = response.json().get("id")
                self.logger.info(
                    f"Successfully created Notion page from template: {title} with ID: {page_id}"
                )

                # Then, append the content blocks to the newly created page
                if processed_content_blocks:
                    append_result = self._append_block_children(
                        page_id, processed_content_blocks
                    )
                    if "error" in append_result:
                        self.logger.error(
                            f"Error appending content to page {page_id}: {append_result['error']}"
                        )
                        return {"error": append_result["error"]}

                return {"page_id": page_id}
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error creating Notion page from template: {e}")
                if response is not None:
                    self.logger.error(f"Notion API response: {response.text}")
                return {"error": str(e)}
        else:
            # Existing logic for creating a page without a template
            data = {
                "parent": {"database_id": self.database_id},
                "properties": properties,
                "children": processed_content_blocks,
            }
            try:
                response = requests.post(
                    create_page_url, headers=self.headers, json=data
                )
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
