"""
Content analyzer for determining AI coding relevance and categorization
"""

import re
from collections import Counter

class ContentAnalyzer:
    def __init__(self):
        # Keywords for AI coding content detection
        self.ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'llm', 'gpt', 
            'claude', 'chatgpt', 'copilot', 'github copilot', 'openai', 'anthropic',
            'neural network', 'deep learning', 'transformer', 'bert', 'nlp'
        ]
        
        self.coding_keywords = [
            'programming', 'coding', 'development', 'software', 'code', 'python',
            'javascript', 'react', 'node', 'web development', 'app development',
            'api', 'framework', 'library', 'tutorial', 'how to code', 'build',
            'create', 'developer', 'engineering'
        ]
        
        self.ai_coding_keywords = [
            'ai coding', 'ai programming', 'code with ai', 'ai assistant',
            'prompt engineering', 'code generation', 'automated coding',
            'ai pair programming', 'intelligent code completion', 'ai debugging',
            'code review ai', 'ai refactoring'
        ]
        
        # Categories for video classification
        self.categories = {
            'claude': ['claude', 'anthropic', 'claude ai', 'claude coding'],
            'chatgpt': ['chatgpt', 'chat gpt', 'openai', 'gpt-4', 'gpt-3'],
            'copilot': ['github copilot', 'copilot', 'microsoft copilot'],
            'tutorials': ['tutorial', 'how to', 'guide', 'learn', 'course', 'lesson'],
            'tools': ['tool', 'extension', 'plugin', 'ide', 'vscode', 'editor'],
            'development': ['build', 'create', 'develop', 'project', 'app'],
            'review': ['review', 'comparison', 'vs', 'versus', 'test', 'demo'],
            'advanced': ['advanced', 'expert', 'professional', 'enterprise', 'scaling']
        }
        
        # Channels known for quality AI coding content
        self.trusted_channels = [
            'fireship', 'coding with john', 'freecodecamp', 'traversy media',
            'the net ninja', 'academind', 'programming with mosh', 'sentdex',
            'tech with tim', 'corey schafer', 'derek banas', 'dev ed'
        ]
    
    def is_ai_coding_relevant(self, video):
        """Determine if video is relevant to AI coding"""
        title = video.get('title', '').lower()
        description = video.get('description', '').lower()
        tags = [tag.lower() for tag in video.get('tags', [])]
        channel = video.get('channel_title', '').lower()
        
        # Combine all text content
        content = f"{title} {description} {' '.join(tags)}"
        
        # Check for AI coding specific keywords (high relevance)
        ai_coding_score = sum(1 for keyword in self.ai_coding_keywords 
                             if keyword in content)
        
        # Check for AI keywords
        ai_score = sum(1 for keyword in self.ai_keywords 
                      if keyword in content)
        
        # Check for coding keywords
        coding_score = sum(1 for keyword in self.coding_keywords 
                          if keyword in content)
        
        # Bonus for trusted channels
        channel_bonus = 2 if any(trusted in channel for trusted in self.trusted_channels) else 0
        
        # Calculate total relevance score
        total_score = ai_coding_score * 3 + ai_score + coding_score + channel_bonus
        
        # Must have both AI and coding elements, or specific AI coding keywords
        has_ai = ai_score > 0 or ai_coding_score > 0
        has_coding = coding_score > 0 or ai_coding_score > 0
        
        # Relevant if high AI coding score or both AI and coding present
        is_relevant = (ai_coding_score >= 1) or (has_ai and has_coding and total_score >= 3)
        
        return is_relevant
    
    def calculate_relevance_score(self, video):
        """Calculate numerical relevance score (0-100)"""
        title = video.get('title', '').lower()
        description = video.get('description', '').lower()
        tags = [tag.lower() for tag in video.get('tags', [])]
        channel = video.get('channel_title', '').lower()
        
        content = f"{title} {description} {' '.join(tags)}"
        
        score = 0
        
        # AI coding specific keywords (high value)
        for keyword in self.ai_coding_keywords:
            if keyword in content:
                score += 15
                if keyword in title:  # Extra points for title
                    score += 10
        
        # AI keywords
        for keyword in self.ai_keywords:
            if keyword in content:
                score += 5
                if keyword in title:
                    score += 5
        
        # Coding keywords
        for keyword in self.coding_keywords:
            if keyword in content:
                score += 3
                if keyword in title:
                    score += 3
        
        # Channel reputation
        if any(trusted in channel for trusted in self.trusted_channels):
            score += 20
        
        # Video metrics bonus (popular videos might be more valuable)
        view_count = video.get('view_count', 0)
        like_count = video.get('like_count', 0)
        
        if view_count > 100000:
            score += 10
        elif view_count > 10000:
            score += 5
        
        if like_count > 1000:
            score += 5
        
        return min(score, 100)  # Cap at 100
    
    def categorize_video(self, video):
        """Categorize video into relevant categories"""
        title = video.get('title', '').lower()
        description = video.get('description', '').lower()
        tags = [tag.lower() for tag in video.get('tags', [])]
        
        content = f"{title} {description} {' '.join(tags)}"
        
        video_categories = []
        
        for category, keywords in self.categories.items():
            if any(keyword in content for keyword in keywords):
                video_categories.append(category)
        
        return video_categories
    
    def extract_topics(self, video):
        """Extract main topics from video content"""
        title = video.get('title', '')
        description = video.get('description', '')
        
        # Simple topic extraction - can be enhanced with NLP
        topics = []
        
        # Common AI coding topics
        topic_patterns = {
            'react': r'\breact\b',
            'python': r'\bpython\b',
            'javascript': r'\b(javascript|js)\b',
            'web_development': r'\bweb\s+development\b',
            'api': r'\bapi\b',
            'tutorial': r'\btutorial\b',
            'beginner': r'\b(beginner|basics?)\b',
            'advanced': r'\b(advanced|expert)\b'
        }
        
        content = f"{title} {description}".lower()
        
        for topic, pattern in topic_patterns.items():
            if re.search(pattern, content):
                topics.append(topic)
        
        return topics
    
    def get_category_breakdown(self, videos):
        """Get breakdown of videos by category"""
        all_categories = []
        for video in videos:
            all_categories.extend(video.get('categories', []))
        
        return dict(Counter(all_categories))
    
    def get_trending_topics(self, videos):
        """Identify trending topics from recent videos"""
        all_topics = []
        for video in videos:
            topics = self.extract_topics(video)
            all_topics.extend(topics)
        
        return dict(Counter(all_topics).most_common(10))
    
    def filter_by_category(self, videos, category):
        """Filter videos by specific category"""
        return [video for video in videos 
                if category in video.get('categories', [])]
    
    def filter_by_relevance(self, videos, min_score=50):
        """Filter videos by minimum relevance score"""
        return [video for video in videos 
                if video.get('relevance_score', 0) >= min_score]

