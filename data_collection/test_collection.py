#!/usr/bin/env python3
"""
Simple test script to verify data collection setup.

Run this to test the collectors without doing a full collection.
"""

import sys
from collectors.elife_collector import ElifeCollector
from collectors.f1000_collector import F1000Collector
from schema import ReviewSource


def test_elife_collector():
    """Test eLife collector with a single known article."""
    print("\n" + "="*60)
    print("Testing eLife Collector")
    print("="*60)

    collector = ElifeCollector(rate_limit_delay=1.0)

    # Test with a known article ID
    test_article_id = "97433"

    print(f"\nAttempting to collect article: {test_article_id}")
    manuscript = collector.collect_single_manuscript(test_article_id)

    if manuscript:
        print(f"✓ Successfully collected manuscript")
        print(f"  Title: {manuscript.title}")
        print(f"  Authors: {len(manuscript.authors)}")
        print(f"  Reviews: {len(manuscript.reviews)}")
        print(f"  Editorial Assessments: {len(manuscript.editorial_assessments)}")

        if manuscript.reviews:
            print(f"\n  First review preview:")
            print(f"    Reviewer: {manuscript.reviews[0].reviewer.name or 'Anonymous'}")
            print(f"    Words: {manuscript.reviews[0].word_count}")
            print(f"    Text preview: {manuscript.reviews[0].review_text[:150]}...")

        validation_issues = manuscript.validate()
        if validation_issues:
            print(f"\n  ⚠ Validation issues: {validation_issues}")
        else:
            print(f"  ✓ No validation issues")

        return True
    else:
        print(f"✗ Failed to collect manuscript")
        return False


def test_f1000_collector():
    """Test F1000Research collector with a single known article."""
    print("\n" + "="*60)
    print("Testing F1000Research Collector")
    print("="*60)

    collector = F1000Collector(rate_limit_delay=1.0)

    # Test with a known article ID
    test_article_id = "1-1655"

    print(f"\nAttempting to collect article: {test_article_id}")
    manuscript = collector.collect_single_manuscript(test_article_id)

    if manuscript:
        print(f"✓ Successfully collected manuscript")
        print(f"  Title: {manuscript.title}")
        print(f"  Authors: {len(manuscript.authors)}")
        print(f"  Reviews: {len(manuscript.reviews)}")

        if manuscript.reviews:
            print(f"\n  First review preview:")
            print(f"    Reviewer: {manuscript.reviews[0].reviewer.name or 'Anonymous'}")
            print(f"    Words: {manuscript.reviews[0].word_count}")
            if manuscript.reviews[0].recommendation:
                print(f"    Recommendation: {manuscript.reviews[0].recommendation}")
            print(f"    Text preview: {manuscript.reviews[0].review_text[:150]}...")

        validation_issues = manuscript.validate()
        if validation_issues:
            print(f"\n  ⚠ Validation issues: {validation_issues}")
        else:
            print(f"  ✓ No validation issues")

        return True
    else:
        print(f"✗ Failed to collect manuscript")
        return False


def test_schema():
    """Test schema imports and basic functionality."""
    print("\n" + "="*60)
    print("Testing Schema")
    print("="*60)

    from schema import Manuscript, Review, Reviewer, ReviewDecision

    # Create test objects
    reviewer = Reviewer(
        reviewer_id="test_reviewer_1",
        name="Test Reviewer",
        is_anonymous=False
    )

    review = Review(
        review_id="test_review_1",
        reviewer=reviewer,
        review_text="This is a test review. " * 50  # Make it long enough
    )

    manuscript = Manuscript(
        manuscript_id="test_001",
        source=ReviewSource.ELIFE,
        source_url="https://example.com/test",
        title="Test Manuscript",
        reviews=[review],
        decision=ReviewDecision.PENDING
    )

    print("\n✓ Schema objects created successfully")
    print(f"  Manuscript: {manuscript.manuscript_id}")
    print(f"  Reviews: {len(manuscript.reviews)}")
    print(f"  Review word count: {review.word_count}")

    # Test validation
    issues = manuscript.validate()
    print(f"  Validation issues: {len(issues)}")

    # Test serialization
    manuscript_dict = manuscript.to_dict()
    print(f"  ✓ Serialization successful")

    return True


def main():
    print("\n" + "="*60)
    print("DATA COLLECTION SYSTEM TEST")
    print("="*60)

    results = {}

    # Test schema
    print("\n[1/3] Testing schema...")
    try:
        results['schema'] = test_schema()
    except Exception as e:
        print(f"✗ Schema test failed: {str(e)}")
        results['schema'] = False

    # Test eLife collector
    print("\n[2/3] Testing eLife collector...")
    try:
        results['elife'] = test_elife_collector()
    except Exception as e:
        print(f"✗ eLife collector test failed: {str(e)}")
        results['elife'] = False

    # Test F1000Research collector
    print("\n[3/3] Testing F1000Research collector...")
    try:
        results['f1000'] = test_f1000_collector()
    except Exception as e:
        print(f"✗ F1000Research collector test failed: {str(e)}")
        results['f1000'] = False

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name.ljust(20)}: {status}")

    all_passed = all(results.values())
    print("\n" + "="*60)

    if all_passed:
        print("✓ All tests passed! System is ready to use.")
        print("\nRun this to start collecting:")
        print("  python collect_reviews.py --config quick_test")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nNote: Network errors are expected if you're offline or if")
        print("the source websites have changed their structure.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
