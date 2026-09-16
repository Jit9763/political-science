import os
import glob
import json
import webbrowser
import threading
from datetime import datetime, timezone, timedelta
import customtkinter as ctk

from main_agent import run_agent
from master_library import MasterNotesLibrary
from uploader import DriveSyncUploader

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

IST = timezone(timedelta(hours=5, minutes=30))

class RASNotesGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RPSC RAS & UPSC Daily News, Editorial & Master Notes AI Dashboard")
        self.geometry("1100x700")

        self.output_dir = os.path.join(os.path.dirname(__file__), "Output_Notes")
        self.config_path = os.path.join(os.path.dirname(__file__), "config.json")
        self.master_kb = MasterNotesLibrary()
        self.uploader = DriveSyncUploader()

        # Grid configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Build UI
        self.create_sidebar()
        self.create_main_tabs()
        
        # Initial Drive Sync when GUI opens
        self.sync_from_drive_quiet()
        self.refresh_notes_list()

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        # App Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="🏛️ RPSC RAS & UPSC\nAI Agent Dashboard", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 15))

        # Drive Sync Button (Hybrid Cloud VM Sync)
        self.btn_sync_drive = ctk.CTkButton(
            self.sidebar_frame,
            text="☁️ गूगल ड्राइव से सिंक करें",
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.on_sync_drive
        )
        self.btn_sync_drive.grid(row=1, column=0, padx=20, pady=8)

        # Action Buttons
        self.btn_gen_today = ctk.CTkButton(
            self.sidebar_frame, 
            text="⚡ आज के नोट्स बनाएं", 
            fg_color="#0f766e", 
            hover_color="#0d9488",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.on_generate_today
        )
        self.btn_gen_today.grid(row=2, column=0, padx=20, pady=10)

        # YouTube URL Field
        self.lbl_yt = ctk.CTkLabel(self.sidebar_frame, text="📺 यूट्यूब क्लास लिंक (Optional):", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_yt.grid(row=3, column=0, padx=20, pady=(5, 2))

        self.entry_yt_url = ctk.CTkEntry(self.sidebar_frame, width=180, placeholder_text="YouTube URL / Live Link")
        self.entry_yt_url.grid(row=4, column=0, padx=20, pady=(0, 10))
        self.entry_yt_url.insert(0, "https://www.youtube.com/@NirmanIAS")

        # Tab Navigation Buttons
        self.btn_tab_daily = ctk.CTkButton(
            self.sidebar_frame, text="📄 दैनिक नोट्स इतिहास", command=lambda: self.tab_view.set("Daily Notes")
        )
        self.btn_tab_daily.grid(row=5, column=0, padx=20, pady=6)

        self.btn_tab_custom = ctk.CTkButton(
            self.sidebar_frame, text="🗓️ तिथि अनुसार नोट्स", command=lambda: self.tab_view.set("Custom Date")
        )
        self.btn_tab_custom.grid(row=6, column=0, padx=20, pady=6)

        self.btn_tab_master = ctk.CTkButton(
            self.sidebar_frame, text="📚 मास्टर नोट्स (Syllabus)", command=lambda: self.tab_view.set("Master Library")
        )
        self.btn_tab_master.grid(row=7, column=0, padx=20, pady=6)

        self.btn_open_wiki = ctk.CTkButton(
            self.sidebar_frame, 
            text="🌐 4 पेपर सिलेबस विकी खोलें", 
            fg_color="#7c3aed",
            hover_color="#6d28d9",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.open_master_wiki_browser
        )
        self.btn_open_wiki.grid(row=8, column=0, padx=20, pady=6)

        self.btn_tab_telegram = ctk.CTkButton(
            self.sidebar_frame, text="📲 टेलीग्राम चैनल्स", command=lambda: self.tab_view.set("Telegram")
        )
        self.btn_tab_telegram.grid(row=9, column=0, padx=20, pady=6)

        self.btn_tab_settings = ctk.CTkButton(
            self.sidebar_frame, text="⚙️ सेटिंग्स (Engine/Drive)", command=lambda: self.tab_view.set("Settings")
        )
        self.btn_tab_settings.grid(row=10, column=0, padx=20, pady=6)

        # Status Label
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="रेडी (Ready)", text_color="#10b981", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=11, column=0, padx=20, pady=10)

    def sync_from_drive_quiet(self):
        """Automatically fetch any missing notes from cloud VM & Google Drive folder on launch."""
        try:
            synced = self.uploader.sync_from_cloud(self.output_dir)
            if synced > 0:
                self.status_label.configure(text=f"☁️ क्लाउड/ड्राइव से {synced} नए नोट्स सिंक हुए!", text_color="#3b82f6")
        except Exception as e:
            print(f"Quiet cloud/drive sync notice: {e}")

    def on_sync_drive(self):
        """Manual trigger to fetch notes from Cloud VM and Google Drive folder."""
        self.status_label.configure(text="☁️ क्लाउड व गूगल ड्राइव से नोट्स सिंक हो रहे हैं...", text_color="#3b82f6")
        synced = self.uploader.sync_from_cloud(self.output_dir)
        self.refresh_notes_list()
        self.refresh_master_library_view()
        if synced > 0:
            self.status_label.configure(text=f"✅ सफलतापूर्वक {synced} नोट्स सिंक हुए!", text_color="#10b981")
        else:
            self.status_label.configure(text="✅ नोट्स पूर्णतया अप-टू-डेट हैं!", text_color="#10b981")

    def open_master_wiki_browser(self):
        wiki_path = os.path.join(self.output_dir, "Master_Syllabus_Wiki.html")
        if os.path.exists(wiki_path):
            webbrowser.open(f"file:///{os.path.abspath(wiki_path)}")
        else:
            self.status_label.configure(text="मास्टर विकी अभी बनी नहीं है, आज के नोट्स बनाएं।", text_color="#ef4444")

    def create_main_tabs(self):
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

        # Tab 1: Daily Notes History
        self.tab_daily = self.tab_view.add("Daily Notes")
        self.setup_daily_notes_tab()

        # Tab 2: Custom Date Generator
        self.tab_custom = self.tab_view.add("Custom Date")
        self.setup_custom_date_tab()

        # Tab 3: Master Notes Library
        self.tab_master = self.tab_view.add("Master Library")
        self.setup_master_library_tab()

        # Tab 4: Telegram Channels
        self.tab_telegram = self.tab_view.add("Telegram")
        self.setup_telegram_tab()

        # Tab 5: Settings
        self.tab_settings = self.tab_view.add("Settings")
        self.setup_settings_tab()

    def setup_daily_notes_tab(self):
        self.lbl_history = ctk.CTkLabel(self.tab_daily, text="📋 जनरेट / ड्राइव से सिंक किए गए दैनिक नोट्स की सूची", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_history.pack(anchor="w", padx=10, pady=10)

        self.notes_scroll = ctk.CTkScrollableFrame(self.tab_daily, width=800, height=450)
        self.notes_scroll.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_custom_date_tab(self):
        now_str = datetime.now(IST).strftime('%Y-%m-%d')
        lbl = ctk.CTkLabel(self.tab_custom, text="🗓️ किसी विशेष तारीख के नोट्स बनाएं (Custom Date)", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(anchor="w", padx=20, pady=15)

        sub_lbl = ctk.CTkLabel(self.tab_custom, text="तारीख दर्ज करें (फॉर्मेट: YYYY-MM-DD):")
        sub_lbl.pack(anchor="w", padx=20, pady=5)

        self.entry_date = ctk.CTkEntry(self.tab_custom, width=250, placeholder_text=now_str)
        self.entry_date.pack(anchor="w", padx=20, pady=5)
        self.entry_date.insert(0, now_str)

        btn_generate_custom = ctk.CTkButton(
            self.tab_custom, 
            text="🚀 चुने गए दिन के RAS Pre & Mains नोट्स जनरेट करें",
            fg_color="#4f46e5",
            hover_color="#4338ca",
            command=self.on_generate_custom
        )
        btn_generate_custom.pack(anchor="w", padx=20, pady=20)

    def setup_master_library_tab(self):
        lbl = ctk.CTkLabel(self.tab_master, text="📚 RAS सिलेबस अनुसार मास्टर नोट्स लाइब्रेरी (Wiki)", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(anchor="w", padx=10, pady=10)

        self.master_scroll = ctk.CTkScrollableFrame(self.tab_master, width=800, height=500)
        self.master_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_master_library_view()

    def setup_telegram_tab(self):
        lbl = ctk.CTkLabel(self.tab_telegram, text="📲 टेलीग्राम चैनल्स एवं दैनिक प्रश्न/क्विज़", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(anchor="w", padx=20, pady=(15, 5))

        desc = ctk.CTkLabel(self.tab_telegram, text="अपने पसंदीदा टेलीग्राम स्टडी चैनल्स (@username या लिंक) यहाँ जोड़ें। AI इनके रोज़ाना के प्रश्न व नोट्स स्वतः फेच करेगा।", text_color="#94a3b8")
        desc.pack(anchor="w", padx=20, pady=(0, 10))

        add_frame = ctk.CTkFrame(self.tab_telegram)
        add_frame.pack(fill="x", padx=20, pady=5)

        self.entry_new_channel = ctk.CTkEntry(add_frame, width=320, placeholder_text="उदा: @currentaffairs या DrishtiIAS")
        self.entry_new_channel.pack(side="left", padx=10, pady=10)

        btn_add = ctk.CTkButton(add_frame, text="➕ चैनल जोड़ें", fg_color="#0f766e", hover_color="#0d9488", command=self.add_telegram_channel)
        btn_add.pack(side="left", padx=10, pady=10)

        btn_open_bank = ctk.CTkButton(add_frame, text="📖 5-माह का मास्टर क्वेश्चन बैंक", fg_color="#2563eb", hover_color="#1d4ed8", command=self.open_master_question_bank)
        btn_open_bank.pack(side="left", padx=10, pady=10)

        self.tg_channels_scroll = ctk.CTkScrollableFrame(self.tab_telegram, width=800, height=350)
        self.tg_channels_scroll.pack(fill="both", expand=True, padx=20, pady=10)

        self.refresh_telegram_channels_list()

    def refresh_telegram_channels_list(self):
        for widget in self.tg_channels_scroll.winfo_children():
            widget.destroy()

        channels = []
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    channels = json.load(f).get("telegram_channels", [])
            except Exception:
                pass

        if not channels:
            empty_lbl = ctk.CTkLabel(self.tg_channels_scroll, text="अभी तक कोई टेलीग्राम चैनल नहीं जोड़ा गया है। ऊपर इनपुट बॉक्स में चैनल का नाम डालें।", text_color="#94a3b8")
            empty_lbl.pack(padx=20, pady=20)
            return

        for ch in channels:
            row = ctk.CTkFrame(self.tg_channels_scroll)
            row.pack(fill="x", padx=5, pady=4)

            lbl = ctk.CTkLabel(row, text=f"📢 @{ch.lstrip('@')}", font=ctk.CTkFont(size=14, weight="bold"))
            lbl.pack(side="left", padx=15, pady=8)

            btn_del = ctk.CTkButton(row, text="❌ हटाएं", width=80, fg_color="#ef4444", hover_color="#dc2626", command=lambda c=ch: self.remove_telegram_channel(c))
            btn_del.pack(side="right", padx=10, pady=8)

    def add_telegram_channel(self):
        val = self.entry_new_channel.get().strip().lstrip('@')
        if 't.me/' in val:
            val = val.split('t.me/')[-1].split('/')[0]
        if not val:
            return

        try:
            cfg = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            ch_list = cfg.get("telegram_channels", [])
            if val not in ch_list:
                ch_list.append(val)
                cfg["telegram_channels"] = ch_list
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, ensure_ascii=False, indent=2)
                self.entry_new_channel.delete(0, "end")
                self.refresh_telegram_channels_list()
                self.status_label.configure(text=f"चैनल @{val} जुड़ गया!", text_color="#10b981")
        except Exception as e:
            self.status_label.configure(text=f"एरर: {e}", text_color="#ef4444")

    def remove_telegram_channel(self, channel_name):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                ch_list = cfg.get("telegram_channels", [])
                if channel_name in ch_list:
                    ch_list.remove(channel_name)
                    cfg["telegram_channels"] = ch_list
                    with open(self.config_path, "w", encoding="utf-8") as f:
                        json.dump(cfg, f, ensure_ascii=False, indent=2)
                    self.refresh_telegram_channels_list()
                    self.status_label.configure(text=f"चैनल हटाया गया", text_color="#f59e0b")
        except Exception as e:
            self.status_label.configure(text=f"एरर: {e}", text_color="#ef4444")

    def open_master_question_bank(self):
        import webbrowser
        bank_path = os.path.join(os.path.dirname(__file__), "Output_Notes", "Rajasthan_5_Months_Telegram_Master_Question_Bank.html")
        if os.path.exists(bank_path):
            webbrowser.open(f"file:///{bank_path.replace(os.sep, '/')}")
            self.status_label.configure(text="5-माह का मास्टर क्वेश्चन बैंक ब्राउज़र में खोला गया!", text_color="#10b981")
        else:
            self.status_label.configure(text="मास्टर क्वेश्चन बैंक फ़ाइल नहीं मिली", text_color="#ef4444")

    def setup_settings_tab(self):
        lbl = ctk.CTkLabel(self.tab_settings, text="⚙️ सिस्टम एवं AI इंजन सेटिंग्स", font=ctk.CTkFont(size=16, weight="bold"))
        lbl.pack(anchor="w", padx=20, pady=15)

        # API Key
        lbl_key = ctk.CTkLabel(self.tab_settings, text="Gemini API Key:")
        lbl_key.pack(anchor="w", padx=20, pady=5)
        
        self.entry_api_key = ctk.CTkEntry(self.tab_settings, width=450, show="*")
        self.entry_api_key.pack(anchor="w", padx=20, pady=5)

        # Google Drive Folder Path
        lbl_drive = ctk.CTkLabel(self.tab_settings, text="गूगल ड्राइव लोकल फोल्डर पाथ (Google Drive Folder):")
        lbl_drive.pack(anchor="w", padx=20, pady=5)
        
        self.entry_drive_path = ctk.CTkEntry(self.tab_settings, width=450)
        self.entry_drive_path.pack(anchor="w", padx=20, pady=5)
        self.entry_drive_path.insert(0, self.uploader.drive_folder)

        # Preferred Engine
        lbl_eng = ctk.CTkLabel(self.tab_settings, text="पसंदीदा AI इंजन:")
        lbl_eng.pack(anchor="w", padx=20, pady=5)
        
        self.combo_engine = ctk.CTkComboBox(self.tab_settings, values=["gemini", "ollama"])
        self.combo_engine.pack(anchor="w", padx=20, pady=5)

        # Save Button
        btn_save = ctk.CTkButton(self.tab_settings, text="💾 सेटिंग्स सेव करें", command=self.save_settings)
        btn_save.pack(anchor="w", padx=20, pady=20)

        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.entry_api_key.insert(0, cfg.get("gemini_api_key", ""))
                    self.combo_engine.set(cfg.get("preferred_engine", "gemini"))
                    drive_p = cfg.get("google_drive_folder", "")
                    if drive_p:
                        self.entry_drive_path.delete(0, "end")
                        self.entry_drive_path.insert(0, drive_p)
            except Exception as e:
                print(f"Error loading settings GUI: {e}")

    def save_settings(self):
        try:
            cfg = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            
            cfg["gemini_api_key"] = self.entry_api_key.get().strip()
            cfg["preferred_engine"] = self.combo_engine.get()
            cfg["google_drive_folder"] = self.entry_drive_path.get().strip()

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            
            self.uploader.load_config()
            self.status_label.configure(text="सेटिंग्स सेव हो गईं!", text_color="#10b981")
        except Exception as e:
            self.status_label.configure(text=f"एरर: {e}", text_color="#ef4444")

    def refresh_notes_list(self):
        for widget in self.notes_scroll.winfo_children():
            widget.destroy()

        files = sorted(glob.glob(os.path.join(self.output_dir, "*.html")), reverse=True)
        if not files:
            lbl = ctk.CTkLabel(self.notes_scroll, text="कोई पूर्व नोट्स उपलब्ध नहीं हैं। 'आज के नोट्स बनाएं' या 'गूगल ड्राइव से सिंक करें' पर क्लिक करें।")
            lbl.pack(padx=20, pady=20)
            return

        for fpath in files:
            fname = os.path.basename(fpath)
            row_frame = ctk.CTkFrame(self.notes_scroll)
            row_frame.pack(fill="x", padx=5, pady=5)

            lbl_file = ctk.CTkLabel(row_frame, text=f"📄 {fname}", font=ctk.CTkFont(size=14, weight="bold"))
            lbl_file.pack(side="left", padx=15, pady=10)

            btn_open = ctk.CTkButton(
                row_frame, 
                text="📖 खोलें और पढ़ें", 
                width=120,
                command=lambda p=fpath: webbrowser.open(f"file:///{os.path.abspath(p)}")
            )
            btn_open.pack(side="right", padx=15, pady=10)

    def refresh_master_library_view(self):
        for widget in self.master_scroll.winfo_children():
            widget.destroy()

        self.master_kb = MasterNotesLibrary()
        topics = self.master_kb.get_all_topics()

        for paper, units in topics.items():
            paper_lbl = ctk.CTkLabel(self.master_scroll, text=f"📘 {paper}", font=ctk.CTkFont(size=16, weight="bold"), text_color="#3b82f6")
            paper_lbl.pack(anchor="w", padx=10, pady=(15, 5))

            for unit_name, items in units.items():
                unit_lbl = ctk.CTkLabel(self.master_scroll, text=f"   • {unit_name}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#0f766e")
                unit_lbl.pack(anchor="w", padx=15, pady=3)

                if not items:
                    empty_lbl = ctk.CTkLabel(self.master_scroll, text="      [अभी तक कोई अपडेट नहीं]", text_color="#94a3b8", font=ctk.CTkFont(size=12))
                    empty_lbl.pack(anchor="w", padx=25, pady=2)

                for item in items:
                    card = ctk.CTkFrame(self.master_scroll)
                    card.pack(fill="x", padx=30, pady=4)

                    t_lbl = ctk.CTkLabel(card, text=f"📌 {item.get('title', '')} (अद्यतन: {item.get('last_updated', '')})", font=ctk.CTkFont(size=13, weight="bold"))
                    t_lbl.pack(anchor="w", padx=10, pady=(6, 2))

                    d_lbl = ctk.CTkLabel(card, text=item.get('current_status', ''), wraplength=700, justify="left")
                    d_lbl.pack(anchor="w", padx=10, pady=(0, 6))

    def on_generate_today(self):
        yt_url = self.entry_yt_url.get().strip()
        self.status_label.configure(text="प्रोसेसिंग... खबरों व यूट्यूब का विश्लेषण...", text_color="#f59e0b")
        threading.Thread(target=self._run_generation, args=(None, yt_url)).start()

    def on_generate_custom(self):
        custom_date = self.entry_date.get().strip()
        yt_url = self.entry_yt_url.get().strip()
        self.status_label.configure(text=f"{custom_date} के नोट्स बन रहे हैं...", text_color="#f59e0b")
        threading.Thread(target=self._run_generation, args=(custom_date, yt_url)).start()

    def _run_generation(self, target_date, youtube_url=None):
        try:
            run_agent(target_date=target_date, youtube_url=youtube_url, auto_open=True)
            self.after(0, self._on_generation_success)
        except Exception as e:
            self.after(0, lambda: self._on_generation_error(str(e)))

    def _on_generation_success(self):
        self.status_label.configure(text="✅ नोट्स सफलतापूर्वक जनरेट हो गए!", text_color="#10b981")
        self.refresh_notes_list()
        self.refresh_master_library_view()

    def _on_generation_error(self, err):
        self.status_label.configure(text=f"❌ त्रुटि: {err[:40]}...", text_color="#ef4444")

if __name__ == '__main__':
    app = RASNotesGUI()
    app.mainloop()
