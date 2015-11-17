
from indicator.observable_object_generator import ObservableObjectGenerator
from indicator.observable_object_type_definition import ObservableObjectTypeDefinition
from cybox.objects.http_session_object import \
    HTTPRequestHeaderFields, HTTPRequestHeader, HTTPClientRequest, HTTPRequestResponse, HTTPSession


class CERTObservableObjectGenerator(ObservableObjectGenerator):

    def __init__(self):
        super(CERTObservableObjectGenerator, self).__init__()

    def _define_object_types(self):
        object_types = super(CERTObservableObjectGenerator, self)._define_object_types()
        object_types['HTTP Session'] = ObservableObjectTypeDefinition(
            'HTTP Session', False, custom_id_prefix='http_session', generator_function=self._generate_http_session
        )
        return object_types

    @staticmethod
    def _generate_http_session(object_data):
        fields = HTTPRequestHeaderFields()
        fields.user_agent = object_data.get('user_agent')

        header = HTTPRequestHeader()
        header.parsed_header = fields

        req = HTTPClientRequest()
        req.http_request_header = header

        req_res = HTTPRequestResponse()
        req_res.http_client_request = req

        session = HTTPSession()
        session.http_request_response = [req_res]

        return session
