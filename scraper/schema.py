
from pydantic import BaseModel, Field, HttpUrl


class BookSchema(BaseModel):
    """Schema for validating extracted book records."""

    title: str = Field(..., description="The title of the book")
    product_url: HttpUrl = Field(..., description="The canonical URL of the book")
    price_text: str = Field(..., description="The raw price text extracted from the page")
    price_gbp: float = Field(..., description="The normalized price as a float in GBP")
    availability_text: str = Field(..., description="The raw availability text")
    rating_text: str = Field(..., description="The raw rating text")
    description: str | None = Field(None, description="The book description, if available")
    source_page: HttpUrl = Field(..., description="The catalogue page where this book was found")
    fetched_at: str = Field(..., description="ISO 8601 timestamp of when the record was fetched")
