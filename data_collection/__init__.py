"""
Peer review data collection package.

Collects openly published peer reviews from multiple sources including
eLife and F1000Research for use in editorial synthesis research.
"""

__version__ = "1.0.0"

from .schema import (
    Manuscript,
    Review,
    Reviewer,
    AuthorResponse,
    EditorialAssessment,
    ReviewSource,
    ReviewDecision,
    CollectionMetadata,
)

from .config import (
    CollectionConfig,
    DEFAULT_CONFIG,
    QUICK_TEST_CONFIG,
    COMPREHENSIVE_CONFIG,
    ELIFE_ONLY_CONFIG,
    F1000_ONLY_CONFIG,
)

__all__ = [
    'Manuscript',
    'Review',
    'Reviewer',
    'AuthorResponse',
    'EditorialAssessment',
    'ReviewSource',
    'ReviewDecision',
    'CollectionMetadata',
    'CollectionConfig',
    'DEFAULT_CONFIG',
    'QUICK_TEST_CONFIG',
    'COMPREHENSIVE_CONFIG',
    'ELIFE_ONLY_CONFIG',
    'F1000_ONLY_CONFIG',
]
