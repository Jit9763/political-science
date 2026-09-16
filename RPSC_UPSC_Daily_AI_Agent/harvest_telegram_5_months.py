import os
import re
import time
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from uploader import DriveSyncUploader
from master_library import MasterNotesLibrary

def clean_post_text(raw_text):
    """Clean markdown artifacts, images and raw links from Telegram post text."""
    # Remove markdown image embeds
    cleaned = re.sub(r'\[?_?!\[[^\]]*\]\([^\)]+\)_?\]?', '', raw_text)
    # Remove standalone links
    lines = [l.strip() for l in cleaned.splitlines() if l.strip()]
    valid_lines = []
    for l in lines:
        if l.startswith('#####') or l.startswith('[Download') or l.startswith('[Join'):
            continue
        if l.startswith('http') and len(l) > 40:
            continue
        if any(ign in l.lower() for ign in ['view in telegram', 'subscribers', 'members,', 'right away', 'if you have **telegram**', 'tg://resolve']):
            continue
        # Remove markdown link formatting [text](url) -> text
        l = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', l)
        valid_lines.append(l)
    return '\n'.join(valid_lines).strip()

def classify_to_ras_paper(text):
    """Classify a question or note into RAS Paper 1, 2, 3, or 4."""
    t = text.lower()
    # Paper 4: Hindi grammar & language
    if any(k in t for k in ['पर्यायवाची', 'विलोम', 'मुहावरा', 'लोकोक्ति', 'शुद्ध वर्तनी', 'संधि', 'समास', 'उपसर्ग', 'प्रत्यय', 'शब्दावली', 'english', 'grammar']):
        return "Paper 4 (सामान्य हिंदी व शब्दावली)"
    
    # Paper 3: Polity, Governance, Commissions, Schemes
    if any(k in t for k in ['संविधान', 'राज्यपाल', 'मुख्यमंत्री', 'आयोग', 'विधानसभा', 'लोक प्रशासन', 'अधिनियम', 'अधिकार', 'योजना', 'नीति', 'पंचायती राज', 'उच्च न्यायालय', 'rpsc', 'loayukta']):
        return "Paper 3 (भारतीय व राजस्थान प्रशासनिक व राजनीतिक व्यवस्था)"

    # Paper 2: Geography, Science & Environment
    if any(k in t for k in ['नदी', 'सहायक नदी', 'बाँध', 'सिंचाई', 'झील', 'पर्वत', 'अरावली', 'अभयारण्य', 'राष्ट्रीय उद्यान', 'खनिज', 'जलवायु', 'मिट्टी', 'विज्ञान', 'इसरो', 'स्पेस', 'ऊर्जा', 'भौतिक']):
        return "Paper 2 (राजस्थान भूगोल, सामान्य विज्ञान व पर्यावरण)"

    # Default to Paper 1: History, Art, Culture, Architecture
    return "Paper 1 (राजस्थान इतिहास, कला, संस्कृति व अर्थव्यवस्था)"

