# What To Do Next

## ✅ What's Complete

You now have a **complete peer review synthesis system**:

1. ✅ **Data Collection System** - Collects peer reviews from eLife and F1000Research
2. ✅ **Sample Dataset** - 76 reviews from 3 manuscripts ready to use
3. ✅ **DocETL Pipeline** - Full 4-step synthesis pipeline (Extract → Resolve → Synthesize → Validate)
4. ✅ **Analysis Tools** - Scripts to evaluate pipeline output
5. ✅ **Documentation** - Comprehensive guides and references

## 🚀 Immediate Next Steps (5 minutes)

### Step 1: Add OpenAI API Key

```bash
cd docetl_pipeline

# Copy template
cp .env.template .env

# Edit the file and add your OpenAI API key
# Change: OPENAI_API_KEY=your_openai_api_key_here
# To:     OPENAI_API_KEY=sk-your-actual-key

nano .env  # or use your preferred editor
```

**Don't have an API key?** Get one at https://platform.openai.com/api-keys

### Step 2: Run Test Pipeline

```bash
./run_pipeline.sh test
```

**What this does:**
- Processes 1 manuscript (19 reviews)
- Tests all pipeline steps
- Takes ~30 seconds
- Costs ~$0.10

**Expected output:**
```
✓ API key loaded
Running TEST pipeline (single manuscript)...
Executing pipeline: config/test_pipeline.yaml
...
✓ Pipeline completed successfully!
```

### Step 3: View Test Results

```bash
# See what was generated
ls -lh output/

# View the output
cat output/test_extraction.jsonl | python -m json.tool | less
```

## 🎯 Next Actions (This Week)

### Run Full Pipeline

Once the test works:

```bash
./run_pipeline.sh full
```

**What this does:**
- Processes all 3 manuscripts (76 reviews)
- Generates complete editorial briefs
- Takes ~5-10 minutes
- Costs ~$2-3

### Analyze Results

```bash
python analyze_results.py
```

**What you'll see:**
- Overall statistics (major issues, minor issues, disagreements)
- Quality metrics (evidence coverage, validation pass rate)
- Per-brief analysis
- Success criteria assessment
- Recommendations for improvement

### Review Output

```bash
# View first editorial brief
head -1 output/editorial_briefs.jsonl | python -m json.tool > brief_example.json
cat brief_example.json
```

**Check for:**
- ✓ Major issues have evidence excerpts
- ✓ Disagreements are explicitly noted
- ✓ Action checklist is specific and testable
- ✓ Consensus snapshot makes sense
- ✓ Validation passed

## 📊 Evaluation Phase (Next 2 Weeks)

### 1. Create Gold Standard

Manually synthesize 5-10 briefs for comparison:

```bash
mkdir gold_standard

# For each manuscript:
# 1. Read all reviews manually
# 2. Write your own editorial brief
# 3. Save as gold_standard/manuscript_{id}.json
```

**Format to match:**
```json
{
  "manuscript_id": "2-150",
  "major_issues": [
    {"description": "...", "category": "methodology"}
  ],
  "minor_issues": [...],
  "consensus": "accept with revisions"
}
```

### 2. Compare Pipeline vs Manual

