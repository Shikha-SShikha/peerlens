# Peer Review Data Collection System

A comprehensive system for collecting openly published peer reviews from multiple sources (eLife, F1000Research) for research on editorial synthesis and decision-making.

## Overview

This package provides:
- **Unified data schema** for peer review data across sources
- **Automated collectors** for eLife and F1000Research
- **Configurable collection** with filtering and validation
- **Structured output** in JSON format with metadata

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Quick Test (5 manuscripts)

```bash
python collect_reviews.py --config quick_test
```

### 2. Default Collection (50 manuscripts from both sources)

```bash
python collect_reviews.py
```

### 3. Custom Collection

```bash
# Collect 30 manuscripts from eLife only
python collect_reviews.py --sources elife --num-manuscripts 30

# Collect from both sources with custom output directory
python collect_reviews.py --num-manuscripts 20 --output-dir ./my_data

# Comprehensive collection (100 manuscripts)
python collect_reviews.py --config comprehensive
```

## Configuration Options

### Predefined Configs

- `default`: 50 manuscripts from both sources
- `quick_test`: 5 manuscripts for testing
- `comprehensive`: 100 manuscripts with full metadata
- `elife_only`: 50 manuscripts from eLife only
- `f1000_only`: 50 manuscripts from F1000Research only

### Command Line Options

```bash
python collect_reviews.py --help
```

Options:
- `--config`: Choose predefined configuration
- `--num-manuscripts`: Number of manuscripts to collect
- `--sources`: Sources to collect from (elife, f1000)
- `--output-dir`: Output directory path
- `--rate-limit`: Delay between requests in seconds

## Output Structure

Each collection run creates a timestamped directory:

```
collected_data/
└── run_20260112_143022/
    ├── README.txt                      # Run summary
    ├── manuscripts/                     # Individual manuscript files
    │   ├── elife_97433.json
    │   ├── elife_95132.json
    │   └── f1000_1-1655.json
    ├── all_manuscripts.json            # All manuscripts combined
    ├── collection_metadata.json        # Collection process metadata
    └── summary_statistics.json         # Summary statistics
```

## Data Schema

### Manuscript Object

```json
{
  "manuscript_id": "97433",
  "source": "elife",
  "source_url": "https://elifesciences.org/reviewed-preprints/97433",
  "title": "Article Title",
  "abstract": "Article abstract...",
  "authors": ["Author 1", "Author 2"],
  "doi": "10.7554/eLife.97433",
  "reviews": [...],
  "editorial_assessments": [...],
  "author_responses": [...],
  "publication_date": "2025-01-15",
  "num_reviews": 3
}
```

### Review Object

```json
{
  "review_id": "97433_review_1",
  "reviewer": {
    "reviewer_id": "97433_reviewer_1",
    "name": "John Smith",
    "affiliation": "University X",
    "is_anonymous": false
  },
  "review_text": "This manuscript...",
  "recommendation": "accept",
  "word_count": 850
}
```

## Use Cases

### For POC Development

Collect a diverse test set for building the DocETL synthesis pipeline:

```bash
# Get 30 manuscripts with various characteristics
python collect_reviews.py --num-manuscripts 30 --sources elife f1000
```

### For Evaluation

Build a gold standard dataset:

```bash
# Comprehensive collection for evaluation
python collect_reviews.py --config comprehensive
```

### For Specific Domains

Currently collecting across all domains, but can be extended to filter by subject area.

## Data Sources

### eLife

- **Model**: Reviewed Preprints (publish, then review)
- **Peer Review**: All reviews published openly
- **Features**: Editorial assessments with significance ratings
- **Decisions**: No accept/reject (all are published)

### F1000Research

- **Model**: Post-publication peer review
- **Peer Review**: Openly published with reviewer names
- **Features**: Approval status (Approved/Approved with Reservations/Not Approved)
- **Decisions**: Approval-based rather than accept/reject

## Key Features

### 1. Comprehensive Metadata

- Full article information (title, authors, abstract, DOI)
- Complete review text with word counts
- Reviewer information (when available)
- Editorial assessments (eLife)
- Author responses to reviews
- Timestamps and version information

### 2. Quality Validation

- Validates presence of required fields
- Checks review text length
- Identifies manuscripts without reviews
- Reports validation issues in summary

### 3. Statistics & Analytics

- Total manuscripts and reviews collected
- Word count statistics
- Success/failure rates per source
- Manuscripts with disagreements
- Validation issues

### 4. Respectful Scraping

- Configurable rate limiting (default: 2 seconds)
- User agent identification
- Error handling and retry logic
- Minimal server load

## Advanced Usage

### Programmatic Use

```python
from data_collection import CollectionConfig, ElifeCollector

# Create custom config
config = CollectionConfig(
    num_manuscripts=20,
    rate_limit_delay=3.0,
    skip_manuscripts_without_reviews=True
)

# Use individual collector
collector = ElifeCollector(rate_limit_delay=2.0)
manuscripts, metadata = collector.collect_manuscripts(num_manuscripts=10)

# Process manuscripts
for manuscript in manuscripts:
    print(f"{manuscript.title}: {len(manuscript.reviews)} reviews")
    summary = manuscript.get_review_summary()
    print(f"  Total words: {summary['total_words']}")
```

### Filtering and Validation

```python
# Filter manuscripts
high_quality = [
    m for m in manuscripts
    if len(m.reviews) >= 2 and not m.validate()
]

# Find manuscripts with disagreements
conflicted = [
    m for m in manuscripts
    if m.has_disagreement()
]
```

## Troubleshooting

### Few articles discovered

If the collectors find few articles, they use fallback article IDs. The HTML structure of source websites may have changed. Check the `_discover_articles` methods in the collectors.

### Rate limit errors

If you get 429 errors, increase the rate limit delay:

```bash
python collect_reviews.py --rate-limit 5.0
```

### Validation errors

Check `summary_statistics.json` for details on validation issues. Common issues:
- Missing reviews
- Very short review text (< 50 chars)
- Missing required metadata

## Next Steps

After collecting data:

1. **Analyze the dataset**: Review `summary_statistics.json`
2. **Build gold standard**: Manually synthesize a few manuscripts for evaluation
3. **Develop DocETL pipeline**: Use collected reviews as input
4. **Evaluate synthesis quality**: Compare against manual synthesis

## Contributing

To add a new data source:

1. Create a new collector in `collectors/` (e.g., `bioRxiv_collector.py`)
2. Inherit from base patterns in existing collectors
3. Map to unified schema in `schema.py`
4. Add configuration in `config.py`
5. Update orchestrator in `collect_reviews.py`

## License & Ethics

- **Use responsibly**: Respect rate limits and terms of service
- **Data privacy**: Peer reviews are publicly available; still handle respectfully
- **Attribution**: Credit eLife and F1000Research in any publications
- **Research only**: This tool is for research and educational purposes

## References

- eLife Peer Review: https://elifesciences.org/about/peer-review
- F1000Research Open Peer Review: https://f1000research.com/for-authors/peer-review
- DocETL: https://ucbepic.github.io/docetl/
