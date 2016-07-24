import shutil
import os

u = os.path.expanduser("~")
assert u != "~"

extensions_path = os.path.join(u, ".ipython", "extensions",
                               "import_wrapper.py")
config_path = os.path.join(u, ".ipython", "profile_default",
                           "ipython_config.py")

shutil.copyfile("import-wrapper.py", extensions_path)

with open(config_path, "a") as f:
    f.write("\nc.InteractiveShellApp.exec_lines.append(\"%load_ext import-wra"
            "pper\")")