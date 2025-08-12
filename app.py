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
from werkzeug.utils import secure_filename
from pathlib import Path
import pandas as pd
import re

# Import our core modules
try:
    from core.trend_retriever import get_trending_snippets, get_trend_age_warning
    from core.calendar_generator import generate_calendar
    from core.excel_exporter import export_to_excel
    from core.cache_handler import get_cached_file, save_to_cache
    from core.video_transcriber import VideoTranscriber
    from core.transcript_analyzer import TranscriptAnalyzer
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

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        
        calendar_text = generate_calendar(snippets, month, include_transcripts=True)
        
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
        
        export_to_excel(calendar_text, output_path, include_transcripts=True)
        
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

@app.route('/upload', methods=['GET', 'POST'])
def upload_calendar():
    """Handle calendar upload and refinement"""
    if request.method == 'GET':
        return render_template('upload.html')
    
    try:
        # Check if file was uploaded
        if 'calendar_file' not in request.files:
            flash('No file uploaded!', 'error')
            return redirect(request.url)
        
        file = request.files['calendar_file']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash('Invalid file type! Please upload Excel (.xlsx, .xls), CSV, or TXT files.', 'error')
            return redirect(request.url)
        
        # Get additional parameters
        target_month = request.form.get('target_month', '').strip()
        refinement_focus = request.form.get('refinement_focus', 'general')
        
        if not target_month:
            flash('Please specify the target month for the calendar!', 'error')
            return redirect(request.url)
        
        # Normalize month
        normalized_month = normalize_month(target_month)
        month_key = f"refined_{normalized_month.replace(' ', '_').lower()}"
        
        # Create unique session ID for this refinement
        session_id = f"{int(time.time())}_{month_key}"
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        upload_path = os.path.join(temp_dir, filename)
        file.save(upload_path)
        
        # Initialize status
        generation_status[session_id] = {
            'status': 'starting',
            'progress': 0,
            'message': 'Processing uploaded calendar...',
            'month': normalized_month,
            'month_key': month_key,
            'file_path': None,
            'error': None,
            'refinement_focus': refinement_focus
        }
        
        # Start refinement in background
        thread = threading.Thread(
            target=refine_calendar_background, 
            args=(session_id, upload_path, normalized_month, month_key, refinement_focus)
        )
        thread.daemon = True
        thread.start()
        
        return render_template('generate.html', 
                             session_id=session_id, 
                             month=normalized_month,
                             raw_month=target_month,
                             is_refinement=True)
        
    except Exception as e:
        print(f"Error in upload_calendar: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        flash(f'Upload error: {str(e)}', 'error')
        return redirect(request.url)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests to prevent 404 errors"""
    return '', 204

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
            'caching': True
        }
    })

def refine_calendar_background(session_id, upload_path, month, month_key, refinement_focus):
    """Background task to refine uploaded calendar"""
    try:
        # Update status - parsing file
        generation_status[session_id].update({
            'status': 'parsing_file',
            'progress': 20,
            'message': 'Parsing uploaded calendar...'
        })
        
        # Parse the uploaded file
        calendar_content = parse_uploaded_calendar(upload_path)
        
        if not calendar_content:
            generation_status[session_id].update({
                'status': 'error',
                'progress': 0,
                'message': 'Could not parse the uploaded calendar file',
                'error': 'File parsing failed'
            })
            return
        
        # Update status - fetching trends
        generation_status[session_id].update({
            'status': 'fetching_trends',
            'progress': 40,
            'message': 'Fetching latest trends for refinement...'
        })
        
        snippets = get_trending_snippets(month)
        trend_warning = get_trend_age_warning(month)
        
        # Update status - refining content
        generation_status[session_id].update({
            'status': 'generating_content',
            'progress': 60,
            'message': 'Refining calendar with strategic improvements...'
        })
        
        # Generate refined calendar
        refined_calendar = refine_calendar_content(calendar_content, snippets, month, refinement_focus)
        
        # Update status - creating excel
        generation_status[session_id].update({
            'status': 'creating_excel',
            'progress': 80,
            'message': 'Creating refined Excel file...'
        })
        
        # Export to Excel
        output_dir = 'data/output'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'refined_calendar_{month_key}_{int(time.time())}.xlsx')
        export_to_excel(refined_calendar, output_path)
        
        # Cache the result
        try:
            save_to_cache(month_key, output_path)
        except Exception as cache_error:
            print(f"Caching failed: {cache_error}")
            # Continue even if caching fails
        
        # Update status - completed
        generation_status[session_id].update({
            'status': 'completed',
            'progress': 100,
            'message': 'Refined calendar ready for download!',
            'file_path': output_path,
            'trend_warning': trend_warning,
            'content_rows': len([line for line in refined_calendar.split('\n') if '|' in line and 'Date' not in line])
        })
        
        # Clean up uploaded file
        try:
            os.remove(upload_path)
            os.rmdir(os.path.dirname(upload_path))
        except:
            pass
        
    except Exception as e:
        generation_status[session_id].update({
            'status': 'error',
            'progress': 0,
            'message': f'Refinement error: {str(e)}',
            'error': str(e)
        })

def parse_uploaded_calendar(file_path):
    """Parse uploaded calendar file and extract content"""
    try:
        file_ext = file_path.lower().split('.')[-1]
        
        if file_ext in ['xlsx', 'xls']:
            # Read Excel file
            df = pd.read_excel(file_path)
            return excel_to_text_format(df)
        
        elif file_ext == 'csv':
            # Read CSV file
            df = pd.read_csv(file_path)
            return excel_to_text_format(df)
        
        elif file_ext == 'txt':
            # Read text file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        
        else:
            return None
            
    except Exception as e:
        print(f"Error parsing file: {e}")
        return None

def excel_to_text_format(df):
    """Convert DataFrame to text format for processing"""
    try:
        # Clean up the DataFrame
        df = df.dropna(how='all')  # Remove completely empty rows
        df = df.fillna('')  # Fill NaN values with empty strings
        
        # Clean column names
        df.columns = [str(col).strip() for col in df.columns]
        
        # Create header
        headers = df.columns.tolist()
        text_lines = ['| ' + ' | '.join(str(h) for h in headers) + ' |']
        
        # Add rows
        for _, row in df.iterrows():
            # Skip rows that are completely empty or just contain separators
            row_values = [str(val).strip() if pd.notna(val) else '' for val in row]
            if any(val for val in row_values):  # Only add if row has content
                row_text = '| ' + ' | '.join(row_values) + ' |'
                text_lines.append(row_text)
        
        result = '\n'.join(text_lines)
        print(f"📝 Converted DataFrame to text format: {len(text_lines)} lines")
        return result
    except Exception as e:
        print(f"Error converting to text format: {e}")
        return None

def refine_calendar_content(original_content, snippets, month, focus):
    """Use the SAME high-quality generation system to refine content"""
    try:
        from core.calendar_generator import get_days_in_month, get_transcript_insights, client
        
        # Parse the original content to understand its structure
        lines = original_content.strip().split('\n')
        data_lines = [line for line in lines if '|' in line and line.strip()]
        
        if len(data_lines) < 2:
            print("⚠️ Original content too short, generating new calendar instead")
            from core.calendar_generator import generate_calendar
            return generate_calendar(snippets, month)
        
        # Extract information from original content
        days_in_month = get_days_in_month(month)
        original_rows = len([line for line in data_lines if 'Day' in line and not any(header in line.lower() for header in ['date', 'title', 'hook'])])
        
        print(f"📋 Refining {original_rows} existing entries for FULL {days_in_month}-day month")
        
        # Get transcript insights for better content generation (same as original)
        transcript_insights = get_transcript_insights()
        
        # Use the EXACT SAME model selection logic as original
        if days_in_month > 20:
            model = "gpt-3.5-turbo"
            max_tokens = 2800
        else:
            model = "gpt-4"
            max_tokens = 2500
        
        # Create a focused refinement strategy based on focus area
        focus_instructions = {
            "general": "comprehensive improvements across all elements",
            "hooks": "dramatically improve hooks to be more scroll-stopping and attention-grabbing",
            "engagement": "maximize engagement with better psychological triggers and interaction prompts",
            "conversion": "strengthen CTAs and conversion elements throughout",
            "trends": "incorporate latest trends and current market insights",
            "professional": "enhance professional quality and strategic depth"
        }
        
        focus_instruction = focus_instructions.get(focus, focus_instructions["general"])
        
        # Build the SAME high-quality format as original generation
        enhanced_format = "Day X | \"Title\" | Hook | Body | CTA | Format | Audio | Hashtags | Production | Optimization"
        if transcript_insights:
            enhanced_format += " | Transcript"
        
        # Create expert-level refinement prompt using SAME structure as original
        if transcript_insights:
            common_phrases_text = ", ".join(transcript_insights["common_phrases"][:5]) if transcript_insights["common_phrases"] else "use engaging language"
            
            prompt = f"""You are an ELITE viral content strategist with 50 years of experience. Create a COMPLETE refined calendar for {month} with ALL {days_in_month} days.

ORIGINAL CONTENT TO IMPROVE AND EXPAND:
{original_content}

CURRENT TRENDS: {', '.join(snippets[:3])}
REFINEMENT FOCUS: {focus_instruction}

TRANSCRIPT INSIGHTS (apply to ALL refined content):
- Script length: ~{transcript_insights["avg_word_count"]} words
- Hook length: ~{transcript_insights["avg_hook_length"]} words  
- Successful phrases: {common_phrases_text}

MANDATORY OUTPUT FORMAT: 
{enhanced_format}

CRITICAL REQUIREMENTS:
1. START with the exact header row: {enhanced_format}
2. Generate EXACTLY {days_in_month} content rows (Day 1 through Day {days_in_month})
3. Each row must follow the format perfectly with | separators
4. Transform and improve the original content, then create additional days to reach {days_in_month} total
5. For Transcript column in EVERY row: Create engaging 25-30 second scripts:
   - Hook (0-3s): {transcript_insights["avg_hook_length"]} words max - GRAB attention immediately
   - Body (3-20s): Main value/insight - conversational, authoritative tone
   - CTA (20-30s): Clear engagement call-to-action

Focus on {focus_instruction}. Generate ALL {days_in_month} days - no shortcuts or partial responses."""

        else:
            prompt = f"""You are an ELITE viral content strategist with 50 years of experience. Create a COMPLETE refined calendar for {month} with ALL {days_in_month} days.

ORIGINAL CONTENT TO IMPROVE AND EXPAND:
{original_content}

CURRENT TRENDS: {', '.join(snippets[:3])}
REFINEMENT FOCUS: {focus_instruction}

MANDATORY OUTPUT FORMAT:
{enhanced_format}

CRITICAL REQUIREMENTS:
1. START with the exact header row: {enhanced_format}
2. Generate EXACTLY {days_in_month} content rows (Day 1 through Day {days_in_month})
3. Each row must follow the format perfectly with | separators
4. Transform and improve the original content, then create additional days to reach {days_in_month} total
5. Apply viral content psychology and conversion optimization
6. Focus on {focus_instruction}

Generate ALL {days_in_month} days with scroll-stopping hooks, psychological triggers, and conversion-focused CTAs. No shortcuts or partial responses."""

        print(f"🤖 Using {model} for high-quality refinement...")
        
        # Use SAME generation approach as original
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=max_tokens
        )

        refined_calendar = response.choices[0].message.content.strip()

        # Validate response has content and proper format (same as original)
        if not refined_calendar:
            raise ValueError("❌ OpenAI returned empty response")
            
        lines_with_pipes = [line for line in refined_calendar.split('\n') if '|' in line and 'Day ' in line]
        print(f"📊 Refined {len(lines_with_pipes)} content rows for {days_in_month}-day month")
        
        # If we didn't get enough content, supplement it (same logic as original generator)
        if len(lines_with_pipes) < days_in_month - 2:  # Allow minimal tolerance
            print(f"⚠️ Insufficient refined content: Expected {days_in_month} rows, got {len(lines_with_pipes)}")
            print("🔄 Supplementing missing days...")
            
            missing_days = days_in_month - len(lines_with_pipes)
            start_day = len(lines_with_pipes) + 1
            
            # Generate additional content for missing days
            supplement_prompt = f"""Continue the refined calendar. Generate EXACTLY {missing_days} more content entries starting from Day {start_day} to Day {days_in_month}.

Format: {enhanced_format}

Generate days {start_day} through {days_in_month} in the same high-quality style as the previous content:"""
            
            try:
                supplement_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Use faster model for supplements
                    messages=[{"role": "user", "content": supplement_prompt}],
                    temperature=0.7,
                    max_tokens=1500
                )
                
                supplement_text = supplement_response.choices[0].message.content.strip()
                supplement_lines = [line for line in supplement_text.split('\n') if 'Day ' in line and '|' in line]
                
                if supplement_lines:
                    refined_calendar += "\n" + "\n".join(supplement_lines)
                    lines_with_pipes = [line for line in refined_calendar.split('\n') if '|' in line and 'Day ' in line]
                    print(f"✅ Supplemented refined content. Total rows now: {len(lines_with_pipes)}")
                
            except Exception as supplement_error:
                print(f"⚠️ Could not supplement refined content: {supplement_error}")
        
        return refined_calendar
        
    except Exception as e:
        print(f"Error refining calendar: {e}")
        # Fallback to original generation if refinement fails
        from core.calendar_generator import generate_calendar
        print("🔄 Falling back to new generation...")
        return generate_calendar(snippets, month)

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