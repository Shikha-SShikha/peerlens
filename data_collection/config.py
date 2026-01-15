"""
Configuration for peer review data collection.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CollectionConfig:
    """Configuration for data collection run."""

    # Number of manuscripts to collect
    num_manuscripts: int = 50

    # Sources to collect from
    collect_from_elife: bool = True
    collect_from_f1000: bool = True

    # Rate limiting (seconds between requests)
    rate_limit_delay: float = 2.0

    # Filters
    subject_areas: Optional[List[str]] = None
    start_date: Optional[str] = None  # Format: YYYY-MM-DD

    # Output settings
    output_dir: str = "./collected_data"
    save_individual_files: bool = True  # Save each manuscript as separate JSON
    save_combined_file: bool = True     # Save all manuscripts in one JSON
    save_summary_stats: bool = True     # Save collection summary

    # Validation
    min_reviews_per_manuscript: int = 1
    skip_manuscripts_without_reviews: bool = True

    # Logging
    verbose: bool = True


# Default configurations for different scenarios

DEFAULT_CONFIG = CollectionConfig()

QUICK_TEST_CONFIG = CollectionConfig(
    num_manuscripts=5,
    collect_from_elife=True,
    collect_from_f1000=True,
    rate_limit_delay=1.0,
)

COMPREHENSIVE_CONFIG = CollectionConfig(
    num_manuscripts=100,
    collect_from_elife=True,
    collect_from_f1000=True,
    rate_limit_delay=2.0,
    save_individual_files=True,
    save_combined_file=True,
    save_summary_stats=True,
)

ELIFE_ONLY_CONFIG = CollectionConfig(
    num_manuscripts=50,
    collect_from_elife=True,
    collect_from_f1000=False,
    rate_limit_delay=2.0,
)

F1000_ONLY_CONFIG = CollectionConfig(
    num_manuscripts=50,
    collect_from_elife=False,
    collect_from_f1000=True,
    rate_limit_delay=2.0,
)
