
from views.urls import urlpatterns, navitems

#ToDo move to somewhere else!

import sys, os
cur_dir = os.path.dirname(os.path.realpath(__file__))
pypdf_path = os.path.join(cur_dir, "lib", "PyPDF2")
sys.path.append(pypdf_path)
ioc_parser_path = os.path.join(cur_dir, "lib", "ioc_parser")
sys.path.append(ioc_parser_path)
