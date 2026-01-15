#!/usr/bin/env python3
"""
Prepare collected peer review data for DocETL pipeline.

Transforms manuscript JSON files into review-level records suitable for
map-reduce processing.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any


def prepare_reviews_for_pipeline(manuscripts_file: str, output_file: str):
    """
    Convert manuscript data into review-level records for DocETL.

    Input: manuscripts with nested reviews
    Output: flat list of review records with manuscript context
    """

    # Load manuscripts
    with open(manuscripts_file, 'r') as f:
        manuscripts = json.load(f)

    print(f"Loaded {len(manuscripts)} manuscripts")

    # Transform into review-level records
    review_records = []

    for manuscript in manuscripts:
        manuscript_id = manuscript['manuscript_id']
        manuscript_title = manuscript['title']
        manuscript_abstract = manuscript.get('abstract', '')
        manuscript_doi = manuscript.get('doi', '')

        print(f"\nProcessing manuscript: {manuscript_id}")
        print(f"  Title: {manuscript_title[:80]}...")
        print(f"  Reviews: {len(manuscript['reviews'])}")

        for review in manuscript['reviews']:
            # Create review record with manuscript context
            review_record = {
                # Manuscript context
                'manuscript_id': manuscript_id,
                'manuscript_title': manuscript_title,
                'manuscript_abstract': manuscript_abstract,
                'manuscript_doi': manuscript_doi,

                # Review identification
                'review_id': review['review_id'],
                'reviewer_id': review['reviewer']['reviewer_id'],
                'reviewer_name': review['reviewer'].get('name'),
                'reviewer_affiliation': review['reviewer'].get('affiliation'),
                'is_anonymous': review['reviewer']['is_anonymous'],

                # Review content
                'review_text': review['review_text'],
                'word_count': review['word_count'],
                'recommendation': review.get('recommendation'),

                # For tracking
                'version': review.get('version_reviewed', 1),
            }

            review_records.append(review_record)

    print(f"\n{'='*80}")
    print(f"Total review records created: {len(review_records)}")
    print(f"{'='*80}")

    # Save to output file as JSON array
    with open(output_file, 'w') as f:
        json.dump(review_records, f, indent=2)

    print(f"\n✓ Review records saved to: {output_file}")

    # Print statistics
    manuscripts_count = len(set(r['manuscript_id'] for r in review_records))
    avg_reviews = len(review_records) / manuscripts_count

    print(f"\nStatistics:")
    print(f"  Manuscripts: {manuscripts_count}")
    print(f"  Total reviews: {len(review_records)}")
    print(f"  Avg reviews per manuscript: {avg_reviews:.1f}")
    print(f"  Word count range: {min(r['word_count'] for r in review_records)} - {max(r['word_count'] for r in review_records)}")

    return review_records


def create_manuscript_context_file(manuscripts_file: str, output_file: str):
    """
    Create a separate file with manuscript-level context for reference.
    """

    with open(manuscripts_file, 'r') as f:
        manuscripts = json.load(f)

    manuscript_contexts = []

    for manuscript in manuscripts:
        context = {
            'manuscript_id': manuscript['manuscript_id'],
            'title': manuscript['title'],
            'abstract': manuscript.get('abstract', ''),
            'doi': manuscript.get('doi', ''),
            'authors': manuscript.get('authors', []),
            'num_reviews': len(manuscript['reviews']),
            'source': manuscript['source'],
            'source_url': manuscript['source_url'],
        }
        manuscript_contexts.append(context)

    # Save as JSON array
    with open(output_file, 'w') as f:
        json.dump(manuscript_contexts, f, indent=2)

    print(f"✓ Manuscript contexts saved to: {output_file}")


def main():
    # Set up paths
    base_dir = Path(__file__).parent.parent
    collection_dir = base_dir / 'data_collection' / 'collected_data'

    # Find most recent collection run
    runs = sorted(collection_dir.glob('run_*'), reverse=True)
    if not runs:
        print("Error: No collection runs found!")
        sys.exit(1)

    latest_run = runs[0]
    print(f"Using latest collection run: {latest_run.name}")

    manuscripts_file = latest_run / 'all_manuscripts.json'
    output_dir = base_dir / 'docetl_pipeline' / 'input'
    output_dir.mkdir(parents=True, exist_ok=True)

    reviews_output = output_dir / 'reviews.json'
    context_output = output_dir / 'manuscripts.json'

    # Prepare review records
    print("\n" + "="*80)
    print("PREPARING INPUT DATA FOR DOCETL PIPELINE")
    print("="*80)

    review_records = prepare_reviews_for_pipeline(str(manuscripts_file), str(reviews_output))

    # Create manuscript context file
    print(f"\n{'='*80}")
    print("Creating manuscript context file...")
    print("="*80)
    create_manuscript_context_file(str(manuscripts_file), str(context_output))

    print("\n" + "="*80)
    print("✓ INPUT PREPARATION COMPLETE")
    print("="*80)
    print(f"\nFiles created:")
    print(f"  - {reviews_output}")
    print(f"  - {context_output}")
    print(f"\nReady for DocETL pipeline processing!")


if __name__ == '__main__':
    main()
