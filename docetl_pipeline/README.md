# DocETL Peer Review Synthesis Pipeline

A production-ready pipeline for synthesizing multiple peer reviews into structured editorial briefs using DocETL.

## Overview

This pipeline implements the design from the opportunity assessment:

```
Reviews (76) → Extract Issues → Resolve Duplicates → Synthesize Briefs → Validate
     ↓              (Map)           (Resolve)          (Reduce)        (Map)
Input Data    Structured Issues  Canonical Issues   Editorial Briefs  Quality Check
```

## Pipeline Steps

### Step A: Map - Extract Issues (per review)
- Extracts structured issues from each review
- Categories: methodology, statistics, clarity, data, interpretation, ethics, etc.
- Severity: MAJOR or MINOR
- **Evidence requirement**: Every issue must cite exact review excerpt

### Step B: Resolve - Canonicalize Issues (cross-review)
- Deduplicates similar issues across reviewers
- Groups issues by manuscript and category
- Preserves all evidence excerpts
- Tracks which reviewers flagged each issue

### Step C: Reduce - Synthesize (per manuscript)
- Creates comprehensive editorial brief
- Sections:
  - Consensus snapshot
  - Ranked major issues
  - Ranked minor issues
  - Disagreements with resolution paths
  - Author action checklist (testable, mapped to issues)
  - Open questions

### Step D: Validate - Quality Gates
- Checks evidence requirements (no claims without excerpts)
- Detects potential hallucinations
- Validates completeness
- Ensures disagreements are explicit

## Setup

### 1. Install Dependencies

```bash
pip install docetl
```

### 2. Prepare Input Data

```bash
# Run from parent directory
cd /home/shikha/Main/Coding/Prototype\ 4/docetl_pipeline
python prepare_input.py
```

This creates:
- `input/reviews.jsonl` - 76 review records
- `input/manuscripts.jsonl` - 3 manuscript contexts

### 3. Configure API Key

```bash
# Copy template
cp .env.template .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

## Running the Pipeline

### Test Run (Single Manuscript)

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh test
```

This runs a simplified pipeline on one manuscript to verify setup.

### Full Pipeline (All Manuscripts)

```bash
./run_pipeline.sh full
```

This processes all 3 manuscripts through the complete pipeline.

### Direct DocETL Commands

```bash
# Test pipeline
docetl run config/test_pipeline.yaml

# Full pipeline
docetl run config/pipeline.yaml

# With optimization
docetl run config/pipeline.yaml --optimize
```

## Output

### Editorial Briefs

`output/editorial_briefs.jsonl` contains synthesized briefs:

```json
{
  "manuscript_id": "2-150",
  "manuscript_title": "...",
  "consensus_snapshot": {
    "overall_recommendation": "accept with minor revisions",
    "confidence": "strong_majority",
    "summary": "...",
    "num_reviews": 19
  },
  "major_issues": [
    {
      "rank": 1,
      "category": "methodology",
      "issue": "Lack of blinding in outcome assessment",
      "reviewers_flagged": ["2-150_reviewer_3", "2-150_reviewer_7"],
      "actionable": true,
      "evidence_excerpts": ["...", "..."]
    }
  ],
  "minor_issues": [...],
  "disagreements": [...],
  "action_checklist": [
    {
      "category": "methodology",
      "action": "Add details on blinding procedures",
      "addresses_issues": ["issue_1"],
      "testable": true
    }
  ],
  "open_questions": [...],
  "traceability_index": {...}
}
```

### Validation Results

`output/editorial_briefs.jsonl` also includes validation:

```json
{
  "validation_passed": true,
  "confidence_score": 85,
  "issues_found": [],
  "warnings": ["Minor issue #3 lacks specific excerpt"],
  "recommendations": ["Consider adding more context to action item 2"]
}
```

## Analysis

### View Results

```bash
# Pretty-print first brief
python -c "import json; print(json.dumps(json.loads(open('output/editorial_briefs.jsonl').readline()), indent=2))"

# Count briefs
wc -l output/editorial_briefs.jsonl
```

### Run Analysis Script

```bash
python analyze_results.py
```

This generates:
- Summary statistics
- Quality metrics
- Comparison to manual briefs (if available)

## Optimization

DocETL can automatically optimize the pipeline:

```bash
# Generate optimized pipeline
docetl optimize config/pipeline.yaml --output config/pipeline_optimized.yaml

# Run optimized version
docetl run config/pipeline_optimized.yaml
```

The optimizer may:
- Add gleaning operations to improve extraction quality
- Decompose complex prompts into steps
- Add resolve operations for better entity resolution
- Suggest validation improvements

## Configuration

### Models

Default configuration:
- Extraction (Map): `gpt-4o` (highest quality)
- Resolution (Resolve): `gpt-4o` (needs strong reasoning)
- Synthesis (Reduce): `gpt-4o` (most critical step)
- Validation (Map): `gpt-4o-mini` (simple checks)

