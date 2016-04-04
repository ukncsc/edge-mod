import re
import urllib2

from django.http import HttpRequest
from django.shortcuts import redirect

_OBJECT_ID_MATCHER = re.compile(
    # {STIX/ID Alias}:{type}-{GUID}
    r".*/([a-z][\w\d-]+:[a-z]+-[a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12})/?$",
    re.IGNORECASE  # | re.DEBUG
)


def discover(request, matched_to, failed_to):
    """
        Discovers a STIX id from the request's referrer.

    Args:
        request (HttpRequest): the request to inspect
        matched_to (Any): model, view name or url redirected to if discovery is successful. `id_` contains the STIX id
        failed_to (Any): model, view name or url redirected to if discovery fails

    Returns:
        A redirect response
    """
    referrer = urllib2.unquote(request.META.get("HTTP_REFERER", ""))
    match = _OBJECT_ID_MATCHER.match(referrer)
    if match is not None and len(match.groups()) == 1:
        id_ = match.group(1)
        return redirect(matched_to, id_=id_)
    else:
        return redirect(failed_to)