def fetch_channel_history(channel_name, max_pages=35):
    """Paginate backwards through public channel web preview via Jina proxy."""
    clean_name = channel_name.strip().lstrip('@')
    if 't.me/' in clean_name:
        clean_name = clean_name.split('t.me/')[-1].split('/')[0]
    
    print(f"\n=======================================================")
    print(f"📥 Harvester: Starting 5-month extraction for @{clean_name}")
    print(f"=======================================================")

    all_posts = []
    seen_texts = set()
    current_before = None
    target_months = {'September', 'August', 'July', 'June', 'May', 'April', 'March'}

    for page in range(1, max_pages + 1):
        if current_before:
            url = f"https://r.jina.ai/https://t.me/s/{clean_name}?before={current_before}"
        else:
            url = f"https://r.jina.ai/https://t.me/s/{clean_name}"

        print(f"  [Page {page}/{max_pages}] Fetching: {url}...")
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            if r.status_code != 200 or len(r.text) < 300:
                print(f"  Warning: Received status {r.status_code}. Breaking pagination.")
                break

            text = r.text

            # Find all message IDs to calculate the next older `before=` cursor
            id_matches = [int(x) for x in re.findall(rf'{re.escape(clean_name)}/(\d+)', text)]
            
            # Split posts by channel header/image blocks
            blocks = re.split(r'\[(?:Image \d+|' + re.escape(clean_name) + r'|[a-zA-Z0-9_\s]+)\]\(https://t\.me/[^\)]+\)', text)
            if len(blocks) <= 1:
                blocks = text.split("\n\n")

            page_new_count = 0
            for b in blocks:
                cleaned = clean_post_text(b)
                if len(cleaned) < 25:
                    continue
                # Skip promotional
                if any(sw in cleaned.lower() for sw in ['discount', 'extra off', 'admission', 'use code', 'coupon', 'promocode']) and not ('?' in cleaned or 'प्रश्न' in cleaned):
                    continue

                if cleaned in seen_texts:
                    continue

                seen_texts.add(cleaned)
                is_q = any(k in cleaned for k in ['?', 'Q.', 'प्रश्न', 'उ.', 'A)', 'B)', 'C)', 'D)', 'Option', 'क)', 'ख)', 'ग)', 'घ)', 'Quiz', '%'])
                paper = classify_to_ras_paper(cleaned)

                # Extract date if present
                date_match = re.search(r'(?:September|August|July|June|May|April|March)\s+\d+', cleaned)
                post_date = date_match.group(0) if date_match else "Recent (2026)"

                all_posts.append({
                    'channel': f"@{clean_name}",
                    'text': cleaned,
                    'is_question': is_q,
                    'paper': paper,
                    'date': post_date
                })
                page_new_count += 1

            print(f"  ✅ Page {page}: Extracted {page_new_count} valid study items (Total so far: {len(all_posts)})")

            if id_matches:
                min_id = min(id_matches)
                # Next page starts before the oldest post on current page
                if current_before and min_id >= current_before:
                    min_id = current_before - 20
                current_before = min_id
                if current_before <= 1:
                    break
            else:
                break

            time.sleep(1.2) # Polite delay

        except Exception as e:
            print(f"  Error on page {page}: {e}")
            break

    print(f"🎉 Completed harvesting @{clean_name}: {len(all_posts)} total items.")
    return all_posts

