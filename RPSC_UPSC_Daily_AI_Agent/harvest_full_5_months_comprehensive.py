import os
import re
import time
import requests
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from uploader import DriveSyncUploader
from master_library import MasterNotesLibrary

def fetch_and_build_comprehensive_5_months():
    print("==================================================================")
    print("🚀 Extracting Full 5-Month Master Series (Facts 1 to 850+) from Channels")
    print("==================================================================")

    # We will fetch across key post IDs from 23820 down to 22700
    target_ids = list(range(23820, 22650, -25))
    print(f"Sampling across {len(target_ids)} checkpoint blocks across the 5 months...")

    raw_fact_dict = {} # Key: cleaned question, Value: answer/fact
    seen_facts = set()

    for idx, pid in enumerate(target_ids, 1):
        url = f"https://r.jina.ai/https://t.me/s/Rajasthan_History_Polity_Culture?before={pid}"
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=12)
            if r.status_code != 200:
                continue
            text = r.text

            # 1. Pattern for numbered facts: e.g. "806.राजस्थान में प्रसिद्ध... - **शीतला माता**"
            matches = re.findall(r'(\d{1,4})\.\s*([^\n\-\–\:]+?)[\-\–\:]\s*\*{0,2}([^\n\*\_]+)', text)
            for num, q, a in matches:
                clean_q = q.strip().replace('**', '').replace('_', '').replace('’', "'").replace('‘', "'")
                clean_a = a.strip().replace('**', '').replace('_', '').replace('’', "'").replace('‘', "'")
                clean_a = re.sub(r'\[.*?\]\(.*?\)', '', clean_a).strip()
                if len(clean_q) > 10 and len(clean_a) > 1 and not any(sw in clean_q.lower() for sw in ['discount', 'code', 'admission']):
                    key = clean_q.lower()
                    if key not in seen_facts:
                        seen_facts.add(key)
                        raw_fact_dict[clean_q] = clean_a

            # 2. Pattern for quiz polls: Question followed by highest percentage or marked option
            quiz_blocks = re.findall(r'([^\n\?]+(?:\?|का संबंध है|कहा जाता है|स्थित है|कहते हैं))[^\n]*\n(?:Anonymous Quiz)?\s*\n\[([0-9% a-zA-Z\u0900-\u097F\s\.\,\-]+)\]', text)
            for q_text, opts_text in quiz_blocks:
                clean_q = q_text.strip().replace('**', '').replace('_', '')
                if len(clean_q) > 15 and not clean_q.startswith('!'):
                    # Find option with highest percentage e.g. "74% A और B दोनों" or first prominent option
                    opts = re.findall(r'(\d+)%\s+([^\d%]+)', opts_text)
                    if opts:
                        # Pick the highest voted option as correct answer
                        best_opt = max(opts, key=lambda x: int(x[0]))[1].strip()
                        key = clean_q.lower()
                        if key not in seen_facts:
                            seen_facts.add(key)
                            raw_fact_dict[clean_q] = best_opt

        except Exception as e:
            pass

        if idx % 10 == 0:
            print(f"  [Progress] Checked {idx}/{len(target_ids)} blocks -> Extracted {len(raw_fact_dict)} unique facts so far...")
        time.sleep(0.8)

    print(f"\n✅ Total Unique Facts Extracted from 5-Month Series: {len(raw_fact_dict)}")

    # Categorize facts into 7 Master Syllabus Modules
    categories = {
        "1. राजस्थान का इतिहास, प्रमुख राजवंश व रियासतें": [],
        "2. राजस्थान का स्वतंत्रता संग्राम, प्रजामण्डल व एकीकरण": [],
        "3. राजस्थान की स्थापत्य कला: दुर्ग, महल, हवेलियां, बावड़ियां व मंदिर": [],
        "4. राजस्थानी चित्रकला, हस्तशिल्प, साहित्य व भाषा": [],
        "5. लोक देवता-देवियां, संत, मेले, त्यौहार व लोक कला": [],
        "6. राजस्थान का भूगोल, नदियां, बाँध, खनिज व जलवायु": [],
        "7. राजस्थान की प्रशासनिक व राजनीतिक व्यवस्था, आयोग व नीतियां": []
    }

    for q, a in raw_fact_dict.items():
        combined = (q + " " + a).lower()

        # Module 2: Freedom struggle, Prajamandal, Integration
        if any(k in combined for k in ['प्रजामण्डल', 'स्वतंत्रता', 'एकीकरण', 'किसान आंदोलन', 'बिजोलिया', 'बेगू', 'मारवाड़ लोक परिषद', 'व्यास', 'माणिक्यलाल', 'भगत आंदोलन', 'गोविंद गिरि', 'रियासती']):
            categories["2. राजस्थान का स्वतंत्रता संग्राम, प्रजामण्डल व एकीकरण"].append((q, a))
        # Module 3: Architecture: Forts, Havelis, Temples
        elif any(k in combined for k in ['हवेली', 'दुर्ग', 'किला', 'महल', 'छतरी', 'बावड़ी', 'मंदिर', 'बच्छावत', 'रामपुरिया', 'गागरोन', 'चित्तौड़', 'कुंभलगढ़', 'मेहरानगढ़', 'शेरगढ़']):
            categories["3. राजस्थान की स्थापत्य कला: दुर्ग, महल, हवेलियां, बावड़ियां व मंदिर"].append((q, a))
        # Module 4: Paintings, Handicrafts, Literature
        elif any(k in combined for k in ['चित्रकला', 'शैली', 'उपशैली', 'पेंटिंग', 'थेवा कला', 'कावड़', 'उस्ता कला', 'सावर', 'ग्रंथ', 'रासो', 'नैणसी', 'कवि', 'साहित्य', 'आगीबाण', 'भाषा', 'बोली']):
            categories["4. राजस्थानी चित्रकला, हस्तशिल्प, साहित्य व भाषा"].append((q, a))
        # Module 5: Folk gods, Saints, Fairs, Festivals
        elif any(k in combined for k in ['मेला', 'त्यौहार', 'उत्सव', 'शीतला', 'रामदेव', 'पाबूजी', 'तेजाजी', 'मीरा', 'दादू', 'जाम्भोजी', 'लोक देवता', 'लोक देवी', 'नृत्य', 'घूमर', 'गेर']):
            categories["5. लोक देवता-देवियां, संत, मेले, त्यौहार व लोक कला"].append((q, a))
        # Module 6: Geography, Rivers, Dams, Climate, Minerals
        elif any(k in combined for k in ['नदी', 'लूनी', 'चम्बल', 'बनास', 'साबी', 'बाँध', 'सिंचाई', 'झील', 'जलवायु', 'कोपेन', 'अरावली', 'खनिज', 'अभयारण्य', 'मिट्टी', 'खेजड़ी', 'थार', 'वन']):
            categories["6. राजस्थान का भूगोल, नदियां, बाँध, खनिज व जलवायु"].append((q, a))
        # Module 7: Polity, Governance, Schemes
        elif any(k in combined for k in ['संविधान', 'राज्यपाल', 'मुख्यमंत्री', 'आयोग', 'विधानसभा', 'लोक सेवा', 'योजना', 'नीति', '74वां', '73वां', 'मिशन पढ़ो', 'आरपीएससी', 'rpsc']):
            categories["7. राजस्थान की प्रशासनिक व राजनीतिक व्यवस्था, आयोग व नीतियां"].append((q, a))
        # Module 1: Default to History & Dynasties
        else:
            categories["1. राजस्थान का इतिहास, प्रमुख राजवंश व रियासतें"].append((q, a))

    # Generate HTML Cards by Category
    sections_html = ""
    for cat_name, items in categories.items():
        if not items:
            continue
        cards_html = ""
        for q, a in items:
            cards_html += f"""
            <div class="fact-card">
                <div class="card-header">
                    <span class="badge badge-raj">RAS Pre (तथ्य)</span>
                    <span class="topic-title">{q}</span>
                </div>
                <p class="fact-text"><strong>उत्तर / मुख्य तथ्य:</strong> {a}</p>
            </div>
            """
        sections_html += f"""
        <div class="section-title">📌 {cat_name} ({len(items)} महत्वपूर्ण तथ्य)</div>
        {cards_html}
        """

    # Add RAS Mains Model Questions (5M & 10M)
    mains_html = """
    <div class="section-title">🔵 मुख्य परीक्षा उत्तर लेखन मॉडल सेट (RAS Mains - 5M एवं 10M विशेष प्रश्नोत्तर)</div>
    
    <div class="mains-card">
        <div class="mains-header">
            <span class="badge badge-5m">5 अंक (Paper 1)</span>
            <span class="subject-tag">राजस्थान स्थापत्य कला</span>
        </div>
        <h3 class="question-text">प्रश्न: राजस्थान में हवेलियों की स्थापत्यगत विशेषताओं पर संक्षिप्त टिप्पणी लिखिए। (~50 शब्द)</h3>
        <div class="answer-box">
            <strong class="ans-label">उत्तर ढांचा (~50 शब्द):</strong>
            <div class="answer-content">
                1. <strong>भौगोलिक अनुकूलन:</strong> अत्यधिक गर्मी व धूल भरी हवाओं से बचाव हेतु खुले चौक (आंगन) एवं ऊंची दीवारें।<br>
                2. <strong>बारीक नक्काशी:</strong> लाल बलुआ पत्थर पर सूक्ष्म जालीदार झरोखे, छज्जे व तोड़े (विशेषकर बीकानेर, शेखावाटी व जैसलमेर)।<br>
                3. <strong>भित्ति चित्र (Fresco):</strong> शेखावाटी की हवेलियों में धार्मिक व सामाजिक विषयों पर ओपन आर्ट गैलरी आधारित चित्रण।
            </div>
        </div>
    </div>

    <div class="mains-card">
        <div class="mains-header">
            <span class="badge badge-5m">5 अंक (Paper 1)</span>
            <span class="subject-tag">राजस्थान का स्वतंत्रता संग्राम</span>
        </div>
        <h3 class="question-text">प्रश्न: जयनारायण व्यास का राजस्थान के जन-जागरण में क्या योगदान था? (~50 शब्द)</h3>
        <div class="answer-box">
            <strong class="ans-label">उत्तर ढांचा (~50 शब्द):</strong>
            <div class="answer-content">
                1. <strong>संस्थापक नेतृत्व:</strong> मारवाड़ प्रजामण्डल एवं मारवाड़ लोक परिषद के माध्यम से जागीरदारी शोषण व बेगार प्रथा का प्रखर विरोध।<br>
                2. <strong>पत्रकारिता क्रांति:</strong> 'आगीबाण' (राजस्थानी भाषा का प्रथम राजनीतिक पत्र), 'पीप' (अंग्रेजी) एवं 'अखण्ड भारत' का संपादन।<br>
                3. <strong>लोकतांत्रिक शासन:</strong> स्वतंत्रता उपरांत राजस्थान के मुख्यमंत्री के रूप में लोकतांत्रिक मूल्यों व भूमि सुधारों की आधारशिला रखी।
            </div>
        </div>
    </div>

    <div class="mains-card">
        <div class="mains-header">
            <span class="badge badge-10m">10 अंक (Paper 1)</span>
            <span class="subject-tag">राजस्थान चित्रकला शैलियां</span>
        </div>
        <h3 class="question-text">प्रश्न: राजस्थानी चित्रकला के उद्भव, प्रमुख शैलियों तथा इसके वैज्ञानिक वर्गीकरण का समालोचनात्मक विश्लेषण कीजिए। (~100 शब्द)</h3>
        <div class="answer-box">
            <div class="ans-section"><strong class="ans-label">भूमिका (Introduction):</strong><br>राजस्थानी चित्रकला का उद्भव 15वीं शताब्दी में अजंता व अपभ्रंश शैली के समन्वय से हुआ। 1916 में आनंद कुमार स्वामी ने अपनी पुस्तक 'राजपूत पेंटिंग' में इसका सर्वप्रथम वैज्ञानिक वर्गीकरण किया।</div>
            <div class="ans-section"><strong class="ans-label">मुख्य भाग (Body & Dimensions):</strong><br><strong>1. प्रमुख स्कूल व शैलियां:</strong><br>• मेवाड़ स्कूल: उदयपुर, चावंड, नाथद्वारा (पिछवाई कला) व सावर उपशैली (प्राकृतिक चटक रंग)।<br>• मारवाड़ स्कूल: जोधपुर, बीकानेर (उस्ता कला व मथेरण कला), किशनगढ़ (बणी-ठणी)।<br>• हाड़ौती स्कूल: बूंदी शैली (पशु-पक्षियों का सजीव अंकन) व कोटा शैली (शिकार के दृश्य)।<br>• ढूंढाड़ स्कूल: जयपुर, आमेर, अलवर व शेखावाटी की हवेलियों के भित्ति चित्र।<br><br><strong>2. विशिष्ट विशेषताएं:</strong> प्राकृतिक रंगों (सोने, चांदी व वनस्पति रंग) का प्रयोग, भाव-प्रवण नयन, ऋतु वर्णन (बारहमासा) तथा लोक जीवन व भक्ति भावना का अद्भुत समन्वय।</div>
            <div class="ans-section"><strong class="ans-label">निष्कर्ष (Conclusion):</strong><br>राजस्थानी चित्रकला भारतीय सांस्कृतिक विरासत का अनूठा स्तंभ है, जो क्षेत्रीय विविधता और उत्कृष्ट सौंदर्यशास्त्र का जीवंत प्रमाण प्रस्तुत करती है।</div>
        </div>
    </div>

    <div class="mains-card">
        <div class="mains-header">
            <span class="badge badge-5m">5 अंक (Paper 2)</span>
            <span class="subject-tag">राजस्थान अपवाह तंत्र</span>
        </div>
        <h3 class="question-text">प्रश्न: लूनी नदी तंत्र की मुख्य भौगोलिक विशेषताओं का उल्लेख कीजिए। (~50 शब्द)</h3>
        <div class="answer-box">
            <strong class="ans-label">उत्तर ढांचा (~50 शब्द):</strong>
            <div class="answer-content">
                1. <strong>उद्गम व प्रवाह:</strong> अजमेर के नाग पहाड़ से निकलकर 495 किमी (राजस्थान में ~330 किमी) बहती हुई कच्छ के रण में विलीन होती है।<br>
                2. <strong>प्रकृति:</strong> बालोतरा (बाड़मेर) तक इसका जल मीठा तथा उसके पश्चात खारा हो जाता है (लवणवती)।<br>
                3. <strong>सहायक नदियां:</strong> सूकड़ी, बांडी, जवाई, गुहिया तथा दाईं ओर से मिलने वाली एकमात्र गैर-अरावली नदी 'जोजड़ी'।
            </div>
        </div>
    </div>

    <div class="mains-card">
        <div class="mains-header">
            <span class="badge badge-10m">10 अंक (Paper 3)</span>
            <span class="subject-tag">स्थानीय स्वशासन एवं संवैधानिक सुधार</span>
        </div>
        <h3 class="question-text">प्रश्न: 74वें संविधान संशोधन अधिनियम, 1992 के प्रमुख प्रावधानों तथा राजस्थान में शहरी स्थानीय निकायों पर इसके प्रभावों की समीक्षा कीजिए। (~100 शब्द)</h3>
        <div class="answer-box">
            <div class="ans-section"><strong class="ans-label">भूमिका (Introduction):</strong><br>74वें संविधान संशोधन अधिनियम 1992 ने शहरी स्थानीय निकायों को संवैधानिक दर्जा प्रदान करते हुए संविधान में 'भाग 9-A' तथा '12वीं अनुसूची' को समाहित किया।</div>
            <div class="ans-section"><strong class="ans-label">मुख्य भाग (Body):</strong><br><strong>1. मुख्य संवैधानिक प्रावधान:</strong><br>• त्रि-स्तरीय शहरी निकाय: नगर पंचायत, नगर पालिका परिषद व नगर निगम।<br>• आरक्षण: महिलाओं हेतु कम से कम 1/3 स्थान तथा SC/ST हेतु जनसंख्या के अनुपात में आरक्षण।<br>• राज्य वित्त आयोग (अनुच्छेद 243-Y) तथा राज्य निर्वाचन आयोग (अनुच्छेद 243-ZA) द्वारा वित्तीय व चुनावी स्वायत्तता।<br>• 12वीं अनुसूची में उल्लिखित 18 कार्यात्मक विषयों का हस्तांतरण।<br><br><strong>2. राजस्थान में प्रभाव:</strong><br>• राजस्थान नगरपालिका अधिनियम में संशोधन कर नगर नियोजन, ठोस अपशिष्ट प्रबंधन तथा स्थानीय कर संग्रहण को सशक्त बनाया गया।<br>• महिलाओं व वंचित वर्गों के राजनीतिक सशक्तीकरण में ऐतिहासिक वृद्धि हुई।</div>
            <div class="ans-section"><strong class="ans-label">निष्कर्ष (Conclusion):</strong><br>74वां संशोधन शहरी विकेंद्रीकरण का मील का पत्थर है, जिसे और अधिक प्रभावी बनाने हेतु वित्तीय स्वायत्तता को और सुदृढ़ करना आवश्यक है।</div>
        </div>
    </div>
    """

    full_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RPSC RAS 5-Month Telegram Master Revision Notes (Full Series)</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #1e1b4b;
            --primary-light: #3b82f6;
            --secondary: #0f766e;
            --accent-gold: #b45309;
            --accent-purple: #6b21a8;
            --accent-red: #9f1239;
            --bg-main: #f1f5f9;
            --card-bg: #ffffff;
            --text-dark: #020617;
            --border-color: #cbd5e1;
        }}
        body {{
            font-family: 'Noto Sans Devanagari', sans-serif;
            background-color: var(--bg-main);
            color: var(--text-dark);
            margin: 0;
            padding: 25px;
            line-height: 1.8;
            font-size: 18px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
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
            flex-wrap: wrap;
            gap: 20px;
        }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 32px; font-weight: 900; }}
        .header p {{ margin: 0; opacity: 0.95; font-size: 19px; }}
        .print-btn {{
            background: #ffffff;
            color: #1e1b4b;
            border: none;
            padding: 14px 24px;
            border-radius: 12px;
            font-weight: 800;
            font-size: 17px;
            cursor: pointer;
            font-family: inherit;
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        .search-bar {{
            width: 100%;
            padding: 15px 22px;
            font-size: 19px;
            border: 2px solid #cbd5e1;
            border-radius: 14px;
            margin-bottom: 30px;
            font-family: inherit;
            box-sizing: border-box;
            background: white;
        }}
        .section-title {{
            font-size: 26px;
            font-weight: 800;
            margin: 40px 0 20px 0;
            padding: 12px 20px;
            background: #ffffff;
            border-radius: 12px;
            border-left: 8px solid var(--primary-light);
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            color: #0f172a;
        }}
        .badge {{ padding: 6px 14px; border-radius: 8px; font-size: 15px; font-weight: 800; color: white; display: inline-block; }}
        .badge-pre {{ background-color: var(--accent-gold); }}
        .badge-raj {{ background-color: var(--accent-purple); }}
        .badge-5m {{ background-color: #0284c7; }}
        .badge-10m {{ background-color: #4338ca; }}
        
        .fact-card, .mains-card {{
            background: var(--card-bg);
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 25px;
            box-shadow: 0 6px 12px -2px rgba(0,0,0,0.08);
            border: 1px solid var(--border-color);
        }}
        .fact-card {{ border-left: 8px solid var(--accent-purple); }}
        .mains-card {{ border-left: 8px solid #4338ca; }}
        
        .card-header, .mains-header {{ display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }}
        .topic-title {{ font-weight: 800; font-size: 20px; color: #0f172a; }}
        .fact-text {{ margin: 0; color: var(--text-dark); font-size: 19px; line-height: 1.8; }}
        .question-text {{ margin: 12px 0 16px 0; color: #1e1b4b; font-size: 22px; font-weight: 800; }}
        .answer-box {{ background: #f8fafc; padding: 22px; border-radius: 12px; font-size: 18px; border: 1px solid #e2e8f0; }}
        .ans-label {{ font-size: 19px; color: #1e3a8a; display: inline-block; margin-bottom: 6px; }}
        .ans-section {{ margin-bottom: 16px; line-height: 1.8; }}
        .subject-tag {{ color: #475569; font-weight: 700; margin-left: auto; font-size: 16px; }}

        @media print {{
            .print-btn, .search-bar {{ display: none; }}
            body {{ background: white; padding: 0; font-size: 14pt; }}
            .container {{ max-width: 100%; }}
            .fact-card, .mains-card {{ break-inside: avoid; border: 1px solid #999; margin-bottom: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>📚 RPSC RAS 5-Month Telegram Master Revision Notes (Full Series)</h1>
                <p>विगत 5 माह के प्रमुख टेलीग्राम चैनल्स से संकलित संपूर्ण {len(raw_fact_dict)} प्रामाणिक तथ्य व मुख्य परीक्षा प्रश्नोत्तर (Pre & Mains)</p>
            </div>
            <div>
                <button class="print-btn" onclick="window.print()">🖨️ PDF प्रिंट करें</button>
            </div>
        </div>

        <input type="text" id="searchInput" class="search-bar" placeholder="🔍 किसी भी विषय, हवेली, नदी, चित्रकला, प्रजामण्डल या कीवर्ड से खोजें..." onkeyup="filterNotes()">

        {sections_html}

        {mains_html}
    </div>

    <script>
        function filterNotes() {{
            let q = document.getElementById('searchInput').value.toLowerCase();
            let cards = document.querySelectorAll('.fact-card, .mains-card');
            cards.forEach(card => {{
                let text = card.innerText.toLowerCase();
                card.style.display = text.includes(q) ? 'block' : 'none';
            }});
        }}
    </script>
</body>
</html>
"""
    output_dir = os.path.join(os.path.dirname(__file__), "Output_Notes")
    os.makedirs(output_dir, exist_ok=True)
    
    html_path = os.path.join(output_dir, "Rajasthan_5_Months_Telegram_Master_Question_Bank.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"✅ Full 5-Month Notes HTML saved: {html_path}")

    # Build Word Document
    doc = Document()
    heading = doc.add_heading(f"RPSC RAS - 5 Month Master Study Notes ({len(raw_fact_dict)} Facts)", 0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("विगत 5 माह के टेलीग्राम चैनल्स से संकलित शुद्ध, प्रामाणिक मास्टर नोट्स (Pre & Mains Pattern)\n" + "="*60)

    for cat_name, items in categories.items():
        if not items:
            continue
        doc.add_heading(f"{cat_name} ({len(items)} तथ्य)", level=1)
        for q, a in items:
            p = doc.add_paragraph()
            p.add_run(f"• {q}: ").bold = True
            p.add_run(a)

    docx_path = os.path.join(output_dir, "Rajasthan_5_Months_Telegram_Master_Question_Bank.docx")
    doc.save(docx_path)
    print(f"✅ Full 5-Month Notes DOCX saved: {docx_path}")

    # Sync to Google Drive Desktop Folder
    uploader = DriveSyncUploader()
    uploader.sync_to_drive(html_path)
    uploader.sync_to_drive(docx_path)
    print("✅ Synced Full 5-Month Notes to Google Drive desktop folder!")

if __name__ == '__main__':
    fetch_and_build_comprehensive_5_months()
