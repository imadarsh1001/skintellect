"""Validated Gemini outputs. Quotes and identities receive additional deterministic checks."""
import re
import unicodedata
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')


KNOWN_ASPECTS=('texture','hydration','stickiness','pilling','stinging','scent','absorption','value')
Aspect = Annotated[str,Field(min_length=1,max_length=64,pattern=r'^[a-z][a-z0-9_]*$')]

def normalize_aspect(value):
    if not isinstance(value,str):return value
    label=unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower().strip()
    label=re.sub(r'[^a-z0-9]+','_',label).strip('_')
    aliases={'fragrance':'scent','smell':'scent','absorbency':'absorption','cost':'value'}
    return aliases.get(label,label)


class ReviewObservation(StrictModel):
    review_id: int
    aspect: Aspect
    sentiment: Literal['positive','negative','neutral','mixed']
    negated: bool
    quote: str = Field(min_length=1, max_length=1500)

    _normalize_aspect=field_validator('aspect',mode='before')(normalize_aspect)


class ReviewExtraction(StrictModel):
    observations: list[ReviewObservation] = Field(max_length=150)


class EvidenceSelection(StrictModel):
    evidence_id: str
    topic: Aspect
    quote: str = Field(min_length=1, max_length=700)

    _normalize_topic=field_validator('topic',mode='before')(normalize_aspect)


class ResearchAnswer(StrictModel):
    selections: list[EvidenceSelection] = Field(max_length=6)
    unanswered_topics: list[str] = Field(max_length=8)


class ResearchPlan(StrictModel):
    tools: list[Literal['reviews','alternatives','retrieve']] = Field(max_length=3)


class ExtractionRequest(StrictModel):
    product_id: int
    limit: int = Field(default=10, ge=1, le=20)


class LabelExtraction(StrictModel):
    ingredients: list[str] = Field(max_length=150)
    uncertain_text: list[str] = Field(max_length=30)
    appears_complete: bool


from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid')


KNOWN_ASPECTS=('texture','hydration','stickiness','pilling','stinging','scent','absorption','value')
Aspect = Annotated[str,Field(min_length=1,max_length=64,pattern=r'^[a-z][a-z0-9_]*$')]

def normalize_aspect(value):
    if not isinstance(value,str):return value
    label=unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower().strip()
    label=re.sub(r'[^a-z0-9]+','_',label).strip('_')
    aliases={'fragrance':'scent','smell':'scent','absorbency':'absorption','cost':'value'}
    return aliases.get(label,label)


class ReviewObservation(StrictModel):
    review_id: int
    aspect: Aspect
    sentiment: Literal['positive','negative','neutral','mixed']
    negated: bool
    quote: str = Field(min_length=1, max_length=1500)

    _normalize_aspect=field_validator('aspect',mode='before')(normalize_aspect)


class ReviewExtraction(StrictModel):
    observations: list[ReviewObservation] = Field(max_length=150)


class EvidenceSelection(StrictModel):
    evidence_id: str
    topic: Aspect
    quote: str = Field(min_length=1, max_length=700)

    _normalize_topic=field_validator('topic',mode='before')(normalize_aspect)


class ResearchAnswer(StrictModel):
    selections: list[EvidenceSelection] = Field(max_length=6)
    unanswered_topics: list[str] = Field(max_length=8)


class ResearchPlan(StrictModel):
    tools: list[Literal['reviews','alternatives','retrieve']] = Field(max_length=3)


class ExtractionRequest(StrictModel):
    product_id: int
    limit: int = Field(default=10, ge=1, le=20)


class LabelExtraction(StrictModel):
    ingredients: list[str] = Field(max_length=150)
    uncertain_text: list[str] = Field(max_length=30)
    appears_complete: bool


class DecisionReviewInput(StrictModel):
    id: int = Field(ge=1)
    text: str = Field(min_length=1,max_length=12000)

    @field_validator('text')
    @classmethod
    def nonblank_text(cls,value):
        if not value.strip():raise ValueError('Review text must not be blank')
        return value


class ReviewDecisionRequest(StrictModel):
    reviews: list[DecisionReviewInput] = Field(min_length=1,max_length=5)

    @model_validator(mode='after')
    def unique_reviews(self):
        if len({r.id for r in self.reviews})!=len(self.reviews):
            raise ValueError('Review IDs must be unique')
        return self



from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class SearchIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: str = "all"
    domain: Literal["skin", "hair", "body", "makeup", "all"] = "skin"
    required_ingredients: list[str] = Field(default_factory=list, max_length=20)
    excluded_ingredients: list[str] = Field(default_factory=list, max_length=20)
    preferred_price_tiers: list[Literal["$", "$$", "$$$", "$$$$"]] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list, max_length=20)
    unresolved_terms: list[str] = Field(default_factory=list)
    text: str = Field(default="", max_length=2000)
    limit: int = Field(default=10, ge=1, le=50)

class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)

class AlternativeRequest(BaseModel):
    product_id: int
    constraints: SearchIntent = Field(default_factory=SearchIntent)
    product_ids: list[Annotated[int,Field(ge=1)]] | None = Field(default=None,min_length=1,max_length=10)
