Set WshShell = CreateObject("WScript.Shell")
Set shortcut = WshShell.CreateShortcut("C:\Users\jiten/Desktop\Daily RAS UPSC AI Dashboard.lnk")
shortcut.TargetPath = "C:\Users\jiten\AppData\Local\Programs\Python\Python314\python.exe"
shortcut.Arguments = """c:\Users\jiten\Desktop\class11\political-science\RPSC_UPSC_Daily_AI_Agent\app_gui.py"""
shortcut.WorkingDirectory = "c:\Users\jiten\Desktop\class11\political-science\RPSC_UPSC_Daily_AI_Agent"
shortcut.WindowStyle = 1
shortcut.Description = "RPSC RAS & UPSC Daily News, Editorial & Master Notes AI Dashboard"
shortcut.Save
