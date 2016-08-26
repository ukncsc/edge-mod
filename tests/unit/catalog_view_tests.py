import unittest

from adapters.certuk_mod.catalog.views import observable_extract
import mock
from edge.generic import EdgeError


class CatalogViewTests(unittest.TestCase):
    def setUp(self):
        self.eo = mock.MagicMock()
        self.eo.ty = 'ind'
        self.eo.id_ = "0"

        self.eo_child = mock.MagicMock()
        self.eo_child.apidata.has_key.return_value = False
        self.eo_child.ty = 'obs'
        self.eo_child.id_ = "1"
        self.eo_child.summary = {'type': "DomainNameObjectType", 'value': "hello"}

        self.eo.edges = [self.eo_child]

    @mock.patch('django.http.request.HttpRequest')
    @mock.patch('adapters.certuk_mod.catalog.views.EdgeObject')
    @mock.patch('adapters.certuk_mod.catalog.views.HttpResponse')
    def testSimple(self, mock_HttpResponse, mock_EdgeObject, mock_HttpRequest):
        mock_EdgeObject.load.side_effect = [self.eo, self.eo_child]
        with mock.patch('adapters.certuk_mod.catalog.views.HttpResponse', mock_HttpResponse):
            response = observable_extract(mock_HttpRequest, "text", "all", 123, "current")
            response.write.assert_called_with("hello\n")

    @mock.patch('django.http.request.HttpRequest')
    @mock.patch('adapters.certuk_mod.catalog.views.EdgeObject')
    @mock.patch('adapters.certuk_mod.catalog.views.HttpResponse')
    def test2LevelsDeep(self, mock_HttpResponse, mock_EdgeObject, mock_HttpRequest):
        eo_gchild = mock.MagicMock()
        eo_gchild.apidata.has_key.return_value = False
        eo_gchild.ty = 'obs'
        eo_gchild.id_ = "2"
        eo_gchild.summary = {'type': "AddressObjectType", 'value': "bye"}
        self.eo_child.edges = [eo_gchild]

        mock_EdgeObject.load.side_effect = [self.eo, self.eo_child, eo_gchild]

        with mock.patch('adapters.certuk_mod.catalog.views.HttpResponse', mock_HttpResponse):
            response = observable_extract(mock_HttpRequest, "text", "all", 123, "current")
            response.write.assert_called_with("hello\nbye\n")

    @mock.patch('django.http.request.HttpRequest')
    @mock.patch('adapters.certuk_mod.catalog.views.EdgeObject')
    @mock.patch('adapters.certuk_mod.catalog.views.HttpResponse')
    def testLooped(self, mock_HttpResponse, mock_EdgeObject, mock_HttpRequest):
        eo_gchild = mock.MagicMock()
        eo_gchild.apidata.has_key.return_value = False
        eo_gchild.ty = 'obs'
        eo_gchild.id_ = "2"
        eo_gchild.summary = {'type': "AddressObjectType", 'value': "bye"}
        self.eo_child.edges = [eo_gchild]
        eo_gchild.edges = [self.eo_child]

        mock_EdgeObject.load.side_effect = [self.eo, self.eo_child, eo_gchild]

        with mock.patch('adapters.certuk_mod.catalog.views.HttpResponse', mock_HttpResponse):
            response = observable_extract(mock_HttpRequest, "text", "all", 123, "current")
            response.write.assert_called_with("hello\nbye\n")

    @mock.patch('django.http.request.HttpRequest')
    @mock.patch('adapters.certuk_mod.catalog.views.EdgeObject')
    @mock.patch('adapters.certuk_mod.catalog.views.HttpResponse')
    def testExternalReference(self, mock_HttpResponse, mock_EdgeObject, mock_HttpRequest):
        eo_gchild = mock.MagicMock()
        eo_gchild.apidata.has_key.return_value = False
        eo_gchild.ty = 'obs'
        eo_gchild.id_ = "2"
        eo_gchild.summary = {'type': "AddressObjectType", 'value': "bye"}
        self.eo_child.edges = [eo_gchild]

        def mock_eo(id, *args, **kwargs):
            if id == "0":
                return self.eo
            if id == "1":
                return self.eo_child
            raise EdgeError

        mock_EdgeObject.load = mock_eo

        with mock.patch('adapters.certuk_mod.catalog.views.HttpResponse', mock_HttpResponse):
            response = observable_extract(mock_HttpRequest, "text", "all", "0", "current")
            response.write.assert_called_with("hello\n")
