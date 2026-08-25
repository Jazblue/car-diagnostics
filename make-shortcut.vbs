Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "C:\Users\Administrator\Desktop\Car Diagnosis.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "python.exe"
oLink.Arguments = "C:\Users\Administrator\Desktop\car-diagnosis\car_diagnosis.py"
oLink.WorkingDirectory = "C:\Users\Administrator\Desktop\car-diagnosis"
oLink.Description = "Car Diagnosis Program"
oLink.Save
WScript.Echo "Shortcut created"
