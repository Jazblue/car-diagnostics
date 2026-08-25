import os, sys
try:
    import win32com.client
    shell = win32com.client.Dispatch("WScript.Shell")
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop, "Car Diagnosis Web.lnk")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.TargetPath = "https://car-diagnostics-93uu0j8i6-jasonmariakierans-projects.vercel.app"
    shortcut.IconLocation = "shell32.dll,13"
    shortcut.save()
    print("Shortcut updated to:", shortcut.TargetPath)
except Exception as e:
    print("Error:", e)
