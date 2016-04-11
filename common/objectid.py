import re
import urllib2

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

# {STIX/ID Alias}:{type}-{GUID}
_STIX_ID_REGEX = r"[a-z][\w\d-]+:[a-z]+-[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12}"
_OBJECT_ID_MATCHER = re.compile("%s$" % _STIX_ID_REGEX, re.IGNORECASE)
_URL_OBJECT_ID_MATCHER = re.compile(r".*/(%s)/?$" % _STIX_ID_REGEX, re.IGNORECASE)


def is_valid_stix_id(candidate_stix_id):
    match = _OBJECT_ID_MATCHER.match(candidate_stix_id)
    return match is not None


def find_id(request):
    """
        Discovers a STIX id from the request's referrer.

    Args:
        request (HttpRequest): the request to inspect

    Returns:
        string: A STIX id
    """
    def has_single_match(match_result):
        return match_result is not None and len(match_result.groups()) == 1
    referrer = urllib2.unquote(request.META.get("HTTP_REFERER", ""))
    match = _URL_OBJECT_ID_MATCHER.match(referrer)
    id_ = None
    if has_single_match(match):
        id_ = match.group(1)
    return id_


def discover(request, matched_to, failed_to):
    """
        Discovers a STIX id from the request's referrer, returning an appropriate redirect response.

    Args:
        request (HttpRequest): the request to inspect
        matched_to (Any): model, view name or url redirected to if discovery is successful. `id_` contains the STIX id
        failed_to (Any): model, view name or url redirected to if discovery fails

    Returns:
        HttpResponse: A redirect response
    """
    id_ = find_id(request)
    if id_:
        response = redirect(matched_to, id_=id_)
    else:
        response = redirect(failed_to)
    return response
