
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'repository.settings'

import mock
import unittest
from import_helper import EdgeObject
from view_loader import get_views_module

# Good luck trying to patch decorators in a nice way... decorators are applied at class definition time, so we need to
# monkey-patch them before we import any modules that use them (in this case, our own 'views' module).
with mock.patch('django.contrib.auth.decorators.login_required', lambda func: func) as login_mock:
    with mock.patch('users.decorators.superuser_or_staff_role', lambda func: func) as superuser_or_staff_patch:
        with mock.patch('users.decorators.json_body', lambda func: func) as json_body_patch:
            views = get_views_module(__name__)


class ViewHandlerTests(unittest.TestCase):

    @mock.patch.object(views, 'render')
    @mock.patch('package_generator.PackageGenerator.build_package')
    @mock.patch(EdgeObject.__module__ + '.' + EdgeObject.__name__ + '.load', new=mock.Mock())
    @mock.patch.object(views, 'objectid_matcher')
    @mock.patch('django.http.request.HttpRequest')
    def test_Review_IfIdMatch_RenderReviewPage(self, mock_request, mock_regex, mock_package_builder, mock_render):
        type(mock_request).META = mock.PropertyMock(return_value={})

        mock_id = 'Dummy ID'
        mock_regex.match.return_value = mock.MagicMock(
            group=mock.Mock(return_value=mock_id),
            groups=mock.Mock(
                return_value=(mock_id,))
        )

        mock_render.return_value = 'Mock render'

        response = views.review(mock_request)

        mock_render.assert_called_with(mock_request, 'publisher_review.html', {
            'root_id': mock_id,
            'package': mock_package_builder.return_value
        })

        self.assertEqual(response, mock_render.return_value)

    @mock.patch.object(views, 'reverse')
    @mock.patch.object(views, 'redirect')
    @mock.patch.object(views, 'objectid_matcher')
    @mock.patch('django.http.request.HttpRequest')
    def test_Review_IfNoIdMatch_RedirectToMissingPage(self, mock_request, mock_regex,
                                                      mock_redirect, mock_reverse):
        type(mock_request).META = mock.PropertyMock(return_value={})

        mock_regex.match.return_value = None

        mock_reverse.return_value = 'Mock reverse call'
        mock_redirect.return_value = 'Mock redirect'

        response = views.review(mock_request)

        mock_reverse.assert_called_with('publisher_not_found')
        mock_redirect.assert_called_with(mock_reverse.return_value)
        self.assertEqual(response, mock_redirect.return_value)

    @mock.patch.object(views, 'PublisherConfig')
    def test_AJAXGetSites_IfConfigOK_ReturnSites(self, mock_publisher):
        mock_publisher.get_sites.return_value = 'Mock sites'

        response = views.ajax_get_sites(None, None)

        self.assertEqual(response, {
            'success': True,
            'error_message': '',
            'sites': mock_publisher.get_sites.return_value
        })

    @mock.patch.object(views, 'PublisherConfig')
    def test_AJAXGetSites_IfConfigFails_ReturnError(self, mock_publisher):
        mock_error = 'Mock error'
        mock_publisher.get_sites.side_effect = Exception(mock_error)

        response = views.ajax_get_sites(None, None)

        self.assertEqual(response, {
            'success': False,
            'error_message': mock_error,
            'sites': []
        })

    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    def test_AJAXSetPublishSite_IfUpdateOK_ReturnOK(self):
        mock_id = 'Mock ID'
        response = views.ajax_set_publish_site(None, {'site_id': mock_id})

        self.assertEqual(response, {
            'success': True,
            'saved_id': mock_id,
            'error_message': ''
        })

    @mock.patch.object(views, 'PublisherConfig')
    def test_AJAXSetPublishSite_IfUpdateFails_ReturnError(self, mock_publisher):
        mock_id = 'Mock ID'
        mock_error = 'Mock error'
        mock_publisher.update_config.side_effect = Exception(mock_error)

        response = views.ajax_set_publish_site(None, {'site_id': mock_id})

        self.assertEqual(response, {
            'success': False,
            'saved_id': '',
            'error_message': mock_error
        })

    @mock.patch.object(views, 'PublisherConfig')
    def test_AJAXSetPublishSite_IfNoSiteId_SetSiteIdToEmpty(self, mock_publisher):
        views.ajax_set_publish_site(None, {})

        mock_publisher.update_config.assert_called_with('')

    @mock.patch.object(views, 'Publisher', mock.Mock())
    @mock.patch.object(views, 'PackageGenerator', mock.Mock())
    @mock.patch.object(views, 'EdgeObject', mock.Mock())
    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    def test_AJAXPublish_IfPublishOK_ReturnOK(self):
        response = views.ajax_publish(None, {'root_id': ''})

        self.assertEqual(response, {
            'success': True,
            'error_message': ''
        })

    @mock.patch.object(views, 'Publisher', mock.Mock())
    @mock.patch.object(views, 'PackageGenerator', mock.Mock())
    @mock.patch.object(views, 'EdgeObject', mock.Mock())
    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    def test_AJAXPublish_IfNoRootId_ReturnError(self):
        response = views.ajax_publish(None, {})

        self.assertEqual(response, {
            'success': False,
            'error_message': 'root_id'
        })

    @mock.patch.object(views, 'Publisher', mock.Mock())
    @mock.patch.object(views, 'PackageGenerator', mock.Mock())
    @mock.patch.object(views, 'EdgeObject')
    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    def test_AJAXPublish_IfEdgeObjectLoadFails_ReturnError(self, mock_edge_object):
        mock_error = 'Mock error'
        mock_edge_object.load.side_effect = Exception(mock_error)

        response = views.ajax_publish(None, {'root_id': ''})

        self.assertEqual(response, {
            'success': False,
            'error_message': mock_error
        })

    @mock.patch.object(views, 'Publisher', mock.Mock())
    @mock.patch.object(views, 'PackageGenerator')
    @mock.patch.object(views, 'EdgeObject', mock.Mock())
    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    def test_AJAXPublish_IfBuildPackageFails_ReturnError(self, mock_package_generator):
        mock_error = 'Mock error'
        mock_package_generator.build_package.side_effect = Exception(mock_error)

        response = views.ajax_publish(None, {'root_id': ''})

        self.assertEqual(response, {
            'success': False,
            'error_message': mock_error
        })

    @mock.patch.object(views, 'Publisher', mock.Mock())
    @mock.patch.object(views, 'PackageGenerator', mock.Mock())
    @mock.patch.object(views, 'EdgeObject')
    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    def test_AJAXPublish_IfEdgeObjectGetNameSpacesFails_ReturnError(self, mock_edge_object):
        mock_error = 'Mock error'
        mock_edge_object.load.return_value.ns_dict.side_effect = Exception(mock_error)

        response = views.ajax_publish(None, {'root_id': ''})

        self.assertEqual(response, {
            'success': False,
            'error_message': mock_error
        })

    @mock.patch.object(views, 'Publisher')
    @mock.patch.object(views, 'PackageGenerator', mock.Mock())
    @mock.patch.object(views, 'EdgeObject', mock.Mock())
    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    def test_AJAXPublish_IfPushPackageFails_ReturnError(self, mock_publisher):
        mock_error = 'Mock error'
        mock_publisher.push_package.side_effect = Exception(mock_error)

        response = views.ajax_publish(None, {'root_id': ''})

        self.assertEqual(response, {
            'success': False,
            'error_message': mock_error
        })


if __name__ == '__main__':
    unittest.main()
