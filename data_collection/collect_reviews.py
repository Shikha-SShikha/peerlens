#!/usr/bin/env python3
"""
Main script for collecting peer review data from multiple sources.

Usage:
    python collect_reviews.py --config quick_test
    python collect_reviews.py --num-manuscripts 30 --sources elife f1000
    python collect_reviews.py --help
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

from config import (
    CollectionConfig,
    DEFAULT_CONFIG,
    QUICK_TEST_CONFIG,
    COMPREHENSIVE_CONFIG,
    ELIFE_ONLY_CONFIG,
    F1000_ONLY_CONFIG,
)
from collectors.elife_collector import ElifeCollector
from collectors.f1000_collector import F1000Collector
from schema import Manuscript, CollectionMetadata


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReviewCollectionOrchestrator:
    """Orchestrates peer review data collection from multiple sources."""

    def __init__(self, config: CollectionConfig):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize collectors
        self.elife_collector = ElifeCollector(rate_limit_delay=config.rate_limit_delay)
        self.f1000_collector = F1000Collector(rate_limit_delay=config.rate_limit_delay)

    def collect_all(self):
        """Run collection from all configured sources."""
        logger.info("="*80)
        logger.info("Starting peer review data collection")
        logger.info("="*80)
        logger.info(f"Target manuscripts: {self.config.num_manuscripts}")
        logger.info(f"Sources: eLife={self.config.collect_from_elife}, F1000={self.config.collect_from_f1000}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("="*80)

        all_manuscripts = []
        all_metadata = []

        # Collect from eLife
        if self.config.collect_from_elife:
            logger.info("\n📚 Collecting from eLife...")
            try:
                manuscripts, metadata = self.elife_collector.collect_manuscripts(
                    num_manuscripts=self.config.num_manuscripts,
                    subject_areas=self.config.subject_areas,
                    start_date=self.config.start_date
                )
                all_manuscripts.extend(manuscripts)
                all_metadata.append(metadata)
                logger.info(f"✓ eLife collection complete: {len(manuscripts)} manuscripts")
            except Exception as e:
                logger.error(f"✗ eLife collection failed: {str(e)}")

        # Collect from F1000Research
        if self.config.collect_from_f1000:
            logger.info("\n📚 Collecting from F1000Research...")
            try:
                manuscripts, metadata = self.f1000_collector.collect_manuscripts(
                    num_manuscripts=self.config.num_manuscripts,
                    subject_areas=self.config.subject_areas,
                    start_date=self.config.start_date
                )
                all_manuscripts.extend(manuscripts)
                all_metadata.append(metadata)
                logger.info(f"✓ F1000Research collection complete: {len(manuscripts)} manuscripts")
            except Exception as e:
                logger.error(f"✗ F1000Research collection failed: {str(e)}")

        # Filter manuscripts based on config
        if self.config.skip_manuscripts_without_reviews:
            original_count = len(all_manuscripts)
            all_manuscripts = [
                m for m in all_manuscripts
                if len(m.reviews) >= self.config.min_reviews_per_manuscript
            ]
            filtered_count = original_count - len(all_manuscripts)
            if filtered_count > 0:
                logger.info(f"Filtered out {filtered_count} manuscripts without sufficient reviews")

        # Save results
        logger.info(f"\n💾 Saving {len(all_manuscripts)} manuscripts...")
        self._save_results(all_manuscripts, all_metadata)

        # Print summary
        self._print_summary(all_manuscripts, all_metadata)

        return all_manuscripts, all_metadata

    def _save_results(self, manuscripts: list[Manuscript], metadata_list: list[CollectionMetadata]):
        """Save collected data to files."""

        # Create timestamped run directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        run_dir = self.output_dir / f"run_{timestamp}"
        run_dir.mkdir(exist_ok=True)

        # Save individual manuscript files
        if self.config.save_individual_files:
            manuscripts_dir = run_dir / "manuscripts"
            manuscripts_dir.mkdir(exist_ok=True)

            for manuscript in manuscripts:
                filename = f"{manuscript.source.value}_{manuscript.manuscript_id}.json"
                filepath = manuscripts_dir / filename

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(manuscript.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(manuscripts)} individual manuscript files to {manuscripts_dir}")

        # Save combined manuscripts file
        if self.config.save_combined_file:
            combined_file = run_dir / "all_manuscripts.json"
            manuscripts_data = [m.to_dict() for m in manuscripts]

            with open(combined_file, 'w', encoding='utf-8') as f:
                json.dump(manuscripts_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved combined manuscripts file to {combined_file}")

        # Save collection metadata
        metadata_file = run_dir / "collection_metadata.json"
        metadata_data = [m.to_dict() for m in metadata_list]

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved collection metadata to {metadata_file}")

        # Save summary statistics
        if self.config.save_summary_stats:
            summary = self._generate_summary_stats(manuscripts, metadata_list)
            summary_file = run_dir / "summary_statistics.json"

            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved summary statistics to {summary_file}")

        # Save a README
        readme_file = run_dir / "README.txt"
        with open(readme_file, 'w') as f:
            f.write(f"Peer Review Data Collection Run\n")
            f.write(f"================================\n\n")
            f.write(f"Collection Date: {timestamp}\n")
            f.write(f"Total Manuscripts: {len(manuscripts)}\n")
            f.write(f"Sources: ")
            if self.config.collect_from_elife:
                f.write("eLife ")
            if self.config.collect_from_f1000:
                f.write("F1000Research")
            f.write(f"\n\nFiles:\n")
            f.write(f"- manuscripts/: Individual manuscript JSON files\n")
            f.write(f"- all_manuscripts.json: All manuscripts in one file\n")
            f.write(f"- collection_metadata.json: Collection process metadata\n")
            f.write(f"- summary_statistics.json: Summary statistics\n")

        logger.info(f"\n✓ All files saved to: {run_dir}")

    def _generate_summary_stats(
        self,
        manuscripts: list[Manuscript],
        metadata_list: list[CollectionMetadata]
    ) -> dict:
        """Generate summary statistics about the collected data."""

        total_reviews = sum(len(m.reviews) for m in manuscripts)
        total_words = sum(
            sum(r.word_count for r in m.reviews)
            for m in manuscripts
        )

        # Reviews per source
        by_source = {}
        for m in manuscripts:
            source = m.source.value
            if source not in by_source:
                by_source[source] = {
                    'count': 0,
                    'with_reviews': 0,
                    'total_reviews': 0,
                }
            by_source[source]['count'] += 1
            if m.reviews:
                by_source[source]['with_reviews'] += 1
                by_source[source]['total_reviews'] += len(m.reviews)

        # Review statistics
        manuscripts_with_multiple_reviews = sum(
            1 for m in manuscripts if len(m.reviews) >= 2
        )
        manuscripts_with_disagreement = sum(
            1 for m in manuscripts if m.has_disagreement()
        )

        # Validation issues
        validation_issues = []
        for m in manuscripts:
            issues = m.validate()
            if issues:
                validation_issues.append({
                    'manuscript_id': m.manuscript_id,
                    'source': m.source.value,
                    'issues': issues
                })

        summary = {
            'collection_timestamp': datetime.now().isoformat(),
            'total_manuscripts': len(manuscripts),
            'total_reviews': total_reviews,
            'total_review_words': total_words,
            'avg_reviews_per_manuscript': total_reviews / len(manuscripts) if manuscripts else 0,
            'avg_words_per_review': total_words / total_reviews if total_reviews > 0 else 0,
            'by_source': by_source,
            'manuscripts_with_multiple_reviews': manuscripts_with_multiple_reviews,
            'manuscripts_with_potential_disagreement': manuscripts_with_disagreement,
            'manuscripts_with_validation_issues': len(validation_issues),
            'validation_issues': validation_issues[:10],  # Include first 10
            'collection_metadata': [
                {
                    'source': m.source.value,
                    'attempted': m.num_manuscripts_attempted,
                    'successful': m.num_manuscripts_successful,
                    'failed': m.num_manuscripts_failed,
                    'error_count': len(m.errors),
                }
                for m in metadata_list
            ]
        }

        return summary

    def _print_summary(self, manuscripts: list[Manuscript], metadata_list: list[CollectionMetadata]):
        """Print collection summary to console."""
        logger.info("\n" + "="*80)
        logger.info("COLLECTION SUMMARY")
        logger.info("="*80)

        summary = self._generate_summary_stats(manuscripts, metadata_list)

        logger.info(f"\nTotal manuscripts collected: {summary['total_manuscripts']}")
        logger.info(f"Total reviews: {summary['total_reviews']}")
        logger.info(f"Average reviews per manuscript: {summary['avg_reviews_per_manuscript']:.1f}")
        logger.info(f"Manuscripts with 2+ reviews: {summary['manuscripts_with_multiple_reviews']}")
        logger.info(f"Manuscripts with potential disagreements: {summary['manuscripts_with_potential_disagreement']}")

        logger.info(f"\nBy source:")
        for source, stats in summary['by_source'].items():
            logger.info(f"  {source}: {stats['count']} manuscripts, {stats['total_reviews']} reviews")

        if summary['manuscripts_with_validation_issues'] > 0:
            logger.info(f"\n⚠ Warning: {summary['manuscripts_with_validation_issues']} manuscripts have validation issues")

        logger.info("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Collect peer review data from open access sources',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test with 5 manuscripts
  python collect_reviews.py --config quick_test

  # Collect 30 manuscripts from both sources
  python collect_reviews.py --num-manuscripts 30

  # Collect only from eLife
  python collect_reviews.py --sources elife --num-manuscripts 20

  # Comprehensive collection
  python collect_reviews.py --config comprehensive
        """
    )

    parser.add_argument(
        '--config',
        choices=['default', 'quick_test', 'comprehensive', 'elife_only', 'f1000_only'],
        default='default',
        help='Use a predefined configuration'
    )

    parser.add_argument(
        '--num-manuscripts',
        type=int,
        help='Number of manuscripts to collect (overrides config)'
    )

    parser.add_argument(
        '--sources',
        nargs='+',
        choices=['elife', 'f1000'],
        help='Sources to collect from (overrides config)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory (overrides config)'
    )

    parser.add_argument(
        '--rate-limit',
        type=float,
        help='Rate limit delay in seconds (overrides config)'
    )

    args = parser.parse_args()

    # Load base configuration
    config_map = {
        'default': DEFAULT_CONFIG,
        'quick_test': QUICK_TEST_CONFIG,
        'comprehensive': COMPREHENSIVE_CONFIG,
        'elife_only': ELIFE_ONLY_CONFIG,
        'f1000_only': F1000_ONLY_CONFIG,
    }

    config = config_map[args.config]

    # Apply command-line overrides
    if args.num_manuscripts:
        config.num_manuscripts = args.num_manuscripts

    if args.sources:
        config.collect_from_elife = 'elife' in args.sources
        config.collect_from_f1000 = 'f1000' in args.sources

    if args.output_dir:
        config.output_dir = args.output_dir

    if args.rate_limit:
        config.rate_limit_delay = args.rate_limit

    # Run collection
    orchestrator = ReviewCollectionOrchestrator(config)

    try:
        manuscripts, metadata = orchestrator.collect_all()
        logger.info("\n✓ Collection completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"\n✗ Collection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
