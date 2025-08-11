#!/usr/bin/env python3
"""
ContentStrategist Web Application
Deploy on Replit for public access
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import tempfile
import threading
import time
from datetime import datetime
import json
import traceback

# Import our core modules
try:
    from core.trend_retriever import get_trending_snippets, get_trend_age_warning
    # Import enhanced calendar generator
    try:
        from core.enhanced_calendar_generator import generate_enhanced_calendar as generate_calendar
        from core.knowledge_base import KnowledgeBase
        print("✅ Enhanced calendar generator loaded")
    except ImportError:
        from core.calendar_generator import generate_calendar
        print("⚠️ Using basic calendar generator (enhanced version unavailable)")
    from core.excel_exporter import export_to_excel
    from core.cache_handler import get_cached_file, save_to_cache
    print("✅ All core modules imported successfully")
except ImportError as e:
    print(f"⚠️  Warning: Could not import some modules: {e}")
    print("📝 Using fallback functions for missing modules")
    # Create fallback functions
    def get_trending_snippets(month):
        return "No trends available - using fallback mode"
    def get_trend_age_warning(month):
        return None
    def generate_calendar(snippets, month):
        return f"""# Sample Content Calendar for {month}

| Date | Hook | Body | CTA | Visual | Audio | Hashtags |
|------|------|------|-----|--------|-------|----------|
| Day 1 | Sample Hook | Sample body content | Sample CTA | Sample visual | Sample audio | #sample #hashtags |
| Day 2 | Sample Hook 2 | Sample body content 2 | Sample CTA 2 | Sample visual 2 | Sample audio 2 | #sample2 #hashtags2 |
"""
    def export_to_excel(text, path):
        # Create a simple text file as fallback
        txt_path = path.replace('.xlsx', '.txt')
        with open(txt_path, 'w') as f:
            f.write(text)
        return txt_path
    def get_cached_file(key):
        return None
    def save_to_cache(key, path):
        pass

# Import helpers - this should always work now
try:
    from utils.helpers import normalize_month
    print("✅ Helper functions imported successfully")
except ImportError as e:
    print(f"❌ Failed to import helpers: {e}")
    def normalize_month(month):
        return month.title() if month else "Current Month"

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-for-sessions')

# Global storage for generation status
generation_status = {}

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_calendar_route():
    """Handle calendar generation request"""
    try:
        # Get user input
        raw_month = request.form.get('month', '').strip()
        if not raw_month:
            flash('Please enter a month!', 'error')
            return redirect(url_for('index'))
        
        # Normalize month
        normalized_month = normalize_month(raw_month)
        month_key = normalized_month.replace(" ", "_").lower()
        
        # Create unique session ID for this generation
        session_id = f"{int(time.time())}_{month_key}"
        
        # Initialize status
        generation_status[session_id] = {
            'status': 'starting',
            'progress': 0,
            'message': 'Initializing...',
            'month': normalized_month,
            'month_key': month_key,
            'file_path': None,
            'error': None
        }
        
        # Start generation in background
        thread = threading.Thread(
            target=generate_calendar_background, 
            args=(session_id, normalized_month, month_key)
        )
        thread.daemon = True
        thread.start()
        
        return render_template('generate.html', 
                             session_id=session_id, 
                             month=normalized_month,
                             raw_month=raw_month)
        
    except Exception as e:
        print(f"Error in generate_calendar_route: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        flash(f'Error starting generation: {str(e)}', 'error')
        return redirect(url_for('index'))

def generate_calendar_background(session_id, month, month_key):
    """Background task to generate calendar"""
    try:
        # Update status
        generation_status[session_id].update({
            'status': 'checking_cache',
            'progress': 10,
            'message': 'Checking for existing calendar...'
        })
        
        # Check cache
        cached_url = get_cached_file(month_key)
        if cached_url:
            generation_status[session_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Found cached calendar!',
                'cached_url': cached_url
            })
            return
        
        # Fetch trends
        generation_status[session_id].update({
            'status': 'fetching_trends',
            'progress': 30,
            'message': 'Fetching latest trends...'
        })
        
        snippets = get_trending_snippets(month)
        trend_warning = get_trend_age_warning(month)
        
        # Generate calendar
        generation_status[session_id].update({
            'status': 'generating_content',
            'progress': 60,
            'message': 'AI is creating your content calendar...'
        })
        
        calendar_text = generate_calendar(snippets, month)
        
        # Export to Excel
        generation_status[session_id].update({
            'status': 'creating_excel',
            'progress': 80,
            'message': 'Creating Excel file...'
        })
        
        # Create temporary file in a permanent location
        output_dir = os.path.join(os.getcwd(), 'data', 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"calendar_{month_key}.xlsx")
        
        export_to_excel(calendar_text, output_path)
        
        # Cache result
        generation_status[session_id].update({
            'status': 'caching',
            'progress': 90,
            'message': 'Saving to cache...'
        })
        
        try:
            save_to_cache(month_key, output_path)
        except Exception as cache_error:
            print(f"Caching failed: {cache_error}")
            # Continue even if caching fails
        
        # Complete
        generation_status[session_id].update({
            'status': 'completed',
            'progress': 100,
            'message': 'Calendar ready for download!',
            'file_path': output_path,
            'trend_warning': trend_warning,
            'content_rows': len([line for line in calendar_text.split('\n') if '|' in line and 'Date' not in line])
        })
        
    except Exception as e:
        generation_status[session_id].update({
            'status': 'error',
            'progress': 0,
            'message': f'Error: {str(e)}',
            'error': str(e)
        })

@app.route('/status/<session_id>')
def get_status(session_id):
    """Get generation status for polling"""
    status = generation_status.get(session_id, {
        'status': 'not_found',
        'progress': 0,
        'message': 'Session not found'
    })
    return jsonify(status)

@app.route('/download/<session_id>')
def download_file(session_id):
    """Download generated Excel file"""
    try:
        status = generation_status.get(session_id)
        if not status:
            flash('Session not found!', 'error')
            return redirect(url_for('index'))
        
        if status['status'] != 'completed':
            flash('Calendar not ready yet!', 'error')
            return redirect(url_for('index'))
        
        file_path = status.get('file_path')
        if not file_path or not os.path.exists(file_path):
            flash('File not found!', 'error')
            return redirect(url_for('index'))
        
        filename = f"content_calendar_{status['month_key']}.xlsx"
        return send_file(file_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'Download error: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')



@app.route('/rag/retrieve', methods=['POST'])
def rag_retrieve():
    """RAG retrieval endpoint for mentor content"""
    try:
        from core.rag_retrieval import RAGRetriever
        
        data = request.get_json()
        query = data.get('query', '')
        creators = data.get('creators', ['hormozi', 'vaibhavsisinty'])
        limit = data.get('limit', 5)  # REGULATED: Default to 5 per creator to prevent oversampling
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        retriever = RAGRetriever()
        results = retriever.retrieve(query, creators, limit)
        
        # Convert to JSON-serializable format
        retrieved_data = []
        for result in results:
            retrieved_data.append({
                'text': result.text,
                'hook': result.hook,
                'caption': result.caption,
                'hashtags': result.hashtags,
                'views': result.views,
                'likes': result.likes,
                'posted_at': result.posted_at,
                'creator_handle': result.creator_handle,
                'reel_id': result.reel_id,
                'reel_url': result.reel_url,
                'relevance_score': result.relevance_score
            })
        
        return jsonify({
            'query': query,
            'results': retrieved_data,
            'count': len(retrieved_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rag/stats')
def rag_stats():
    """Get RAG system statistics"""
    try:
        from core.rag_retrieval import RAGRetriever
        
        retriever = RAGRetriever()
        stats = retriever.get_stats()
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/pipeline/run', methods=['POST'])
def run_rag_pipeline():
    """Run the Instagram RAG pipeline"""
    try:
        from core.instagram_rag_pipeline import InstagramRAGPipeline
        
        pipeline = InstagramRAGPipeline()
        results = pipeline.run_pipeline()
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'month_normalization': True,
            'trend_retrieval': True,
            'ai_generation': True,
            'excel_export': True,
            'caching': True,
            'rag_retrieval': True,
            'instagram_pipeline': True
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data/output', exist_ok=True)
    print("📁 Created data/output directory")
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("🚀 CONTENT STRATEGIST WEB APP STARTING")
    print(f"📡 Server: http://0.0.0.0:{port}")
    print(f"🔧 Debug mode: {debug}")
    print("🌐 Access your app at the URL shown in the Replit webview")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use. Trying port {port + 1}")
            app.run(host='0.0.0.0', port=port + 1, debug=debug)
        else:
            raise e