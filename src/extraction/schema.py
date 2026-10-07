from pydantic import BaseModel


class ExtractedValue(BaseModel):
    """
    Stores an extracted value together with
    the page where the value was found.
    """
    value: str | None = None
    page: int | None = None


class InvoiceItem(BaseModel):
    description: str | None = None
    quantity: float | None = None
    unit_price: float | None = None
    amount: float | None = None

    # Page containing this line item
    page: int | None = None


class Party(BaseModel):
    name: str
    city: str | None = None
    state: str | None = None
    country: str | None = None


class Invoice(BaseModel):
    invoice_number: str | None = None
    invoice_date: str | None = None

    seller: Party | None = None
    customer: Party | None = None

    items: list[InvoiceItem] = []

    subtotal: float | None = None
    gst: float | None = None
    total: float | None = None