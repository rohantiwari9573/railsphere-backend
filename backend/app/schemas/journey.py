from pydantic import BaseModel


class JourneyResponse(BaseModel):
    train_number: str
    train_name: str
    route_code: str
    start_time: str
    end_time: str