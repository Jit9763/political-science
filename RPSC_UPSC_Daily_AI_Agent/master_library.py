import os
import json
from datetime import datetime

class MasterNotesLibrary:
    def __init__(self, kb_path=None):
        if kb_path is None:
            kb_path = os.path.join(os.path.dirname(__file__), "Master_Library", "ras_master_kb.json")
        self.kb_path = kb_path
        os.makedirs(os.path.dirname(self.kb_path), exist_ok=True)
        self.data = self.load_kb()

    def get_default_kb_structure(self):
        return {
            "metadata": {
                "title": "RPSC RAS & UPSC Master Syllabus Knowledge Base",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "topics": {
                "Paper 1": {
                    "Unit 1: इतिहास, कला, संस्कृति, साहित्य एवं विरासत": [],
                    "Unit 2: भारतीय एवं राजस्थान अर्थव्यवस्था": [],
                    "Unit 3: समाजशास्त्र, प्रबंधन, लेखांकन एवं अंकेक्षण": []
                },
                "Paper 2": {
                    "Unit 1: प्रशासकीय नीतिशास्त्र (Administrative Ethics)": [],
                    "Unit 2: सामान्य विज्ञान एवं प्रौद्योगिकी": [],
                    "Unit 3: भूगोल (राजस्थान, भारत एवं विश्व)": []
                },
                "Paper 3": {
                    "Unit 1: भारतीय राजनीतिक व्यवस्था एवं अंतरराष्ट्रीय संबंध": [],
                    "Unit 2: लोक प्रशासन, राज्य प्रशासनिक ढांचा एवं आयोग/नियम": [],
                    "Unit 3: खेल एवं योग, व्यवहार तथा विधि (राजस्थान विशेष अधिनियम)": []
                },
                "Paper 4": {
                    "Unit 1: सामान्य हिंदी (प्रशासनिक शब्दावली, प्रारूप लेखन)": [],
                    "Unit 2: General English (Administrative Vocabulary & Comprehension)": []
                }
            }
        }

    def load_kb(self):
        if os.path.exists(self.kb_path):
            try:
                with open(self.kb_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading Master KB: {e}")
        return self.get_default_kb_structure()

    def save_kb(self):
        self.data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.kb_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def update_or_add_topic(self, paper, unit, title, details, keywords=None, is_update=False):
        """Add a new item or update an existing topic to prevent duplication."""
        if paper not in self.data["topics"]:
            self.data["topics"][paper] = {}
        if unit not in self.data["topics"][paper]:
            self.data["topics"][paper][unit] = []

        unit_list = self.data["topics"][paper][unit]
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Check for existing matching topic
        matched_item = None
        for item in unit_list:
            if item["title"].strip().lower() == title.strip().lower() or (keywords and any(kw in item.get("keywords", []) for kw in keywords)):
                matched_item = item
                break

        if matched_item:
            # Update existing record (Dynamic Fact Updating)
            matched_item["last_updated"] = today_str
            matched_item["updates_history"] = matched_item.get("updates_history", [])
            matched_item["updates_history"].append({
                "date": today_str,
                "update_notes": details
            })
            matched_item["current_status"] = details
            print(f"Updated Master KB Topic: [{paper} -> {unit}] {title}")
        else:
            # Insert new record
            new_entry = {
                "title": title,
                "created_at": today_str,
                "last_updated": today_str,
                "current_status": details,
                "keywords": keywords or [],
                "updates_history": [{
                    "date": today_str,
                    "update_notes": details
                }]
            }
            unit_list.append(new_entry)
            print(f"Added NEW Master KB Topic: [{paper} -> {unit}] {title}")

        self.save_kb()

    def get_all_topics(self):
        return self.data["topics"]

if __name__ == '__main__':
    kb = MasterNotesLibrary()
    kb.update_or_add_topic(
        "Paper 3",
        "Unit 2: लोक प्रशासन, राज्य प्रशासनिक ढांचा एवं आयोग/नियम",
        "राजस्थान राज्य मानव अधिकार आयोग (SHRC)",
        "अध्यक्ष एवं सदस्यों की नियुक्ति प्रक्रिया तथा अद्यतन नियम व क्षेत्राधिकार।",
        keywords=["मानव अधिकार", "SHRC", "आयोग"]
    )
    print("Master Notes Library Test Complete. Saved to:", kb.kb_path)
