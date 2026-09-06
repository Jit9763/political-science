import os
import sys
import argparse
from datetime import datetime

from fetchers import NewsFetcher
from analyzer import NewsAnalyzer
from formatter import NotesFormatter
from uploader import DriveSyncUploader
from master_library import MasterNotesLibrary

def run_agent(target_date=None, youtube_url=None, auto_open=True):
    date_str = target_date if target_date else datetime.now().strftime('%Y-%m-%d')
    print(f"===========================================================")
    print(f"🚀 Starting RPSC RAS & UPSC Daily News & Editorial AI Agent")
    print(f"📅 Target Date: {date_str}")
    if youtube_url:
        print(f"📺 YouTube Class Stream: {youtube_url}")
    print(f"===========================================================")

    # Step 1: Fetch Full News & YouTube Transcript
    fetcher = NewsFetcher()
    corpus = fetcher.fetch_all_daily_news(target_date=date_str, youtube_url=youtube_url)

    # Step 2: AI Analysis
    analyzer = NewsAnalyzer()
    analysis_data = analyzer.analyze_daily_corpus(corpus)

    # Step 3: Format Output with Large Teacher Fonts & Visual Styling
    formatter = NotesFormatter()
    html_path = formatter.render_daily_html(analysis_data)
    docx_path = formatter.render_daily_docx(analysis_data)

    # Step 4: Sync to Google Drive
    uploader = DriveSyncUploader()
    uploader.sync_to_drive(html_path)
    uploader.sync_to_drive(docx_path)

    # Step 5: Open in browser if requested
    if auto_open and os.path.exists(html_path):
        uploader.open_in_browser(html_path)

    print("===========================================================")
    print(f"✅ Daily Agent Execution Finished Successfully!")
    print(f"📄 Notes File: {html_path}")
    print(f"===========================================================")
    return html_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="RAS & UPSC Daily News AI Agent")
    parser.add_argument("--date", type=str, help="Target date YYYY-MM-DD", default=None)
    parser.add_argument("--youtube", type=str, help="YouTube Current Affairs Video URL/ID", default=None)
    parser.add_argument("--no-browser", action="store_true", help="Disable opening browser")
    args = parser.parse_args()

    run_agent(target_date=args.date, youtube_url=args.youtube, auto_open=not args.no_browser)
