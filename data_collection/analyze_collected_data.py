#!/usr/bin/env python3
"""
Analyze collected peer review data and generate detailed report.
"""

import json
import sys
from pathlib import Path
from collections import Counter


def analyze_collection(run_dir):
    """Analyze a collection run and print detailed report."""

    run_path = Path(run_dir)

    # Load summary statistics
    with open(run_path / 'summary_statistics.json', 'r') as f:
        summary = json.load(f)

    # Load all manuscripts
    with open(run_path / 'all_manuscripts.json', 'r') as f:
        manuscripts = json.load(f)

    print("\n" + "="*80)
    print("PEER REVIEW DATA COLLECTION ANALYSIS")
    print("="*80)

    # Overall Statistics
    print(f"\n📊 OVERALL STATISTICS")
    print(f"{'─'*80}")
    print(f"  Total Manuscripts: {summary['total_manuscripts']}")
    print(f"  Total Reviews: {summary['total_reviews']}")
    print(f"  Total Words: {summary['total_review_words']:,}")
    print(f"  Avg Reviews per Manuscript: {summary['avg_reviews_per_manuscript']:.1f}")
    print(f"  Avg Words per Review: {summary['avg_words_per_review']:.1f}")
    print(f"  Manuscripts with 2+ Reviews: {summary['manuscripts_with_multiple_reviews']}")
    print(f"  Manuscripts with Disagreements: {summary['manuscripts_with_potential_disagreement']}")

    # Per-source breakdown
    print(f"\n📚 BY SOURCE")
    print(f"{'─'*80}")
    for source, stats in summary['by_source'].items():
        print(f"  {source.upper()}:")
        print(f"    Manuscripts: {stats['count']}")
        print(f"    Total Reviews: {stats['total_reviews']}")
        print(f"    Avg Reviews/Manuscript: {stats['total_reviews']/stats['count']:.1f}")

    # Detailed manuscript analysis
    print(f"\n📄 MANUSCRIPT DETAILS")
    print(f"{'─'*80}")

    for i, manuscript in enumerate(manuscripts, 1):
        print(f"\n  [{i}] {manuscript['title'][:70]}...")
        print(f"      ID: {manuscript['manuscript_id']}")
        print(f"      DOI: {manuscript['doi']}")
        print(f"      Reviews: {len(manuscript['reviews'])}")
        print(f"      Authors: {len(manuscript['authors'])}")

        # Review breakdown
        recommendations = [r['recommendation'] for r in manuscript['reviews'] if r['recommendation']]
        if recommendations:
            rec_counts = Counter(recommendations)
            print(f"      Recommendations: {dict(rec_counts)}")

        # Word count stats
        word_counts = [r['word_count'] for r in manuscript['reviews']]
        if word_counts:
            print(f"      Review lengths: min={min(word_counts)}, max={max(word_counts)}, avg={sum(word_counts)/len(word_counts):.0f} words")

        # Check for named reviewers
        named_reviewers = [r['reviewer']['name'] for r in manuscript['reviews']
                          if not r['reviewer']['is_anonymous']]
        if named_reviewers:
            print(f"      Named Reviewers: {len(named_reviewers)}/{len(manuscript['reviews'])}")

    # Review quality analysis
    print(f"\n🔍 REVIEW QUALITY ANALYSIS")
    print(f"{'─'*80}")

    all_reviews = []
    for m in manuscripts:
        all_reviews.extend(m['reviews'])

    word_counts = [r['word_count'] for r in all_reviews]

    print(f"  Total Reviews Collected: {len(all_reviews)}")
    print(f"  Word Count Distribution:")
    print(f"    Min: {min(word_counts)} words")
    print(f"    Max: {max(word_counts)} words")
    print(f"    Median: {sorted(word_counts)[len(word_counts)//2]} words")
    print(f"    Average: {sum(word_counts)/len(word_counts):.0f} words")

    # Count by length category
    short = sum(1 for w in word_counts if w < 100)
    medium = sum(1 for w in word_counts if 100 <= w < 500)
    long = sum(1 for w in word_counts if w >= 500)

    print(f"  Length Categories:")
    print(f"    Short (<100 words): {short} ({100*short/len(word_counts):.1f}%)")
    print(f"    Medium (100-500 words): {medium} ({100*medium/len(word_counts):.1f}%)")
    print(f"    Long (500+ words): {long} ({100*long/len(word_counts):.1f}%)")

    # Reviewer anonymity
    anonymous = sum(1 for r in all_reviews if r['reviewer']['is_anonymous'])
    named = len(all_reviews) - anonymous

    print(f"\n👤 REVIEWER INFORMATION")
    print(f"{'─'*80}")
    print(f"  Anonymous Reviews: {anonymous} ({100*anonymous/len(all_reviews):.1f}%)")
    print(f"  Named Reviews: {named} ({100*named/len(all_reviews):.1f}%)")

    # Recommendations analysis
    all_recommendations = [r['recommendation'] for r in all_reviews if r['recommendation']]
    if all_recommendations:
        rec_counts = Counter(all_recommendations)
        print(f"\n✅ RECOMMENDATIONS BREAKDOWN")
        print(f"{'─'*80}")
        for rec, count in rec_counts.most_common():
            print(f"  {rec}: {count} ({100*count/len(all_recommendations):.1f}%)")

    # Suitability for POC
    print(f"\n🎯 SUITABILITY FOR POC")
    print(f"{'─'*80}")

    suitable_count = sum(1 for m in manuscripts if len(m['reviews']) >= 2)
    print(f"  ✓ Manuscripts with 2+ reviews: {suitable_count}/{len(manuscripts)}")

    disagreement_count = summary['manuscripts_with_potential_disagreement']
    print(f"  ✓ Manuscripts with disagreements: {disagreement_count}/{len(manuscripts)}")

    long_reviews = sum(1 for r in all_reviews if r['word_count'] >= 200)
    print(f"  ✓ Substantial reviews (200+ words): {long_reviews}/{len(all_reviews)}")

    print(f"\n  📌 Recommendation:")
    if suitable_count >= len(manuscripts) * 0.7:
        print(f"     EXCELLENT for POC testing! Most manuscripts have multiple reviews.")
    elif suitable_count >= len(manuscripts) * 0.5:
        print(f"     GOOD for POC testing. Sufficient multi-review manuscripts.")
    else:
        print(f"     MARGINAL for POC. Consider collecting more manuscripts.")

    # Use case mapping
    print(f"\n💡 USE CASE MAPPING (from opportunity assessment)")
    print(f"{'─'*80}")
    print(f"  ✓ Consensus synthesis: {suitable_count} manuscripts available")
    print(f"  ✓ Disagreement resolution: {disagreement_count} manuscripts with conflicts")
    print(f"  ✓ Issue extraction: {len(all_reviews)} reviews for training")
    print(f"  ✓ Traceability testing: All reviews have full text for excerpt extraction")

    print(f"\n" + "="*80)
    print(f"Analysis complete! Data saved in: {run_path}")
    print("="*80 + "\n")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_dir = sys.argv[1]
    else:
        # Find most recent run
        collected_data = Path('collected_data')
        runs = sorted(collected_data.glob('run_*'), reverse=True)
        if not runs:
            print("No collection runs found!")
            sys.exit(1)
        run_dir = runs[0]
        print(f"Analyzing most recent run: {run_dir.name}")

    analyze_collection(run_dir)
