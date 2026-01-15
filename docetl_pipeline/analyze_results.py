#!/usr/bin/env python3
"""
Analyze DocETL pipeline results and generate quality metrics.
"""

import json
import sys
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any


def load_results(output_file: str) -> List[Dict[str, Any]]:
    """Load pipeline output JSON file."""
    with open(output_file, 'r') as f:
        data = json.load(f)
    # Handle both list and single object
    if isinstance(data, list):
        return data
    else:
        return [data]


def analyze_brief(brief: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a single editorial brief."""

    analysis = {
        'manuscript_id': brief.get('manuscript_id', 'unknown'),
        'title': brief.get('manuscript_title', '')[:80],
        'num_major_issues': len(brief.get('major_issues', [])),
        'num_minor_issues': len(brief.get('minor_issues', [])),
        'num_disagreements': len(brief.get('disagreements', [])),
        'num_action_items': len(brief.get('action_checklist', [])),
        'num_open_questions': len(brief.get('open_questions', [])),
        'consensus_confidence': brief.get('consensus_snapshot', {}).get('confidence', 'unknown'),
    }

    # Check evidence coverage
    major_issues = brief.get('major_issues', [])
    major_with_evidence = sum(
        1 for issue in major_issues
        if issue.get('evidence_excerpts') and len(issue.get('evidence_excerpts', [])) > 0
    )

    analysis['evidence_coverage'] = (
        100 * major_with_evidence / len(major_issues)
        if major_issues else 100
    )

    # Validation metrics
    validation = brief.get('validation_passed')
    if validation is not None:
        analysis['validation_passed'] = validation
        analysis['validation_confidence'] = brief.get('confidence_score', 0)
        analysis['validation_warnings'] = len(brief.get('warnings', []))

    return analysis


def generate_summary(briefs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics across all briefs."""

    analyses = [analyze_brief(brief) for brief in briefs]

    summary = {
        'total_briefs': len(briefs),
        'total_major_issues': sum(a['num_major_issues'] for a in analyses),
        'total_minor_issues': sum(a['num_minor_issues'] for a in analyses),
        'total_disagreements': sum(a['num_disagreements'] for a in analyses),
        'total_action_items': sum(a['num_action_items'] for a in analyses),
        'avg_major_issues_per_brief': sum(a['num_major_issues'] for a in analyses) / len(analyses) if analyses else 0,
        'avg_minor_issues_per_brief': sum(a['num_minor_issues'] for a in analyses) / len(analyses) if analyses else 0,
        'avg_action_items_per_brief': sum(a['num_action_items'] for a in analyses) / len(analyses) if analyses else 0,
    }

    # Evidence coverage stats
    coverage_scores = [a['evidence_coverage'] for a in analyses]
    summary['avg_evidence_coverage'] = sum(coverage_scores) / len(coverage_scores) if coverage_scores else 0
    summary['min_evidence_coverage'] = min(coverage_scores) if coverage_scores else 0
    summary['max_evidence_coverage'] = max(coverage_scores) if coverage_scores else 0

    # Validation stats
    if 'validation_passed' in analyses[0]:
        passed_count = sum(1 for a in analyses if a.get('validation_passed'))
        summary['validation_pass_rate'] = 100 * passed_count / len(analyses)
        summary['avg_validation_confidence'] = sum(a.get('validation_confidence', 0) for a in analyses) / len(analyses)

    # Confidence distribution
    confidence_dist = Counter(a['consensus_confidence'] for a in analyses)
    summary['confidence_distribution'] = dict(confidence_dist)

    return summary, analyses


def print_report(briefs: List[Dict[str, Any]]):
    """Print comprehensive analysis report."""

    summary, analyses = generate_summary(briefs)

    print("\n" + "="*80)
    print("DOCETL PIPELINE RESULTS ANALYSIS")
    print("="*80)

    # Overall Statistics
    print(f"\n📊 OVERALL STATISTICS")
    print(f"{'─'*80}")
    print(f"  Total Editorial Briefs: {summary['total_briefs']}")
    print(f"  Total Major Issues: {summary['total_major_issues']}")
    print(f"  Total Minor Issues: {summary['total_minor_issues']}")
    print(f"  Total Disagreements: {summary['total_disagreements']}")
    print(f"  Total Action Items: {summary['total_action_items']}")

    # Averages
    print(f"\n📈 AVERAGES PER BRIEF")
    print(f"{'─'*80}")
    print(f"  Major Issues: {summary['avg_major_issues_per_brief']:.1f}")
    print(f"  Minor Issues: {summary['avg_minor_issues_per_brief']:.1f}")
    print(f"  Action Items: {summary['avg_action_items_per_brief']:.1f}")

    # Quality Metrics
    print(f"\n✅ QUALITY METRICS")
    print(f"{'─'*80}")
    print(f"  Evidence Coverage (avg): {summary['avg_evidence_coverage']:.1f}%")
    print(f"  Evidence Coverage (min): {summary['min_evidence_coverage']:.1f}%")
    print(f"  Evidence Coverage (max): {summary['max_evidence_coverage']:.1f}%")

    target_coverage = 95.0
    if summary['avg_evidence_coverage'] >= target_coverage:
        print(f"  ✓ MEETS target (≥{target_coverage}%)")
    else:
        print(f"  ⚠ BELOW target (≥{target_coverage}%) - consider improving extraction")

    # Validation Results
    if 'validation_pass_rate' in summary:
        print(f"\n🔍 VALIDATION RESULTS")
        print(f"{'─'*80}")
        print(f"  Pass Rate: {summary['validation_pass_rate']:.1f}%")
        print(f"  Avg Confidence: {summary['avg_validation_confidence']:.1f}/100")

        if summary['validation_pass_rate'] >= 90:
            print(f"  ✓ EXCELLENT - High validation pass rate")
        elif summary['validation_pass_rate'] >= 70:
            print(f"  ⚠ GOOD - Some briefs need improvement")
        else:
            print(f"  ❌ POOR - Pipeline needs optimization")

    # Confidence Distribution
    print(f"\n🎯 CONSENSUS CONFIDENCE DISTRIBUTION")
    print(f"{'─'*80}")
    for confidence, count in summary['confidence_distribution'].items():
        pct = 100 * count / summary['total_briefs']
        print(f"  {confidence}: {count} ({pct:.1f}%)")

    # Per-Brief Details
    print(f"\n📄 PER-BRIEF ANALYSIS")
    print(f"{'─'*80}")

    for i, analysis in enumerate(analyses, 1):
        print(f"\n  [{i}] {analysis['title']}...")
        print(f"      ID: {analysis['manuscript_id']}")
        print(f"      Consensus: {analysis['consensus_confidence']}")
        print(f"      Major Issues: {analysis['num_major_issues']}")
        print(f"      Minor Issues: {analysis['num_minor_issues']}")
        print(f"      Disagreements: {analysis['num_disagreements']}")
        print(f"      Action Items: {analysis['num_action_items']}")
        print(f"      Evidence Coverage: {analysis['evidence_coverage']:.0f}%")

        if 'validation_passed' in analysis:
            status = "✓ PASSED" if analysis['validation_passed'] else "✗ FAILED"
            print(f"      Validation: {status} (confidence: {analysis.get('validation_confidence', 0)})")
            if analysis.get('validation_warnings', 0) > 0:
                print(f"      Warnings: {analysis['validation_warnings']}")

    # Success Criteria Assessment
    print(f"\n🎯 SUCCESS CRITERIA ASSESSMENT (from opportunity assessment)")
    print(f"{'─'*80}")

    print(f"\n  Traceability Coverage: {summary['avg_evidence_coverage']:.1f}%")
    if summary['avg_evidence_coverage'] >= 95:
        print(f"    ✓ MEETS target (≥95%)")
    else:
        print(f"    ✗ Below target (≥95%)")

    # Note: Recall and precision require manual gold standard
    print(f"\n  Note: Major issue recall and precision require manual gold standard briefs")
    print(f"        Create gold standard and run: python evaluate_against_gold.py")

    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print(f"{'─'*80}")

    if summary['avg_evidence_coverage'] < 95:
        print(f"  • Improve evidence extraction in Step A (Map)")
        print(f"  • Consider adding gleaning operation")

    if 'validation_pass_rate' in summary and summary['validation_pass_rate'] < 90:
        print(f"  • Review failed validations for patterns")
        print(f"  • Consider stronger models for synthesis")

    if summary['total_disagreements'] == 0:
        print(f"  • No disagreements found - verify detection logic")
        print(f"  • May need to improve disagreement identification")

    if summary['avg_major_issues_per_brief'] < 2:
        print(f"  • Low major issue count - check extraction thresholds")

    print(f"\n  ✓ Run optimization: docetl optimize config/pipeline.yaml")
    print(f"  ✓ Create manual gold standard for evaluation")
    print(f"  ✓ Test on more manuscripts (target: 30-50)")

    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80 + "\n")


def export_summary(briefs: List[Dict[str, Any]], output_file: str):
    """Export summary to JSON."""
    summary, analyses = generate_summary(briefs)

    export_data = {
        'summary': summary,
        'per_brief_analysis': analyses,
        'timestamp': Path('output/editorial_briefs.json').stat().st_mtime
    }

    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"Summary exported to: {output_file}")


def main():
    output_file = 'output/editorial_briefs.json'

    if not Path(output_file).exists():
        print(f"❌ Error: {output_file} not found!")
        print(f"\nRun the pipeline first:")
        print(f"  ./run_pipeline.sh full")
        sys.exit(1)

    # Load results
    print(f"Loading results from: {output_file}")
    briefs = load_results(output_file)

    if not briefs:
        print(f"❌ Error: No briefs found in {output_file}")
        sys.exit(1)

    print(f"Loaded {len(briefs)} editorial briefs")

    # Generate report
    print_report(briefs)

    # Export summary
    export_summary(briefs, 'output/analysis_summary.json')


if __name__ == '__main__':
    main()
