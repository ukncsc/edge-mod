#!/usr/bin/env python
import uuid
import os
import re
import sys

_UUID_REGEX = r"[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}"


def main(*args):
    file_path = args[0][0]
    file_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_contents = open(file_path, 'r').read()

    for i in xrange(1000):
        ids = {}

        def generate(m):
            id_ = m.group(0)
            if id_ not in ids:
                ids[id_] = str(uuid.uuid4())
            return ids[id_]

        str_out = re.sub(_UUID_REGEX, generate, file_contents)
        new_file_name = os.path.splitext(file_name)[0] + str(uuid.uuid4()) + os.path.splitext(file_name)[1]
        open(os.path.join(file_dir, new_file_name), 'w').write(str_out)


# stix_xml_duplicator full_path_to_stix.xml
if __name__ == '__main__':
    main(sys.argv[1:])
