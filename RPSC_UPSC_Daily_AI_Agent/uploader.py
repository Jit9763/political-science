import os
import shutil
import json
import webbrowser

class DriveSyncUploader:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        self.config_path = config_path
        self.drive_folder = os.path.expanduser("~/Desktop/Google_Drive_RAS_UPSC_Notes")
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.drive_folder = cfg.get("google_drive_folder", self.drive_folder)
            except Exception as e:
                print(f"Warning loading uploader config: {e}")

    def sync_to_drive(self, filepath):
        """Copy generated report file to Google Drive directory."""
        if not filepath or not os.path.exists(filepath):
            print(f"Error: File does not exist for drive sync: {filepath}")
            return False

        try:
            os.makedirs(self.drive_folder, exist_ok=True)
            filename = os.path.basename(filepath)
            dest_path = os.path.join(self.drive_folder, filename)
            shutil.copy2(filepath, dest_path)
            print(f"Synced file to Google Drive Folder: {dest_path}")
            
            # Also sync Master Syllabus Wiki HTML if present
            wiki_local = os.path.join(os.path.dirname(filepath), "Master_Syllabus_Wiki.html")
            if os.path.exists(wiki_local):
                wiki_dest = os.path.join(self.drive_folder, "Master_Syllabus_Wiki.html")
                shutil.copy2(wiki_local, wiki_dest)
                print(f"Synced Master Syllabus Wiki to Google Drive Folder: {wiki_dest}")

            return dest_path
        except Exception as e:
            print(f"Error syncing to Drive folder ({self.drive_folder}): {e}")
            return False

    def open_in_browser(self, html_filepath):
        """Open the HTML report in the user's default browser."""
        if os.path.exists(html_filepath):
            webbrowser.open(f"file:///{os.path.abspath(html_filepath)}")
            print(f"Opened report in web browser: {html_filepath}")

if __name__ == '__main__':
    uploader = DriveSyncUploader()
    print("Uploader ready. Target drive folder:", uploader.drive_folder)
