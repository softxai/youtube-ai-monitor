#!/usr/bin/env python3
"""
Fixed test script for YouTube AI Monitor
"""

import os
import sys

# Add src directory to path for imports
sys.path.insert(0, 'src')

def test_monitor_simple():
    """Simple test of monitor functionality"""
    print("\n📺 Testing monitor functionality...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Test the API first
        from youtube_api import YouTubeAPI
        api_key = os.getenv('YOUTUBE_API_KEY')
        api = YouTubeAPI(api_key)
        
        # Search for a few AI coding videos
        print("   🔍 Searching for AI coding videos...")
        videos = api.search_videos('AI coding tutorial', max_results=3)
        
        if videos:
            print(f"   ✅ Found {len(videos)} videos!")
            for i, video in enumerate(videos[:2], 1):
                print(f"      {i}. {video['title'][:50]}...")
            
            # Save one video as test data
            import json
            os.makedirs('data/videos', exist_ok=True)
            
            for video in videos[:1]:  # Save first video
                video['discovered_at'] = '2025-07-24T04:00:00'
                video['categories'] = ['tutorials', 'ai']
                video['relevance_score'] = 85
                
                with open(f"data/videos/{video['id']}.json", 'w') as f:
                    json.dump(video, f, indent=2)
                print(f"   💾 Saved test video: {video['title'][:30]}...")
            
            return True
        else:
            print("   ⚠️  No videos found")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def start_working_dashboard():
    """Start dashboard on port 5001"""
    print("\n🌐 Starting dashboard on port 5001...")
    
    from flask import Flask, jsonify, render_template_string
    import json
    import glob
    
    app = Flask(__name__)
    
    dashboard_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 YouTube AI Monitor</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .video-card { margin-bottom: 15px; }
            .relevance-score { font-weight: bold; }
            .category-badge { margin-right: 5px; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-dark bg-dark">
            <div class="container">
                <span class="navbar-brand">🤖 YouTube AI Monitor</span>
                <span class="navbar-text">{{ videos|length }} Videos Discovered</span>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row">
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5>📺 Total Videos</h5>
                            <h2 class="text-primary">{{ videos|length }}</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5>🎯 System Status</h5>
                            <h4 class="text-success">✅ Running</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5>🔑 API Status</h5>
                            <h4 class="text-success">✅ Connected</h4>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="mt-4">
                <h3>🚀 Recent Discoveries</h3>
                {% if videos %}
                    {% for video in videos %}
                    <div class="card video-card">
                        <div class="card-body">
                            <h5 class="card-title">
                                <a href="{{ video.url }}" target="_blank" class="text-decoration-none">
                                    {{ video.title }}
                                </a>
                                <span class="badge bg-primary relevance-score">{{ video.relevance_score }}%</span>
                            </h5>
                            <p class="card-text">
                                <strong>{{ video.channel_title }}</strong> • 
                                {{ "{:,}".format(video.view_count) }} views
                            </p>
                            <p class="text-muted">{{ video.description[:200] }}...</p>
                            {% for category in video.categories %}
                            <span class="badge bg-secondary category-badge">{{ category }}</span>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="alert alert-info">
                        <h4>🎯 Ready to Discover Videos!</h4>
                        <p>Run the commands below to start finding AI coding videos:</p>
                        <pre class="bg-dark text-light p-3 rounded">
# Test the system
python3 test_dashboard.py

# Discover videos once
python3 -c "
import sys; sys.path.insert(0, 'src')
from monitor import YouTubeMonitor
monitor = YouTubeMonitor()
monitor.run_monitoring_cycle()
"

# Start continuous monitoring
python3 src/monitor.py
                        </pre>
                    </div>
                {% endif %}
            </div>
            
            <div class="mt-4">
                <h3>📋 Quick Commands</h3>
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">🔍 Discover Videos</div>
                            <div class="card-body">
                                <code>python3 src/monitor.py --once</code>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">📊 View Data</div>
                            <div class="card-body">
                                <code>ls data/videos/</code>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    
    @app.route('/')
    def dashboard():
        # Load discovered videos
        videos = []
        if os.path.exists('data/videos'):
            for filename in glob.glob('data/videos/*.json'):
                try:
                    with open(filename, 'r') as f:
                        video = json.load(f)
                        videos.append(video)
                except:
                    pass
        
        # Sort by relevance score
        videos = sorted(videos, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return render_template_string(dashboard_template, videos=videos)
    
    @app.route('/api/videos')
    def api_videos():
        videos = []
        if os.path.exists('data/videos'):
            for filename in glob.glob('data/videos/*.json'):
                try:
                    with open(filename, 'r') as f:
                        video = json.load(f)
                        videos.append(video)
                except:
                    pass
        return jsonify(videos)
    
    print("🎯 Dashboard starting on: http://localhost:5001")
    print("   Alternative URL: http://127.0.0.1:5001")
    print("   Press Ctrl+C to stop")
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")

def main():
    """Main function"""
    print("🚀 YouTube AI Monitor - Fixed Version")
    print("=" * 40)
    
    # Change to project directory
    os.chdir('/Users/xjs/Desktop/youtube-ai-monitor')
    
    # Test monitor functionality
    test_monitor_simple()
    
    print("\n" + "=" * 40)
    print("🎉 Starting dashboard...")
    start_working_dashboard()

if __name__ == "__main__":
    main()
