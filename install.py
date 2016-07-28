import shutil
import os

u = os.path.expanduser("~")
assert u != "~"

extensions_path = os.path.join(u, ".ipython", "extensions",
                               "autoimport.py")
config_path = os.path.join(u, ".ipython", "profile_default",
                           "autoimport.py")

shutil.copyfile("autoimport.py", extensions_path)

with open(config_path, "a") as f:
    f.write("\nget_config().InteractiveShellApp.exec_lines.append(\"%load_ext autoimport\")")

print("Installation complete.")
try:
	import colorama
except ImportError:
	print("NOTE: Install 'colorama' for best results: 'pip install colorama'")