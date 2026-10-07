from pydantic import BaseModel


class ReviewField(BaseModel):
    # Name/path of the field that needs attention.
    # Example: "seller.state"
    field: str

    # The value that the AI extracted.
    value: str | None = None

    # Explanation of why the field needs review.
    reason: str


class ReviewResult(BaseModel):
    # Overall processing status.
    # Either "accepted" or "needs_review".
    status: str

    # Individual fields that require human attention.
    review_fields: list[ReviewField] = []