#!/usr/bin/env python3
"""
Setup script for YouTube AI Monitor
Helps with initial configuration and testing
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return
    
    if not os.path.exists('.env.template'):
        print("❌ .env.template not found")
        return
    
    print("📝 Creating .env file from template...")
    with open('.env.template', 'r') as template:
        with open('.env', 'w') as env_file:
            env_file.write(template.read())
    
    print("✅ .env file created")
    print("⚠️  Please edit .env file and add your YouTube API key")

def create_directories():
    """Create necessary data directories"""
    directories = ['data', 'data/videos', 'data/reports', 'templates', 'static']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")

def test_youtube_api():
    """Test YouTube API connection"""
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key or api_key == 'your_youtube_api_key_here':
        print("⚠️  YouTube API key not configured")
        print("   Please update YOUTUBE_API_KEY in .env file")
        return False
    
    print("🔑 Testing YouTube API...")
    try:
        from src.youtube_api import YouTubeAPI
        api = YouTubeAPI(api_key)
        
        # Test with a simple search
        videos = api.search_videos('python programming', max_results=1)
        if videos:
            print("✅ YouTube API connection successful")
            print(f"   Found video: {videos[0]['title']}")
            return True
        else:
            print("⚠️  YouTube API test returned no results")
            return False
            
    except ImportError:
        print("❌ Cannot import YouTube API module")
        return False
    except Exception as e:
        print(f"❌ YouTube API test failed: {e}")
        return False

def create_basic_templates():
    """Create basic HTML templates"""
    templates = {
        'templates/base.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}YouTube AI Monitor{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .video-card { margin-bottom: 20px; }
        .relevance-score { font-weight: bold; }
        .category-badge { margin-right: 5px; }
        .stats-card { margin-bottom: 20px; }
        .video-thumbnail { width: 120px; height: 90px; object-fit: cover; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">🤖 YouTube AI Monitor</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/videos">Videos</a>
                <a class="nav-link" href="/reports">Reports</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>''',
        
        'templates/dashboard.html': '''{% extends "base.html" %}
{% block content %}
<div class="row">
    <div class="col-md-3">
        <div class="card stats-card">
            <div class="card-body text-center">
                <h5>Total Videos</h5>
                <h2 class="text-primary">{{ stats.total_videos }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stats-card">
            <div class="card-body text-center">
                <h5>Recent Videos</h5>
                <h2 class="text-success">{{ stats.recent_videos }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stats-card">
            <div class="card-body text-center">
                <h5>Avg Relevance</h5>
                <h2 class="text-info">{{ "%.1f"|format(stats.avg_relevance) }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stats-card">
            <div class="card-body text-center">
                <h5>Categories</h5>
                <h2 class="text-warning">{{ stats.categories|length }}</h2>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-8">
        <h3>🔥 Recent High-Quality Discoveries</h3>
        {% if recent_videos %}
            {% for video in recent_videos[:10] %}
            <div class="card video-card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-2">
                            {% if video.thumbnail_url %}
                            <img src="{{ video.thumbnail_url }}" class="video-thumbnail rounded" alt="Thumbnail">
                            {% endif %}
                        </div>
                        <div class="col-md-10">
                            <h5 class="card-title">
                                <a href="{{ video.url }}" target="_blank" class="text-decoration-none">{{ video.title }}</a>
                                <span class="badge bg-primary relevance-score">{{ video.relevance_score }}%</span>
                            </h5>
                            <p class="card-text">
                                <strong>{{ video.channel_title }}</strong> • 
                                {{ video.view_count|number_format }} views • 
                                {{ video.discovered_at|timeago }}
                            </p>
                            {% for category in video.categories %}
                            <span class="badge bg-secondary category-badge">{{ category }}</span>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="alert alert-info">
                <h5>No videos discovered yet!</h5>
                <p>Run the monitor to start discovering AI coding videos:</p>
                <code>python src/monitor.py --once</code>
            </div>
        {% endif %}
    </div>
    <div class="col-md-4">
        <h3>📊 Top Categories</h3>
        <div class="card">
            <div class="card-body">
                {% if stats.categories %}
                    {% for category, count in stats.categories.items() %}
                    <div class="d-flex justify-content-between mb-2">
                        <span>{{ category.title() }}</span>
                        <span class="badge bg-primary">{{ count }}</span>
                    </div>
                    {% endfor %}
                {% else %}
                    <p class="text-muted">No categories yet</p>
                {% endif %}
            </div>
        </div>
        
        {% if stats.trending_topics %}
        <h3 class="mt-4">🔍 Trending Topics</h3>
        <div class="card">
            <div class="card-body">
                {% for topic, count in stats.trending_topics.items() %}
                <div class="d-flex justify-content-between mb-2">
                    <span>{{ topic.replace('_', ' ').title() }}</span>
                    <span class="badge bg-success">{{ count }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}''',
        
        'templates/videos.html': '''{% extends "base.html" %}
{% block content %}
<h2>🎥 AI Coding Videos</h2>

<div class="row mb-3">
    <div class="col-md-12">
        <form method="GET" class="row g-3">
            <div class="col-md-3">
                <input type="text" class="form-control" name="search" placeholder="Search videos..." value="{{ current_filters.search }}">
            </div>
            <div class="col-md-2">
                <select class="form-select" name="category">
                    <option value="">All Categories</option>
                    {% for cat in categories %}
                    <option value="{{ cat }}" {% if cat == current_filters.category %}selected{% endif %}>{{ cat.title() }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-2">
                <input type="number" class="form-control" name="min_score" placeholder="Min Score" value="{{ current_filters.min_score or '' }}">
            </div>
            <div class="col-md-2">
                <select class="form-select" name="days">
                    <option value="7" {% if current_filters.days == 7 %}selected{% endif %}>Last 7 days</option>
                    <option value="30" {% if current_filters.days == 30 %}selected{% endif %}>Last 30 days</option>
                    <option value="90" {% if current_filters.days == 90 %}selected{% endif %}>Last 90 days</option>
                    <option value="0" {% if current_filters.days == 0 %}selected{% endif %}>All time</option>
                </select>
            </div>
            <div class="col-md-3">
                <button type="submit" class="btn btn-primary">Filter</button>
                <a href="/videos" class="btn btn-secondary">Clear</a>
            </div>
        </form>
    </div>
</div>

<p class="text-muted">Found {{ videos|length }} videos</p>

{% for video in videos %}
<div class="card video-card">
    <div class="card-body">
        <div class="row">
            <div class="col-md-2">
                {% if video.thumbnail_url %}
                <img src="{{ video.thumbnail_url }}" class="video-thumbnail rounded" alt="Thumbnail">
                {% endif %}
            </div>
            <div class="col-md-10">
                <h5 class="card-title">
                    <a href="{{ video.url }}" target="_blank" class="text-decoration-none">{{ video.title }}</a>
                    <span class="badge bg-primary relevance-score">{{ video.relevance_score }}%</span>
                </h5>
                <p class="card-text">{{ video.description[:300] }}{% if video.description|length > 300 %}...{% endif %}</p>
                <small class="text-muted">
                    <strong>{{ video.channel_title }}</strong> • 
                    {{ video.view_count|number_format }} views • 
                    {{ video.like_count|number_format }} likes • 
                    {{ video.discovered_at|timeago }}
                </small>
                <br>
                {% for category in video.categories %}
                <span class="badge bg-secondary category-badge">{{ category }}</span>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endfor %}

{% if not videos %}
<div class="alert alert-info">
    <h5>No videos found with current filters</h5>
    <p>Try adjusting your search criteria or run the monitor to discover new videos.</p>
</div>
{% endif %}
{% endblock %}''',

        'templates/reports.html': '''{% extends "base.html" %}
{% block content %}
<h2>📈 Daily Reports</h2>

{% if reports %}
    {% for report in reports %}
    <div class="card mb-3">
        <div class="card-header">
            <h5>{{ report.date }} 
                <span class="badge bg-primary">{{ report.total_videos }} videos</span>
            </h5>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-6">
                    <h6>Categories</h6>
                    {% for category, count in report.categories.items() %}
                    <span class="badge bg-secondary me-1">{{ category }}: {{ count }}</span>
                    {% endfor %}
                </div>
                <div class="col-md-6">
                    <h6>Top Videos</h6>
                    <ul class="list-unstyled">
                        {% for video in report.top_videos[:3] %}
                        <li><a href="{{ video.url }}" target="_blank">{{ video.title[:60] }}...</a></li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>
    </div>
    {% endfor %}
{% else %}
    <div class="alert alert-info">
        <h5>No reports available yet</h5>
        <p>Reports will be generated automatically after running the monitor.</p>
    </div>
{% endif %}
{% endblock %}'''
    }
    
    for filename, content in templates.items():
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            f.write(content)
        print(f"📄 Created template: {filename}")

def setup_default_config():
    """Setup default monitoring configuration"""
    print("⚙️  Setting up default configuration...")
    
    # Default channels for AI coding content
    default_channels = [
        "UCFbNIlppjAuEX4znoulh0Cw",  # Web Dev Simplified
        "UC29ju8bIPH5as8OGnQzwJyA",  # Traversy Media
        "UCnX8YZy0rppWRaGE7hDYzjQ",  # Fireship
        "UC8butISFwT-Wl7EV0hUK0BQ",  # freeCodeCamp
        "UCWv7vMbMWH4-V0ZXdmDpPBA"   # Programming with Mosh
    ]
    
    # Default search terms
    default_search_terms = [
        "AI coding tutorial",
        "ChatGPT programming",
        "Claude AI coding",
        "GitHub Copilot tutorial",
        "AI programming assistant",
        "machine learning coding",
        "LLM development"
    ]
    
    print(f"📺 Default channels: {len(default_channels)} tech education channels")
    print(f"🔍 Default search terms: {len(default_search_terms)} AI coding terms")

def main():
    """Main setup function"""
    print("🚀 YouTube AI Monitor Setup")
    print("=" * 40)
    
    # Check requirements
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    install_dependencies()
    
    # Create .env file
    create_env_file()
    
    # Create templates
    create_basic_templates()
    
    # Setup default config
    setup_default_config()
    
    # Test API
    api_works = test_youtube_api()
    
    print("\n" + "=" * 40)
    print("🎉 Setup Complete!")
    
    if api_works:
        print("\n✅ Ready to start monitoring!")
        print("\n📋 Next Steps:")
        print("1. Run a test: python src/monitor.py --once")
        print("2. Start dashboard: python src/dashboard.py")
        print("3. Start continuous monitoring: python src/monitor.py")
        print("\n🌐 Dashboard will be available at: http://localhost:5000")
    else:
        print("\n⚠️  Please configure your YouTube API key in .env file")
        print("   Then run: python setup.py")

if __name__ == "__main__":
    main()
