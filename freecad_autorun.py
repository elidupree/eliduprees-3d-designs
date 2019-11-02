r'''
use with
eliduprees_3d_designs_path = r"C:\Users\Eli\Documents\eliduprees-3d-designs\"
exec(open(eliduprees_3d_designs_path+"freecad_autorun.py").read())
autorun(eliduprees_3d_designs_path+"freecad_experiments.py")

or
eliduprees_3d_designs_path = open("/n/elidupree-autobuild/share_prefix").read().strip() + "/eliduprees-3d-designs/"
exec(open(eliduprees_3d_designs_path+"freecad_autorun.py").read())
autorun(eliduprees_3d_designs_path+"freecad_experiments.py")

'''

def autorun(source_path):
 from PyQt5 import QtCore
 import os.path


 def check_source():
  try:
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
   globals()["autorun_timer"].stop()
 globals()["autorun_timer"] = QtCore.QTimer()
 globals()["autorun_timer"].timeout.connect (check_source)
 globals()["autorun_timer"].start(250)
