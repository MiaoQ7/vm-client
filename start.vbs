Set WshShell = CreateObject("WScript.Shell")
cmds = "cmd /c python app.py --type=pycl --name=001"
WshShell.Run cmds, 0, True