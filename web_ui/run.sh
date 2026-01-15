#!/bin/bash
# Run the Peer Review Synthesis Web UI

set -e

echo "=================================="
echo "Peer Review Synthesis Web UI"
echo "=================================="

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Flask not found. Installing dependencies..."
    pip install -q -r requirements.txt
fi

# Check if .env file exists in docetl_pipeline
if [ ! -f "../docetl_pipeline/.env" ]; then
    echo "⚠️  Warning: .env file not found in docetl_pipeline/"
    echo "The pipeline execution will fail without an OpenAI API key."
    echo ""
    echo "Please create ../docetl_pipeline/.env with:"
    echo "OPENAI_API_KEY=your_key_here"
    echo ""
fi

# Check if data exists
if [ ! -d "../data_collection/collected_data" ]; then
    echo "⚠️  Warning: No collected data found"
    echo "Run data collection first:"
    echo "  cd ../data_collection && python collect_reviews.py"
    echo ""
fi

echo ""
echo "Starting web server..."
echo "Open your browser to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run Flask app
python3 app.py
