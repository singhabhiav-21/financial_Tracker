from pydantic import BaseModel


class ReportGenerateRequest(BaseModel):
    month: str  # Format: YYYY-MM


class ReportDeleteRequest(BaseModel):
    user_id: int