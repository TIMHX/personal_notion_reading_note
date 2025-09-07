# Notion Personal Reading Notes Tracker

A Python tool designed to automate the process of summarizing PDF documents using the Gemini AI model and pushing the processed content, including key points, notes, summary, and the original content, to Notion. This helps in organizing and tracking personal reading notes efficiently.

## Features

*   **PDF Content Extraction**: Extracts text from PDF files located in a specified directory.
*   **AI-Powered Summarization**: Utilizes the Gemini AI model to generate key points, detailed notes, and a comprehensive summary of the extracted text.
*   **Notion Integration**: Creates new pages in a specified Notion database with the processed reading notes, including structured content (key points as bulleted lists, summary and notes as paragraphs, and original content with proper headings).
*   **Configurable**: Allows configuration of Notion database IDs and reading folder via a `config.yaml` file.
*   **Logging**: Provides detailed logging for tracking the process and troubleshooting. Log files are generated in the `logging/app.log` file.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/TIMHX/personal_notion_reading_note.git
    cd personal_notion_reading_note
    ```

2.  **Install uv**:
    If you don't have `uv` installed, you can install it using `pip`:
    ```bash
    pip install uv
    ```

3.  **Install dependencies**:
    ```bash
    uv sync
    ```
    This will install the dependencies listed in `pyproject.toml`.

## Configuration

1.  **Environment Variables**: Create a `.env` file in the root directory and add the following:
    ```
    NOTION_API_KEY="your_notion_api_key"
    NOTION_DATABASE_ID="your_notion_database_id"
    GEMINI_API_KEY="your_gemini_api_key"
    LOG_LEVEL="WARNING" # Optional: Set to INFO, DEBUG, WARNING, ERROR, CRITICAL
    ```
    *   `NOTION_API_KEY`: Obtain this from your Notion integration settings.
    *   `NOTION_DATABASE_ID`: The ID of the Notion database where reading notes will be stored.
    *   `GEMINI_API_KEY`: Your API key for the Google Gemini AI model.

2.  **`config.yaml`**: Create a `config.yaml` file in the root directory with the following structure:
    ```yaml
    reading_folder: "readings"
    subject_id: "your_notion_subject_relation_id"
    assignments_id: "your_notion_assignments_relation_id"
    # reading_template_id: "your_notion_reading_template_id" # Optional
    ```
    *   `reading_folder`: The directory where your PDF files are located (e.g., `readings/`).
    *   `subject_id`: The Notion relation ID for the 'subject' property in your database.
    *   `assignments_id`: The Notion relation ID for the 'assignments' property in your database.
    *   `reading_template_id`: (Optional) The ID of a Notion template to use when creating new reading pages.
    *   `prompts`: A list of prompt configurations for the Gemini AI. Each prompt has a `name` and `content`.
    *   `active_prompt`: The name of the prompt to be used for processing documents. This should match one of the `name` values in the `prompts` list.

## Usage

1.  Place your PDF documents in the directory specified by `reading_folder` in `config.yaml` (e.g., `./readings/`). For demonstration purposes, `readings/AI_ch1-1.pdf` will be used as an example.
2.  Run the main script:
    ```bash
    uv run src/main.py
    ```
    The script will:
    *   Read all PDF files from the `reading_folder`.
    *   Process each PDF using the Gemini AI to extract key points, notes, and a summary.
    *   Create a new page in your specified Notion database for each PDF, populating it with the extracted information and the original content.

## Output example (Notion)
![alt text](image.png)


## Project Structure

## Usage of MCPs (Model Context Protocol) during Development

This project leverages the Model Context Protocol (MCP) for enhanced development and interaction with external services. Specifically, it integrates with:

*   **Notion MCP**: Used for direct interaction with the Notion API, allowing for programmatic creation and management of Notion pages and databases. This is crucial for the core functionality of pushing reading notes to Notion.
*   **Context7**: Utilized for retrieving up-to-date documentation and code examples for various libraries. This aids in understanding and implementing features by providing relevant context during development.
*   **Gemini-2.5-Pro**: The Gemini AI model is used for summarizing PDF content, extracting key points, and generating detailed notes. During development, the Gemini-2.5-Pro model can be used for more advanced summarization and content generation tasks.

## Notion API Usage in `src/notion_client.py`

The `src/notion_client.py` file is responsible for all interactions with the Notion API. It uses the `requests` library to make HTTP requests to the Notion API endpoints.

Key functionalities and API endpoints used:

*   **Initialization (`__init__`)**:
    *   Stores the Notion API key, database ID, and an optional reading template ID.
    *   Sets up `Authorization` headers with the API key and `Notion-Version` to `2022-06-28`.
    *   Initializes a logger for tracking API interactions.

*   **Creating a Reading Page (`create_reading_page`)**:
    *   **Endpoint**: `POST https://api.notion.com/v1/pages`
    *   **Purpose**: Creates a new page in the specified Notion database.
    *   **Payload**:
        *   `parent`: Specifies the `database_id` where the page will be created.
        *   `icon`: Sets an external SVG icon (e.g., `https://www.notion.so/icons/book_open_brown.svg`) for the new page. For more details on Notion page icons via API, refer to this [Reddit post](https://www.reddit.com/r/Notion/comments/10mld67/notion_page_icons_through_api/).
        *   `properties`: Defines the page's properties, including:
            *   `notes`: The title of the page.
            *   `review level`: A select property set to "📖 reading".
            *   `day`: The creation date of the page.
            *   `subject` and `assignments`: Relation properties linked by their IDs.
        *   `children`: An array of block objects that form the content of the page. This includes:
            *   A `column_list` block containing two `column` blocks for "Key Points" and "Summary and Notes".
            *   `heading_3` blocks for "Key Points", "Summary", and "Notes".
            *   `bulleted_list_item` blocks for individual key points.
            *   `paragraph` blocks for summary and notes content.
            *   A `heading_2` block for "Original Content".
            *   Dynamically created `heading_1`, `heading_2`, `heading_3`, and `paragraph` blocks for the original PDF content, handling chunking for large paragraphs.
    *   **Error Handling**: Logs errors and Notion API responses for debugging.

*   **Creating Heading Blocks (`_create_heading_block`)**:
    *   A helper method to construct Notion heading blocks (h1, h2, h3) with rich text content.

This client abstracts the complexities of the Notion API, providing a clean interface for the main application to create and populate Notion pages with structured reading notes.

```
.
├── .env                  # Environment variables (API keys)
├── .gitignore            # Git ignore file
├── config.yaml           # Configuration for reading folder and Notion IDs
├── pyproject.toml        # Project metadata and dependencies
├── README.md             # This README file
├── uv.lock               # Dependency lock file
└── src/
    ├── __init__.py
    ├── gemini_processor.py   # Handles interaction with Gemini AI for summarization
    ├── logger_utils.py       # Utility for logging
    ├── main.py               # Main script to orchestrate PDF processing and Notion integration
    └── notion_client.py      # Handles interaction with Notion API for page creation
