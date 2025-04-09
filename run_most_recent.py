import os
import subprocess
import time

candidates = []
exclusions = [os.path.basename(__file__), "pyocct_system.py", "pyocct_api_wrappers.py", "pyocct_utils.py", "face_depthmap_loader.py", "gcode_stuff/gcode_utils.py", "single_wall_layer_optimizer.py", "svg_utils.py", "unroll.py", "depthmap.py", "gcode_utils.py", "spiral_printing.py", "code_generation.py", "gears.py", "thread_sweeping.py", "t_slots.py"]
# suppressions = ["gcode_direct_test.py"]
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py") and file not in exclusions:
            candidates.append(os.path.join(root, file))

winner = max(candidates, key = os.path.getmtime)

if winner == __file__:
    print("avoiding infinite loop")
else:
    if os.path.getmtime(winner) > time.time() - 2*60*60:
    # if "live_printer_control" in winner:
    #     print(f"Not running {winner} because it was explicitly suppressed")
    # else:
        print(f"Running most recent: {winner}")
        subprocess.run(["python", winner])
    else:
        # avoid the case of "jump into editing one of the excluded files when you are not even thinking of the project that you touched last"
        print(f"Not running {winner} because it wasn't edited in the last 2 hours")
