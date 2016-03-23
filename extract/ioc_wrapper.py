from cybox.utils.idgen import  set_id_namespace as cybox_set_id_namespace
from cybox.utils.nsparser import Namespace
from edge import IDManager, LOCAL_ALIAS
from stix.utils import set_id_namespace

from ioc_parser.iocp import IOC_Parser

from StringIO import StringIO
import contextlib


@contextlib.contextmanager
def capture():
    import sys
    from cStringIO import StringIO
    oldout,olderr = sys.stdout, sys.stderr
    try:
        out=[StringIO(), StringIO()]
        sys.stdout,sys.stderr = out
        yield out
    finally:
        sys.stdout,sys.stderr = oldout, olderr
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()


def parse_file(file_to_parse):
    NAMESPACE = {IDManager().get_namespace() : LOCAL_ALIAS}
    set_id_namespace(NAMESPACE)
    cybox_set_id_namespace(Namespace(IDManager().get_namespace(), LOCAL_ALIAS))

    parser = IOC_Parser(None, 'pdf', True, "pypdf2", "stix")
    with capture() as out:
        parser.parse_pdf_pypdf2(file_to_parse, file_to_parse._name)
        res = StringIO(out[0].getvalue())
    print res.buf
    return res
