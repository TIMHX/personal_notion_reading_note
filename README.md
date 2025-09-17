# Notion Personal Reading Notes Tracker

A Python tool designed to automate the process of summarizing PDF documents using the Gemini AI model and pushing the processed content to Notion. This project uses `dspy-ai` to structure AI prompts and workflows and `pydantic` for robust data modeling.

## Features

*   **PDF Content Extraction**: Extracts text from PDF files located in a specified directory.
*   **AI-Powered Summarization**: Utilizes the Gemini AI model via a structured DSPy workflow to generate key points, detailed notes, and a comprehensive summary.
*   **Structured Data**: Employs Pydantic models for configuration and data handling, ensuring robustness and type safety.
*   **Notion Integration**: Creates new pages in a specified Notion database with the processed reading notes.
*   **Configurable**: Allows configuration of Notion database IDs and reading folder via a `config.yaml` file.
*   **Logging**: Provides detailed logging for tracking the process and troubleshooting.

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
    This will install the dependencies listed in `pyproject.toml`, including `dspy-ai` and `pydantic`.

## Configuration

1.  **Environment Variables**: Create a `.env` file in the root directory and add the following:
    ```
    NOTION_API_KEY="your_notion_api_key"
    NOTION_DATABASE_ID="your_notion_database_id"
    GEMINI_API_KEY="your_gemini_api_key"
    LOG_LEVEL="WARNING" # Optional: Set to INFO, DEBUG, WARNING, ERROR, CRITICAL
    ```

2.  **`config.yaml`**: Create a `config.yaml` file in the root directory with the following structure:
    ```yaml
    reading_folder: "readings"
    subject_id: "your_notion_subject_relation_id"
    assignments_id: "your_notion_assignments_relation_id"
    # reading_template_id: "your_notion_reading_template_id" # Optional
    ```
    *   `reading_folder`: The directory where your PDF files are located.
    *   `subject_id`: The Notion relation ID for the 'subject' property.
    *   `assignments_id`: The Notion relation ID for the 'assignments' property.

## Usage

1.  Place your PDF documents in the directory specified by `reading_folder` in `config.yaml`.
2.  Run the main script:
    ```bash
    uv run python src/main.py
    ```
    The script will:
    *   Read all PDF files from the `reading_folder`.
    *   Process each PDF using the DSPy module to extract key points, notes, and a summary.
    *   Create a new page in your specified Notion database for each PDF.

## Project Structure

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
    ├── dspy_modules.py       # Defines DSPy signatures and modules for the AI workflow
    ├── gemini_processor.py   # Handles interaction with Gemini AI via DSPy
    ├── logger_utils.py       # Utility for logging
    ├── main.py               # Main script to orchestrate the workflow
    ├── models.py             # Pydantic models for configuration and data
    └── notion_client.py      # Handles interaction with Notion API
```

## Output example (Notion)
![alt text](demo/image.png)
![alt text](demo/image-1.png)
