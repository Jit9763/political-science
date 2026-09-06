import urllib.request
import re

def get_latest_video_id_from_channel(channel_input):
    """Resolve latest video ID from channel handle or video URL."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # If it's already a direct video link or ID
    if 'v=' in channel_input or '/live/' in channel_input or len(channel_input) == 11:
        match = re.search(r'(?:v=|\/live\/|\/embed\/|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})', channel_input)
        if match:
            return match.group(1)
        if len(channel_input) == 11:
            return channel_input

    # If it's a channel handle like @NirmanIAS or channel URL
    channel_url = channel_input
    if not channel_url.startswith('http'):
        if not channel_url.startswith('@'):
            channel_url = '@' + channel_url
        channel_url = f"https://www.youtube.com/{channel_url}/videos"

    print(f"Finding latest video for channel URL: {channel_url}...")
    try:
        req = urllib.request.Request(channel_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            unique_ids = []
            for m in matches:
                if m not in unique_ids:
                    unique_ids.append(m)
            if unique_ids:
                print(f"Found latest channel video ID: {unique_ids[0]}")
                return unique_ids[0]
    except Exception as e:
        print(f"Error fetching channel videos: {e}")
    return ""

if __name__ == '__main__':
    vid = get_latest_video_id_from_channel("https://www.youtube.com/@NirmanIAS")
    print("Resolved Video ID:", vid)
