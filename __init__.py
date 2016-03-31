from adapters.certuk_mod.patch import remap_patch
remap_patch.apply_patch()

#ToDo should I need this?

import sys, os
cur_dir = os.path.dirname(os.path.realpath(__file__))

lib_path = os.path.join(cur_dir, "lib")
sys.path.append(lib_path)

pypdf_path = os.path.join(cur_dir, "lib", "PyPDF2")
sys.path.append(pypdf_path)

ioc_parser_path = os.path.join(cur_dir, "lib", "ioc_parser")
sys.path.append(ioc_parser_path)

