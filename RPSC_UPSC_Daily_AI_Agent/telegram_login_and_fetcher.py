import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

USER_DATA_DIR = os.path.join(os.path.dirname(__file__), "telegram_browser_profile")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def open_telegram_for_qr_login():
    """Launch Chrome with persistent user profile so user can scan QR code once."""
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    print("==================================================================")
    print("📱 Telegram Web QR Code Login Launcher")
    print(f"📁 Session Profile Directory: {USER_DATA_DIR}")
    print("==================================================================")
    print("1. Chrome विन्डो खुलेगी और Telegram Web QR Code लोड होगा।")
    print("2. अपने मोबाइल में Telegram खोलें -> Settings -> Devices -> Link Desktop Device")
    print("3. स्क्रीन पर दिख रहे QR Code को मोबाइल कैमरे से स्कैन करें।")
    print("4. लॉगिन होते ही यह सेशन हमेशा के लिए सेव हो जाएगा!")
    print("==================================================================")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            executable_path=CHROME_PATH if os.path.exists(CHROME_PATH) else None,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-default-browser-check",
                "--start-maximized"
            ],
            viewport=None
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://web.telegram.org/a/", wait_until="load")
        
        print("\n⏳ प्रतीक्षा कर रहे हैं... कृपया अपने मोबाइल से QR कोड स्कैन करें।")
        print("(लॉगिन होने के बाद स्क्रीन पर आपकी चैट लिस्ट दिखने लगेगी...)")

        # Wait until user logs in (chat list appears)
        logged_in = False
        for i in range(120): # wait up to 4 minutes
            time.sleep(2)
            chat_list = page.query_selector(".chat-list, .ListItem-button, #column-left")
            if chat_list:
                logged_in = True
                print("\n🎉 बधाई हो! Telegram Web सफलतापूर्वक लॉगिन हो गया है!")
                break
        
        if logged_in:
            time.sleep(3)
            # Find joined chats/channels
            chats = page.query_selector_all(".ListItem-button, .chat-list-item")
            print(f"📊 कुल मिली हुई चैट्स/ग्रुप्स: {len(chats)}")
            context.close()
            return True
        else:
            print("\n⚠️ समय समाप्त (Timeout) या अभी लॉगिन पूरा नहीं हुआ। आप दोबारा चला सकते हैं।")
            context.close()
            return False

if __name__ == '__main__':
    open_telegram_for_qr_login()
