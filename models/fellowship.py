from pydantic import BaseModel
from typing import Optional, List


class Fellowship(BaseModel):
    program_name: str
    institution: Optional[str]
    location: Optional[str]
    director_name: Optional[str]
    faculty_names: Optional[List[str]]
    pgy_level: Optional[str]
    email: Optional[str]
    website: Optional[str]
