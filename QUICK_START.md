# Quick Start Guide - Peer Review Collection

## Installation

```bash
cd data_collection
pip install -r requirements.txt
```

## Collecting Data

### Quick Test (5 manuscripts)
```bash
python collect_reviews.py --config quick_test
```

### Standard Collection (50 manuscripts)
```bash
python collect_reviews.py
```

### Custom Collection
```bash
# 30 manuscripts from F1000Research only
python collect_reviews.py --sources f1000 --num-manuscripts 30

# 20 from eLife only
python collect_reviews.py --sources elife --num-manuscripts 20

# Both sources with custom output
python collect_reviews.py --num-manuscripts 40 --output-dir ./my_data
```

### Comprehensive Collection (100 manuscripts)
```bash
python collect_reviews.py --config comprehensive
```

## Analyzing Collected Data

### View Latest Collection Results
```bash
python analyze_collected_data.py
```

### Analyze Specific Run
```bash
python analyze_collected_data.py collected_data/run_20260112_163251
```

## Output Files

Each collection creates a timestamped directory:
```
collected_data/run_YYYYMMDD_HHMMSS/
├── manuscripts/              # Individual JSON files
├── all_manuscripts.json      # All data combined
├── collection_metadata.json  # Collection stats
├── summary_statistics.json   # Analytics
└── README.txt               # Run summary
```

## Data Structure

### Access Data Programmatically
```python
import json

# Load all manuscripts
with open('collected_data/run_XXXXX/all_manuscripts.json', 'r') as f:
    manuscripts = json.load(f)

# Process each manuscript
for manuscript in manuscripts:
    print(f"Title: {manuscript['title']}")
    print(f"Reviews: {len(manuscript['reviews'])}")

    for review in manuscript['reviews']:
        print(f"  - {review['word_count']} words")
        print(f"  - Recommendation: {review['recommendation']}")
```

### Key Fields
```python
manuscript = {
    'manuscript_id': str,
    'title': str,
    'abstract': str,
    'authors': [str],
    'doi': str,
    'reviews': [
        {
            'review_id': str,
            'review_text': str,
            'word_count': int,
            'recommendation': str,
            'reviewer': {
                'name': str,
                'is_anonymous': bool,
                'affiliation': str
            }
        }
    ]
}
```

## Common Tasks

### Filter Manuscripts with Multiple Reviews
```python
multi_review = [m for m in manuscripts if len(m['reviews']) >= 3]
```

### Find Manuscripts with Disagreements
```python
disagreements = [m for m in manuscripts if m['has_disagreement']]
```

### Export Review Text Only
```python
for manuscript in manuscripts:
    for review in manuscript['reviews']:
        with open(f"review_{review['review_id']}.txt", 'w') as f:
            f.write(review['review_text'])
```

## Troubleshooting

### Few Articles Found
The HTML structure of source sites may have changed. Check logs for discovery errors.

### Rate Limit Errors (429)
Increase delay: `--rate-limit 5.0`

### Connection Errors
Check internet connection and try again. Some articles may be temporarily unavailable.

## Next Steps

1. **Collect more data**: Aim for 30-50 manuscripts
2. **Create gold standard**: Manually synthesize 10-15 briefs
3. **Build DocETL pipeline**: Use collected reviews as input
4. **Evaluate**: Compare pipeline output vs manual briefs

## Support

- Documentation: `data_collection/README.md`
- Test system: `python test_collection.py`
- Analysis: `python analyze_collected_data.py`
