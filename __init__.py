import os
import sys


from adapters.certuk_mod.patch import hash_patch, inbox_patch, remap_patch, identity_patch, catalog_patch

hash_patch.apply_patch()
inbox_patch.apply_patch()
remap_patch.apply_patch()
identity_patch.apply_patch()
catalog_patch.apply_patch()


cur_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(cur_dir, "lib"))
sys.path.append(os.path.join(cur_dir, "lib", "PyPDF2"))
