import unittest

import mock

from adapters.certuk_mod.tests.support.view_loader import get_views_module


def dummy_decorator(original_decorator):
    def actual_decorator(func):
        if not isinstance(func, mock.Mock):
            func = mock.Mock()
            func.decorated_by = {}

        func.decorated_by[original_decorator] = func.decorated_by.get(original_decorator, 0) + 1

        return func

    return actual_decorator


class UserAccessTests(unittest.TestCase):

    login_decorator_key = 'login'
    superuser_or_staff_decorator_key = 'superuser_or_decorator'

    def setUp(self):
        self.login_patch = mock.patch('django.contrib.auth.decorators.login_required',
                                      new=mock.Mock(side_effect=dummy_decorator(UserAccessTests.login_decorator_key)))
        self.superuser_or_staff_patch = mock.patch('users.decorators.superuser_or_staff_role',
                                                   new=mock.Mock(
                                                       side_effect=dummy_decorator(
                                                           UserAccessTests.superuser_or_staff_decorator_key)))
        self.json_body_patch = mock.patch('users.decorators.json_body', lambda func: func)

        self.login_mock = self.login_patch.start()
        self.superuser_or_staff_mock = self.superuser_or_staff_patch.start()
        self.json_body_mock = self.json_body_patch.start()

        self.views = get_views_module(__name__)

    def assertDecoratorPresent(self, view_func, decorator_name):
        self.assertEqual(view_func.decorated_by.get(decorator_name), 1)

    def assertDecoratorNotPresent(self, view_func, decorator_name):
        self.assertIsNone(view_func.decorated_by.get(decorator_name))

    def test_RequestReview_LoginCheck_Present(self):
        self.assertDecoratorPresent(self.views.review, UserAccessTests.login_decorator_key)

    def test_RequestReview_AdminCheck_NotPresent(self):
        self.assertDecoratorNotPresent(self.views.review, UserAccessTests.superuser_or_staff_decorator_key)

    def test_RequestNotFound_LoginCheck_Present(self):
        self.assertDecoratorPresent(self.views.not_found, UserAccessTests.login_decorator_key)

    def test_RequestNotFound_AdminCheck_NotPresent(self):
        self.assertDecoratorNotPresent(self.views.not_found, UserAccessTests.superuser_or_staff_decorator_key)

    def test_RequestConfig_LoginCheck_Present(self):
        self.assertDecoratorPresent(self.views.config, UserAccessTests.login_decorator_key)

    def test_RequestConfig_AdminCheck_Present(self):
        self.assertDecoratorPresent(self.views.config, UserAccessTests.superuser_or_staff_decorator_key)

    def test_AJAXGetSites_LoginCheck_Present(self):
        self.assertDecoratorPresent(self.views.ajax_get_sites, UserAccessTests.login_decorator_key)

    def test_AJAXGetSites_AdminCheck_Present(self):
        self.assertDecoratorPresent(self.views.ajax_get_sites, UserAccessTests.superuser_or_staff_decorator_key)

    def test_AJAXSetPublishSite_LoginCheck_Present(self):
        self.assertDecoratorPresent(self.views.ajax_set_publish_site, UserAccessTests.login_decorator_key)

    def test_AJAXSetPublishSite_AdminCheck_Present(self):
        self.assertDecoratorPresent(self.views.ajax_set_publish_site, UserAccessTests.superuser_or_staff_decorator_key)

    def test_AJAXPublish_LoginCheck_Present(self):
        self.assertDecoratorPresent(self.views.ajax_publish, UserAccessTests.login_decorator_key)

    def test_AJAXPublish_AdminCheck_NotPresent(self):
        self.assertDecoratorNotPresent(self.views.ajax_publish, UserAccessTests.superuser_or_staff_decorator_key)

    def tearDown(self):
        self.login_patch.stop()
        self.superuser_or_staff_patch.stop()
        self.json_body_patch.stop()
