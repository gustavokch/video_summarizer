import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from video_summarizer import VideoSummarizer, AVAILABLE_MODELS
from log_watchdog import monitor_log_for_pattern
import asyncio

summarizer = VideoSummarizer()

async def bg_processes():
    summarizer.log_watcher()
    summarizer.ollama_server()
app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main route to handle video summarization requests
    """
    if request.method == 'POST':
        try:
            # Get video URL and selected model
            video_url = request.form.get('video_url', '').strip()
            selected_model = request.form.get('model', AVAILABLE_MODELS[0])

            if not video_url:
                return jsonify({
                    'error': 'Please provide a valid YouTube video URL'
                }), 400

            # Initialize VideoSummarizer
            #
            #asyncio.run(VideoSummarizer.ollama_server())

            # Process the video
            transcription_file, summary = summarizer.process_video(
                video_url, 
                model_name=selected_model
            )

            # Read transcription and summary
            with open(transcription_file, 'r') as f:
                transcription = f.read()

            return jsonify({
                'summary': summary,
                'transcription': transcription,
                'success': True
            })

        except Exception as e:
            return jsonify({
                'error': str(e),
                'success': False
            }), 500

    # Render the main page for GET requests
    return render_template(
        'index.html', 
        models=AVAILABLE_MODELS
    )

@app.errorhandler(413)
def request_entity_too_large(error):
    """
    Handler for file size exceeded error
    """
    return jsonify({
        'error': 'File too large. Maximum size is 16 MB',
        'success': False
    }), 413

if __name__ == '__main__':
    asyncio.run(bg_processes())
    app.run(debug=True, host='0.0.0.0', port=5000)


    
