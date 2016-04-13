from StringIO import StringIO
from cStringIO import StringIO as cStringIO
import contextlib
import sys

from cybox.utils.idgen import set_id_namespace as cybox_set_id_namespace
from cybox.utils.nsparser import Namespace
from edge import IDManager, LOCAL_ALIAS
from stix.utils import set_id_namespace
from ioc_parser.iocp import IOC_Parser


@contextlib.contextmanager
def capture():
    old_out, old_err = sys.stdout, sys.stderr
    try:
        out = [cStringIO(), cStringIO()]
        sys.stdout, sys.stderr = out
        yield out
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class IOCParseException(Exception):
    pass


def parse_using_func(file_to_parse, parse_func_name):
    parser = IOC_Parser(None, "txt", True, "pypdf2", "stix")
    with capture() as out:
        parser_func = getattr(parser, parse_func_name)
        parser_func(file_to_parse, file_to_parse._name)
        result = StringIO(out[0].getvalue())
    return result


def parse_file(file_to_parse):
    set_id_namespace({IDManager().get_namespace(): LOCAL_ALIAS})
    cybox_set_id_namespace(Namespace(IDManager().get_namespace(), LOCAL_ALIAS))

    parse_func = 'parse_txt'
    if 'pdf' in file_to_parse.content_type:
        parse_func = 'parse_pdf_pypdf2'

    try:
        return parse_using_func(file_to_parse, parse_func)
    except Exception as e:
        raise (IOCParseException(e.message))