Create comparison script (you'll need to write this):

```python
# evaluate_against_gold.py
# Calculate:
# - Major issue recall (% of manual issues found by pipeline)
# - Major issue precision (% of pipeline issues that are real)
# - Disagreement accuracy
```

### 3. Measure Success Metrics

From opportunity assessment:

| Metric | Target | How to Check |
|--------|--------|--------------|
| Major issue recall | ≥85% | Compare to gold standard |
| Major issue precision | ≥80% | Validate pipeline issues |
| Traceability coverage | ≥95% | Check evidence excerpts (done automatically) |
| Disagreement fidelity | ≥4/5 | Rate conflict capture accuracy |

## 🔧 Optimization Phase (Next 2-4 Weeks)

### Run DocETL Optimizer

```bash
cd docetl_pipeline

# Generate optimized pipeline
docetl optimize config/pipeline.yaml --output config/pipeline_optimized.yaml

# Run optimized version
docetl run config/pipeline_optimized.yaml
```

**What the optimizer does:**
- Analyzes your pipeline performance
- Suggests improvements (gleaning, prompt decomposition, etc.)
- Generates optimized configuration
- Can improve quality by 10-30%

### Iterate Based on Results

If metrics don't meet targets:

**Low recall (missing issues):**
- Strengthen extraction prompts
- Add gleaning operation (iterative extraction)
- Use more powerful model for Step A

**Low precision (false positives):**
- Improve severity classification
- Add filtering in Step A
- Strengthen validation in Step D

**Poor traceability:**
- Enforce stricter evidence requirements
- Add validation rules
- Filter issues without excerpts

**Missed disagreements:**
- Improve Step B resolution logic
- Don't merge conflicting issues
- Enhance Step C synthesis prompts

## 📈 Scaling Phase (1-2 Months)

### Collect More Data

```bash
cd data_collection

# Collect 30 manuscripts
python collect_reviews.py --num-manuscripts 30 --sources f1000

# Or 50 manuscripts
python collect_reviews.py --config comprehensive
```

### Process Larger Dataset

```bash
# Prepare new data
cd ../docetl_pipeline
python prepare_input.py

# Run pipeline
./run_pipeline.sh full

# Analyze
python analyze_results.py
```

### Cost Management

For larger datasets:

```yaml
# Edit config/pipeline.yaml
# Change models to cheaper options:
default_model: gpt-4o-mini  # Instead of gpt-4o

# Or be selective:
operations:
  - name: extract_review_issues
    model: gpt-4o  # Keep high quality here
  - name: synthesize_manuscript
    model: gpt-4o  # And here
  - name: validate_synthesis
    model: gpt-4o-mini  # But use cheaper for validation
```

## 🎯 POC Completion Checklist

- [ ] Pipeline executed successfully on test data
- [ ] Full pipeline run on all 3 manuscripts
- [ ] Results analyzed and documented
- [ ] Gold standard created (10-15 briefs)
- [ ] Metrics measured against targets
- [ ] Optimization iteration completed
- [ ] Scaled to 30-50 manuscripts
- [ ] Final evaluation report written
- [ ] (Optional) Editor feedback gathered
- [ ] POC presentation prepared

## 📝 Documentation You Have

### Quick Reference
- `docetl_pipeline/QUICKSTART.md` - Quick start guide
- `NEXT_STEPS.md` - This file

### Comprehensive Docs
- `docetl_pipeline/README.md` - Full pipeline documentation
- `PIPELINE_SUMMARY.md` - Build summary and deliverables
- `SYSTEM_ARCHITECTURE.md` - Complete system architecture
- `COLLECTION_RESULTS.md` - Data collection analysis

### Technical Specs
- `opportunity assessment.md` - Original requirements
- `data_collection/README.md` - Collection system docs
- `docetl_pipeline/config/pipeline.yaml` - Pipeline configuration

## 🆘 Getting Help

### Common Issues

**"No API key found"**
```bash
cat .env | grep OPENAI_API_KEY
# Should show your key, not the placeholder
```

**"File not found"**
```bash
ls input/
# Should show: reviews.jsonl, manuscripts.jsonl
# If missing: python prepare_input.py
```

**"Pipeline fails"**
```bash
# Check logs
cat output/*.log

# Try test first
./run_pipeline.sh test

# Check DocETL installation
pip list | grep docetl
```

**"Poor quality results"**
```bash
# Run optimizer
docetl optimize config/pipeline.yaml

# Use stronger models
# Edit pipeline.yaml: change gpt-4o-mini to gpt-4o
```

### Resources

- DocETL Docs: https://ucbepic.github.io/docetl/
- OpenAI API: https://platform.openai.com/docs
- Project Issues: Check the troubleshooting sections in README files

## 💡 Pro Tips

1. **Start Small**: Always run test pipeline before full pipeline
2. **Monitor Costs**: Check OpenAI usage dashboard regularly
3. **Validate Often**: Run analyze_results.py after each pipeline run
4. **Save Everything**: Keep all output files for comparison
5. **Iterate Quickly**: Test → Analyze → Optimize → Repeat
6. **Document Findings**: Keep notes on what works/doesn't work
7. **Compare Versions**: Run both original and optimized pipelines

## 🎓 Learning More

### About DocETL
- Tutorial: https://ucbepic.github.io/docetl/tutorial/
- Examples: https://github.com/ucbepic/docetl/tree/main/examples
- Paper: (check DocETL website)

### About Your Pipeline
- Read `config/pipeline.yaml` - it's well-commented
- Experiment with prompts
- Try different models
- Adjust thresholds and parameters

## 📞 Next Action

**Right now, do this:**

```bash
cd /home/shikha/Main/Coding/Prototype\ 4/docetl_pipeline
cp .env.template .env
nano .env
# Add your OpenAI API key
./run_pipeline.sh test
```

**Then:**
```bash
python analyze_results.py
```

**If successful:**
```bash
./run_pipeline.sh full
python analyze_results.py
```

---

## Success Criteria

You'll know you're successful when:

✅ Test pipeline runs without errors
✅ Full pipeline generates 3 editorial briefs
✅ Evidence coverage ≥95%
✅ Validation pass rate ≥90%
✅ Briefs are readable and useful
✅ Major issues are identified with evidence
✅ Disagreements are captured
✅ Action checklist is actionable

---

**You're ready to go! Start with the test pipeline now.**

Good luck! 🚀
