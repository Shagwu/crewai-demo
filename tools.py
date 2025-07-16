from langchain.tools import BaseTool
from deep_translator import GoogleTranslator
from typing import Type
from pydantic import BaseModel

# Define the input schema
class TranslationInput(BaseModel):
    text: str

# Define the translation tool
class TranslateToFrenchTool(BaseTool):
    name: str = "translate_to_french"
    description: str = "Translates a given English sentence into French"
    args_schema: Type[BaseModel] = TranslationInput

    def _run(self, text: str) -> str:
        try:
            return GoogleTranslator(source='auto', target='french').translate(text)
        except Exception as e:
            return f"Translation failed: {str(e)}"

    def _arun(self, text: str):
        raise NotImplementedError("Async not supported")