"""
YouTube API wrapper for video discovery and data retrieval
"""

import os
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def get_channel_videos(self, channel_id, max_results=50, published_after=None):
        """Get recent videos from a specific channel"""
        try:
            # First get the uploads playlist ID
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                return []
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            playlist_request = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            )
            
            videos = []
            
            while playlist_request:
                playlist_response = playlist_request.execute()
                
                for item in playlist_response['items']:
                    video_id = item['snippet']['resourceId']['videoId']
                    published_at = datetime.fromisoformat(
                        item['snippet']['publishedAt'].replace('Z', '+00:00')
                    )
                    
                    # Filter by date if specified
                    if published_after and published_at < published_after.replace(tzinfo=published_at.tzinfo):
                        continue
                    
                    # Get detailed video info
                    video_details = self.get_video_details(video_id)
                    if video_details:
                        videos.append(video_details)
                
                # Get next page
                playlist_request = self.youtube.playlistItems().list_next(
                    playlist_request, playlist_response
                )
                
                if len(videos) >= max_results:
                    break
            
            return videos[:max_results]
            
        except HttpError as e:
            print(f"HTTP error getting channel videos: {e}")
            return []
        except Exception as e:
            print(f"Error getting channel videos: {e}")
            return []
    
    def search_videos(self, query, max_results=50, published_after=None):
        """Search for videos using query terms"""
        try:
            search_params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': min(max_results, 50),  # API limit
                'order': 'relevance'
            }
            
            # Add date filter if specified
            if published_after:
                search_params['publishedAfter'] = published_after.isoformat() + 'Z'
            
            search_response = self.youtube.search().list(**search_params).execute()
            
            videos = []
            for item in search_response['items']:
                video_id = item['id']['videoId']
                video_details = self.get_video_details(video_id)
                if video_details:
                    videos.append(video_details)
            
            return videos
            
        except HttpError as e:
            print(f"HTTP error searching videos: {e}")
            return []
        except Exception as e:
            print(f"Error searching videos: {e}")
            return []
    
    def get_video_details(self, video_id):
        """Get detailed information about a specific video"""
        try:
            response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()
            
            if not response['items']:
                return None
            
            item = response['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            return {
                'id': video_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'channel_id': snippet['channelId'],
                'channel_title': snippet['channelTitle'],
                'published_at': snippet['publishedAt'],
                'thumbnail_url': snippet['thumbnails'].get('high', {}).get('url', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'duration': content_details.get('duration', ''),
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId', ''),
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }
            
        except HttpError as e:
            print(f"HTTP error getting video details: {e}")
            return None
        except Exception as e:
            print(f"Error getting video details: {e}")
            return None
    
    def get_video_transcript(self, video_id):
        """Get video transcript/captions (requires additional setup)"""
        # This would require youtube-transcript-api package
        # For now, return None - can be implemented later
        return None
    
    def get_channel_info(self, channel_id):
        """Get information about a YouTube channel"""
        try:
            response = self.youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            ).execute()
            
            if not response['items']:
                return None
            
            item = response['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})
            
            return {
                'id': channel_id,
                'title': snippet['title'],
                'description': snippet['description'],
                'thumbnail_url': snippet['thumbnails'].get('high', {}).get('url', ''),
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'video_count': int(statistics.get('videoCount', 0)),
                'view_count': int(statistics.get('viewCount', 0)),
                'custom_url': snippet.get('customUrl', ''),
                'country': snippet.get('country', ''),
                'published_at': snippet['publishedAt']
            }
            
        except HttpError as e:
            print(f"HTTP error getting channel info: {e}")
            return None
        except Exception as e:
            print(f"Error getting channel info: {e}")
            return None

def test_api():
    """Test the YouTube API functionality"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Please set YOUTUBE_API_KEY environment variable")
        return
    
    api = YouTubeAPI(api_key)
    
    # Test search
    print("Testing search for 'AI coding'...")
    videos = api.search_videos('AI coding', max_results=5)
    print(f"Found {len(videos)} videos")
    
    for video in videos[:2]:
        print(f"- {video['title']} by {video['channel_title']}")
    
if __name__ == "__main__":
    test_api()
