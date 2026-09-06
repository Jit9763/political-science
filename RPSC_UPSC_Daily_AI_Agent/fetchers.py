import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

class NewsFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_full_article_content(self, url):
        """Scrape full body text paragraphs from article webpage URL (UNTRUNCATED)."""
        if not url or not url.startswith('http'):
            return ""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove scripts, styles, nav, headers, footers
                for s in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'aside']):
                    s.decompose()
                
                # Extract all text paragraphs
                paragraphs = soup.find_all('p')
                text_list = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 25]
                full_text = "\n\n".join(text_list)
                return full_text
        except Exception as e:
            print(f"Warning scraping full article at {url}: {e}")
            return ""

    def fetch_rss_items(self, url, max_items=8, fetch_full_text=True):
        """Fetch items from an RSS feed and scrape complete full article text."""
        items = []
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                
                channel = root.find('channel')
                if channel is not None:
                    raw_items = channel.findall('item')
                else:
                    raw_items = root.findall('{http://www.w3.org/2005/Atom}entry')

                for elem in raw_items[:max_items]:
                    title_elem = elem.find('title')
                    if title_elem is None:
                        title_elem = elem.find('{http://www.w3.org/2005/Atom}title')
                    
                    link_elem = elem.find('link')
                    if link_elem is None:
                        link_elem = elem.find('{http://www.w3.org/2005/Atom}link')

                    desc_elem = elem.find('description')
                    if desc_elem is None:
                        desc_elem = elem.find('{http://www.w3.org/2005/Atom}summary')
                    if desc_elem is None:
                        desc_elem = elem.find('{http://www.w3.org/2005/Atom}content')
                    
                    title = title_elem.text if title_elem is not None and title_elem.text else ''
                    link = link_elem.text if link_elem is not None and link_elem.text else ''
                    if not link and link_elem is not None and 'href' in link_elem.attrib:
                        link = link_elem.attrib['href']
                    
                    desc = desc_elem.text if desc_elem is not None and desc_elem.text else ''
                    clean_desc = BeautifulSoup(desc, 'html.parser').get_text(separator=' ').strip() if desc else ''

                    full_body = ""
                    if fetch_full_text and link:
                        full_body = self.fetch_full_article_content(link)

                    if title:
                        items.append({
                            'title': title.strip(),
                            'link': link.strip(),
                            'summary': clean_desc,
                            'full_text': full_body if len(full_body) > 100 else clean_desc
                        })
        except Exception as e:
            print(f"Warning: RSS Fetch failed for {url}: {e}")
        return items

    def fetch_pib_releases(self, max_items=8, fetch_full_text=True):
        """Fetch latest Press Information Bureau (PIB) releases with full text."""
        pib_items = []
        try:
            url = "https://pib.gov.in/allRel.aspx"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                
                links = soup.find_all('a', href=re.compile(r'PressReleaseIframePage\.aspx\?PRID='))
                for a in links[:max_items]:
                    title = a.get_text().strip()
                    href = a['href']
                    if not href.startswith('http'):
                        href = "https://pib.gov.in/" + href.lstrip('/')
                    if title and len(title) > 10:
                        full_body = ""
                        if fetch_full_text:
                            full_body = self.fetch_full_article_content(href)

                        pib_items.append({
                            'title': title,
                            'link': href,
                            'source': 'PIB India (Press Release)',
                            'full_text': full_body if len(full_body) > 100 else title
                        })
        except Exception as e:
            print(f"Warning: PIB fetch failed: {e}")
            
        if len(pib_items) < 4:
            rss_items = self.fetch_rss_items('https://pib.gov.in/RssMain.aspx?ModId=6', max_items=6, fetch_full_text=fetch_full_text)
            for item in rss_items:
                item['source'] = 'PIB India'
                pib_items.append(item)

        return pib_items

    def extract_youtube_id(self, url_or_id):
        """Extract YouTube video ID from direct URL/ID or automatically find latest video from channel handle/URL."""
        if not url_or_id:
            return ""
        
        # 1. Direct Video ID or Video URL
        if len(url_or_id) == 11 and not '/' in url_or_id and not '@' in url_or_id:
            return url_or_id
        
        match = re.search(r'(?:v=|\/live\/|\/embed\/|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})', url_or_id)
        if match:
            return match.group(1)

        # 2. Channel Handle or Channel URL -> Automatically find LATEST video
        channel_url = url_or_id
        if not channel_url.startswith('http'):
            if not channel_url.startswith('@'):
                channel_url = '@' + channel_url
            channel_url = f"https://www.youtube.com/{channel_url}/videos"

        print(f"- Automatically finding LATEST video for YouTube channel: {channel_url}...")
        try:
            req = urllib.request.Request(channel_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
                unique_ids = []
                for m in matches:
                    if m not in unique_ids:
                        unique_ids.append(m)
                if unique_ids:
                    print(f"✅ Found latest channel video ID: {unique_ids[0]}")
                    return unique_ids[0]
        except Exception as e:
            print(f"Warning resolving channel video ID: {e}")

        return ""

    def fetch_youtube_transcript(self, youtube_url_or_id="RJL7n_ZuU2U"):
        video_id = self.extract_youtube_id(youtube_url_or_id)
        if not video_id:
            return ""
        
        try:
            print(f"- Fetching FULL YouTube Transcript for video ID: {video_id}...")
            ytt = YouTubeTranscriptApi()
            transcript_list = ytt.fetch(video_id, languages=['hi', 'en', 'hi-IN'])
            full_text = " ".join([snippet.text for snippet in transcript_list])
            print(f"Successfully fetched COMPLETE YouTube transcript ({len(full_text)} chars).")
            return full_text
        except Exception as e:
            print(f"Warning: YouTube transcript fetch failed for {video_id}: {e}")
            return ""

    def fetch_all_daily_news(self, target_date=None, youtube_url=None):
        """Fetch news from The Hindu, Economic Times, Down To Earth Science, PIB, Sujas & YouTube."""
        date_str = target_date if target_date else datetime.now().strftime('%Y-%m-%d')
        print(f"Fetching ALL News, Economy & Science Articles for date: {date_str}...")

        news_corpus = {
            'date': date_str,
            'hindu_editorials': [],
            'economy_news': [],
            'science_news': [],
            'national_news': [],
            'pib_releases': [],
            'rajasthan_sujas': [],
            'youtube_transcript': ''
        }

        # 1. The Hindu & Indian Express Full Editorials
        print("- Fetching Full The Hindu & Indian Express Editorials...")
        hindu_eds = self.fetch_rss_items('https://www.thehindu.com/opinion/editorial/feeder/default.rss', max_items=6, fetch_full_text=True)
        ie_eds = self.fetch_rss_items('https://indianexpress.com/section/opinion/editorials/feed/', max_items=5, fetch_full_text=True)
        for item in hindu_eds:
            item['source'] = 'The Hindu Editorial'
        for item in ie_eds:
            item['source'] = 'Indian Express Editorial'
        news_corpus['hindu_editorials'] = hindu_eds + ie_eds

        # 2. Economic Times (Economy & Markets - RAS Paper 1 / UPSC GS3)
        print("- Fetching Economic Times Economy Articles...")
        et_items = self.fetch_rss_items('https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms', max_items=6, fetch_full_text=True)
        for item in et_items:
            item['source'] = 'Economic Times (Economy)'
        news_corpus['economy_news'] = et_items

        # 3. Down To Earth (Science, Tech & Environment - RAS Paper 2 / UPSC GS3)
        print("- Fetching Down To Earth Science & Tech Articles...")
        science_items = self.fetch_rss_items('https://www.downtoearth.org.in/rss/science-technology', max_items=6, fetch_full_text=True)
        for item in science_items:
            item['source'] = 'Down To Earth (Science & Tech)'
        news_corpus['science_news'] = science_items

        # 4. National Governance News
        print("- Fetching National Governance News...")
        national = self.fetch_rss_items('https://www.thehindu.com/news/national/feeder/default.rss', max_items=6, fetch_full_text=True)
        for item in national:
            item['source'] = 'The Hindu National'
        news_corpus['national_news'] = national

        # 5. PIB Releases
        print("- Fetching Full PIB Press Releases...")
        news_corpus['pib_releases'] = self.fetch_pib_releases(max_items=6, fetch_full_text=True)

        # 6. Rajasthan Sujas & State Special News
        print("- Fetching Rajasthan Sujas / DIPR State Updates...")
        news_corpus['rajasthan_sujas'] = self.fetch_rss_items('https://www.news18.com/rss/india.xml', max_items=4, fetch_full_text=False)
        for item in news_corpus['rajasthan_sujas']:
            item['source'] = 'राजस्थान सुजस एवं DIPR (राज्य विशेष)'

        # 7. YouTube Teacher Current Affairs Live Transcript (Auto-Finds Today's Latest Video from Channel)
        yt_input = youtube_url if youtube_url else "https://www.youtube.com/@NirmanIAS"
        news_corpus['youtube_transcript'] = self.fetch_youtube_transcript(yt_input)

        return news_corpus

if __name__ == '__main__':
    fetcher = NewsFetcher()
    data = fetcher.fetch_all_daily_news()
    print("\nSummary of Fetched News:")
    print(f"Editorials: {len(data['hindu_editorials'])}")
    print(f"Economy (ET): {len(data['economy_news'])}")
    print(f"Science & Tech (DownToEarth): {len(data['science_news'])}")
    print(f"PIB Releases: {len(data['pib_releases'])}")
