import os
import sys
import subprocess

def create_desktop_shortcut():
    desktop_dir = os.path.expanduser("~/Desktop")
    shortcut_path = os.path.join(desktop_dir, "Daily RAS UPSC AI Dashboard.lnk")
    target_script = "c:\\Users\\jiten\\Desktop\\class11\\political-science\\RPSC_UPSC_Daily_AI_Agent\\app_gui.py"
    work_dir = "c:\\Users\\jiten\\Desktop\\class11\\political-science\\RPSC_UPSC_Daily_AI_Agent"
    python_exe = sys.executable

    vbs_script = f'Set WshShell = CreateObject("WScript.Shell")\n' \
                 f'Set shortcut = WshShell.CreateShortcut("{shortcut_path}")\n' \
                 f'shortcut.TargetPath = "{python_exe}"\n' \
                 f'shortcut.Arguments = """{target_script}"""\n' \
                 f'shortcut.WorkingDirectory = "{work_dir}"\n' \
                 f'shortcut.WindowStyle = 1\n' \
                 f'shortcut.Description = "RPSC RAS & UPSC Daily News, Editorial & Master Notes AI Dashboard"\n' \
                 f'shortcut.Save\n'

    vbs_file = os.path.join(work_dir, "make_shortcut.vbs")
    with open(vbs_file, "w", encoding="utf-8") as f:
        f.write(vbs_script)

    try:
        subprocess.run(["cscript", "//Nologo", vbs_file], check=True)
        print(f"✅ Desktop Shortcut successfully created at:\n{shortcut_path}")
    except Exception as e:
        print(f"Error creating shortcut via VBScript: {e}")

if __name__ == '__main__':
    create_desktop_shortcut()
