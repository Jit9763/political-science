import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

CDP_URL = "http://127.0.0.1:9222"
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "telegram_extracted_posts.json")

def read_and_mark_read_telegram(cdp_url=CDP_URL, max_channels=15, max_messages_per_chat=10):
    print("==================================================================")
    print("🤖 Connecting to Active Telegram Web Session via DevTools (CDP)...")
    print(f"🔗 Target Port: {cdp_url}")
    print("==================================================================")

    extracted_data = []

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("Chrome must be running with --remote-debugging-port=9222")
            return []

        tg_page = None
        for ctx in browser.contexts:
            for page in ctx.pages:
                if "web.telegram.org" in page.url:
                    tg_page = page
                    break
            if tg_page:
                break

        if not tg_page:
            print("❌ Could not find open Telegram Web tab in Chrome!")
            return []

        print(f"✅ Found Telegram Web tab: {tg_page.title()} ({tg_page.url})")
        tg_page.bring_to_front()
        time.sleep(2)

        # Wait for chat list to be visible
        tg_page.wait_for_selector(".chat-list, .ListItem-button, #column-left", timeout=15000)

        # Find all chat items
        chat_elements = tg_page.query_selector_all(".ListItem-button, .chat-list-item")
        print(f"📋 Found {len(chat_elements)} chats/channels in sidebar!")

        found_channels = []
        for elem in chat_elements[:max_channels]:
            try:
                title_elem = elem.query_selector(".title, .ListItem-title, h3")
                badge_elem = elem.query_selector(".badge, .unread, .ChatBadge")
                title_text = title_elem.inner_text().strip() if title_elem else "Unknown"
                unread_count = badge_elem.inner_text().strip() if badge_elem else "0"
                found_channels.append({
                    "element": elem,
                    "title": title_text,
                    "unread": unread_count
                })
            except Exception:
                pass

        print(f"\n📑 Active Channels Detected:")
        for ch in found_channels:
            unread_str = f" [🔔 {ch['unread']} unread]" if ch['unread'] != '0' else ""
            print(f"  • {ch['title']}{unread_str}")

        # Click each channel to read and mark as read
        for ch in found_channels:
            elem = ch["element"]
            ch_title = ch["title"]
            try:
                print(f"\n🔍 Opening: {ch_title}...")
                elem.click()
                time.sleep(1.5)

                # Scroll to bottom to ensure "mark as read"
                tg_page.keyboard.press("End")
                time.sleep(1)

                # Extract latest message elements
                msg_elements = tg_page.query_selector_all(".message-content, .text-content, .bubble-content")
                chat_posts = []

                for m in msg_elements[-max_messages_per_chat:]:
                    txt = m.inner_text().strip()
                    if len(txt) > 15:
                        is_q = any(k in txt for k in ['?', 'Q.', 'प्रश्न', 'उ.', 'A)', 'B)', 'C)', 'D)', 'Option', 'क)', 'ख)', 'ग)', 'घ)'])
                        chat_posts.append({
                            "channel": ch_title,
                            "text": txt,
                            "is_question": is_q
                        })

                print(f"  📥 Extracted {len(chat_posts)} messages/questions (Marked as read ✅)")
                extracted_data.extend(chat_posts)

            except Exception as ce:
                print(f"  ⚠️ Error in channel {ch_title}: {ce}")

        # Save extracted posts
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)

        print(f"\n🎉 Successfully extracted {len(extracted_data)} total items from Telegram!")
        print(f"📁 Saved to: {OUTPUT_JSON}")
        return extracted_data

if __name__ == '__main__':
    read_and_mark_read_telegram()
