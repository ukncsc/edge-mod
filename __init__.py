import sys, os
from adapters.certuk_mod.patch import remap_patch
remap_patch.apply_patch()

cur_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(cur_dir, "lib"))
sys.path.append(os.path.join(cur_dir, "lib", "PyPDF2"))
sys.path.append(os.path.join(cur_dir, "lib", "ioc_parser"))

