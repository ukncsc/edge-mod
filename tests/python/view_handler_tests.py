
import mock
from import_helper import EdgeObject
import django.test
import views


class ViewHandlerTests(django.test.SimpleTestCase):

    @mock.patch('views.render')
    @mock.patch('package_generator.PackageGenerator.build_package')
    @mock.patch(EdgeObject.__module__ + '.' + EdgeObject.__name__ + '.load', new=mock.Mock())
    @mock.patch('views.objectid_matcher')
    @mock.patch('django.http.request.HttpRequest')
    @mock.patch('views.login_required', new=mock.Mock())
    def test_Review_IfIdMatch_RenderReviewPage(self, mock_request, mock_regex, mock_package_builder, mock_render):
        type(mock_request).META = mock.PropertyMock(return_value={})

        mock_id = 'Dummy ID'
        mock_regex.match.return_value = mock.MagicMock(
            group=mock.Mock(return_value=mock_id),
            groups=mock.Mock(
                return_value=(mock_id,))
        )

        response = views.review(mock_request)

        expected_response = mock_render(mock_request, 'publisher_review.html', {
            'root_id': mock_id,
            'package': mock_package_builder.return_value
        })

        self.assertEqual(response, expected_response)

    @mock.patch('views.render')
    @mock.patch('package_generator.PackageGenerator.build_package')
    @mock.patch(EdgeObject.__module__ + '.' + EdgeObject.__name__ + '.load', new=mock.Mock())
    @mock.patch('views.objectid_matcher')
    @mock.patch('django.http.request.HttpRequest')
    @mock.patch('views.login_required', new=mock.Mock())
    def test_Review_IfNoIdMatch_RedirectToMissingPage(self, mock_request, mock_regex, mock_package_builder, mock_render):
        pass