def build_master_question_bank():
    """Main routine: harvests all user channels, builds searchable HTML & Word DOCX, updates Wiki and Google Drive."""
    channels = [
        "Rajasthan_History_Polity_Culture",
        "CivilSigmaRAS",
        "Rajasthan_Gk_history_culture",
        "RAS_RPSC_REET_Rajasthan_Patwari"
    ]

    all_harvested = []
    for ch in channels:
        posts = fetch_channel_history(ch, max_pages=30)
        all_harvested.extend(posts)

    if not all_harvested:
        print("No items harvested.")
        return

    print(f"\n=======================================================")
    print(f"📊 Total Harvested Across All Channels: {len(all_harvested)} Items")
    print(f"=======================================================")

    # Group by RAS Paper
    grouped = {
        "Paper 1": [],
        "Paper 2": [],
        "Paper 3": [],
        "Paper 4": []
    }

    for p in all_harvested:
        paper_key = p['paper'].split(' ')[0] + ' ' + p['paper'].split(' ')[1]
        if paper_key in grouped:
            grouped[paper_key].append(p)
        else:
            grouped["Paper 1"].append(p)

    # Ingest key factual topics into Master Syllabus Wiki KB
    master_kb = MasterNotesLibrary()
    for p in all_harvested:
        txt = p['text']
        if not p['is_question'] and len(txt) > 60:
            lines = [l for l in txt.splitlines() if l.strip()]
            title = lines[0][:80]
            master_kb.update_or_add_topic(
                p['paper'].split(' ')[0] + ' ' + p['paper'].split(' ')[1],
                "टेलीग्राम रिवीजन बैंक एवं राजस्थान तथ्य",
                title,
                txt,
                keywords=["राजस्थान सामान्य ज्ञान", "टेलीग्राम तथ्य", "RPSC"]
            )

    output_dir = os.path.join(os.path.dirname(__file__), "Output_Notes")
    os.makedirs(output_dir, exist_ok=True)

    # 1. Render Interactive Searchable HTML Bank
    cards_html = ""
    for idx, item in enumerate(all_harvested, 1):
        ch = item['channel']
        paper = item['paper']
        txt = item['text'].replace('\n', '<br>')
        is_q = item['is_question']
        badge_type = "badge-q" if is_q else "badge-note"
        badge_label = "❓ क्विज़ / बहुविकल्पीय प्रश्न" if is_q else "📌 त्वरित तथ्य एवं रिवीजन नोट्स"

        cards_html += f"""
        <div class="bank-card" data-paper="{paper[:7]}">
            <div class="card-top">
                <span class="badge {badge_type}">{badge_label}</span>
                <span class="badge badge-paper">{paper}</span>
                <span class="channel-tag">{ch}</span>
                <span class="date-tag">📅 {item.get('date', '')}</span>
            </div>
            <div class="card-content">
                {txt}
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RPSC RAS 5-Month Telegram Master Question & Notes Bank</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #0f172a;
            --primary-light: #2563eb;
            --accent: #d97706;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --border: #e2e8f0;
        }}
        body {{
            font-family: 'Noto Sans Devanagari', sans-serif;
            background-color: var(--bg);
            color: #0f172a;
            margin: 0;
            padding: 20px;
            line-height: 1.8;
            font-size: 18px;
        }}
        .header {{
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0d9488 100%);
            color: white;
            padding: 35px 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 32px; font-weight: 900; }}
        .header p {{ margin: 0; font-size: 19px; opacity: 0.95; }}
        .stats-bar {{
            display: flex;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        .stat-badge {{
            background: rgba(255,255,255,0.18);
            padding: 8px 16px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 16px;
        }}
        .controls {{
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .search-box {{
            flex: 1;
            min-width: 280px;
            padding: 14px 20px;
            font-size: 18px;
            border: 2px solid #cbd5e1;
            border-radius: 12px;
            font-family: inherit;
        }}
        .filter-btn {{
            background: white;
            border: 2px solid #cbd5e1;
            padding: 12px 22px;
            border-radius: 12px;
            font-weight: 800;
            font-size: 17px;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.2s;
        }}
        .filter-btn.active {{
            background: #1e3a8a;
            color: white;
            border-color: #1e3a8a;
        }}
        .bank-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.04);
            border-left: 8px solid #2563eb;
        }}
        .card-top {{
            display: flex;
            gap: 12px;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }}
        .badge {{
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 800;
            color: white;
        }}
        .badge-q {{ background: #d97706; }}
        .badge-note {{ background: #059669; }}
        .badge-paper {{ background: #4f46e5; }}
        .channel-tag {{ font-weight: 800; color: #1e3a8a; font-size: 15px; }}
        .date-tag {{ color: #64748b; font-size: 15px; margin-left: auto; }}
        .card-content {{
            font-size: 19px;
            color: #1e293b;
            font-weight: 600;
        }}
        @media print {{
            .controls, .header button {{ display: none; }}
            body {{ background: white; padding: 0; }}
            .bank-card {{ break-inside: avoid; border: 1px solid #999; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 RPSC RAS 5-Month Telegram Master Question & Notes Bank</h1>
        <p>विगत 5 महीनों (@Rajasthan_History_Polity_Culture व अन्य प्रमुख चैनल्स) से संकलित संपूर्ण प्रश्नोत्तरी, क्विज़ व प्रामाणिक नोट्स</p>
        <div class="stats-bar">
            <div class="stat-badge">📊 कुल संकलित सामग्री: {len(all_harvested)} कार्ड्स</div>
            <div class="stat-badge">📘 Paper 1: {len(grouped['Paper 1'])}</div>
            <div class="stat-badge">📗 Paper 2: {len(grouped['Paper 2'])}</div>
            <div class="stat-badge">📙 Paper 3: {len(grouped['Paper 3'])}</div>
            <div class="stat-badge">📕 Paper 4: {len(grouped['Paper 4'])}</div>
        </div>
    </div>

    <div class="controls">
        <input type="text" id="searchBox" class="search-box" placeholder="🔍 किसी भी टॉपिक, प्रश्न, शासक, नदी, योजना या कीवर्ड से खोजें..." onkeyup="filterCards()">
        <button class="filter-btn active" onclick="setFilter('ALL', this)">सभी ({len(all_harvested)})</button>
        <button class="filter-btn" onclick="setFilter('Paper 1', this)">📘 Paper 1 ({len(grouped['Paper 1'])})</button>
        <button class="filter-btn" onclick="setFilter('Paper 2', this)">📗 Paper 2 ({len(grouped['Paper 2'])})</button>
        <button class="filter-btn" onclick="setFilter('Paper 3', this)">📙 Paper 3 ({len(grouped['Paper 3'])})</button>
        <button class="filter-btn" onclick="setFilter('Paper 4', this)">📕 Paper 4 ({len(grouped['Paper 4'])})</button>
        <button class="filter-btn" style="background:#0f172a; color:white; border-color:#0f172a;" onclick="window.print()">🖨️ PDF प्रिंट करें</button>
    </div>

    <div id="cardsContainer">
        {cards_html}
    </div>

    <script>
        let currentPaper = 'ALL';

        function setFilter(paper, btn) {{
            currentPaper = paper;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterCards();
        }}

        function filterCards() {{
            let q = document.getElementById('searchBox').value.toLowerCase();
            let cards = document.querySelectorAll('.bank-card');
            cards.forEach(card => {{
                let cardPaper = card.getAttribute('data-paper');
                let text = card.innerText.toLowerCase();
                let matchesPaper = (currentPaper === 'ALL' || cardPaper === currentPaper);
                let matchesSearch = text.includes(q);
                card.style.display = (matchesPaper && matchesSearch) ? 'block' : 'none';
            }});
        }}
    </script>
</body>
</html>
"""
    html_path = os.path.join(output_dir, "Rajasthan_5_Months_Telegram_Master_Question_Bank.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Master Question Bank HTML saved: {html_path}")

    # 2. Render Formatted Word DOCX Document
    doc = Document()
    title_p = doc.add_heading("RPSC RAS - 5 Month Telegram Master Question & Notes Bank", 0)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"संकलन तिथि: {datetime.now().strftime('%d %B %Y')} | कुल प्रश्न व नोट्स: {len(all_harvested)}")

    for paper_name in ["Paper 1", "Paper 2", "Paper 3", "Paper 4"]:
        items = grouped.get(paper_name, [])
        if not items:
            continue
        doc.add_heading(f"{paper_name} - राजस्थान विशेष प्रश्नोत्तरी व नोट्स ({len(items)} आइटम्स)", level=1)
        for i, it in enumerate(items, 1):
            p = doc.add_paragraph()
            prefix = "❓ [प्रश्न] " if it['is_question'] else "📌 [नोट्स] "
            p.add_run(f"{i}. {prefix}").bold = True
            p.add_run(it['text'])
            doc.add_paragraph(f"स्रोत: {it['channel']} | {it.get('date', '')}\n" + "-"*40)

    docx_path = os.path.join(output_dir, "Rajasthan_5_Months_Telegram_Master_Question_Bank.docx")
    doc.save(docx_path)
    print(f"✅ Master Question Bank DOCX saved: {docx_path}")

    # 3. Render Updated Master Syllabus Wiki
    from formatter import NotesFormatter
    fmt = NotesFormatter()
    fmt.render_master_syllabus_html()

    # 4. Sync All Output Files to Google Drive Folder
    uploader = DriveSyncUploader()
    uploader.sync_to_drive(html_path)
    uploader.sync_to_drive(docx_path)
    uploader.sync_to_drive(os.path.join(output_dir, "Master_Syllabus_Wiki.html"))

    print(f"\n=======================================================")
    print(f"🎉 5-Month Telegram Master Question Bank is LIVE!")
    print(f"📄 HTML Bank: {html_path}")
    print(f"📄 Word Document: {docx_path}")
    print(f"=======================================================")

if __name__ == '__main__':
    build_master_question_bank()
