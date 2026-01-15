"""
Unified data schema for peer review collection from multiple sources.
Ensures consistency across eLife, F1000Research, and other platforms.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ReviewSource(Enum):
    """Source platform for the review."""
    ELIFE = "elife"
    F1000RESEARCH = "f1000research"
    BIORXIV = "biorxiv"
    OTHER = "other"


class ReviewDecision(Enum):
    """Editorial decision types."""
    ACCEPT = "accept"
    REJECT = "reject"
    REVISE = "revise"
    PENDING = "pending"
    NO_DECISION = "no_decision"  # For platforms like eLife that don't make binary decisions


@dataclass
class Reviewer:
    """Individual reviewer information."""
    reviewer_id: str
    name: Optional[str] = None  # May be anonymous
    affiliation: Optional[str] = None
    is_anonymous: bool = True


@dataclass
class Review:
    """Individual peer review content and metadata."""
    review_id: str
    reviewer: Reviewer
    review_text: str
    recommendation: Optional[str] = None  # e.g., "accept", "major revisions"
    date_submitted: Optional[str] = None
    version_reviewed: int = 1

    # Structured extractions (if available)
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    major_issues: Optional[List[str]] = None
    minor_issues: Optional[List[str]] = None
    confidence_score: Optional[str] = None

    # Metadata
    word_count: int = 0

    def __post_init__(self):
        if self.review_text and self.word_count == 0:
            self.word_count = len(self.review_text.split())


@dataclass
class AuthorResponse:
    """Author's response to reviews."""
    response_id: str
    response_text: str
    date_submitted: Optional[str] = None
    version: int = 1


@dataclass
class EditorialAssessment:
    """Editorial assessment/summary (if available, e.g., from eLife)."""
    assessment_id: str
    assessment_text: str
    significance: Optional[str] = None  # e.g., "landmark", "important", "useful"
    strength_of_evidence: Optional[str] = None  # e.g., "exceptional", "solid", "inadequate"
    date_submitted: Optional[str] = None


@dataclass
class Manuscript:
    """Complete manuscript with all associated reviews and metadata."""

    # Core identifiers
    manuscript_id: str
    source: ReviewSource
    source_url: str

    # Article metadata
    title: str
    abstract: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    subject_areas: List[str] = field(default_factory=list)

    # Dates
    preprint_date: Optional[str] = None
    submission_date: Optional[str] = None
    publication_date: Optional[str] = None

    # DOI and identifiers
    doi: Optional[str] = None
    preprint_doi: Optional[str] = None

    # Review content
    reviews: List[Review] = field(default_factory=list)
    author_responses: List[AuthorResponse] = field(default_factory=list)
    editorial_assessments: List[EditorialAssessment] = field(default_factory=list)

    # Editorial decision
    decision: ReviewDecision = ReviewDecision.PENDING
    decision_date: Optional[str] = None

    # Statistics
    num_reviews: int = 0
    review_rounds: int = 1

    # Metadata
    collection_date: str = field(default_factory=lambda: datetime.now().isoformat())
    raw_data: Dict[str, Any] = field(default_factory=dict)  # Store original API response

    def __post_init__(self):
        if self.num_reviews == 0:
            self.num_reviews = len(self.reviews)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, handling enums properly."""
        result = asdict(self)
        result['source'] = self.source.value
        result['decision'] = self.decision.value
        return result

    def get_review_summary(self) -> Dict[str, Any]:
        """Get summary statistics about reviews."""
        return {
            'total_reviews': len(self.reviews),
            'anonymous_reviews': sum(1 for r in self.reviews if r.reviewer.is_anonymous),
            'named_reviews': sum(1 for r in self.reviews if not r.reviewer.is_anonymous),
            'total_words': sum(r.word_count for r in self.reviews),
            'avg_words_per_review': sum(r.word_count for r in self.reviews) / len(self.reviews) if self.reviews else 0,
            'has_author_response': len(self.author_responses) > 0,
            'has_editorial_assessment': len(self.editorial_assessments) > 0,
        }

    def has_disagreement(self) -> bool:
        """Check if reviews have differing recommendations (basic heuristic)."""
        recommendations = [r.recommendation for r in self.reviews if r.recommendation]
        return len(set(recommendations)) > 1

    def validate(self) -> List[str]:
        """Validate manuscript data and return list of issues."""
        issues = []

        if not self.manuscript_id:
            issues.append("Missing manuscript_id")
        if not self.title:
            issues.append("Missing title")
        if not self.source_url:
            issues.append("Missing source_url")
        if len(self.reviews) == 0:
            issues.append("No reviews found")

        for i, review in enumerate(self.reviews):
            if not review.review_text or len(review.review_text.strip()) < 50:
                issues.append(f"Review {i+1} has insufficient text (< 50 chars)")

        return issues


@dataclass
class CollectionMetadata:
    """Metadata about the data collection run."""
    collection_id: str
    source: ReviewSource
    start_time: str
    end_time: Optional[str] = None
    num_manuscripts_attempted: int = 0
    num_manuscripts_successful: int = 0
    num_manuscripts_failed: int = 0
    errors: List[Dict[str, str]] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['source'] = self.source.value
        return result
