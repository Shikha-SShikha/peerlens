#!/bin/bash
# Run the DocETL peer review synthesis pipeline

set -e

echo "=================================="
echo "DocETL Peer Review Synthesis"
echo "=================================="

# Check for .env file
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "Please create a .env file with your OpenAI API key:"
    echo "  cp .env.template .env"
    echo "  # Then edit .env and add your OPENAI_API_KEY"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set in .env file!"
    exit 1
fi

echo "✓ API key loaded"

# Determine which pipeline to run
PIPELINE=${1:-full}

if [ "$PIPELINE" == "test" ]; then
    echo ""
    echo "Running TEST pipeline (single manuscript)..."
    CONFIG="config/test_pipeline.yaml"
elif [ "$PIPELINE" == "full" ]; then
    echo ""
    echo "Running FULL synthesis pipeline..."
    CONFIG="config/pipeline.yaml"
else
    echo "❌ Unknown pipeline: $PIPELINE"
    echo "Usage: ./run_pipeline.sh [test|full]"
    exit 1
fi

# Create output directory
mkdir -p output

# Run DocETL pipeline
echo ""
echo "Executing pipeline: $CONFIG"
echo "=================================="
docetl run "$CONFIG"

# Check results
if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✓ Pipeline completed successfully!"
    echo "=================================="
    echo ""
    echo "Output files:"
    ls -lh output/
    echo ""
    echo "Next steps:"
    echo "  - Review the output in output/"
    echo "  - Run analysis: python analyze_results.py"
else
    echo ""
    echo "❌ Pipeline failed!"
    exit 1
fi
