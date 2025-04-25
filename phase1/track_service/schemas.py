from pydantic import BaseModel

class AppEvent(BaseModel):
    event_type: str = "page_view"
    user_id: str
    page: str 