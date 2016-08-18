import json
from django.http.response import JsonResponse


def json_response(func):
    def wrapper(request, *args, **kwargs):
        ct = request.META.get('CONTENT_TYPE','')
        d = json.loads(request.body or '{}') if ct.startswith('application/json') else {}
        if not d or d == {}:
            for arg in args:
                if isinstance(arg, dict) and arg != {}:
                    d = arg
        response = func(request, d)
        if isinstance(response, JsonResponse):
            return response
        else:
            raise TypeError("Return Content type has to be of JSON Response")
    return wrapper
