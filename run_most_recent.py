import os
import subprocess

candidates = []
exclusions = [os.path.basename(__file__), "pyocct_system.py", "pyocct_api_wrappers.py", "pyocct_utils.py", "face_depthmap_loader.py", "gcode_stuff/gcode_utils.py", "single_wall_layer_optimizer.py", "svg_utils.py"]
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py") and file not in exclusions:
            candidates.append(os.path.join(root, file))

winner = max(candidates, key = os.path.getmtime)

if winner == __file__:
    print("avoiding infinite loop")
else:
    print(f"Running most recent: {winner}")
    subprocess.run(["python", winner])
