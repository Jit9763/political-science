# Class 11 Political Science Repository - Architecture & Brain Structure

## 📌 Repository Overview
This repository contains interactive, rich educational web notes for **Class 11 Political Science (NCERT Hindi Medium)**.

Each chapter is structured as a self-contained, copy-ready HTML master file (`copy_master_ch*.html`) with:
- Rich modern typography and styling.
- 1-click Google Docs formatted HTML copy button.
- 16:9 widescreen educational vector visual cards (`images/ch*/`).
- CBSE Board Exam Special Q&A blocks.
- Pure solid white backgrounds and clean Devanagari Hindi text labels on all visuals.

---

## 📁 Workspace Directory Structure

```
political-science/
├── copy_master_ch1.html to copy_master_ch15.html  # Chapter HTML master files (Class 12)
├── qa_master_ch1.html to qa_master_ch15.html      # Question-Answer master files (Class 12)
├── index.html                                    # Main portal / dashboard
├── images/                                        # Chapter visual assets (WebP format)
│   ├── ch1/ ... ch15/
├── scripts/
│   └── generate_educational_visuals.py            # Image generation automation script
└── BRAIN_STRUCTURE.md                             # Repository architecture and prompts guide
```

---

## 🎨 16:9 Educational Visual Generation Protocol

### Image Generation Script (`scripts/generate_educational_visuals.py`)
To generate new educational visual cards for any chapter using Google Gemini CDP automation:

```bash
# Ensure Chrome with CDP debugging is running at port 9222
# Run single prompt generation:
python scripts/generate_educational_visuals.py \
  --prompt "Generate an image: A 16:9 widescreen rich vibrant educational cartoon illustration..." \
  --output "images/ch11/visual_custom.webp"
```

### Visual Style Requirements:
1. **Aspect Ratio**: 16:9 widescreen vector visual card.
2. **Background**: Pure solid white background (zero dark backgrounds or device mockups).
3. **Typography**: Clean Devanagari Hindi labels inside rounded white badge rectangles.
4. **Art Style**: Minimalist, colorful 2D educational textbook vector cartoon illustration.
5. **No Generic Meta Labels**: Descriptions in HTML should be titled `ऐतिहासिक चित्र`, `मानचित्र विश्लेषण`, `विशेष विवरण`, `कूटनीतिक विश्लेषण`, etc.

---

## 🖼️ Chapter 11 Visual Cards Summary (31 Valid Images)

1. `article_51_box.webp` - अनुच्छेद 51 संवैधानिक निर्देश
2. `visual_foreign_policy_pillars.webp` - विदेश नीति के मूल स्तंभ
3. `bandung_conference.webp` - बांडुंग सम्मेलन 1955
4. `nehru_tightrope_cartoon.webp` - नेहरू गुटनिरपेक्षता संतुलन
5. `page_58_girl_cartoon.webp` - विदेश नीति शक्ति विश्लेषण
6. `visual_nam_principles.webp` - गुटनिरपेक्ष आंदोलन के 5 सिद्धांत
7. `soviet_friendship_treaty_cartoon.webp` - सोवियत-भारत मैत्री संबंध
8. `nehru_zhou_talks.webp` - नेहरू-झोउ एनलाई बातचीत 1954
9. `dalai_lama_escape.webp` - दलाई लामा का भारत आगमन 1959
10. `india_china_border_map.webp` - भारत-चीन सीमा विवाद मानचित्र
11. `china_intrusion_cartoon.webp` - 1962 चीन घुसपैठ व्यंग्य
12. `china_war_clippings.webp` - 1962 युद्ध समाचार पत्र क्लिप्स
13. `amul_bye_bye_cartoon.webp` - अमूल बाय-बाय कार्टून
14. `krishna_menon_stamp.webp` - वी.के. कृष्ण मेनन डाक टिकट
15. `haqeeqat_movie.webp` - हकीकत फिल्म पोस्ट
16. `visual_1947_kashmir_accession.webp` - 1947 कश्मीर विलय व सुरक्षा
17. `visual_india_pak_conflicts_map.webp` - भारत-पाक युद्ध एवं सीमा मानचित्र
18. `pak_war_1965_tank.webp` - 1965 भारत-पाक टैंक युद्ध
19. `jai_jawan_stamp.webp` - जय जवान डाक टिकट
20. `jai_kisan_stamp.webp` - जय किसान डाक टिकट
21. `emergency_1971_clipping.webp` - 1971 युद्ध आपातकाल समाचार पत्र
22. `instrument_of_surrender_1971.webp` - ढाका समर्पण 1971
23. `visual_tashkent_simla_agreements.webp` - ताशकंद एवं शिमला समझौते
24. `visual_1999_kargil_operation_vijay.webp` - 1999 कारगिल ऑपरेशन विजय
25. `visual_1974_pokhran1_smiling_buddha.webp` - 1974 पोखरण-I स्माइलिंग बुद्धा
26. `visual_nuclear_policy_nfu.webp` - भारत की परमाणु नीति नो फर्स्ट यूज़
27. `visual_india_ussr_relations.webp` - भारत-सोवियत (रूस) मैत्री संबंध
28. `visual_india_usa_relations.webp` - भारत-अमेरिका रणनीतिक साझेदारी
29. `visual_israel_palestine_policy.webp` - पश्चिम एशिया इज़राइल-फ़िलिस्तीन नीति
30. `visual_multipolar_foreign_policy.webp` - 21वीं सदी बहुध्रुवीय विदेश नीति
31. `visual_brics_g20_global_south.webp` - G20, BRICS व ग्लोबल साउथ नेतृत्व

---
*Maintained and structured for Class 11 Political Science Notes.*
