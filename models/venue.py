from pydantic import BaseModel


class Venue(BaseModel):
    """
    Represents the data structure of a Venue.
    """

    name: str
    PGY: str
    Image_link: str
