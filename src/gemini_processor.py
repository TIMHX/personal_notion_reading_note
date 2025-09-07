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

    def process_document(self, text: str) -> dict:
        prompt = f"""
        请对以下文档进行处理，并提供以下内容：
        1. **要点 (Key Points)**：文档的主要观点或重要信息，以项目符号列表形式呈现。
        2. **笔记 (Notes)**：对文档内容的个人理解、思考或补充说明，以段落形式呈现。
        3. **摘要 (Summary)**：文档的详细总结，以段落形式呈现。

        请确保输出格式如下，并使用明确的标题分隔每个部分：

        **要点**
        *   [要点 1]
        *   [要点 2]
        *   [要点 3]

        **笔记**
        [您的笔记内容]

        **摘要**
        [您的摘要内容]

        文档:
        ---
        {text}
        ---
        """
        try:
            self.logger.debug(
                f"Sending document processing prompt to Gemini:\n{prompt}"
            )
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            key_points = []
            notes = ""
            summary = ""

            # 解析响应
            parts = response_text.split("**")
            for i, part in enumerate(parts):
                if "要点" in part:
                    kp_content = parts[i + 1].strip()
                    key_points = [
                        item.strip().replace("* ", "")
                        for item in kp_content.split("\n")
                        if item.strip().startswith("*")
                    ]
                elif "笔记" in part:
                    notes = parts[i + 1].strip()
                elif "摘要" in part:
                    summary = parts[i + 1].strip()

            return {"key_points": key_points, "notes": notes, "summary": summary}
        except Exception as e:
            self.logger.error(f"Error processing document with Gemini: {e}")
            return {
                "key_points": [],
                "notes": "Error generating notes.",
                "summary": "Error generating summary.",
            }


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
