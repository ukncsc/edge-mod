import unittest

import mock

from adapters.certuk_mod.audit import status
from adapters.certuk_mod.builder.kill_chain_definition import KILL_CHAIN_PHASES
from adapters.certuk_mod.tests.support.view_loader import get_views_module
from edge.generic import EdgeObject

# Good luck trying to patch decorators in a nice way... decorators are applied at class definition time, so we need to
# monkey-patch them before we import any modules that use them (in this case, our own 'views' module).
with mock.patch('django.contrib.auth.decorators.login_required', lambda func: func) as login_mock:
    with mock.patch('users.decorators.superuser_or_staff_role', lambda func: func) as superuser_or_staff_patch:
        with mock.patch('users.decorators.json_body', lambda func: func) as json_body_patch:
            views = get_views_module(__name__)


class ViewHandlerTests(unittest.TestCase):

    @mock.patch('adapters.certuk_mod.common.objectid.redirect')
    @mock.patch(EdgeObject.__module__ + '.' + EdgeObject.__name__ + '.load', new=mock.Mock())
    @mock.patch('adapters.certuk_mod.common.objectid.find_id')
    @mock.patch('django.http.request.HttpRequest')
    def test_Discover_IfIdMatch_RedirectToReviewPage(self, mock_request, mock_find_id, mock_redirect):
        type(mock_request).META = mock.PropertyMock(return_value={})

        mock_id = 'Dummy ID'
        mock_find_id.return_value = mock_id

        mock_redirect.return_value = 'Mock redirect'

        response = views.discover(mock_request)

        mock_redirect.assert_called_with('publisher_review', id_=mock_id)

        self.assertEqual(response, mock_redirect.return_value)

    @mock.patch('adapters.certuk_mod.common.objectid.redirect')
    @mock.patch('adapters.certuk_mod.common.objectid.find_id')
    @mock.patch('django.http.request.HttpRequest')
    def test_Discover_IfNoIdMatch_RedirectToMissingPage(self, mock_request, mock_find_id, mock_redirect):
        type(mock_request).META = mock.PropertyMock(return_value={})

        mock_find_id.return_value = None

        mock_redirect.return_value = 'Mock redirect'

        response = views.discover(mock_request)

        mock_redirect.assert_called_with('publisher_not_found')
        self.assertEqual(response, mock_redirect.return_value)

    @mock.patch.object(views, 'render')
    @mock.patch('adapters.certuk_mod.validation.package.validator.PackageValidationInfo.validate')
    @mock.patch('adapters.certuk_mod.publisher.package_generator.PackageGenerator.build_package')
    @mock.patch(EdgeObject.__module__ + '.' + EdgeObject.__name__ + '.load', new=mock.Mock())
    @mock.patch('adapters.certuk_mod.common.objectid.find_id')
    @mock.patch('django.http.request.HttpRequest')
    def test_Review_IfIdOK_RenderReviewPage(self, mock_request, find_id, mock_package_builder, mock_validate,
                                            mock_render):
        mock_id = 'Dummy ID'
        find_id.return_value = mock_id

        mock_render.return_value = 'Mock render'

        response = views.review(mock_request, id_=mock_id)

        mock_render.assert_called_with(mock_request, 'publisher_review.html', {
            'root_id': mock_id,
            'validation_info': mock_validate.return_value,
            'package': mock_package_builder.return_value,
            'kill_chain_phases': {item['phase_id']: item['name'] for item in KILL_CHAIN_PHASES}
        })

        self.assertEqual(response, mock_render.return_value)

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
    @mock.patch.object(views, 'PublisherEdgeObject', mock.Mock())
    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    @mock.patch.object(views, 'OnPublish')
    @mock.patch.object(views, 'format_audit_message')
    def test_AJAXPublish_IfPublishOK_ReturnOK(self, mock_message_formatter, mock_event_publisher):
        mock_id = 'blah'
        mock_user = 'mr'
        mock_message_formatter.return_value = 'dummy message'
        mock_publication_message = 'publication message'

        response = views.ajax_publish(mock.Mock(user=mock_user), {
            'root_id': mock_id,
            'publicationMessage': mock_publication_message
        })

        mock_event_publisher.raise_event.assert_called_with(views.ajax_publish, publish_status=status.PUBLISH_SUCCESS,
                                                            stix_id=mock_id, user=mock_user,
                                                            message=mock_message_formatter.return_value)
        mock_message_formatter.assert_called_with('', mock_publication_message)
        self.assertEqual(response, {
            'success': True,
            'error_message': ''
        })

    @mock.patch.object(views, 'Publisher', mock.Mock())
    @mock.patch.object(views, 'PackageGenerator', mock.Mock())
    @mock.patch.object(views, 'PublisherEdgeObject', mock.Mock())
    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    @mock.patch.object(views, 'OnPublish')
    @mock.patch.object(views, 'format_audit_message')
    def test_AJAXPublish_IfNoRootId_ReturnError(self, mock_message_formatter, mock_event_publisher):
        mock_user = 'mr'
        mock_message_formatter.return_value = 'dummy message'
        mock_publication_message = 'publication message'
        expected_error_message = 'root_id'

        response = views.ajax_publish(mock.Mock(user=mock_user), {
            'publicationMessage': mock_publication_message
        })

        mock_event_publisher.raise_event.assert_called_with(views.ajax_publish, publish_status=status.PUBLISH_FAIL,
                                                            stix_id=None, user=mock_user,
                                                            message=mock_message_formatter.return_value)
        mock_message_formatter.assert_called_with(expected_error_message, mock_publication_message)
        self.assertEqual(response, {
            'success': False,
            'error_message': expected_error_message
        })

    @mock.patch.object(views, 'Publisher', mock.Mock())
    @mock.patch.object(views, 'PackageGenerator', mock.Mock())
    @mock.patch.object(views, 'PublisherEdgeObject')
    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    @mock.patch.object(views, 'OnPublish')
    @mock.patch.object(views, 'format_audit_message')
    def test_AJAXPublish_IfEdgeObjectLoadFails_ReturnError(self, mock_message_formatter, mock_event_publisher,
                                                           mock_edge_object):
        mock_error = 'Mock error'
        mock_edge_object.load.side_effect = Exception(mock_error)
        mock_id = 'blah'
        mock_user = 'mr'
        mock_message_formatter.return_value = 'dummy message'
        mock_publication_message = 'publication message'

        response = views.ajax_publish(mock.Mock(user=mock_user), {
            'root_id': mock_id,
            'publicationMessage': mock_publication_message
        })

        mock_event_publisher.raise_event.assert_called_with(views.ajax_publish, publish_status=status.PUBLISH_FAIL,
                                                            stix_id=mock_id, user=mock_user,
                                                            message=mock_message_formatter.return_value)
        mock_message_formatter.assert_called_with(mock_error, mock_publication_message)
        self.assertEqual(response, {
            'success': False,
            'error_message': mock_error
        })

    @mock.patch.object(views, 'Publisher', mock.Mock())
    @mock.patch.object(views, 'PackageGenerator')
    @mock.patch.object(views, 'PublisherEdgeObject', mock.Mock())
    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    @mock.patch.object(views, 'OnPublish')
    @mock.patch.object(views, 'format_audit_message')
    def test_AJAXPublish_IfBuildPackageFails_ReturnError(self, mock_message_formatter, mock_event_publisher,
                                                         mock_package_generator):
        mock_error = 'Mock error'
        mock_package_generator.build_package.side_effect = Exception(mock_error)
        mock_id = 'blah'
        mock_user = 'mr'
        mock_message_formatter.return_value = 'dummy message'
        mock_publication_message = 'publication message'

        response = views.ajax_publish(mock.Mock(user=mock_user), {
            'root_id': mock_id,
            'publicationMessage': mock_publication_message
        })

        mock_event_publisher.raise_event.assert_called_with(views.ajax_publish, publish_status=status.PUBLISH_FAIL,
                                                            stix_id=mock_id, user=mock_user,
                                                            message=mock_message_formatter.return_value)
        mock_message_formatter.assert_called_with(mock_error, mock_publication_message)
        self.assertEqual(response, {
            'success': False,
            'error_message': mock_error
        })

    @mock.patch.object(views, 'Publisher', mock.Mock())
    @mock.patch.object(views, 'PackageGenerator', mock.Mock())
    @mock.patch.object(views, 'PublisherEdgeObject')
    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    @mock.patch.object(views, 'OnPublish')
    @mock.patch.object(views, 'format_audit_message')
    def test_AJAXPublish_IfEdgeObjectGetNameSpacesFails_ReturnError(self, mock_message_formatter, mock_event_publisher,
                                                                    mock_edge_object):
        mock_error = 'Mock error'
        mock_edge_object.load.return_value.ns_dict.side_effect = Exception(mock_error)
        mock_id = 'blah'
        mock_user = 'mr'
        mock_message_formatter.return_value = 'dummy message'
        mock_publication_message = 'publication message'

        response = views.ajax_publish(mock.Mock(user=mock_user), {
            'root_id': mock_id,
            'publicationMessage': mock_publication_message
        })

        mock_event_publisher.raise_event.assert_called_with(views.ajax_publish, publish_status=status.PUBLISH_FAIL,
                                                            stix_id=mock_id, user=mock_user,
                                                            message=mock_message_formatter.return_value)
        mock_message_formatter.assert_called_with(mock_error, mock_publication_message)
        self.assertEqual(response, {
            'success': False,
            'error_message': mock_error
        })

    @mock.patch.object(views, 'Publisher')
    @mock.patch.object(views, 'PackageGenerator', mock.Mock())
    @mock.patch.object(views, 'PublisherEdgeObject', mock.Mock())
    @mock.patch.object(views, 'PublisherConfig', mock.Mock())
    @mock.patch.object(views, 'OnPublish')
    @mock.patch.object(views, 'format_audit_message')
    def test_AJAXPublish_IfPushPackageFails_ReturnError(self, mock_message_formatter, mock_event_publisher,
                                                        mock_publisher):
        mock_error = 'Mock error'
        mock_publisher.push_package.side_effect = Exception(mock_error)
        mock_id = 'blah'
        mock_user = 'mr'
        mock_message_formatter.return_value = 'dummy message'
        mock_publication_message = 'publication message'

        response = views.ajax_publish(mock.Mock(user=mock_user), {
            'root_id': mock_id,
            'publicationMessage': mock_publication_message
        })

        mock_event_publisher.raise_event.assert_called_with(views.ajax_publish, publish_status=status.PUBLISH_FAIL,
                                                            stix_id=mock_id, user=mock_user,
                                                            message=mock_message_formatter.return_value)
        mock_message_formatter.assert_called_with(mock_error, mock_publication_message)
        self.assertEqual(response, {
            'success': False,
            'error_message': mock_error
        })

    @mock.patch.object(views, 'BuilderValidationInfo')
    def test_AJAXValidate_IfOK_ReturnsSuccess(self, mock_validator):
        mock_validation_info = 'dummy validation info'
        mock_validator.validate.return_value = mock.Mock(validation_dict=mock_validation_info)

        response = views.ajax_validate(None, {})

        self.assertDictEqual(response, {
            'success': True,
            'error_message': '',
            'validation_info': mock_validation_info
        })

    @mock.patch.object(views, 'BuilderValidationInfo')
    def test_AJAXValidate_IfError_ReturnsError(self, mock_validator):
        mock_error = Exception('error')
        mock_validator.validate.side_effect = mock_error

        response = views.ajax_validate(None, {})

        self.assertDictEqual(response, {
            'success': False,
            'error_message': mock_error.message,
            'validation_info': {}
        })