To change models, edit `config/pipeline.yaml`:

```yaml
operations:
  - name: extract_review_issues
    model: gpt-4o-mini  # Use cheaper model
```

### Cost Estimation

Approximate costs for 3 manuscripts with 76 reviews:

- Extraction: 76 reviews × $0.02 = **$1.52**
- Resolution: ~200 comparisons × $0.005 = **$1.00**
- Synthesis: 3 manuscripts × $0.10 = **$0.30**
- Validation: 3 briefs × $0.01 = **$0.03**

**Total: ~$2.85** for full pipeline run

For 50 manuscripts (~1,250 reviews):
- Estimated: **~$40-60** depending on review length

### Rate Limits

If you hit rate limits:

```yaml
# Add to pipeline.yaml
rate_limit:
  requests_per_minute: 20
  tokens_per_minute: 40000
```

## Evaluation

### Success Metrics (from Opportunity Assessment)

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Major issue recall | ≥85% | Compare to manual briefs |
| Major issue precision | ≥80% | Editor validation |
| Traceability coverage | ≥95% | Check excerpt citations |
| Disagreement fidelity | ≥4/5 | Accuracy of conflicts |

### Creating Gold Standard

To evaluate, create manual briefs for 10-15 manuscripts:

1. Manually read all reviews for a manuscript
2. Write your own editorial brief
3. Save as `gold_standard/manuscript_{id}.json`
4. Run comparison: `python evaluate_against_gold.py`

### Quality Checks

```bash
# Check validation pass rate
cat output/editorial_briefs.jsonl | jq '.validation_passed' | grep -c true

# Check evidence coverage
cat output/editorial_briefs.jsonl | jq '.major_issues[].evidence_excerpts | length'

# Check for hallucinations (issues without evidence)
cat output/editorial_briefs.jsonl | jq '.warnings[] | select(contains("lacks evidence"))'
```

## Troubleshooting

### "No such file" errors
```bash
# Ensure input files exist
ls -l input/

# Re-run preparation if needed
python prepare_input.py
```

### API errors
```bash
# Check API key
grep OPENAI_API_KEY .env

# Test API access
python -c "import openai; openai.api_key='YOUR_KEY'; print(openai.Model.list())"
```

### Out of memory
```bash
# Process one manuscript at a time
# Edit pipeline.yaml and add filter:
- name: filter_one
  type: filter
  filter: "input.manuscript_id == '2-150'"
```

### Poor quality output
```bash
# Enable optimization
docetl run config/pipeline.yaml --optimize

# Use stronger models (edit pipeline.yaml)
default_model: gpt-4o  # Instead of gpt-4o-mini

# Add gleaning for iterative improvement
# DocETL optimizer will suggest this automatically
```

## Advanced Usage

### Custom Prompts

Edit prompts in `config/pipeline.yaml` to:
- Focus on specific issue types
- Adjust severity thresholds
- Change categorization scheme
- Add domain-specific checks

### Multi-domain Processing

To handle different journal domains:

```yaml
# Add domain-specific operations
- name: extract_stats_issues
  type: map
  filter: "input.category == 'statistics'"
  prompt: |
    Focus on statistical issues in this review...
```

### Integration with Editorial Systems

Export to standard formats:

```bash
# Convert to CSV
python -c "import json, csv; ..."

# Export to database
python export_to_db.py --db editorial_system.db
```

## Project Structure

```
docetl_pipeline/
├── config/
│   ├── pipeline.yaml              # Main pipeline configuration
│   ├── test_pipeline.yaml         # Test/development pipeline
│   └── pipeline_optimized.yaml    # Optimizer output (generated)
├── input/
│   ├── reviews.jsonl              # 76 review records
│   └── manuscripts.jsonl          # 3 manuscript contexts
├── output/
│   ├── editorial_briefs.jsonl     # Pipeline output
│   └── test_extraction.jsonl      # Test output
├── prepare_input.py               # Data preparation script
├── run_pipeline.sh                # Pipeline execution script
├── analyze_results.py             # Results analysis
├── .env.template                  # Environment template
└── README.md                      # This file
```

## Next Steps

1. ✅ Setup complete - Pipeline ready to run
2. 🔄 Add API key to `.env`
3. 🚀 Run test pipeline: `./run_pipeline.sh test`
4. 🚀 Run full pipeline: `./run_pipeline.sh full`
5. 📊 Analyze results: `python analyze_results.py`
6. 📝 Create gold standard for evaluation
7. 🎯 Measure against success metrics
8. 🔧 Optimize based on results

## References

- DocETL Documentation: https://ucbepic.github.io/docetl/
- Opportunity Assessment: `../opportunity assessment.md`
- Collection Results: `../COLLECTION_RESULTS.md`
- LiteLLM (multi-provider support): https://docs.litellm.ai/

---

*Pipeline designed for the Peer Review Synthesis POC*
*Following opportunity assessment requirements*
*Ready for production testing*
