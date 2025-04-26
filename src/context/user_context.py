from dataclasses import dataclass
from openai import images

@dataclass
class UserContext:
    user_id: str
    preferred_number_of_papers: int = 5
    attachment: object = None