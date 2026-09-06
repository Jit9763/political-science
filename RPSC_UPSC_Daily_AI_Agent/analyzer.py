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
        nat_text = "\n\n".join([f"=== [{item.get('source', '')}] {item.get('title', '')} ===\n{item.get('full_text', item.get('summary', ''))}" for item in news_corpus.get('national_news', [])])
        pib_text = "\n\n".join([f"=== [{item.get('source', '')}] {item.get('title', '')} ===\n{item.get('full_text', item.get('summary', ''))}" for item in news_corpus.get('pib_releases', [])])
        sujas_text = "\n".join([f"- [{item.get('source', '')}] {item.get('title', '')}: {item.get('summary', '')}" for item in news_corpus.get('rajasthan_sujas', [])])
        yt_transcript = news_corpus.get('youtube_transcript', '')

        prompt = f"""
आप RPSC RAS एवं UPSC परीक्षा के सर्वोच्च विशेषज्ञ शिक्षक एवं विश्लेषक हैं।
तारीख: {date_str}

नीचे दिए गए दैनिक समाचारों, सम्पादकीयों (The Hindu, Indian Express के पूर्ण सम्पादकीय पाठ), PIB की संपूर्ण प्रेस विज्ञप्तियों, राजस्थान सुजस (DIPR) तथा यूट्यूब करंट अफेयर्स लाइव क्लास के 100% पूर्ण ट्रांसक्रिप्ट का गहन अध्ययन करें और बिना किसी जानकारी को छोड़े अत्यंत विस्तृत, संपूर्ण एवं बहुआयामी अध्ययन नोट्स तैयार करें।

=== सम्पादकीय का पूरा पाठ (Full The Hindu & Express Editorials) ===
{eds_text}

=== राष्ट्रीय शासन एवं नीति (National News Full Text) ===
{nat_text}

=== PIB प्रेस विज्ञप्तियां (Full PIB Press Releases) ===
{pib_text}

=== राजस्थान सुजस एवं DIPR समाचार ===
{sujas_text}

=== यूट्यूब लाइव कोचिंग क्लास संपूर्ण ट्रांसक्रिप्ट (Teacher's Full Live Speech) ===
{yt_transcript if yt_transcript else "कोई यूट्यूब ट्रांसक्रिप्ट उपलब्ध नहीं।"}

=== अति-महत्वपूर्ण निर्देश (Strict Rules for Comprehensive Exhaustive Coverage) ===
1. सामग्री में दी गई किसी भी महत्वपूर्ण खबर, सम्पादकीय या यूट्यूब क्लास में शिक्षक द्वारा समझाए गए किसी भी टॉपिक को न छोड़ें।
2. RAS Mains उत्तर लेखन में 2-अंक के प्रश्न पूरी तरह समाप्त हो चुके हैं। केवल 5-अंक (लघुउत्तरीय ~50 शब्द) और 10-अंक (दीर्घ/विश्लेषणात्मक ~100-200 शब्द) के प्रश्न ही बनाएं।
3. सम्पादकीय विश्लेषण (editorial_deep_dive): कम से कम 5 से 8 विस्तृत सम्पादकीय विश्लेषण बनाएं।
4. यूट्यूब क्लास विश्लेषण (youtube_teacher_analysis): यूट्यूब ट्रांसक्रिप्ट में शिक्षक द्वारा चर्चा किए गए सभी अलग-अलग विषयों पर कम से कम 4 से 6 विस्तृत कोचिंग कार्ड्स बनाएं।
5. प्रारंभिक परीक्षा तथ्य (prelims_facts): कम से कम 10 से 15 प्रिलिम्स फैक्ट कार्ड्स बनाएं।
6. मुख्य परीक्षा मॉडल उत्तर (mains_questions): कम से कम 4 से 6 RAS Mains (5-अंक व 10-अंक) मॉडल प्रश्न-उत्तर बनाएं।

कृपया अपनी प्रतिक्रिया शुद्ध JSON फॉर्मेट में प्रदान करें जिसका ढांचा इस प्रकार हो:

```json
{{
  "date": "{date_str}",
  "prelims_facts": [
    {{
      "topic": "विषय का नाम",
      "exam_tag": "RAS Pre / UPSC Pre",
      "fact": "महत्वपूर्ण तथ्य, तिथि, आयोग, योजना आंकड़े",
      "rajasthan_special": true/false
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
      "title": "सम्पादकीय का विस्तृत शीर्षक",
      "source": "The Hindu / Indian Express",
      "syllabus_topic": "GS2 / GS3 / RAS Paper 2",
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
      "title": "सुजस योजना / आयोग / नियम शीर्षक",
      "department": "विभागीय जानकारी",
      "key_points": ["बिंदु 1", "बिंदु 2", "बिंदु 3"],
      "rpsc_relevance": "RAS परीक्षा हेतु महत्व"
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

        print("Sending 100% UNTRUNCATED full news corpus, editorials & YouTube transcript to AI Engine for analysis...")
        raw_response = self.llm.generate_analysis(prompt, system_instruction)

        # Parse JSON output
        try:
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

            return analysis_data
        except Exception as e:
            print(f"Error parsing AI response JSON: {e}")
            return {
                "date": news_corpus.get('date', ''),
                "raw_text": raw_response,
                "prelims_facts": [
                    {
                        "topic": "राजस्थान समसामयिकी एवं आयोग अपडेट",
                        "exam_tag": "RAS Pre",
                        "fact": "राजस्थान सरकार की फ्लैगशिप योजनाएं एवं सुजस ई-बुलेटिन आधारित अद्यतन आंकड़े।",
                        "rajasthan_special": True
                    }
                ],
                "mains_questions": [
                    {
                        "marks": 5,
                        "paper": "Paper 3",
                        "subject": "राज्य प्रशासनिक व्यवस्था",
                        "question": "राजस्थान में लोक सेवाओं के प्रदान की गारंटी अधिनियम के मुख्य प्रावधानों का उल्लेख कीजिए।",
                        "model_answer": "1. उद्देश्य: नागरिकों को पारदर्शी एवं समयबद्ध सेवाएं प्रदान करना।\n2. प्रथम व द्वितीय अपील तंत्र का प्रावधान।\n3. नियत समयावधि में सेवा न मिलने पर शास्ति का प्रावधान।"
                    }
                ],
                "editorial_deep_dive": [],
                "youtube_teacher_analysis": [],
                "rajasthan_sujas_special": [],
                "master_library_updates": []
            }

if __name__ == '__main__':
    print("NewsAnalyzer updated for exhaustive untruncated prompt analysis.")
