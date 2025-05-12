from dataclasses import dataclass
from openai import images
import datetime

@dataclass
class UserContext:
    user_id: str
    preferred_number_of_papers: int = None
    attachment: object = None
    attachment_type: str = None
    attachment_name: str = None
    from_date: datetime.date = None
    to_date: datetime.date = None