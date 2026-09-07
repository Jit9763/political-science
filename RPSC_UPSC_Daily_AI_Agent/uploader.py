import os
import shutil
import json
import glob
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

    def sync_from_drive(self, local_output_dir):
        """Sync files FROM Google Drive folder TO local Output_Notes folder when GUI opens."""
        if not os.path.exists(self.drive_folder):
            print(f"Drive folder does not exist yet: {self.drive_folder}")
            return 0

        os.makedirs(local_output_dir, exist_ok=True)
        synced_count = 0

        try:
            drive_files = glob.glob(os.path.join(self.drive_folder, "*.*"))
            for src in drive_files:
                fname = os.path.basename(src)
                if not (fname.endswith(".html") or fname.endswith(".docx") or fname.endswith(".md")):
                    continue

                dest = os.path.join(local_output_dir, fname)
                
                # Copy if dest doesn't exist or src is newer
                should_copy = False
                if not os.path.exists(dest):
                    should_copy = True
                else:
                    src_mtime = os.path.getmtime(src)
                    dest_mtime = os.path.getmtime(dest)
                    if src_mtime > dest_mtime + 2: # 2 sec buffer
                        should_copy = True

                if should_copy:
                    shutil.copy2(src, dest)
                    synced_count += 1
                    print(f"Synced FROM Google Drive to local Output_Notes: {fname}")

        except Exception as e:
            print(f"Error syncing from Drive to local: {e}")

        return synced_count

    def open_in_browser(self, html_filepath):
        """Open the HTML report in the user's default browser."""
        if os.path.exists(html_filepath):
            webbrowser.open(f"file:///{os.path.abspath(html_filepath)}")
            print(f"Opened report in web browser: {html_filepath}")

if __name__ == '__main__':
    uploader = DriveSyncUploader()
    print("Uploader ready. Target drive folder:", uploader.drive_folder)
    out_dir = os.path.join(os.path.dirname(__file__), "Output_Notes")
    count = uploader.sync_from_drive(out_dir)
    print(f"Test sync from Drive complete. {count} files synced.")
