"""Pydantic models for request/response payloads.

Mirrors frontend/lib/schema.ts so the contract is explicit on both sides.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonEmpty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
NonEmptyMax200 = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]
DateString = Annotated[str, StringConstraints(pattern=r"^\d{4}-\d{2}-\d{2}$")]


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
