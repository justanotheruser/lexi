from pydantic import BaseModel


class StoryCreationParams(BaseModel):
    """Story parameters for story creation (input by user)"""

    target_language_code: str
    protagonist: str
    setting: str
    native_language_code: str
