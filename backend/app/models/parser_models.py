"""Pydantic models for parser and intake data."""

from pydantic import BaseModel, Field
from pydantic import ConfigDict


class W2ParsedData(BaseModel):
    """Only the W-2 fields needed for MVP."""

    box1: float = Field(default=0.0, description="W-2 box 1 wages")
    box2: float = Field(default=0.0, description="W-2 box 2 federal withholding")


class Form1098TParsedData(BaseModel):
    """Only the 1098-T fields needed for MVP."""

    box1: float = Field(default=0.0, description="1098-T box 1 payments received")
    box5: float = Field(default=0.0, description="1098-T box 5 scholarships/grants")


class ParsedTaxData(BaseModel):
    """Normalized parsed data from uploaded documents."""

    model_config = ConfigDict(populate_by_name=True)

    w2: W2ParsedData | None = None
    form_1098t: Form1098TParsedData | None = Field(
        default=None, alias="1098t", serialization_alias="1098t"
    )


class ParseDocumentsResponse(BaseModel):
    """Response contract for parser endpoint."""

    session_id: str
    parsed_data: ParsedTaxData
    source: str = Field(description="mock or parsed")
