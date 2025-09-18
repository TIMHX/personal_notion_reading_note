from pydantic import BaseModel, Field
import dspy


class ReadingNotes(BaseModel):
    key_points: list[str] = Field(
        ...,
        description="Directly and comprehensively list all core information from the document. Focus on extracting and explaining key concepts, important definitions, core principles, and key terminology, especially content that is highlighted in the original text (e.g., in bold). Each point should be independent, clear, and contain sufficient context or explanation, rather than being a mere list of single words, presented as a bulleted list with no sub bullet.",
    )
    notes: str = Field(
        ...,
        description="Provide a detailed elaboration and supplement to the key information. Explain the logical relationships, hierarchical structure, and interconnections among the various key points. Provide a more in-depth explanation of important theories or models, and describe their practical applications or significance. This section should serve as a deeper dive and extension of the 'Key Points,' not as personal reflection, presented in paragraph form.",
    )
    summary: str = Field(
        ...,
        description="Provide a comprehensive and detailed summary of the document's content. This summary must cover all the information listed in the 'Key Points' and be organized according to the logical sequence of the original text. Ensure the summary is of sufficient length to completely reproduce the core content of the document, including major theories, the evidence or examples that support them, and the final conclusions drawn. The summary should strive for completeness of content and accuracy of information, avoiding the omission of any critical details, presented in paragraph form.",
    )


class DocumentProcessor(dspy.Signature):
    """
    Perform an in-depth analysis of the following textbook document and provide the following content.
    Ensure that each section is detailed, clear, and includes as much key information and detail as possible.
    """

    document_content: str = dspy.InputField(
        desc="The content of the document to be processed."
    )
    processed_document: ReadingNotes = dspy.OutputField(
        desc="The extracted key points, notes, and summary in JSON format."
    )


class ProcessDocument(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_notes = dspy.ChainOfThought(DocumentProcessor)

    def forward(self, document_content):
        response = self.generate_notes(document_content=document_content)
        return response
