import os
import sys
import subprocess

def setup_task_scheduler():
    python_exe = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto_daily_runner.py")
    task_name = "Daily_RAS_UPSC_Notes_12PM"

    task_run_cmd = f'"{python_exe}" "{script_path}"'
    print(f"Configuring Windows Task Scheduler for: {task_name}")
    print(f"Task Command: {task_run_cmd}")

    cmd = [
        "schtasks", "/Create",
        "/SC", "DAILY",
        "/TN", task_name,
        "/TR", task_run_cmd,
        "/ST", "12:00",
        "/F"
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    print("STDOUT:", res.stdout)
    print("STDERR:", res.stderr)
    print("Return code:", res.returncode)

    if res.returncode == 0:
        print("✅ Task successfully registered with Windows Task Scheduler!")
    else:
        print("❌ Error registering task.")

if __name__ == '__main__':
    setup_task_scheduler()
