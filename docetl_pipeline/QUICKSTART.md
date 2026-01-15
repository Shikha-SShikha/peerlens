# DocETL Pipeline Quick Start

## Prerequisites

✅ Input data prepared (76 reviews from 3 manuscripts)
✅ DocETL installed
✅ Pipeline configuration ready

## Setup (2 minutes)

### 1. Add OpenAI API Key

```bash
# Copy template
cp .env.template .env

# Edit .env and add your key
nano .env
# Add: OPENAI_API_KEY=sk-...
```

### 2. Verify Setup

```bash
# Check input files
ls -lh input/
# Should see: reviews.jsonl (76 reviews), manuscripts.jsonl (3 manuscripts)

# Check API key
grep OPENAI_API_KEY .env
```

## Run Pipeline

### Option 1: Test Run (Recommended First)

```bash
./run_pipeline.sh test
```

**What it does:** Processes 1 manuscript to verify setup
**Time:** ~30 seconds
**Cost:** ~$0.10

### Option 2: Full Pipeline

```bash
./run_pipeline.sh full
```

**What it does:** Processes all 3 manuscripts through complete pipeline
**Time:** ~5-10 minutes
**Cost:** ~$2-3

## View Results

### Quick Look

```bash
# See output files
ls -lh output/

# Count briefs
wc -l output/editorial_briefs.jsonl

# View first brief
head -1 output/editorial_briefs.jsonl | python -m json.tool | less
```

### Comprehensive Analysis

```bash
python analyze_results.py
```

This shows:
- Overall statistics
- Quality metrics
- Evidence coverage
- Validation results
- Per-brief analysis
- Success criteria assessment

## Understanding Output

Each editorial brief contains:

```json
{
  "manuscript_id": "2-150",
  "consensus_snapshot": {
    "overall_recommendation": "...",
    "confidence": "strong_majority",
    "summary": "..."
  },
  "major_issues": [
    {
      "rank": 1,
      "category": "methodology",
      "issue": "...",
      "evidence_excerpts": ["...", "..."]
    }
  ],
  "minor_issues": [...],
  "disagreements": [...],
  "action_checklist": [...],
  "open_questions": [...]
}
```

## Troubleshooting

### "No API key" error
```bash
# Check .env file exists
cat .env | grep OPENAI_API_KEY

# Make sure it's loaded
export $(cat .env | grep -v '^#' | xargs)
```

### "File not found" error
```bash
# Re-prepare input
python prepare_input.py
```

### Pipeline fails
```bash
# Check logs
cat output/*.log

# Try test pipeline first
./run_pipeline.sh test
```

## Next Steps

1. ✅ Run test pipeline
2. ✅ Run full pipeline
3. 📊 Analyze results
4. 📝 Create manual gold standard (10-15 briefs)
5. 🎯 Evaluate against success metrics
6. 🔧 Optimize: `docetl optimize config/pipeline.yaml`
7. 📈 Scale to 30-50 manuscripts

## Pipeline Architecture

```
Step A: EXTRACT (Map)
  76 reviews → Extract issues → 200+ structured issues

Step B: RESOLVE (Resolve)
  200+ issues → Deduplicate → 50-100 canonical issues

Step C: SYNTHESIZE (Reduce)
  3 manuscripts × 19-33 reviews → 3 editorial briefs

Step D: VALIDATE (Map)
  3 briefs → Quality check → Validation results
```

## Cost Summary

- Test run: ~$0.10
- Full run (3 manuscripts): ~$2-3
- 30 manuscripts: ~$30-40
- 50 manuscripts: ~$50-60

Using gpt-4o-mini can reduce costs by ~70% with slightly lower quality.

## Help

- Full documentation: `README.md`
- Pipeline config: `config/pipeline.yaml`
- Test config: `config/test_pipeline.yaml`
- Analysis: `python analyze_results.py --help`

---

**Ready to start!** Run: `./run_pipeline.sh test`
