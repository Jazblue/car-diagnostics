import os
import sys

def create_shortcut():
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut_path = os.path.join(os.path.expanduser("~"), "Desktop", "Car Diagnosis.lnk")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = os.path.join(os.path.dirname(__file__), "car_diagnosis.py")
        shortcut.WorkingDirectory = os.path.dirname(__file__)
        shortcut.Description = "Car Diagnosis Program"
        shortcut.save()
        print(f"Shortcut created at: {shortcut_path}")
    except ImportError:
        print("win32com not available, creating .bat file instead")
        bat_path = os.path.join(os.path.expanduser("~"), "Desktop", "Car Diagnosis.bat")
        with open(bat_path, 'w') as f:
            f.write(f'@echo off\n"{sys.executable}" "{os.path.join(os.path.dirname(__file__), "car_diagnosis.py")}"\n')
        print(f"Batch launcher created at: {bat_path}")

if __name__ == "__main__":
    create_shortcut()
