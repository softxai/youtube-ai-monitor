"""
YouTube AI Coding Monitor - Main monitoring script
Automatically discovers and tracks AI coding-related YouTube videos
"""

import os
import json
import time
import schedule
from datetime import datetime, timedelta
from dotenv import load_dotenv
from youtube_api import YouTubeAPI
from analyzer import ContentAnalyzer

load_dotenv()

class YouTubeMonitor:
    def __init__(self):
        self.api = YouTubeAPI(os.getenv('YOUTUBE_API_KEY'))
        self.analyzer = ContentAnalyzer()
        self.data_dir = 'data'
        self.videos_dir = os.path.join(self.data_dir, 'videos')
        self.reports_dir = os.path.join(self.data_dir, 'reports')
        
        # Create data directories
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Load configuration
        self.channels = os.getenv('MONITOR_CHANNELS', '').split(',')
        self.search_terms = os.getenv('SEARCH_TERMS', '').split(',')
        self.max_videos = int(os.getenv('MAX_VIDEOS_PER_SEARCH', 50))
        self.days_lookback = int(os.getenv('DAYS_LOOKBACK', 7))
        
    def monitor_channels(self):
        """Monitor specific YouTube channels for new AI coding content"""
        print(f"🔍 Monitoring {len(self.channels)} channels...")
        new_videos = []
        
        for channel_id in self.channels:
            if not channel_id.strip():
                continue
                
            try:
                print(f"  📺 Checking channel: {channel_id}")
                videos = self.api.get_channel_videos(
                    channel_id.strip(), 
                    max_results=self.max_videos,
                    published_after=datetime.now() - timedelta(days=self.days_lookback)
                )
                
                for video in videos:
                    if self.is_ai_coding_content(video):
                        new_videos.append(video)
                        self.save_video(video)
                        
            except Exception as e:
                print(f"  ❌ Error checking channel {channel_id}: {e}")
                
        return new_videos
    
    def monitor_search_terms(self):
        """Search for videos using AI coding-related terms"""
        print(f"🔍 Searching with {len(self.search_terms)} terms...")
        new_videos = []
        
        for term in self.search_terms:
            if not term.strip():
                continue
                
            try:
                print(f"  🔎 Searching: '{term.strip()}'")
                videos = self.api.search_videos(
                    term.strip(),
                    max_results=self.max_videos,
                    published_after=datetime.now() - timedelta(days=self.days_lookback)
                )
                
                for video in videos:
                    if self.is_ai_coding_content(video):
                        new_videos.append(video)
                        self.save_video(video)
                        
            except Exception as e:
                print(f"  ❌ Error searching '{term}': {e}")
                
        return new_videos
    
    def is_ai_coding_content(self, video):
        """Determine if video is relevant AI coding content"""
        return self.analyzer.is_ai_coding_relevant(video)
    
    def save_video(self, video):
        """Save video metadata to JSON file"""
        video_id = video['id']
        filename = os.path.join(self.videos_dir, f"{video_id}.json")
        
        # Don't save if already exists
        if os.path.exists(filename):
            return
            
        # Add analysis data
        video['discovered_at'] = datetime.now().isoformat()
        video['categories'] = self.analyzer.categorize_video(video)
        video['relevance_score'] = self.analyzer.calculate_relevance_score(video)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(video, f, indent=2, ensure_ascii=False)
            
        print(f"  💾 Saved: {video['title'][:50]}...")
    
    def generate_daily_report(self):
        """Generate daily summary of discovered videos"""
        today = datetime.now().strftime('%Y-%m-%d')
        report_file = os.path.join(self.reports_dir, f"daily_report_{today}.json")
        
        # Load today's videos
        today_videos = []
        for filename in os.listdir(self.videos_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.videos_dir, filename), 'r') as f:
                    video = json.load(f)
                    discovered_date = video.get('discovered_at', '')[:10]
                    if discovered_date == today:
                        today_videos.append(video)
        
        # Create report
        report = {
            'date': today,
            'total_videos': len(today_videos),
            'categories': self.analyzer.get_category_breakdown(today_videos),
            'top_videos': sorted(today_videos, 
                               key=lambda x: x.get('relevance_score', 0), 
                               reverse=True)[:10],
            'channels': list(set(v.get('channel_title', '') for v in today_videos)),
            'generated_at': datetime.now().isoformat()
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📊 Daily report generated: {len(today_videos)} videos found")
        return report
    
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        print(f"\n🚀 Starting monitoring cycle at {datetime.now()}")
        
        try:
            # Monitor channels and search terms
            channel_videos = self.monitor_channels()
            search_videos = self.monitor_search_terms()
            
            # Remove duplicates
            all_videos = {v['id']: v for v in channel_videos + search_videos}.values()
            
            print(f"✅ Monitoring cycle complete: {len(all_videos)} new videos")
            
            # Generate daily report
            self.generate_daily_report()
            
        except Exception as e:
            print(f"❌ Error in monitoring cycle: {e}")
    
    def start_scheduler(self):
        """Start the scheduled monitoring"""
        interval_hours = int(os.getenv('CHECK_INTERVAL_HOURS', 6))
        
        print(f"⏰ Starting scheduler - checking every {interval_hours} hours")
        print("🎯 Target content: AI coding, Claude, ChatGPT, GitHub Copilot, LLM development")
        
        # Schedule monitoring
        schedule.every(interval_hours).hours.do(self.run_monitoring_cycle)
        
        # Run initial check
        self.run_monitoring_cycle()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main entry point"""
    print("🤖 YouTube AI Coding Monitor Starting...")
    
    # Check for API key
    if not os.getenv('YOUTUBE_API_KEY'):
        print("❌ Error: Please set YOUTUBE_API_KEY in .env file")
        print("   Get your API key from: https://console.developers.google.com/")
        return
    
    monitor = YouTubeMonitor()
    
    # Run based on arguments
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run once and exit
        monitor.run_monitoring_cycle()
    else:
        # Run continuously
        monitor.start_scheduler()

if __name__ == "__main__":
    main()
