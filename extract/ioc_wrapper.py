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

class IOCParseException(Exception):
    pass


def parse_as_type(file_to_parse, parse_func_name):
    parser = IOC_Parser(None, "txt", True, "pypdf2", "stix")
    with capture() as out:
        parser_func = getattr(parser, parse_func_name)
        parser_func(file_to_parse, file_to_parse._name)
        result = StringIO(out[0].getvalue())
        error = StringIO(out[1].getvalue())

        if error.buf:
            raise IOCParseException(error.buf)
    return result


def parse_file(file_to_parse):
    set_id_namespace({IDManager().get_namespace(): LOCAL_ALIAS})
    cybox_set_id_namespace(Namespace(IDManager().get_namespace(), LOCAL_ALIAS))

    parse_func = 'parse_txt'
    if 'pdf' in file_to_parse.content_type:
        parse_func = 'parse_pdf_pypdf2'

    return parse_as_type(file_to_parse, parse_func)
