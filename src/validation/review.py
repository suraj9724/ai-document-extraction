from pydantic import BaseModel


class ReviewField(BaseModel):
    field: str
    value: str | float | int | None = None
    page: int | None = None
    reason: str


class ReviewResult(BaseModel):
    status: str
    review_fields: list[ReviewField] = []