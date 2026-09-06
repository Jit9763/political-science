import os
import re
import urllib.request
import warnings
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

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
        """Fetch items from an RSS feed and scrape complete full article text with fault-tolerant HTML/XML parsing."""
        items = []
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
                soup = BeautifulSoup(xml_data, 'html.parser')
                raw_elems = soup.find_all(['item', 'entry'])
                
                for elem in raw_elems[:max_items]:
                    t_tag = elem.find('title')
                    l_tag = elem.find('link')
                    d_tag = elem.find(['description', 'summary', 'content'])
                    
                    title = t_tag.get_text().strip() if t_tag else ''
                    
                    # Extract link
                    link = ''
                    if l_tag:
                        link = l_tag.get_text().strip()
                        if not link and l_tag.get('href'):
                            link = l_tag.get('href')
                    
                    # Clean cdata or description text
                    desc = ''
                    if d_tag:
                        raw_desc = d_tag.get_text()
                        desc = BeautifulSoup(raw_desc, 'html.parser').get_text(separator=' ').strip()
                    
                    full_body = ""
                    if fetch_full_text and link and link.startswith('http'):
                        full_body = self.fetch_full_article_content(link)

                    if title and len(title) > 5:
                        items.append({
                            'title': title,
                            'link': link,
                            'summary': desc,
                            'full_text': full_body if len(full_body) > 100 else desc
                        })
        except Exception:
            pass
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
        """Extract YouTube video ID from direct URL/ID or target 'The Hindu Analysis' / 'Current Affairs' video from channel RSS."""
        if not url_or_id:
            return ""
        
        # 1. Direct Video ID or Video URL
        if len(url_or_id) == 11 and not '/' in url_or_id and not '@' in url_or_id:
            return url_or_id
        
        match = re.search(r'(?:v=|\/live\/|\/embed\/|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})', url_or_id)
        if match:
            return match.group(1)

        # 2. Channel Handle or Channel URL -> Targeted 'The Hindu / Current Affairs' Video Search
        channel_name = url_or_id
        if not channel_name.startswith('http'):
            if not channel_name.startswith('@'):
                channel_name = '@' + channel_name
            channel_url = f"https://www.youtube.com/{channel_name}"
        else:
            channel_url = url_or_id

        print(f"- Automatically finding 'The Hindu / Current Affairs' video for YouTube channel: {channel_url}...")
        try:
            req = urllib.request.Request(channel_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                
                # Extract channel ID (UC...)
                channel_id_match = re.search(r'"externalChannelId":"(UC[a-zA-Z0-9_-]+)"', html)
                if not channel_id_match:
                    channel_id_match = re.search(r'https://www\.youtube\.com/channel/(UC[a-zA-Z0-9_-]+)', html)

                if channel_id_match:
                    channel_id = channel_id_match.group(1)
                    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                    
                    rss_req = urllib.request.Request(rss_url, headers=self.headers)
                    with urllib.request.urlopen(rss_req, timeout=10) as rss_resp:
                        rss_xml = rss_resp.read()
                        root = ET.fromstring(rss_xml)
                        ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}
                        
                        target_keywords = ['hindu', 'current affairs', 'dnc', 'editorial', 'pib', 'indian express', 'डेली न्यूज', 'द हिंदू', 'न्यूज']
                        fallback_id = None
                        fallback_title = None

                        for entry in root.findall('atom:entry', ns):
                            title_elem = entry.find('atom:title', ns)
                            video_id_elem = entry.find('yt:videoId', ns)
                            if title_elem is not None and video_id_elem is not None:
                                title = title_elem.text
                                v_id = video_id_elem.text
                                if not fallback_id:
                                    fallback_id = v_id
                                    fallback_title = title
                                
                                title_lower = title.lower()
                                if any(kw in title_lower for kw in target_keywords):
                                    print(f"✅ Found targeted Hindu Analysis video: \"{title}\" (ID: {v_id})")
                                    return v_id

                        if fallback_id:
                            print(f"✅ Found channel video: \"{fallback_title}\" (ID: {fallback_id})")
                            return fallback_id

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

    def fetch_downtoearth_articles(self, max_items=5, fetch_full_text=True):
        """Directly scrape Down To Earth Science & Technology articles from section page."""
        items = []
        try:
            url = "https://www.downtoearth.org.in/science-technology"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                links = soup.find_all('a', href=True)
                seen_urls = set()
                for a in links:
                    href = a['href']
                    title = a.get_text().strip()
                    if '/science-technology/' in href and len(title) > 20:
                        if not href.startswith('http'):
                            href = "https://www.downtoearth.org.in" + href
                        if href not in seen_urls:
                            seen_urls.add(href)
                            full_body = self.fetch_full_article_content(href) if fetch_full_text else ""
                            items.append({
                                'title': title,
                                'link': href,
                                'source': 'Down To Earth (Science & Environment)',
                                'summary': title,
                                'full_text': full_body if len(full_body) > 100 else title
                            })
                            if len(items) >= max_items:
                                break
        except Exception as e:
            print(f"Warning scraping Down To Earth: {e}")
        return items

    def fetch_all_daily_news(self, target_date=None, youtube_url=None):
        """Fetch news from The Hindu, Indian Express, Economic Times, LiveMint, Business Standard, Down To Earth Science, PIB, Sujas & YouTube."""
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

        # 2. Economic Times, LiveMint & Business Standard (Economy & Markets - RAS Paper 1 / UPSC GS3)
        print("- Fetching Economic Times, LiveMint & Business Standard Economy Articles...")
        et_items = self.fetch_rss_items('https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms', max_items=5, fetch_full_text=True)
        mint_items = self.fetch_rss_items('https://www.livemint.com/rss/opinion', max_items=5, fetch_full_text=True)
        bs_items = self.fetch_rss_items('https://www.business-standard.com/rss/economy-policy-102.rss', max_items=5, fetch_full_text=True)
        
        for item in et_items:
            item['source'] = 'Economic Times (Economy)'
        for item in mint_items:
            item['source'] = 'LiveMint (Opinion & Economy)'
        for item in bs_items:
            item['source'] = 'Business Standard (Policy & Economy)'
            
        news_corpus['economy_news'] = et_items + mint_items + bs_items

        # 3. Science & Tech (Down To Earth, The Hindu Sci-Tech, Indian Express Tech, ScienceDaily - RAS Paper 2 / UPSC GS3)
        print("- Fetching Science, Technology, Environment & Defence Articles...")
        dte_items = self.fetch_downtoearth_articles(max_items=5, fetch_full_text=True)
        hindu_sci = self.fetch_rss_items('https://www.thehindu.com/sci-tech/science/feeder/default.rss', max_items=5, fetch_full_text=True)
        hindu_tech = self.fetch_rss_items('https://www.thehindu.com/sci-tech/technology/feeder/default.rss', max_items=5, fetch_full_text=True)
        ie_tech = self.fetch_rss_items('https://indianexpress.com/section/technology/feed/', max_items=5, fetch_full_text=True)
        scidaily_items = self.fetch_rss_items('https://www.sciencedaily.com/rss/top/science.xml', max_items=5, fetch_full_text=False)

        for item in hindu_sci:
            item['source'] = 'The Hindu (Science)'
        for item in hindu_tech:
            item['source'] = 'The Hindu (Technology)'
        for item in ie_tech:
            item['source'] = 'Indian Express (Technology)'
        for item in scidaily_items:
            item['source'] = 'ScienceDaily (Global Science Update)'

        news_corpus['science_news'] = dte_items + hindu_sci + hindu_tech + ie_tech + scidaily_items

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

        # 7. YouTube Teacher Current Affairs Live Transcript (Auto-Finds Today's Targeted Hindu Analysis Video)
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
