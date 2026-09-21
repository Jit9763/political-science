Set WshShell = CreateObject("WScript.Shell")
Set shortcut = WshShell.CreateShortcut("C:\Users\jiten/Desktop\Daily RAS UPSC AI Dashboard.lnk")
shortcut.TargetPath = "c:\Users\jiten\Desktop\class11\political-science\RPSC_UPSC_Daily_AI_Agent\Launch_Dashboard.bat"
shortcut.Arguments = ""
shortcut.WorkingDirectory = "c:\Users\jiten\Desktop\class11\political-science\RPSC_UPSC_Daily_AI_Agent"
shortcut.WindowStyle = 7
shortcut.Description = "RPSC RAS & UPSC Daily News, Editorial & Master Notes AI Dashboard"
shortcut.Save
