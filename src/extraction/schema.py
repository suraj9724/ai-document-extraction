from pydantic import BaseModel


class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    amount: float


class Party(BaseModel):
    name: str
    city: str | None = None
    state: str | None = None


class Invoice(BaseModel):
    invoice_number: str | None = None
    invoice_date: str | None = None

    seller: Party | None = None
    customer: Party | None = None

    items: list[InvoiceItem] = []

    subtotal: float | None = None
    gst: float | None = None
    total: float | None = None