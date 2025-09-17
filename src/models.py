from pydantic import BaseModel, Field
from typing import List, Optional

class PromptConfig(BaseModel):
    name: str
    content: str

class Config(BaseModel):
    reading_folder: str
    subject_id: str
    assignments_id: str
    reading_template_id: Optional[str] = None
    active_prompt: str
    prompts: List[PromptConfig]

class ReadingData(BaseModel):
    key_points: List[str] = Field(..., description="List of key points from the document.")
    notes: str = Field(..., description="Detailed notes and elaboration on the key points.")
    summary: str = Field(..., description="A comprehensive summary of the document.")