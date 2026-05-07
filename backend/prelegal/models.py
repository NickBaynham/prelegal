"""Pydantic models for request/response payloads.

Mirrors frontend/lib/schema.ts so the contract is explicit on both sides.
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from pydantic.functional_validators import AfterValidator

NonEmpty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
NonEmptyMax200 = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]


def _check_calendar_date(value: str) -> str:
    date.fromisoformat(value)
    return value


DateString = Annotated[
    str,
    StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2}$"),
    AfterValidator(_check_calendar_date),
]


class Party(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    print_name: NonEmpty = Field(alias="printName")
    title: NonEmpty
    company: NonEmpty
    notice_address: NonEmpty = Field(alias="noticeAddress")
    signed_date: str = Field(default="", alias="signedDate")


class MndaTermExpires(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["expires"]
    years: int = Field(ge=1, le=50)


class MndaTermContinues(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["continues"]


MndaTerm = Annotated[MndaTermExpires | MndaTermContinues, Field(discriminator="type")]


class TermOfConfidentialityYears(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["years"]
    years: int = Field(ge=1, le=99)


class TermOfConfidentialityPerpetuity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["perpetuity"]


TermOfConfidentiality = Annotated[
    TermOfConfidentialityYears | TermOfConfidentialityPerpetuity,
    Field(discriminator="type"),
]


class NdaFormValues(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    title: NonEmptyMax200
    purpose: NonEmpty
    effective_date: DateString = Field(alias="effectiveDate")
    mnda_term: MndaTerm = Field(alias="mndaTerm")
    term_of_confidentiality: TermOfConfidentiality = Field(alias="termOfConfidentiality")
    governing_law: NonEmpty = Field(alias="governingLaw")
    jurisdiction: NonEmpty
    modifications: str = ""
    parties: tuple[Party, Party]


class PartialParty(BaseModel):
    """A Party where every field is optional, used for incremental AI extraction."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    print_name: str | None = Field(default=None, alias="printName")
    title: str | None = None
    company: str | None = None
    notice_address: str | None = Field(default=None, alias="noticeAddress")
    signed_date: str | None = Field(default=None, alias="signedDate")


class PartialNdaFormValues(BaseModel):
    """An NDA in progress. All fields optional; AI returns only what it confidently extracted.

    party1 maps to parties[0] (the first party on the cover page);
    party2 maps to parties[1].
    """

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    title: str | None = None
    purpose: str | None = None
    effective_date: str | None = Field(default=None, alias="effectiveDate")
    mnda_term: MndaTerm | None = Field(default=None, alias="mndaTerm")
    term_of_confidentiality: TermOfConfidentiality | None = Field(
        default=None, alias="termOfConfidentiality"
    )
    governing_law: str | None = Field(default=None, alias="governingLaw")
    jurisdiction: str | None = None
    modifications: str | None = None
    party1: PartialParty | None = None
    party2: PartialParty | None = None


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    messages: list[ChatMessage]
    current_values: PartialNdaFormValues = Field(alias="currentValues")


class ChatResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    assistant_message: str = Field(alias="assistantMessage")
    extracted_values: PartialNdaFormValues = Field(alias="extractedValues")


class DocumentRow(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class VersionRow(BaseModel):
    id: str
    document_id: str
    version_number: int
    data: NdaFormValues
    rendered_markdown: str
    created_at: str


class DocumentSummary(DocumentRow):
    latest_version_number: int
    latest_version_id: str


class DocumentDetail(BaseModel):
    document: DocumentRow
    latest_version: VersionRow


class CreateDocumentResponse(BaseModel):
    id: str
    latest_version_id: str
    latest_version_number: int


class CreateVersionResponse(BaseModel):
    version_id: str
    version_number: int
