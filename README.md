# YouTube AI Coding Monitor

An automated system for discovering and tracking new AI coding-related YouTube videos.

## Features

- 🔍 **Smart Search**: Monitors specific channels and search terms for AI coding content
- 📊 **Data Collection**: Stores video metadata, transcripts, and categorizes content
- 📈 **Analytics**: Tracks trends, popular topics, and content patterns
- 🌐 **Web Dashboard**: Simple interface to browse and filter discovered videos
- 📧 **Notifications**: Daily/weekly summaries of new content
- 🏷️ **Auto-Tagging**: Categorizes videos by topic (LLMs, Copilot, Claude, etc.)

## Project Structure

```
youtube-ai-monitor/
├── src/
│   ├── monitor.py          # Main monitoring script
│   ├── youtube_api.py      # YouTube API wrapper
│   ├── analyzer.py         # Content analysis and categorization
│   └── dashboard.py        # Web dashboard (Flask)
├── data/
│   ├── videos/            # Stored video metadata
│   ├── reports/           # Generated reports
│   └── config/            # Channel lists and search terms
├── templates/             # HTML templates for dashboard
├── static/               # CSS, JS for dashboard
├── requirements.txt      # Python dependencies
└── README.md
```

## Target Content

**Channels to Monitor:**
- AI coding tutorials
- Claude, ChatGPT, GitHub Copilot content
- Programming with AI assistants
- LLM development tutorials
- No-code/low-code AI tools

**Search Terms:**
- "AI coding", "Claude programming", "ChatGPT coding"
- "GitHub Copilot", "AI assistant programming"
- "LLM development", "prompt engineering for code"

## Quick Start

1. **Setup**: `pip install -r requirements.txt`
2. **Configure**: Add YouTube API key and channels to monitor
3. **Run Monitor**: `python src/monitor.py`
4. **View Dashboard**: `python src/dashboard.py`

## Getting Started

This system will help you stay updated with the latest AI coding content without manually browsing YouTube!
