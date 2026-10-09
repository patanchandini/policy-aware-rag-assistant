from datetime import date
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID


class AccessLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class SourceType(str, Enum):
    PRODUCT_DOC = "product_doc"
    FAQ = "faq"
    POLICY = "policy"
    TROUBLESHOOTING = "troubleshooting"


class DocumentMetadata(BaseModel):
    doc_id: str
    version: str
    product: str
    region: str
    access_level: AccessLevel
    effective_date: date
    expiry_date: Optional[date] = None
    source_type: SourceType
    supersedes: List[str] = Field(default_factory=list)
    citation_label: str


class Chunk(BaseModel):
    id: UUID
    content: str
    metadata: DocumentMetadata
    similarity: float = 0.0


class UserContext(BaseModel):
    user_id: str
    access_levels: List[AccessLevel]
    authorized_products: List[str]
    authorized_regions: List[str]


class QueryType(str, Enum):
    CURRENT = "current"
    HISTORICAL = "historical"


class ParsedQuery(BaseModel):
    raw_query: str
    query_type: QueryType
    target_date: Optional[date] = None
    product: Optional[str] = None
    region: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    user_context: UserContext
    historical_date: Optional[date] = None


class Citation(BaseModel):
    citation_label: str
    doc_id: str
    version: str
    effective_date: date


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation] = Field(default_factory=list)
    refused: bool = False
    refusal_reason: Optional[str] = None
    clarification_needed: bool = False
    clarification_question: Optional[str] = None