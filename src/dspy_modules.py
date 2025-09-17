import dspy
from src.models import ReadingData

class DocumentAnalysisSignature(dspy.Signature):
    """Analyzes a document and extracts key points, notes, and a summary."""

    document = dspy.InputField(desc="The content of the document to be analyzed.")
    reading_data = dspy.OutputField(desc="The structured output containing key points, notes, and a summary.", type=ReadingData)

class ReadingModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_reading_data = dspy.Predict(DocumentAnalysisSignature)

    def forward(self, document):
        return self.generate_reading_data(document=document)