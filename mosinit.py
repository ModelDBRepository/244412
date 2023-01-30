#moddir mod_files
from neuron import h, gui
exec(compile(open("run_GUI.py", "rb").read(), "run_GUI.py", 'exec'))
