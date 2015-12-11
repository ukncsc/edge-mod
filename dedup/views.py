from django.http import HttpResponseBadRequest, HttpResponseServerError

from users.decorators import *
from users.models import Repository_User


# @json_body
# @login_required_ajax
def ajax_import(request, username):
    if request.method != 'POST':
        return HttpResponseBadRequest(content='%s not allowed' % request.method)

    user = Repository_User.objects.get(username=username)
    if user is None:
        return HttpResponseBadRequest(content='User %s not found' % username)

    return HttpResponseServerError(content='Not implemented')
