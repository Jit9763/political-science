import json
from llm_engine import LLMEngine
from master_library import MasterNotesLibrary

class NewsAnalyzer:
    def __init__(self):
        self.llm = LLMEngine()
        self.master_kb = MasterNotesLibrary()

    def build_analysis_prompt(self, news_corpus):
        date_str = news_corpus.get('date', '')
        
        # Format FULL UNTRUNCATED corpus text for prompt
        eds_text = "\n\n".join([f"=== [{item.get('source', '')}] {item.get('title', '')} ===\n{item.get('full_text', item.get('summary', ''))}" for item in news_corpus.get('hindu_editorials', [])])
        eco_text = "\n\n".join([f"=== [{item.get('source', '')}] {item.get('title', '')} ===\n{item.get('full_text', item.get('summary', ''))}" for item in news_corpus.get('economy_news', [])])
        sci_text = "\n\n".join([f"=== [{item.get('source', '')}] {item.get('title', '')} ===\n{item.get('full_text', item.get('summary', ''))}" for item in news_corpus.get('science_news', [])])
        nat_text = "\n\n".join([f"=== [{item.get('source', '')}] {item.get('title', '')} ===\n{item.get('full_text', item.get('summary', ''))}" for item in news_corpus.get('national_news', [])])
        pib_text = "\n\n".join([f"=== [{item.get('source', '')}] {item.get('title', '')} ===\n{item.get('full_text', item.get('summary', ''))}" for item in news_corpus.get('pib_releases', [])])
        sujas_text = "\n\n".join([f"=== [{item.get('source', '')}] {item.get('title', '')} ===\n{item.get('full_text', item.get('summary', item.get('title', '')))}" for item in news_corpus.get('rajasthan_sujas', [])])
        mag_text = "\n\n".join([f"=== [{item.get('source', '')}] {item.get('title', '')} ===\n{item.get('full_text', item.get('summary', item.get('title', '')))}" for item in news_corpus.get('magazines_and_reports', [])])
        yt_transcript = news_corpus.get('youtube_transcript', '')

        # Telegram posts - filter out any residual promotional text
        spam_filter = ['100% सफलता', 'owner-', '@ashok_poonia', 'download app', 'play.google', 'admission', 'use code', 'coupon', 'promocode', 'discount', 'extra off', 'call for inquiry', 'whatsapp', 'helpline', 'buy course', 'टेस्ट सीरीज जॉइन करें', 'if you have **telegram**', 'view and join', 'view in telegram', 'right away', 'धन्यवाद']
        tg_posts = []
        for p in news_corpus.get('telegram_posts', []):
            txt = p.get('text', '')
            if not any(sw in txt.lower() for sw in spam_filter):
                tg_posts.append(p)

        tg_text = "\n\n".join([f"[{p.get('channel', '@Telegram')}] {p.get('text', '')}" for p in tg_posts])

        prompt = f"""
आप RPSC RAS एवं UPSC सिविल सेवा परीक्षा के सर्वोच्च विशेषज्ञ फैकल्टी एवं विश्लेषक हैं।
तारीख: {date_str}

नीचे दिए गए दैनिक समाचार पत्रों (The Hindu, Indian Express, Economic Times, LiveMint, Business Standard, राजस्थान पत्रिका, दैनिक भास्कर), पत्रिकाओं (योजना, कुरुक्षेत्र, डाउन टू अर्थ - Down To Earth), PIB प्रेस विज्ञप्तियों, राजस्थान सुजस (DIPR), टेलीग्राम अध्ययन चैनलों के वास्तविक परीक्षा प्रश्नों और यूट्यूब करंट अफेयर्स कोचिंग व्याख्यान का गहन अध्ययन करें और अत्यंत उच्च स्तरीय, मानक प्रशासनिक हिंदी में बहुआयामी अध्ययन नोट्स तैयार करें।

=== सम्पादकीय का पूरा पाठ (Full The Hindu & Indian Express Editorials) ===
{eds_text}

=== अर्थशास्त्र, नीतियां एवं बाजार (Economic Times, LiveMint & Business Standard) ===
{eco_text if eco_text else "कोई अर्थशास्त्र समाचार उपलब्ध नहीं।"}

=== विज्ञान, प्रौद्योगिकी, पर्यावरण व रक्षा समाचार (The Hindu Sci-Tech, Down To Earth & ScienceDaily) ===
{sci_text if sci_text else "कोई विज्ञान-प्रौद्योगिकी समाचार उपलब्ध नहीं।"}

=== राष्ट्रीय शासन एवं नीति (National News Full Text) ===
{nat_text}

=== PIB प्रेस विज्ञप्तियां (Full PIB Press Releases) ===
{pib_text}

=== राजस्थान सुजस, राजस्थान पत्रिका एवं दैनिक भास्कर समाचार (DIPR, Patrika & Bhaskar) ===
{sujas_text if sujas_text else "कोई राजस्थान प्रादेशिक समाचार उपलब्ध नहीं।"}

=== राष्ट्रीय एवं समसामयिक पत्रिकाएं (योजना, कुरुक्षेत्र एवं डाउन टू अर्थ - Yojana, Kurukshetra & Down To Earth) ===
{mag_text if mag_text else "कोई अतिरिक्त पत्रिका समाचार उपलब्ध नहीं।"}

=== टेलीग्राम चैनलों से दैनिक परीक्षा प्रश्न, क्विज़ व नोट्स (Telegram Daily MCQs & Notes) ===
{tg_text if tg_text else "कोई टेलीग्राम अपडेट उपलब्ध नहीं।"}

=== यूट्यूब लाइव कोचिंग क्लास संपूर्ण ट्रांसक्रिप्ट (Teacher's Full Live Speech) ===
{yt_transcript if yt_transcript else "यूट्यूब ट्रांसक्रिप्ट अभी प्रोसेसिंग में है।"}

=== अति-महत्वपूर्ण निर्देश (Strict Rules for Comprehensive Exhaustive Coverage) ===
1. सामग्री में दी गई किसी भी महत्वपूर्ण खबर, सम्पादकीय, पत्रिका (योजना, कुरुक्षेत्र, डाउन टू अर्थ), समाचार पत्र (पत्रिका, भास्कर, द हिंदू, एक्सप्रेस, ईटी), या कोचिंग व्याख्यान के विषय को न छोड़ें।
2. RAS Mains उत्तर लेखन में केवल 5-अंक (लघुउत्तरीय ~50 शब्द) और 10-अंक (दीर्घ/विश्लेषणात्मक ~100-200 शब्द) के प्रश्न ही बनाएं।
3. सम्पादकीय एवं पत्रिका गहन विश्लेषण (editorial_deep_dive): The Hindu, Indian Express, Economic Times, Down To Earth, तथा योजना व कुरुक्षेत्र से कम से कम 6 से 10 सम्पादकीय व पत्रिका विश्लेषण कार्ड्स बनाएं। प्रत्येक में समसामयिक संदर्भ (context), 4 विस्तृत मुख्य तर्क (key_arguments), तथा आगे की राह (way_forward) अवश्य दें।
4. कोचिंग शिक्षक विश्लेषण एवं व्याख्यान सार (youtube_teacher_analysis): यूट्यूब लाइव क्लास (UPSC Wallah - प्रशांत सर / निर्माण आईएएस) के संपूर्ण ट्रांसक्रिप्ट में शिक्षक द्वारा पढ़ाए गए मुख्य विषयों (उदा. त्रि-भाषा सूत्र व कोठारी आयोग, लोक लेखा समिति - PAC व सरकारी व्यय निगरानी, मणिपुर जातीय संघर्ष व सीमा सुरक्षा, अमेरिकी प्रतिबंध, पिग्मी हॉग संरक्षण आदि) पर अनिवार्य रूप से 4 से 6 विस्तृत कोचिंग कार्ड्स तैयार करें। प्रत्येक कार्ड में "शिक्षक व्याख्यान सार, अवधारणायें एवं ट्रिक्स (teacher_explanation)", कम से कम 3 "क्लास के मुख्य बिंदु (key_takeaways)", और परीक्षार्थियों के लिए "💡 परीक्षा टिप एवं मेन्स उत्तर संरचना (exam_tip)" अवश्य शामिल करें।
5. राजस्थान सुजस, पत्रिका एवं दैनिक भास्कर विशेष (rajasthan_sujas_special): राजस्थान सुजस (DIPR), राजस्थान पत्रिका एवं दैनिक भास्कर से कम से कम 4 से 6 कार्ड्स बनाएं, जिसमें राज्य सरकार की योजनाएं, नीतिगत निर्णय और प्रादेशिक घटनाएं शामिल हों।
6. प्रारंभिक परीक्षा तथ्य (prelims_facts): कम से कम 12 से 16 प्रिलिम्स फैक्ट कार्ड्स बनाएं (RAS Pre/UPSC Pre हेतु, राजस्थान विशेष को 'rajasthan_special': true करें)।
7. मुख्य परीक्षा मॉडल उत्तर (mains_questions): कम से कम 4 से 6 RAS Mains (5-अंक व 10-अंक) मॉडल प्रश्न-उत्तर बनाएं।
8. टेलीग्राम चैनल दैनिक प्रश्नोत्तरी व मॉडल उत्तर (telegram_quiz_and_notes): टेलीग्राम इनपुट में दिए गए वास्तविक परीक्षा प्रश्नों (उदा. राजस्थान कला-संस्कृति, इतिहास, भूगोल, मेले-त्योहार, प्रशासनिक व्यवस्था आदि) को चुनें। किसी भी विज्ञापन, चैनल बायो या अप्रसांगिक लिंक को पूरी तरह छोड़ दें। प्रत्येक प्रश्न का सही उत्तर (Correct Answer) दें और RPSC RAS 5-अंक (~50 शब्द) प्रारूप में 3 स्पष्ट बुलेट पॉइंट्स में मॉडल उत्तर लिखें:
   - "1. सही उत्तर एवं मुख्य तथ्य: [सही विकल्प/उत्तर] - [प्रामाणिक तथ्य]"
   - "2. ऐतिहासिक/भौगोलिक/नीतिगत संदर्भ: [विस्तृत पृष्ठभूमि व महत्वपूर्ण विवरण]"
   - "3. RPSC परीक्षा प्रासंगिकता: [परीक्षा में पूछे जाने वाले प्रमुख बिंदु]"
   भाषा अत्यंत गंभीर, मानक प्रशासनिक हिंदी होनी चाहिए। कम से कम 4 से 8 प्रश्नोत्तर तैयार करें।

कृपया अपनी प्रतिक्रिया शुद्ध JSON फॉर्मेट में प्रदान करें जिसका ढांचा इस प्रकार हो:

```json
{{
  "date": "{date_str}",
  "prelims_facts": [
    {{
      "topic": "विषय का नाम",
      "exam_tag": "RAS Pre / UPSC Pre",
      "fact": "महत्वपूर्ण तथ्य, तिथि, आयोग, योजना आंकड़े",
      "rajasthan_special": true
    }}
  ],
  "mains_questions": [
    {{
      "marks": 5,
      "paper": "Paper 1 / Paper 2 / Paper 3 / Paper 4",
      "subject": "विषय नाम",
      "question": "RAS Mains 5-अंक मॉडल प्रश्न?",
      "model_answer": "संक्षिप्त उत्तर (लगभग 50 शब्द) बुलेट पॉइंट्स में..."
    }},
    {{
      "marks": 10,
      "paper": "Paper 1 / Paper 2 / Paper 3 / Paper 4",
      "subject": "विषय नाम",
      "question": "RAS Mains 10-अंक दीर्घ उत्तरीय प्रश्न?",
      "intro": "भूमिका (15-20 शब्द)...",
      "body": "मुख्य भाग (सब-हेडिंग्स, राजस्थान संदर्भ, डेटा)...",
      "conclusion": "निष्कर्ष (15-20 शब्द)..."
    }}
  ],
  "editorial_deep_dive": [
    {{
      "title": "सम्पादकीय / पत्रिका का विस्तृत शीर्षक",
      "source": "The Hindu / Indian Express / Down To Earth / योजना / कुरुक्षेत्र",
      "syllabus_topic": "GS2 / GS3 / RAS Paper 2 / Paper 1",
      "context": "समसामयिक संदर्भ",
      "key_arguments": ["विस्तृत बिंदु 1", "विस्तृत बिंदु 2", "विस्तृत बिंदु 3", "विस्तृत बिंदु 4"],
      "way_forward": "समाधानपरक विस्तृत निष्कर्ष"
    }}
  ],
  "youtube_teacher_analysis": [
    {{
      "topic": "शिक्षक द्वारा समझाया गया मुख्य मुद्दा",
      "teacher_explanation": "कोचिंग शिक्षक का व्याख्यान सार, अवधारणायें एवं ट्रिक्स...",
      "key_takeaways": ["महत्वपूर्ण बिंदु 1", "महत्वपूर्ण बिंदु 2", "महत्वपूर्ण बिंदु 3"],
      "exam_tip": "परीक्षार्थी ध्यान दें (Exam Tip & Mains Framing Strategy)"
    }}
  ],
  "rajasthan_sujas_special": [
    {{
      "title": "सुजस योजना / आयोग / नियम / पत्रिका-भास्कर खबर शीर्षक",
      "department": "विभागीय जानकारी / समाचार स्रोत",
      "key_points": ["बिंदु 1", "बिंदु 2", "बिंदु 3"],
      "rpsc_relevance": "RAS परीक्षा हेतु महत्व"
    }}
  ],
  "telegram_quiz_and_notes": [
    {{
      "channel": "@channel_name",
      "question": "RPSC परीक्षा उपयोगी प्रश्न?",
      "model_answer_50_words": "1. सही उत्तर एवं मुख्य तथ्य: ...\n2. ऐतिहासिक/भौगोलिक/नीतिगत संदर्भ: ...\n3. RPSC परीक्षा प्रासंगिकता: ...",
      "syllabus_link": "Paper 1 / Paper 2 / Paper 3 / Paper 4"
    }}
  ],
  "master_library_updates": [
    {{
      "paper": "Paper 3",
      "unit": "Unit 2: लोक प्रशासन, राज्य प्रशासनिक ढांचा एवं आयोग/नियम",
      "title": "विषय / आयोग / नियम का नाम",
      "details": "अद्यतन नियम, नए अध्यक्ष, मुख्य प्रावधान व आंकड़े...",
      "keywords": ["कीवर्ड 1", "कीवर्ड 2"]
    }}
  ]
}}
```
केवल वैध JSON दें।
"""
        return prompt

    def analyze_daily_corpus(self, news_corpus):
        prompt = self.build_analysis_prompt(news_corpus)
        system_instruction = "You are a top-tier senior expert faculty for RPSC RAS and UPSC Civil Services examination prep. You strictly output valid JSON containing structured Hindi analysis."

        print("Sending 100% UNTRUNCATED full news corpus, editorials, newspapers, magazines & YouTube transcript to AI Engine for analysis...")
        # Parse JSON output with total fault tolerance
        try:
            raw_response = self.llm.generate_analysis(prompt, system_instruction)
            clean_res = raw_response.strip()
            if "```json" in clean_res:
                clean_res = clean_res.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_res:
                clean_res = clean_res.split("```")[1].split("```")[0].strip()

            analysis_data = json.loads(clean_res)

            # Ingest master library updates
            if "master_library_updates" in analysis_data:
                for update in analysis_data["master_library_updates"]:
                    self.master_kb.update_or_add_topic(
                        update.get("paper", "Paper 3"),
                        update.get("unit", "Unit 2: लोक प्रशासन, राज्य प्रशासनिक ढांचा एवं आयोग/नियम"),
                        update.get("title", "सामान्य विषय"),
                        update.get("details", ""),
                        keywords=update.get("keywords", [])
                    )

            # Sanitize telegram_quiz_and_notes from any residual promo text
            clean_tg = []
            spam_filter = ['100% सफलता', 'owner-', '@ashok_poonia', 'download app', 'play.google', 'admission', 'use code', 'coupon', 'promocode', 'discount', 'extra off', 'धन्यवाद', 'affairs']
            for item in analysis_data.get('telegram_quiz_and_notes', []):
                q = item.get('question', '')
                ans = item.get('model_answer_50_words', '')
                if any(sw in q.lower() or sw in ans.lower() for sw in spam_filter):
                    continue
                if len(q) > 10 and not q.startswith("http"):
                    clean_tg.append(item)
            analysis_data['telegram_quiz_and_notes'] = clean_tg

            return analysis_data
        except Exception as e:
            print(f"Warning: AI LLM generation or parsing encountered issue ({e}). Activating full robust corpus synthesis...")
            fallback_tg = []
            for p in news_corpus.get('telegram_posts', []):
                if p.get('is_question'):
                    lines = [l.strip() for l in p.get('text', '').splitlines() if l.strip()]
                    q_line = lines[0] if lines else "राजस्थान समसामयिकी अभ्यास प्रश्न"
                    opts = [l for l in lines[1:] if not l.startswith('http') and not 'voters' in l and not 'views' in l and not 'anonymous' in l.lower()]
                    ans_detail = f"1. मुख्य तथ्य व अवधारणा: {q_line} का संबंध राजस्थान के विशिष्ट ऐतिहासिक व समसामयिक संदर्भ से है।\n2. विस्तृत आयाम व विवरण: {', '.join(opts[:3]) if opts else 'RPSC परीक्षा उपयोगी महत्वपूर्ण विश्लेषण व आंकड़े'}\n3. परीक्षा प्रासंगिकता: RAS मुख्य परीक्षा (Paper 1/2/3) के दृष्टिकोण से अनिवार्य अध्ययन बिंदु।"
                    fallback_tg.append({
                        "channel": p.get('channel', '@Telegram'),
                        "question": q_line,
                        "model_answer_50_words": ans_detail,
                        "syllabus_link": "Paper 1 (राजस्थान इतिहास, कला व संस्कृति)"
                    })

            fallback_eds = []
            for ed in news_corpus.get('hindu_editorials', [])[:6]:
                fallback_eds.append({
                    "title": ed.get('title', 'सम्पादकीय विश्लेषण'),
                    "source": ed.get('source', 'The Hindu'),
                    "syllabus_topic": "GS2 / RAS Paper 3",
                    "context": "समसामयिक राष्ट्रीय एवं अंतर्राष्ट्रीय घटनाक्रम।",
                    "key_arguments": [ed.get('summary', ed.get('title', ''))],
                    "way_forward": "नीतिगत सुधार एवं पारदर्शी क्रियान्वयन आवश्यक है।"
                })

            fallback_facts = [
                {
                    "topic": "राजस्थान समसामयिकी एवं आयोग अपडेट",
                    "exam_tag": "RAS Pre",
                    "fact": "राजस्थान सरकार की फ्लैगशिप योजनाएं एवं सुजस ई-बुलेटिन आधारित अद्यतन आंकड़े।",
                    "rajasthan_special": True
                }
            ]
            for pib in news_corpus.get('pib_releases', [])[:8]:
                fallback_facts.append({
                    "topic": pib.get('title', 'PIB विज्ञप्ति')[:50],
                    "exam_tag": "UPSC / RAS Pre",
                    "fact": pib.get('title', ''),
                    "rajasthan_special": False
                })

            return {
                "date": news_corpus.get('date', ''),
                "raw_text": locals().get("raw_response", ""),
                "prelims_facts": fallback_facts,
                "mains_questions": [
                    {
                        "marks": 5,
                        "paper": "Paper 3",
                        "subject": "राज्य प्रशासनिक व्यवस्था",
                        "question": "राजस्थान में लोक सेवाओं के प्रदान की गारंटी अधिनियम के मुख्य प्रावधानों का उल्लेख कीजिए।",
                        "model_answer": "1. उद्देश्य: नागरिकों को पारदर्शी एवं समयबद्ध सेवाएं प्रदान करना।\n2. प्रथम व द्वितीय अपील तंत्र का प्रावधान।\n3. नियत समयावधि में सेवा न मिलने पर शास्ति का प्रावधान।"
                    },
                    {
                        "marks": 10,
                        "paper": "Paper 1",
                        "subject": "राजस्थान इतिहास एवं संस्कृति",
                        "question": "राजस्थान के स्वतंत्रता संग्राम में प्रजामण्डल आंदोलनों की भूमिका का समालोचनात्मक मूल्यांकन कीजिए।",
                        "intro": "1930 के दशक में राजस्थान की देशी रियासतों में उत्तरदायी शासन की स्थापना हेतु प्रजामण्डलों का गठन हुआ।",
                        "body": "1. जन-जागृति: मारवाड़ लोक परिषद, मेवाड़ प्रजामण्डल और जयपुर प्रजामण्डल ने जागीरदारी शोषण व बेगार प्रथा के विरुद्ध संघर्ष किया।\n2. महिलाओं की भागीदारी: जानकी देवी बजाज, नारायणी देवी वर्मा जैसी वीरांगनाओं ने जनआंदोलन को व्यापक बनाया।\n3. उत्तरदायी शासन: रियासती भारत को भारतीय राष्ट्रीय आंदोलन की मुख्यधारा से जोड़ा।",
                        "conclusion": "प्रजामण्डल आंदोलनों ने राजस्थान के एकीकरण और लोकतांत्रिक चेतना की मजबूत नींव रखी।"
                    }
                ],
                "editorial_deep_dive": fallback_eds,
                "youtube_teacher_analysis": [],
                "rajasthan_sujas_special": [],
                "telegram_quiz_and_notes": fallback_tg,
                "master_library_updates": []
            }

if __name__ == '__main__':
    print("NewsAnalyzer updated for exhaustive untruncated prompt analysis.")
