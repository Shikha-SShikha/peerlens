#!/usr/bin/env python3
"""
Peer Review Synthesis Web UI
Professional interface for demonstrating the DocETL synthesis pipeline
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Global state for pipeline execution
pipeline_status = {
    'running': False,
    'stage': None,
    'progress': 0,
    'message': '',
    'results': None,
    'error': None
}


@app.route('/')
def index():
    """Main landing page - shows user journey"""
    return render_template('index.html')


@app.route('/data-selection')
def data_selection():
    """Step 1: Select or upload review data"""
    # Get available collected datasets
    collection_dir = Path('../data_collection/collected_data')
    available_runs = []

    if collection_dir.exists():
        for run_dir in sorted(collection_dir.glob('run_*'), reverse=True):
            summary_file = run_dir / 'summary_statistics.json'
            if summary_file.exists():
                with open(summary_file) as f:
                    summary = json.load(f)
                available_runs.append({
                    'id': run_dir.name,
                    'date': run_dir.name.replace('run_', ''),
                    'manuscripts': summary.get('total_manuscripts', 0),
                    'reviews': summary.get('total_reviews', 0),
                    'path': str(run_dir)
                })

    return render_template('data_selection.html', runs=available_runs)


@app.route('/pipeline-config')
def pipeline_config():
    """Step 2: Configure pipeline settings"""
    return render_template('pipeline_config.html')


@app.route('/processing')
def processing():
    """Step 3: Show pipeline execution in real-time"""
    return render_template('processing.html')


@app.route('/results')
def results():
    """Step 4: Display synthesis results"""
    # Load latest results
    results_file = Path('../docetl_pipeline/output/editorial_briefs.json')
    briefs = []

    if results_file.exists():
        with open(results_file) as f:
            briefs = json.load(f)

    # Calculate statistics
    def safe_int(value, default=0):
        """Safely convert value to int, return default if not possible"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def safe_float(value, default=0.0):
        """Safely convert value to float, return default if not possible"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    stats = {
        'total_briefs': len(briefs),
        'validated': sum(1 for b in briefs if b.get('validation_passed')),
        'avg_confidence': sum(safe_float(b.get('confidence_score', 0)) for b in briefs) / len(briefs) if briefs else 0,
        'total_reviews': sum(safe_int(b.get('num_reviews_synthesized', 0)) for b in briefs)
    }

    return render_template('results.html', briefs=briefs, stats=stats)


@app.route('/api/run-pipeline', methods=['POST'])
def run_pipeline():
    """API endpoint to execute the pipeline"""
    global pipeline_status

    if pipeline_status['running']:
        return jsonify({'error': 'Pipeline already running'}), 400

    data = request.json
    run_id = data.get('run_id')

    # Start pipeline in background thread
    thread = threading.Thread(target=execute_pipeline, args=(run_id,))
    thread.start()

    return jsonify({'status': 'started'})


@app.route('/api/pipeline-status')
def get_pipeline_status():
    """Get current pipeline execution status"""
    return jsonify(pipeline_status)


@app.route('/api/brief/<brief_id>')
def get_brief(brief_id):
    """Get a specific editorial brief"""
    results_file = Path('../docetl_pipeline/output/editorial_briefs.json')

    if results_file.exists():
        with open(results_file) as f:
            briefs = json.load(f)

        for brief in briefs:
            if brief.get('manuscript_id') == brief_id:
                return jsonify(brief)

    return jsonify({'error': 'Brief not found'}), 404


@app.route('/api/export/<format>')
def export_results(format):
    """Export results in various formats"""
    results_file = Path('../docetl_pipeline/output/editorial_briefs.json')

    if format == 'json':
        return send_file(results_file, as_attachment=True)

    elif format == 'summary':
        # Generate summary report
        with open(results_file) as f:
            briefs = json.load(f)

        summary = generate_summary_report(briefs)

        # Save to temp file
        temp_file = Path('uploads/summary_report.txt')
        with open(temp_file, 'w') as f:
            f.write(summary)

        return send_file(temp_file, as_attachment=True, download_name='synthesis_summary.txt')

    return jsonify({'error': 'Invalid format'}), 400


def execute_pipeline(run_id):
    """Execute the DocETL pipeline in background"""
    global pipeline_status

    try:
        pipeline_status['running'] = True
        pipeline_status['error'] = None

        # Stage 1: Prepare input
        pipeline_status['stage'] = 'prepare'
        pipeline_status['progress'] = 10
        pipeline_status['message'] = 'Preparing input data...'

        os.chdir('../docetl_pipeline')
        subprocess.run(['python', 'prepare_input.py'], check=True, capture_output=True)

        # Stage 2: Extract issues
        pipeline_status['stage'] = 'extract'
        pipeline_status['progress'] = 30
        pipeline_status['message'] = 'Extracting issues from reviews...'

        # Stage 3: Synthesize
        pipeline_status['stage'] = 'synthesize'
        pipeline_status['progress'] = 60
        pipeline_status['message'] = 'Synthesizing editorial briefs...'

        # Run pipeline
        result = subprocess.run(
            ['docetl', 'run', 'config/pipeline_simple.yaml'],
            check=True,
            capture_output=True,
            text=True
        )

        # Stage 4: Validate
        pipeline_status['stage'] = 'validate'
        pipeline_status['progress'] = 90
        pipeline_status['message'] = 'Validating results...'

        # Load results
        with open('output/editorial_briefs.json') as f:
            briefs = json.load(f)

        pipeline_status['stage'] = 'complete'
        pipeline_status['progress'] = 100
        pipeline_status['message'] = f'Complete! Generated {len(briefs)} editorial briefs'
        pipeline_status['results'] = {
            'briefs_generated': len(briefs),
            'validated': sum(1 for b in briefs if b.get('validation_passed'))
        }

    except Exception as e:
        pipeline_status['stage'] = 'error'
        pipeline_status['error'] = str(e)
        pipeline_status['message'] = f'Error: {str(e)}'

    finally:
        pipeline_status['running'] = False
        os.chdir('../web_ui')


def generate_summary_report(briefs):
    """Generate a text summary report"""
    report = []
    report.append("=" * 80)
    report.append("PEER REVIEW SYNTHESIS REPORT")
    report.append("=" * 80)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total Briefs: {len(briefs)}")
    report.append(f"Validated: {sum(1 for b in briefs if b.get('validation_passed'))}")
    report.append("\n" + "=" * 80)

    for i, brief in enumerate(briefs, 1):
        report.append(f"\n\n[{i}] {brief.get('manuscript_title', 'Unknown')}")
        report.append("-" * 80)
        report.append(f"Manuscript ID: {brief.get('manuscript_id')}")
        report.append(f"Reviews Synthesized: {brief.get('num_reviews_synthesized')}")
        report.append(f"\nCONSENSUS:\n{brief.get('consensus_summary', 'N/A')}")
        report.append(f"\nMAJOR ISSUES:\n{brief.get('major_issues', 'None')}")
        report.append(f"\nACTION CHECKLIST:\n{brief.get('action_checklist', 'None')}")
        report.append(f"\nVALIDATION: {'✓ Passed' if brief.get('validation_passed') else '✗ Failed'}")
        report.append(f"Confidence: {brief.get('confidence_score')}/100")

    return "\n".join(report)


if __name__ == '__main__':
    # Get port from environment variable (Render provides this) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # Bind to 0.0.0.0 to allow external connections (required for Render)
    # Only enable debug mode if not in production
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
