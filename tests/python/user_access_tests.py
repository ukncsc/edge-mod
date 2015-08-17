
import unittest
import mock
import views


class RequestResponseTests(unittest.TestCase):

    def test_RequestReview_UserNotAuthenticated_RedirectToLogin(self):
        pass

    def test_RequestReview_UserAuthenticated_OK(self):
        pass

    def test_RequestConfig_UserNotAuthenticated_RedirectToLogin(self):
        pass

    def test_RequestConfig_NormalUserAuthenticated_RedirectToLogin(self):
        pass

    def test_RequestConfig_StaffOrSuperUserAuthenticated_OK(self):
        pass

    def test_RequestGetSites_UserNotAuthenticated_RedirectToLogin(self):
        pass

    def test_RequestGetSites_NormalUserAuthenticated_RedirectToLogin(self):
        pass

    def test_RequestGetSites_StaffOrSuperUserAuthenticated_OK(self):
        pass

    def test_RequestSetPublishSite_UserNotAuthenticated_RedirectToLogin(self):
        pass

    def test_RequestSetPublishSite_NormalUserAuthenticated_RedirectToLogin(self):
        pass

    def test_RequestSetPublishSite_StaffOrSuperUserAuthenticated_OK(self):
        pass

    def test_RequestPublish_UserNotAuthenticated_RedirectToLogin(self):
        pass

    def test_RequestPublish_UserAuthenticated_OK(self):
        pass

if __name__ == '__main__':
    unittest.main()
