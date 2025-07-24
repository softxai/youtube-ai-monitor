"""
Flask web dashboard for viewing discovered AI coding videos
"""

import os
import json
import glob
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from analyzer import ContentAnalyzer

app = Flask(__name__)
analyzer = ContentAnalyzer()

# Data directories
DATA_DIR = 'data'
VIDEOS_DIR = os.path.join(DATA_DIR, 'videos')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')

def load_videos():
    """Load all discovered videos from JSON files"""
    videos = []
    
    if not os.path.exists(VIDEOS_DIR):
        return videos
    
    for filename in glob.glob(os.path.join(VIDEOS_DIR, "*.json")):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                video = json.load(f)
                videos.append(video)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    
    return videos

def load_reports():
    """Load daily reports"""
    reports = []
    
    if not os.path.exists(REPORTS_DIR):
        return reports
    
    for filename in glob.glob(os.path.join(REPORTS_DIR, "daily_report_*.json")):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                report = json.load(f)
                reports.append(report)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    
    return sorted(reports, key=lambda x: x['date'], reverse=True)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    videos = load_videos()
    
    # Sort by relevance score and discovery date
    videos = sorted(videos, 
                   key=lambda x: (x.get('relevance_score', 0), 
                                x.get('discovered_at', '')), 
                   reverse=True)
    
    # Get recent videos (last 7 days)
    cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
    recent_videos = [v for v in videos 
                    if v.get('discovered_at', '') >= cutoff_date]
    
    # Statistics
    stats = {
        'total_videos': len(videos),
        'recent_videos': len(recent_videos),
        'categories': analyzer.get_category_breakdown(videos),
        'trending_topics': analyzer.get_trending_topics(recent_videos),
        'avg_relevance': sum(v.get('relevance_score', 0) for v in videos) / len(videos) if videos else 0
    }
    
    return render_template('dashboard.html', 
                         videos=videos[:50],  # Show top 50
                         stats=stats,
                         recent_videos=recent_videos[:20])

@app.route('/videos')
def videos():
    """Videos listing page with filters"""
    all_videos = load_videos()
    
    # Get filter parameters
    category = request.args.get('category', '')
    min_score = int(request.args.get('min_score', 0))
    search = request.args.get('search', '')
    days = int(request.args.get('days', 30))
    
    # Apply filters
    filtered_videos = all_videos
    
    if category:
        filtered_videos = analyzer.filter_by_category(filtered_videos, category)
    
    if min_score > 0:
        filtered_videos = analyzer.filter_by_relevance(filtered_videos, min_score)
    
    if search:
        search_lower = search.lower()
        filtered_videos = [v for v in filtered_videos 
                          if search_lower in v.get('title', '').lower() or 
                             search_lower in v.get('description', '').lower() or
                             search_lower in v.get('channel_title', '').lower()]
    
    if days > 0:
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        filtered_videos = [v for v in filtered_videos 
                          if v.get('discovered_at', '') >= cutoff_date]
    
    # Sort by relevance score
    filtered_videos = sorted(filtered_videos, 
                           key=lambda x: x.get('relevance_score', 0), 
                           reverse=True)
    
    # Get unique categories for filter dropdown
    all_categories = set()
    for video in all_videos:
        all_categories.update(video.get('categories', []))
    
    return render_template('videos.html', 
                         videos=filtered_videos,
                         categories=sorted(all_categories),
                         current_filters={
                             'category': category,
                             'min_score': min_score,
                             'search': search,
                             'days': days
                         })

@app.route('/reports')
def reports():
    """Reports page showing daily summaries"""
    daily_reports = load_reports()
    
    return render_template('reports.html', reports=daily_reports)

@app.route('/api/videos')
def api_videos():
    """API endpoint for videos data"""
    videos = load_videos()
    
    # Apply filters
    category = request.args.get('category')
    min_score = request.args.get('min_score', type=int)
    limit = request.args.get('limit', 50, type=int)
    
    if category:
        videos = analyzer.filter_by_category(videos, category)
    
    if min_score:
        videos = analyzer.filter_by_relevance(videos, min_score)
    
    # Sort and limit
    videos = sorted(videos, key=lambda x: x.get('relevance_score', 0), reverse=True)
    videos = videos[:limit]
    
    return jsonify(videos)

@app.route('/api/stats')
def api_stats():
    """API endpoint for dashboard statistics"""
    videos = load_videos()
    
    cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
    recent_videos = [v for v in videos if v.get('discovered_at', '') >= cutoff_date]
    
    stats = {
        'total_videos': len(videos),
        'recent_videos': len(recent_videos),
        'categories': analyzer.get_category_breakdown(videos),
        'trending_topics': analyzer.get_trending_topics(recent_videos),
        'avg_relevance': sum(v.get('relevance_score', 0) for v in videos) / len(videos) if videos else 0,
        'top_channels': {}
    }
    
    # Top channels
    from collections import Counter
    channels = [v.get('channel_title', '') for v in videos]
    stats['top_channels'] = dict(Counter(channels).most_common(10))
    
    return jsonify(stats)

@app.route('/video/<video_id>')
def video_detail(video_id):
    """Detailed view of a specific video"""
    video_file = os.path.join(VIDEOS_DIR, f"{video_id}.json")
    
    if not os.path.exists(video_file):
        return "Video not found", 404
    
    with open(video_file, 'r', encoding='utf-8') as f:
        video = json.load(f)
    
    return render_template('video_detail.html', video=video)

@app.template_filter('timeago')
def timeago_filter(date_string):
    """Template filter to show relative time"""
    try:
        date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        now = datetime.now(date.tzinfo)
        diff = now - date
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"
    except:
        return date_string

@app.template_filter('number_format')
def number_format_filter(num):
    """Template filter to format large numbers"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)

def create_templates_directory():
    """Create templates directory and basic HTML files if they don't exist"""
    templates_dir = 'templates'
    os.makedirs(templates_dir, exist_ok=True)
    
    # Basic HTML will be created in next commit
    pass

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    create_templates_directory()
    
    # Run the Flask app
    host = os.getenv('FLASK_HOST', 'localhost')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🌐 Starting dashboard at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
