r'''
use with
exec(open(r"C:\Users\Eli\Documents\eliduprees-3d-designs\freecad_autorun.py").read())
'''

from PyQt5 import QtCore
import os.path


def check_source():
  try:
    source_path = r"C:\Users\Eli\Documents\eliduprees-3d-designs\freecad_experiments.py"
    modified_time = None
    try:
      modified_time = os.path.getmtime (source_path)
    except OSError:
      pass
    
    if modified_time is not None:
      if "last_modified_time" not in globals() or modified_time > globals()["last_modified_time"]:
        globals()["last_modified_time"] = modified_time
        on_change(source_path)
  except Exception as e:
    import traceback
    App.Console.PrintError(traceback.format_exc())
    
def on_change(source_path):
  with open (source_path) as file:
    shared_globals = ['App', 'Log', 'Msg', 'Err', 'Wrn', 'traceback', 'FreeCADGui', 'Gui', 'Workbench', 'PathCommandGroup', 'WebGui', 'sys', 'Start', 'StartPage', 'WebPage', 'WebView', 'webView']
    exec (file.read(), {
      g: globals()[g] for g in shared_globals
    })

if "autorun_timer" in globals():
  autorun_timer.stop()
autorun_timer = QtCore.QTimer()
autorun_timer.timeout.connect (check_source)
autorun_timer.start(250)