def test_analyzer():
    """Test the content analyzer"""
    analyzer = ContentAnalyzer()
    
    # Test videos
    test_videos = [
        {
            'title': 'Build a ChatGPT Clone with React and OpenAI API',
            'description': 'Learn how to create your own AI chat application using React, Node.js and the OpenAI API',
            'tags': ['react', 'chatgpt', 'openai', 'tutorial'],
            'channel_title': 'JavaScript Mastery',
            'view_count': 50000,
            'like_count': 2000
        },
        {
            'title': 'GitHub Copilot vs ChatGPT for Coding - Which is Better?',
            'description': 'Comprehensive comparison of AI coding assistants',
            'tags': ['github copilot', 'chatgpt', 'coding', 'ai'],
            'channel_title': 'Fireship',
            'view_count': 200000,
            'like_count': 8000
        }
    ]
    
    for video in test_videos:
        is_relevant = analyzer.is_ai_coding_relevant(video)
        score = analyzer.calculate_relevance_score(video)
        categories = analyzer.categorize_video(video)
        topics = analyzer.extract_topics(video)
        
        print(f"\nVideo: {video['title']}")
        print(f"Relevant: {is_relevant}")
        print(f"Score: {score}")
        print(f"Categories: {categories}")
        print(f"Topics: {topics}")

if __name__ == "__main__":
    test_analyzer()
