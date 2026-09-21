import os
import json
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from master_library import MasterNotesLibrary

class NotesFormatter:
    def __init__(self, output_dir=None):
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), "Output_Notes")
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.master_kb = MasterNotesLibrary()

    def render_master_syllabus_html(self):
        """Render complete interactive RAS Master Syllabus Wiki HTML website."""
        topics_data = self.master_kb.get_all_topics()
        last_updated = self.master_kb.data.get("metadata", {}).get("last_updated", "Recently")

        today_str = datetime.now().strftime("%Y-%m-%d")
        recent_updates_html = ""
        recent_count = 0

        paper_sections_html = ""
        for paper_name, units in topics_data.items():
            units_html = ""
            for unit_name, items in units.items():
                items_html = ""
                if not items:
                    items_html = '<div class="empty-topic">नवीनतम दैनिक समाचारों से इस टॉपिक का अध्ययन जल्द ही अद्यतन होगा।</div>'
                else:
                    for item in items:
                        updates_list = ""
                        for u in item.get("updates_history", []):
                            u_notes = u.get('update_notes', '').replace('\n', '<br>')
                            updates_list += f"""
                            <div class="update-entry">
                                <span class="update-date">📅 {u.get('date', '')}</span>
                                <div class="update-text">{u_notes}</div>
                            </div>
                            """
                        status_text = item.get('current_status', '').replace('\n', '<br>')
                        
                        # Collect recent updates for top banner
                        if item.get('last_updated') == today_str or (recent_count < 3 and item.get('last_updated')):
                            recent_count += 1
                            recent_updates_html += f"""
                            <div class="syllabus-topic-card" style="border-left:6px solid #dc2626; background:#fff1f2;">
                                <div class="topic-header">
                                    <span class="topic-name">🔥 [{paper_name}] {item.get('title', '')}</span>
                                    <span class="badge" style="background:#dc2626; color:white; font-weight:bold;">ताज़ा अपडेट: {item.get('last_updated', '')}</span>
                                </div>
                                <div class="current-status-box">
                                    <strong>अद्यतन स्थिति एवं मुख्य तथ्य:</strong>
                                    <p>{status_text}</p>
                                </div>
                            </div>
                            """

                        items_html += f"""
                        <div class="syllabus-topic-card">
                            <div class="topic-header">
                                <span class="topic-name">📌 {item.get('title', '')}</span>
                                <span class="badge badge-update">अद्यतन तिथि: {item.get('last_updated', '')}</span>
                            </div>
                            <div class="current-status-box">
                                <strong>वर्तमान स्थिति एवं अद्यतन तथ्य:</strong>
                                <p>{status_text}</p>
                            </div>
                            <details class="history-details">
                                <summary>📜 अपडेट इतिहास एवं पूर्व विवरण देखें</summary>
                                <div class="history-body">{updates_list}</div>
                            </details>
                        </div>
                        """

                units_html += f"""
                <div class="unit-block">
                    <h3 class="unit-header">📘 {unit_name}</h3>
                    {items_html}
                </div>
                """

            paper_sections_html += f"""
            <div id="{paper_name.replace(' ', '_')}" class="paper-tab-content">
                <h2 class="paper-title">🏛️ RAS {paper_name} - विस्तृत पाठ्यक्रम एवं मास्टर नोट्स</h2>
                {units_html}
            </div>
            """

        wiki_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAS Master Syllabus Wiki - RPSC 4 Papers Knowledge Base</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #0f172a;
            --primary-light: #2563eb;
            --accent-green: #059669;
            --accent-purple: #7c3aed;
            --bg-main: #f8fafc;
            --card-bg: #ffffff;
            --text-dark: #020617;
            --border-color: #cbd5e1;
        }}
        body {{
            font-family: 'Noto Sans Devanagari', 'Segoe UI', Tahoma, sans-serif;
            background-color: var(--bg-main);
            color: var(--text-dark);
            margin: 0;
            padding: 0;
            line-height: 1.85;
            font-size: 22px;
        }}
        .top-navbar {{
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
            color: white;
            padding: 30px 45px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.15);
            border-bottom: 4px solid #2563eb;
        }}
        .top-navbar h1 {{
            margin: 0 0 8px 0;
            font-size: 34px;
            font-weight: 900;
        }}
        .top-navbar p {{
            margin: 0;
            opacity: 0.95;
            font-size: 20px;
            font-weight: 600;
        }}
        .container {{
            max-width: 1300px;
            margin: 30px auto;
            padding: 0 25px;
        }}
        .tab-buttons {{
            display: flex;
            gap: 15px;
            margin-bottom: 35px;
            border-bottom: 3px solid #cbd5e1;
            padding-bottom: 12px;
            flex-wrap: wrap;
        }}
        .tab-btn {{
            background: #ffffff;
            color: #1e293b;
            border: 2px solid #94a3b8;
            padding: 14px 28px;
            border-radius: 14px;
            font-size: 22px;
            font-weight: 800;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.2s;
        }}
        .tab-btn:hover, .tab-btn.active {{
            background: #2563eb;
            color: white;
            border-color: #1d4ed8;
            box-shadow: 0 6px 15px rgba(37,99,235,0.35);
        }}
        .paper-title {{
            font-size: 32px;
            font-weight: 900;
            color: #1e3a8a;
            margin-bottom: 30px;
            padding-bottom: 12px;
            border-bottom: 4px solid #3b82f6;
        }}
        .unit-block {{
            background: white;
            border-radius: 18px;
            padding: 32px;
            margin-bottom: 35px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.06);
            border: 2px solid var(--border-color);
        }}
        .unit-header {{
            font-size: 28px;
            font-weight: 900;
            color: #0f766e;
            margin-top: 0;
            margin-bottom: 24px;
            padding-bottom: 10px;
            border-bottom: 3px solid #ccfbf1;
        }}
        .syllabus-topic-card {{
            background: #f8fafc;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 24px;
            border-left: 10px solid #2563eb;
            border: 2px solid #e2e8f0;
            border-left-width: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        }}
        .topic-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .topic-name {{ font-size: 25px; font-weight: 900; color: #0f172a; }}
        .badge-update {{ background: #059669; color: white; padding: 6px 16px; border-radius: 8px; font-size: 16px; font-weight: 800; }}
        
        .current-status-box {{
            background: #ffffff;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid #cbd5e1;
            font-size: 22px;
            line-height: 1.85;
        }}
        .history-details {{ margin-top: 14px; font-size: 18px; color: #475569; }}
        .history-body {{ margin-top: 12px; padding: 16px; background: #f1f5f9; border-radius: 10px; font-size: 19px; }}
        .update-entry {{ margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px dashed #cbd5e1; }}
        .update-date {{ font-weight: 800; color: #1e3a8a; font-size: 18px; }}
        .empty-topic {{ color: #94a3b8; font-style: italic; padding: 12px 0; font-size: 20px; }}

        .search-box {{
            width: 100%;
            padding: 16px 24px;
            font-size: 22px;
            border-radius: 14px;
            border: 3px solid #cbd5e1;
            margin-bottom: 30px;
            font-family: inherit;
            box-sizing: border-box;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="top-navbar">
        <h1>📚 RPSC RAS 4 पेपर मास्टर सिलेबस नॉलेज बेस (Syllabus Wiki)</h1>
        <p>पाठ्यक्रम अनुसार व्यवस्थित अध्ययन सामग्री एवं स्वतः अद्यतन तथ्य | अंतिम अद्यतन: {last_updated}</p>
    </div>

    <div class="container">
        <input type="text" class="search-box" id="syllabusSearch" onkeyup="filterTopics()" placeholder="🔍 RAS सिलेबस टॉपिक, आयोग, नियम या विषय खोजें...">

        {f'''
        <div style="background:#fff1f2; border:2px solid #fecdd3; border-radius:14px; padding:20px; margin-bottom:25px;">
            <h2 style="margin:0 0 15px 0; color:#991b1b; font-size:22px; font-weight:900;">🔥 हाल ही में अद्यतन किए गए नवीन तथ्य (Recent Live Updates)</h2>
            {recent_updates_html}
        </div>
        ''' if recent_updates_html else ''}

        <div class="tab-buttons">
            <button class="tab-btn active" onclick="showPaper('Paper_1', this)">📘 Paper 1</button>
            <button class="tab-btn" onclick="showPaper('Paper_2', this)">📗 Paper 2</button>
            <button class="tab-btn" onclick="showPaper('Paper_3', this)">📙 Paper 3</button>
            <button class="tab-btn" onclick="showPaper('Paper_4', this)">📕 Paper 4</button>
        </div>

        {paper_sections_html}
    </div>

    <script>
        function showPaper(paperId, btn) {{
            let contents = document.querySelectorAll('.paper-tab-content');
            contents.forEach(c => c.style.display = 'none');
            document.getElementById(paperId).style.display = 'block';

            let buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }}

        function filterTopics() {{
            let input = document.getElementById('syllabusSearch').value.toLowerCase();
            let cards = document.querySelectorAll('.syllabus-topic-card');
            cards.forEach(card => {{
                let text = card.innerText.toLowerCase();
                card.style.display = text.includes(input) ? 'block' : 'none';
            }});
        }}

        // Default open Paper 1
        showPaper('Paper_1', document.querySelector('.tab-btn'));
    </script>
</body>
</html>
"""
        master_wiki_path = os.path.join(self.output_dir, "Master_Syllabus_Wiki.html")
        with open(master_wiki_path, "w", encoding="utf-8") as f:
            f.write(wiki_html)
        print(f"Master Syllabus Wiki HTML saved to: {master_wiki_path}")
        self.render_master_wiki_markdown(topics_data, self.master_kb.data.get("metadata", {}))
        return master_wiki_path

    def render_master_wiki_markdown(self, topics, metadata):
        """Generates GitHub Markdown Wiki file for repository Wiki tab."""
        md_content = f"# 📚 RPSC RAS & UPSC Master Syllabus Wiki\n\n"
        md_content += f"*अंतिम अद्यतन: {metadata.get('last_updated', '')}*\n\n"
        md_content += "---" + "\n\n"

        for paper_name, units in topics.items():
            md_content += f"## 📄 {paper_name}\n\n"
            for unit_name, items in units.items():
                if not items:
                    continue
                md_content += f"### 📘 {unit_name}\n\n"
                for item in items:
                    md_content += f"#### 📌 {item.get('title', '')}\n"
                    md_content += f"- **अद्यतन तिथि**: `{item.get('last_updated', '')}`\n"
                    md_content += f"- **वर्तमान स्थिति एवं तथ्य**: {item.get('current_status', '')}\n\n"
                    if item.get("updates_history"):
                        md_content += "<details><summary>📜 अपडेट इतिहास</summary>\n\n"
                        for u in item.get("updates_history", []):
                            md_content += f"- **{u.get('date', '')}**: {u.get('update_notes', '')}\n"
                        md_content += "</details>\n\n"

        md_path = os.path.join(self.output_dir, "Master_Syllabus_Wiki.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"Master Syllabus Wiki Markdown saved to: {md_path}")
        return md_path

    def render_daily_html(self, analysis_data):
        date_str = analysis_data.get('date', 'Today')
        
        prelims_facts = analysis_data.get('prelims_facts', [])
        mains_qs = analysis_data.get('mains_questions', [])
        editorials = analysis_data.get('editorial_deep_dive', [])
        yt_analysis = analysis_data.get('youtube_teacher_analysis', [])
        sujas = analysis_data.get('rajasthan_sujas_special', [])

        prelims_cards_html = ""
        for item in prelims_facts:
            tag_class = "badge-raj" if item.get('rajasthan_special') else "badge-pre"
            prelims_cards_html += f"""
            <div class="fact-card">
                <div class="card-header">
                    <span class="badge {tag_class}">{item.get('exam_tag', 'RAS/UPSC Pre')}</span>
                    <span class="topic-title">{item.get('topic', '')}</span>
                </div>
                <p class="fact-text">{item.get('fact', '')}</p>
            </div>
            """

        mains_qs_html = ""
        for q in mains_qs:
            marks = q.get('marks', 5)
            badge_class = "badge-5m" if marks == 5 else "badge-10m"
            
            if marks == 5:
                model_ans = q.get('model_answer', '').replace('\n', '<br>')
                answer_body = f"""
                <div class="answer-box">
                    <strong class="ans-label">उत्तर ढांचा (~50 शब्द):</strong>
                    <div class="answer-content">{model_ans}</div>
                </div>
                """
            else:
                body_text = q.get('body', '').replace('\n', '<br>')
                answer_body = f"""
                <div class="answer-box">
                    <div class="ans-section"><strong class="ans-label">भूमिका (Introduction):</strong><br>{q.get('intro', '')}</div>
                    <div class="ans-section"><strong class="ans-label">मुख्य भाग (Body & Rajasthan Context):</strong><br>{body_text}</div>
                    <div class="ans-section"><strong class="ans-label">निष्कर्ष (Conclusion):</strong><br>{q.get('conclusion', '')}</div>
                </div>
                """

            mains_qs_html += f"""
            <div class="mains-card">
                <div class="mains-header">
                    <span class="badge {badge_class}">{marks} अंक ({q.get('paper', 'Paper')})</span>
                    <span class="subject-tag">{q.get('subject', '')}</span>
                </div>
                <h3 class="question-text">प्रश्न: {q.get('question', '')}</h3>
                {answer_body}
            </div>
            """

        yt_html = ""
        for yt in yt_analysis:
            yt_html += f"""
            <div class="yt-card">
                <div class="yt-header">
                    <span class="badge badge-yt">📺 कोचिंग शिक्षक विश्लेषण</span>
                    <span class="topic-title">{yt.get('topic', '')}</span>
                </div>
                <div class="yt-explanation">
                    <strong>शिक्षक व्याख्यान एवं ट्रिक्स:</strong>
                    <p>{yt.get('teacher_explanation', '')}</p>
                </div>
                <div class="key-args">
                    <strong>क्लास के मुख्य बिंदु (Key Lecture Points):</strong>
                    <ul>
                        {"".join([f"<li>{pt}</li>" for pt in yt.get('key_takeaways', [])])}
                    </ul>
                </div>
                <div class="exam-tip-box"><strong>💡 परीक्षा टिप (Exam Tip):</strong> {yt.get('exam_tip', '')}</div>
            </div>
            """

        sujas_html = ""
        for s in sujas:
            sujas_html += f"""
            <div class="sujas-card">
                <div class="sujas-header">
                    <span class="badge badge-sujas">राजस्थान सुजस विशेष</span>
                    <strong>{s.get('department', 'DIPR Rajasthan')}</strong>
                </div>
                <h3>{s.get('title', '')}</h3>
                <ul>
                    {"".join([f"<li>{pt}</li>" for pt in s.get('key_points', [])])}
                </ul>
                <div class="relevance-box"><strong>RPSC महत्व:</strong> {s.get('rpsc_relevance', '')}</div>
            </div>
            """

        editorial_html = ""
        for ed in editorials:
            editorial_html += f"""
            <div class="editorial-card">
                <div class="editorial-header">
                    <span class="badge badge-ed">{ed.get('source', 'Editorial')}</span>
                    <span class="syllabus-tag">{ed.get('syllabus_topic', '')}</span>
                </div>
                <h3>{ed.get('title', '')}</h3>
                <p class="context"><strong>समसामयिक संदर्भ:</strong> {ed.get('context', '')}</p>
                <div class="key-args">
                    <strong>सम्पादकीय का पूरा सार एवं तर्क (Deep Dive Takeaways):</strong>
                    <ul>
                        {"".join([f"<li>{arg}</li>" for arg in ed.get('key_arguments', [])])}
                    </ul>
                </div>
                <div class="way-forward"><strong>आगे की राह (Way Forward):</strong> {ed.get('way_forward', '')}</div>
            </div>
            """

        tg_items = analysis_data.get('telegram_quiz_and_notes', [])
        tg_html = ""
        for item in tg_items:
            ch = item.get('channel', '@Telegram')
            q_text = item.get('question', item.get('question_or_topic', ''))
            ans = item.get('model_answer_50_words', item.get('correct_answer', '')).replace('\n', '<br>')
            paper_tag = item.get('syllabus_link', 'Paper 1 (राजस्थान विशेष)')
            tg_html += f"""
            <div class="mains-card" style="border-left: 8px solid #0284c7; margin-bottom: 25px;">
                <div class="mains-header">
                    <span class="badge" style="background:#0284c7; color:white;">5 अंक (~50 शब्द)</span>
                    <span class="badge" style="background:#1e3a8a; color:white;">{ch}</span>
                    <span class="subject-tag">{paper_tag}</span>
                </div>
                <h3 class="question-text">प्रश्न: {q_text}</h3>
                <div class="answer-box">
                    <strong class="ans-label">उत्तर ढांचा एवं विस्तृत नोट्स (~50 शब्द):</strong>
                    <div class="answer-content">{ans}</div>
                </div>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAS & UPSC Daily Notes - {date_str}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style id="customStyle">
        :root {{
            --base-font-size: 24px;
            --base-line-height: 1.85;
            --primary: #1e1b4b;
            --primary-light: #2563eb;
            --secondary: #0f766e;
            --accent-gold: #b45309;
            --accent-purple: #6b21a8;
            --accent-red: #9f1239;
            --bg-main: #f8fafc;
            --card-bg: #ffffff;
            --text-dark: #020617;
            --border-color: #cbd5e1;
            --box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        }}

        body.dark-mode {{
            --bg-main: #090d16;
            --card-bg: #111827;
            --text-dark: #f8fafc;
            --border-color: #374151;
            --box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }}

        body.sepia-mode {{
            --bg-main: #fbf0d9;
            --card-bg: #fffdf7;
            --text-dark: #2d2215;
            --border-color: #e2d3b5;
        }}

        body {{
            font-family: 'Noto Sans Devanagari', 'Segoe UI', Tahoma, sans-serif;
            background-color: var(--bg-main);
            color: var(--text-dark);
            margin: 0;
            padding: 25px;
            line-height: var(--base-line-height);
            font-size: var(--base-font-size);
            transition: background-color 0.2s, font-size 0.15s;
            -webkit-font-smoothing: antialiased;
        }}

        /* Eye-Comfort High Definition Typography */
        p, li, div, span, td, th {{
            font-size: var(--base-font-size);
            line-height: var(--base-line-height);
        }}

        b, strong {{
            color: #b91c1c;
            font-weight: 800;
        }}
        body.dark-mode b, body.dark-mode strong {{
            color: #f87171;
        }}

        .blue-highlight {{
            color: #1e3a8a;
            font-weight: 800;
        }}
        body.dark-mode .blue-highlight {{
            color: #60a5fa;
        }}

        .container {{
            max-width: 1300px;
            margin: 0 auto;
        }}

        /* Sticky Eye-Comfort Controls Toolbar */
        .reader-toolbar {{
            position: sticky;
            top: 15px;
            z-index: 999;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(10px);
            color: white;
            padding: 12px 24px;
            border-radius: 50px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.25);
            margin-bottom: 25px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            border: 2px solid #334155;
        }}

        .toolbar-title {{
            font-size: 19px;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .toolbar-btns {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .t-btn {{
            background: #1e293b;
            color: white;
            border: 1px solid #475569;
            padding: 8px 16px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
            font-family: inherit;
        }}

        .t-btn:hover, .t-btn.active {{
            background: #2563eb;
            border-color: #60a5fa;
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(37,99,235,0.4);
        }}

        .header {{
            background: linear-gradient(135deg, #09090b 0%, #1e1b4b 50%, #0f766e 100%);
            color: white;
            padding: 35px 40px;
            border-radius: 20px;
            box-shadow: 0 15px 30px -5px rgba(0,0,0,0.25);
            margin-bottom: 35px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 3px solid #3b82f6;
        }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 36px; font-weight: 900; letter-spacing: -0.5px; }}
        .header p {{ margin: 0; opacity: 0.95; font-size: 22px; font-weight: 600; }}

        /* Large Chapter 7 Style Section Headers */
        .section-title {{
            font-size: 32px;
            font-weight: 900;
            margin: 45px 0 25px 0;
            padding: 18px 26px;
            background: var(--card-bg);
            border-radius: 14px;
            border-left: 14px solid var(--primary-light);
            box-shadow: var(--box-shadow);
            color: var(--text-dark);
            border-top: 1px solid var(--border-color);
            border-right: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
        }}

        .badge {{
            padding: 8px 16px;
            border-radius: 10px;
            font-size: 17px;
            font-weight: 800;
            color: white;
            display: inline-block;
        }}
        .badge-pre {{ background-color: var(--accent-gold); }}
        .badge-raj {{ background-color: var(--accent-purple); }}
        .badge-5m {{ background-color: #0284c7; }}
        .badge-10m {{ background-color: #4338ca; }}
        .badge-sujas {{ background-color: #0d9488; }}
        .badge-ed {{ background-color: var(--accent-red); }}
        .badge-yt {{ background-color: #dc2626; }}

        /* Big, Comfortable Eye-Friendly Cards */
        .fact-card, .mains-card, .sujas-card, .editorial-card, .yt-card {{
            background: var(--card-bg);
            border-radius: 18px;
            padding: 32px;
            margin-bottom: 30px;
            box-shadow: var(--box-shadow);
            border: 2px solid var(--border-color);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .fact-card:hover, .mains-card:hover, .sujas-card:hover, .editorial-card:hover, .yt-card:hover {{
            box-shadow: 0 12px 28px rgba(0,0,0,0.1);
        }}

        .fact-card {{ border-left: 14px solid var(--accent-gold); }}
        .mains-card {{ border-left: 14px solid #4338ca; }}
        .sujas-card {{ border-left: 14px solid var(--accent-purple); }}
        .editorial-card {{ border-left: 14px solid var(--accent-red); }}
        .yt-card {{ border-left: 14px solid #dc2626; background: var(--card-bg); }}

        .card-header, .mains-header, .sujas-header, .editorial-header, .yt-header {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }}
        .topic-title {{ font-weight: 900; font-size: 26px; color: var(--text-dark); }}
        .fact-text {{ margin: 0; color: var(--text-dark); font-size: var(--base-font-size); line-height: var(--base-line-height); font-weight: 500; }}
        .question-text {{ margin: 12px 0 18px 0; color: #1e3a8a; font-size: calc(var(--base-font-size) + 4px); font-weight: 900; line-height: 1.6; }}
        body.dark-mode .question-text {{ color: #93c5fd; }}

        .answer-box {{
            background: #f1f5f9;
            padding: 26px;
            border-radius: 14px;
            font-size: var(--base-font-size);
            border: 2px solid #cbd5e1;
            line-height: var(--base-line-height);
        }}
        body.dark-mode .answer-box {{
            background: #1f2937;
            border-color: #4b5563;
        }}
        body.sepia-mode .answer-box {{
            background: #f4ebd0;
            border-color: #dcd0b1;
        }}

        .ans-label {{
            font-size: calc(var(--base-font-size) + 2px);
            color: #1e3a8a;
            display: block;
            margin-bottom: 10px;
            font-weight: 800;
        }}
        body.dark-mode .ans-label {{ color: #60a5fa; }}

        .relevance-box, .way-forward {{
            background: #ecfdf5;
            color: #065f46;
            padding: 18px 24px;
            border-radius: 12px;
            margin-top: 20px;
            font-size: calc(var(--base-font-size) - 1px);
            border-left: 8px solid #10b981;
            font-weight: 600;
            border: 1px solid #a7f3d0;
            border-left-width: 8px;
        }}
        body.dark-mode .relevance-box, body.dark-mode .way-forward {{
            background: #064e3b;
            color: #a7f3d0;
            border-color: #059669;
        }}

        .exam-tip-box {{
            background: #fefce8;
            color: #854d0e;
            padding: 18px 24px;
            border-radius: 12px;
            margin-top: 20px;
            font-size: calc(var(--base-font-size) - 1px);
            border-left: 8px solid #eab308;
            font-weight: 600;
            border: 1px solid #fef08a;
            border-left-width: 8px;
        }}
        body.dark-mode .exam-tip-box {{
            background: #713f12;
            color: #fef08a;
            border-color: #eab308;
        }}

        ul {{ margin: 12px 0; padding-left: 30px; }}
        li {{ margin-bottom: 12px; font-size: var(--base-font-size); line-height: var(--base-line-height); }}

        @media print {{
            .reader-toolbar, .print-btn {{ display: none !important; }}
            body {{ background: white !important; color: black !important; padding: 0 !important; font-size: 16pt !important; }}
            .container {{ max-width: 100% !important; }}
            .fact-card, .mains-card, .sujas-card, .editorial-card, .yt-card {{ page-break-inside: avoid; border: 1px solid #999 !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Floating Interactive Eye-Comfort Toolbar -->
        <div class="reader-toolbar">
            <div class="toolbar-title">
                <span>👁️ नेत्र-अनुकूल फॉन्ट व पठन मोड</span>
            </div>
            <div class="toolbar-btns">
                <button class="t-btn" onclick="setFontSize(22)">A सामान्य (22px)</button>
                <button class="t-btn active" id="btn-ch7" onclick="setFontSize(26)">🔠 बड़ा / Ch-7 स्टाइल (26px)</button>
                <button class="t-btn" onclick="setFontSize(30)">🔍 अल्ट्रा लार्ज (30px)</button>
                <button class="t-btn" onclick="toggleTheme('light')">☀️ लाइट</button>
                <button class="t-btn" onclick="toggleTheme('sepia')">📜 सेपिया</button>
                <button class="t-btn" onclick="toggleTheme('dark')">🌙 डार्क मोड</button>
                <button class="t-btn" style="background:#059669; border-color:#10b981;" onclick="window.print()">🖨️ PDF प्रिंट</button>
            </div>
        </div>

        <div class="header">
            <div>
                <h1>RPSC RAS & UPSC दैनिक समसामयिकी एवं सम्पादकीय विश्लेषण</h1>
                <p>दिनांक: {date_str} | RAS Pre & Mains (5M & 10M) विशेष मास्टर नोट्स</p>
            </div>
        </div>

        <div class="section-title">🟡 प्रारंभिक परीक्षा तथ्य (RAS & UPSC Prelims Tracker)</div>
        {prelims_cards_html if prelims_cards_html else '<p>आज के लिए प्रिलिम्स तथ्य प्रस्तुत हैं।</p>'}

        <div class="section-title">🔵 मुख्य परीक्षा उत्तर लेखन मॉडल सेट (RAS Mains - 5M & 10M)</div>
        {mains_qs_html if mains_qs_html else '<p>आज के लिए मुख्य परीक्षा प्रश्न मॉडल सेट।</p>'}

        {f'<div class="section-title">📺 कोचिंग शिक्षक विश्लेषण एवं यूट्यूब लाइव क्लास सार</div>{yt_html}' if yt_html else ''}

        <div class="section-title">🟣 राजस्थान सुजस, पत्रिका एवं दैनिक भास्कर (Rajasthan Sujas, Patrika & Bhaskar)</div>
        {sujas_html if sujas_html else '<p>सुजस एवं राजस्थान राज्य सरकार की अद्यतन घोषणाएं।</p>'}

        <div class="section-title">🔴 सम्पादकीय एवं पत्रिका गहन विश्लेषण (The Hindu, Indian Express, ET, DownToEarth, योजना व कुरुक्षेत्र)</div>
        {editorial_html if editorial_html else '<p>दैनिक सम्पादकीय एवं पत्रिका विश्लेषण प्रस्तुत है।</p>'}

        {f'<div class="section-title">📲 टेलीग्राम चैनल दैनिक प्रश्नोत्तरी व नोट्स (Telegram Daily Quiz & Notes)</div>{tg_html}' if tg_html else ''}
    </div>

    <script>
        function setFontSize(size) {{
            document.documentElement.style.setProperty('--base-font-size', size + 'px');
            localStorage.setItem('ras_notes_font_size', size);
            document.querySelectorAll('.toolbar-btns .t-btn').forEach(b => {{
                if (b.innerText.includes(size + 'px')) b.classList.add('active');
                else if (b.innerText.includes('px')) b.classList.remove('active');
            }});
        }}

        function toggleTheme(theme) {{
            document.body.classList.remove('dark-mode', 'sepia-mode');
            if (theme === 'dark') document.body.classList.add('dark-mode');
            else if (theme === 'sepia') document.body.classList.add('sepia-mode');
            localStorage.setItem('ras_notes_theme', theme);
        }}

        // Load saved preferences
        (function() {{
            const savedSize = localStorage.getItem('ras_notes_font_size') || 26;
            setFontSize(savedSize);
            const savedTheme = localStorage.getItem('ras_notes_theme');
            if (savedTheme) toggleTheme(savedTheme);
        }})();
    </script>
</body>
</html>
"""
        filepath = os.path.join(self.output_dir, f"RAS_UPSC_Notes_{date_str}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Render updated Master Syllabus Wiki HTML as well!
        self.render_master_syllabus_html()

        print(f"HTML Daily Notes saved to: {filepath}")
        return filepath

    def render_daily_docx(self, analysis_data):
        date_str = analysis_data.get('date', 'Today')
        doc = Document()
        
        heading = doc.add_heading(f'RAS & UPSC Daily Notes - {date_str}', 0)
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 1. Prelims Facts
        doc.add_heading('1. प्रारंभिक परीक्षा तथ्य (Prelims Tracker)', level=1)
        for item in analysis_data.get('prelims_facts', []):
            p = doc.add_paragraph()
            p.add_run(f"• [{item.get('topic', '')}] ").bold = True
            p.add_run(item.get('fact', ''))

        # 2. Mains Questions (5M & 10M)
        doc.add_heading('2. मुख्य परीक्षा मॉडल उत्तर सेट (RAS Mains - 5M & 10M)', level=1)
        for q in analysis_data.get('mains_questions', []):
            p = doc.add_paragraph()
            p.add_run(f"प्रश्न [{q.get('marks', 5)} अंक - {q.get('paper', '')}]: {q.get('question', '')}\n").bold = True
            if q.get('marks') == 5:
                p.add_run(f"उत्तर ढांचा (~50 शब्द):\n{q.get('model_answer', '')}\n")
            else:
                p.add_run(f"भूमिका: {q.get('intro', '')}\n")
                p.add_run(f"मुख्य भाग: {q.get('body', '')}\n")
                p.add_run(f"निष्कर्ष: {q.get('conclusion', '')}\n")
            doc.add_paragraph("-" * 35)

        # 3. Coaching Teacher Analysis
        yt_data = analysis_data.get('youtube_teacher_analysis', [])
        if yt_data:
            doc.add_heading('3. कोचिंग शिक्षक विश्लेषण एवं व्याख्यान सार (Lecture Analysis & Exam Tips)', level=1)
            for yt in yt_data:
                p = doc.add_paragraph()
                p.add_run(f"विषय: {yt.get('topic', '')}\n").bold = True
                p.add_run(f"शिक्षक व्याख्यान एवं ट्रिक्स: {yt.get('teacher_explanation', '')}\n")
                p.add_run("क्लास के मुख्य बिंदु:\n")
                for pt in yt.get('key_takeaways', []):
                    p.add_run(f"  • {pt}\n")
                p.add_run(f"💡 परीक्षा टिप: {yt.get('exam_tip', '')}\n")
                doc.add_paragraph("-" * 35)

        # 4. Rajasthan Sujas, Patrika & Bhaskar
        sujas_data = analysis_data.get('rajasthan_sujas_special', [])
        if sujas_data:
            doc.add_heading('4. राजस्थान सुजस, पत्रिका एवं दैनिक भास्कर विशेष (RPSC Special)', level=1)
            for s in sujas_data:
                p = doc.add_paragraph()
                p.add_run(f"शीर्षक: {s.get('title', '')} [{s.get('department', 'DIPR Rajasthan')}]\n").bold = True
                for pt in s.get('key_points', []):
                    p.add_run(f"  • {pt}\n")
                p.add_run(f"RPSC महत्व: {s.get('rpsc_relevance', '')}\n")
                doc.add_paragraph("-" * 35)

        # 5. Editorial & Magazine Deep Dives
        eds_data = analysis_data.get('editorial_deep_dive', [])
        if eds_data:
            doc.add_heading('5. सम्पादकीय एवं पत्रिका गहन विश्लेषण (The Hindu, Express, ET, DownToEarth, योजना व कुरुक्षेत्र)', level=1)
            for ed in eds_data:
                p = doc.add_paragraph()
                p.add_run(f"[{ed.get('source', 'Editorial')} - {ed.get('syllabus_topic', '')}] {ed.get('title', '')}\n").bold = True
                p.add_run(f"समसामयिक संदर्भ: {ed.get('context', '')}\n")
                p.add_run("मुख्य विश्लेषण व तर्क:\n")
                for pt in ed.get('key_arguments', []):
                    p.add_run(f"  • {pt}\n")
                p.add_run(f"आगे की राह: {ed.get('way_forward', '')}\n")
                doc.add_paragraph("-" * 35)

        # 6. Telegram Study Channels Q&A
        tg_data = analysis_data.get('telegram_quiz_and_notes', [])
        if tg_data:
            doc.add_heading('6. टेलीग्राम चैनल दैनिक मॉडल प्रश्नोत्तर व नोट्स (~50 शब्द प्रारूप)', level=1)
            for item in tg_data:
                q_text = item.get('question', item.get('question_or_topic', ''))
                ans_text = item.get('model_answer_50_words', item.get('correct_answer', ''))
                p = doc.add_paragraph()
                p.add_run(f"प्रश्न [5 अंक - {item.get('syllabus_link', 'Paper 1')} - {item.get('channel', '@Telegram')}]: {q_text}\n").bold = True
                p.add_run(f"उत्तर ढांचा एवं विस्तृत नोट्स (~50 शब्द):\n{ans_text}\n")
                doc.add_paragraph("-" * 40)

        docx_path = os.path.join(self.output_dir, f"RAS_UPSC_Notes_{date_str}.docx")
        doc.save(docx_path)
        print(f"Word DOCX Notes saved to: {docx_path}")
        return docx_path

if __name__ == '__main__':
    formatter = NotesFormatter()
    formatter.render_master_syllabus_html()
    print("Master Syllabus Wiki HTML rendering tested.")
