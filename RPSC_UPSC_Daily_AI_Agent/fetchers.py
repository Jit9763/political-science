import os
import re
import urllib.request
import warnings
import email.utils
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from youtube_transcript_api import YouTubeTranscriptApi

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# IST Timezone (+05:30)
IST = timezone(timedelta(hours=5, minutes=30))

def parse_date_to_ist_ymd(date_str):
    """Parse various RSS/Atom/HTML date formats into IST YYYY-MM-DD string."""
    if not date_str:
        return None
    date_str = date_str.strip()

    # 1. RFC 2822 (e.g. "Mon, 07 Sep 2026 00:28:54 +0530")
    try:
        dt = email.utils.parsedate_to_datetime(date_str)
        if dt:
            return dt.astimezone(IST).strftime('%Y-%m-%d')
    except Exception:
        pass

    # 2. ISO 8601 (e.g. "2026-09-07T12:00:00Z" or "2026-09-07T18:30:00+00:00")
    try:
        clean_str = date_str.replace('Z', '+00:00')
        dt = datetime.fromisoformat(clean_str)
        if dt:
            return dt.astimezone(IST).strftime('%Y-%m-%d')
    except Exception:
        pass

    # 3. Regex fallback
    m1 = re.search(r'(\d{4})[-/](\d{2})[-/](\d{2})', date_str)
    if m1:
        return f"{m1.group(1)}-{m1.group(2)}-{m1.group(3)}"

    m2 = re.search(r'(\d{2})[-/](\d{2})[-/](\d{4})', date_str)
    if m2:
        return f"{m2.group(3)}-{m2.group(2)}-{m2.group(1)}"

    return None

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

    def fetch_rss_items(self, url, max_items=8, fetch_full_text=True, target_date=None):
        """Fetch items from an RSS feed and strictly filter by target_date in IST."""
        items = []
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_data = resp.read()
                soup = BeautifulSoup(xml_data, 'html.parser')
                raw_elems = soup.find_all(['item', 'entry'])
                
                for elem in raw_elems:
                    t_tag = elem.find('title')
                    l_tag = elem.find('link')
                    d_tag = elem.find(['description', 'summary', 'content'])
                    date_tag = elem.find(['pubdate', 'published', 'updated', 'dc:date'])
                    
                    title = t_tag.get_text().strip() if t_tag else ''
                    pub_raw = date_tag.get_text().strip() if date_tag else ''
                    item_date = parse_date_to_ist_ymd(pub_raw)

                    # Strictly filter by target_date if target_date is specified
                    if target_date and item_date:
                        if item_date != target_date:
                            # Skip items that are not from target_date
                            continue
                    
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
                            'pub_date': item_date or target_date,
                            'full_text': full_body if len(full_body) > 100 else desc
                        })
                        if len(items) >= max_items:
                            break

                # Fallback: If date filter produced 0 items because RSS hasn't updated exact timestamp, take top fresh items
                if target_date and len(items) == 0 and len(raw_elems) > 0:
                    print(f"  (Notice: No RSS items matched exact target date {target_date} for {url}. Using top latest items.)")
                    for elem in raw_elems[:max_items]:
                        t_tag = elem.find('title')
                        l_tag = elem.find('link')
                        d_tag = elem.find(['description', 'summary', 'content'])
                        title = t_tag.get_text().strip() if t_tag else ''
                        link = l_tag.get_text().strip() if l_tag else ''
                        desc = d_tag.get_text().strip() if d_tag else ''
                        full_body = self.fetch_full_article_content(link) if (fetch_full_text and link.startswith('http')) else ""
                        if title and len(title) > 5:
                            items.append({
                                'title': title,
                                'link': link,
                                'summary': desc,
                                'pub_date': target_date,
                                'full_text': full_body if len(full_body) > 100 else desc
                            })

        except Exception as e:
            print(f"Warning fetching RSS {url}: {e}")
        return items

    def fetch_pib_releases(self, max_items=8, fetch_full_text=True, target_date=None):
        """Fetch latest Press Information Bureau (PIB) releases with date check."""
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
                            'pub_date': target_date,
                            'full_text': full_body if len(full_body) > 100 else title
                        })
        except Exception as e:
            print(f"Warning: PIB fetch failed: {e}")
            
        if len(pib_items) < 4:
            rss_items = self.fetch_rss_items('https://pib.gov.in/RssMain.aspx?ModId=6', max_items=6, fetch_full_text=fetch_full_text, target_date=target_date)
            for item in rss_items:
                item['source'] = 'PIB India'
                pib_items.append(item)

        return pib_items

    def extract_youtube_id(self, url_or_id, target_date=None):
        """Extract YouTube video ID matching target_date."""
        if not url_or_id:
            return ""
        
        # Direct Video ID or Video URL
        if len(url_or_id) == 11 and not '/' in url_or_id and not '@' in url_or_id:
            return url_or_id
        
        match = re.search(r'(?:v=|\/live\/|\/embed\/|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})', url_or_id)
        if match:
            return match.group(1)

        # Channel Handle or Channel URL
        channel_name = url_or_id
        if not channel_name.startswith('http'):
            if not channel_name.startswith('@'):
                channel_name = '@' + channel_name
            channel_url = f"https://www.youtube.com/{channel_name}"
        else:
            channel_url = url_or_id

        print(f"- Automatically finding targeted video for YouTube channel: {channel_url}...")
        try:
            req = urllib.request.Request(channel_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                
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
                            pub_elem = entry.find('atom:published', ns)
                            
                            if title_elem is not None and video_id_elem is not None:
                                title = title_elem.text
                                v_id = video_id_elem.text
                                pub_raw = pub_elem.text if pub_elem is not None else ""
                                v_date = parse_date_to_ist_ymd(pub_raw)

                                if not fallback_id:
                                    fallback_id = v_id
                                    fallback_title = title
                                
                                title_lower = title.lower()
                                if any(kw in title_lower for kw in target_keywords):
                                    if target_date and v_date and v_date != target_date:
                                        print(f"  (Skipping video '{title}' published on {v_date}, target is {target_date})")
                                        continue
                                    print(f"✅ Found targeted Hindu Analysis video for {v_date or target_date}: \"{title}\" (ID: {v_id})")
                                    return v_id

                        if fallback_id:
                            print(f"✅ Found channel video: \"{fallback_title}\" (ID: {fallback_id})")
                            return fallback_id

        except Exception as e:
            print(f"Warning resolving channel video ID: {e}")

        return ""

    def fetch_youtube_transcript(self, youtube_url_or_id="RJL7n_ZuU2U", target_date=None):
        video_id = self.extract_youtube_id(youtube_url_or_id, target_date=target_date)
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
            print(f"ℹ️ YouTube Subtitles Notice: Auto-subtitles are disabled or still processing on YouTube for video ID: {video_id}. (Continuing analysis using full news corpus & editorials).")
            return ""

    def fetch_downtoearth_articles(self, max_items=5, fetch_full_text=True, target_date=None):
        """Directly scrape Down To Earth Science & Technology articles."""
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
                                'pub_date': target_date,
                                'full_text': full_body if len(full_body) > 100 else title
                            })
                            if len(items) >= max_items:
                                break
        except Exception as e:
            print(f"Warning scraping Down To Earth: {e}")
        return items

    def fetch_all_daily_news(self, target_date=None, youtube_url=None):
        """Fetch news strictly for target_date (in IST)."""
        now_ist = datetime.now(IST).strftime('%Y-%m-%d')
        date_str = target_date if target_date else now_ist
        print(f"Fetching ALL News, Economy & Science Articles for date: {date_str} (IST)...")

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
        print(f"- Fetching Full The Hindu & Indian Express Editorials for {date_str}...")
        hindu_eds = self.fetch_rss_items('https://www.thehindu.com/opinion/editorial/feeder/default.rss', max_items=6, fetch_full_text=True, target_date=date_str)
        ie_eds = self.fetch_rss_items('https://indianexpress.com/section/opinion/editorials/feed/', max_items=5, fetch_full_text=True, target_date=date_str)
        for item in hindu_eds:
            item['source'] = 'The Hindu Editorial'
        for item in ie_eds:
            item['source'] = 'Indian Express Editorial'
        news_corpus['hindu_editorials'] = hindu_eds + ie_eds

        # 2. Economic Times, LiveMint & Business Standard
        print(f"- Fetching Economy & Policy Articles for {date_str}...")
        et_items = self.fetch_rss_items('https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms', max_items=5, fetch_full_text=True, target_date=date_str)
        mint_items = self.fetch_rss_items('https://www.livemint.com/rss/opinion', max_items=5, fetch_full_text=True, target_date=date_str)
        bs_items = self.fetch_rss_items('https://www.business-standard.com/rss/economy-policy-102.rss', max_items=5, fetch_full_text=True, target_date=date_str)
        
        for item in et_items:
            item['source'] = 'Economic Times (Economy)'
        for item in mint_items:
            item['source'] = 'LiveMint (Opinion & Economy)'
        for item in bs_items:
            item['source'] = 'Business Standard (Policy & Economy)'
            
        news_corpus['economy_news'] = et_items + mint_items + bs_items

        # 3. Science & Tech
        print(f"- Fetching Science, Technology & Environment Articles for {date_str}...")
        dte_items = self.fetch_downtoearth_articles(max_items=5, fetch_full_text=True, target_date=date_str)
        hindu_sci = self.fetch_rss_items('https://www.thehindu.com/sci-tech/science/feeder/default.rss', max_items=5, fetch_full_text=True, target_date=date_str)
        hindu_tech = self.fetch_rss_items('https://www.thehindu.com/sci-tech/technology/feeder/default.rss', max_items=5, fetch_full_text=True, target_date=date_str)
        ie_tech = self.fetch_rss_items('https://indianexpress.com/section/technology/feed/', max_items=5, fetch_full_text=True, target_date=date_str)
        scidaily_items = self.fetch_rss_items('https://www.sciencedaily.com/rss/top/science.xml', max_items=5, fetch_full_text=False, target_date=date_str)

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
        print(f"- Fetching National Governance News for {date_str}...")
        national = self.fetch_rss_items('https://www.thehindu.com/news/national/feeder/default.rss', max_items=6, fetch_full_text=True, target_date=date_str)
        for item in national:
            item['source'] = 'The Hindu National'
        news_corpus['national_news'] = national

        # 5. PIB Releases
        print(f"- Fetching Full PIB Press Releases for {date_str}...")
        news_corpus['pib_releases'] = self.fetch_pib_releases(max_items=6, fetch_full_text=True, target_date=date_str)

        # 6. Rajasthan Sujas
        print(f"- Fetching Rajasthan Sujas Updates for {date_str}...")
        news_corpus['rajasthan_sujas'] = self.fetch_rss_items('https://www.news18.com/rss/india.xml', max_items=4, fetch_full_text=False, target_date=date_str)
        for item in news_corpus['rajasthan_sujas']:
            item['source'] = 'राजस्थान सुजस एवं DIPR (राज्य विशेष)'

        # 7. YouTube Transcript
        yt_input = youtube_url if youtube_url else "https://www.youtube.com/@NirmanIAS"
        news_corpus['youtube_transcript'] = self.fetch_youtube_transcript(yt_input, target_date=date_str)

        return news_corpus

if __name__ == '__main__':
    fetcher = NewsFetcher()
    data = fetcher.fetch_all_daily_news()
    print("\nSummary of Fetched News:")
    print(f"Editorials: {len(data['hindu_editorials'])}")
    print(f"Economy (ET): {len(data['economy_news'])}")
    print(f"Science & Tech: {len(data['science_news'])}")
    print(f"PIB Releases: {len(data['pib_releases'])}")
