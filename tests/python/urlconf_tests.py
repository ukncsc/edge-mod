
import unittest
import django.test
from django.core.urlresolvers import reverse, resolve
from django.conf.urls import patterns, url
from urls import publisher_urls
import views

publisher_url_patterns = [url(item[0], item[1], name=item[2]) for item in publisher_urls]
urlpatterns = patterns('', *publisher_url_patterns)


class URLConfTests(django.test.SimpleTestCase):

    urls = 'tests.python.urlconf_tests'

    def test_Reverse_PublisherReview_ReturnsCorrectURL(self):
        review_url = reverse('publisher_review')
        self.assertEqual(review_url, '/review/')

    def test_Resolve_PublisherReview_ReturnsCorrectHandler(self):
        review_resolve_match = resolve('/review/')
        self.assertEqual(review_resolve_match.func, views.review)

    def test_Reverse_PublisherNotFound_ReturnsCorrectURL(self):
        not_found_url = reverse('publisher_not_found')
        self.assertEqual(not_found_url, '/missing/')

    def test_Resolve_PublisherNotFound_ReturnsCorrectHandler(self):
        not_found_resolve_match = resolve('/missing/')
        self.assertEqual(not_found_resolve_match.func, views.not_found)

    def test_Reverse_PublisherConfig_ReturnsCorrectURL(self):
        config_url = reverse('publisher_config')
        self.assertEqual(config_url, '/config/')

    def test_Resolve_PublisherConfig_ReturnsCorrectHandler(self):
        config_resolve_match = resolve('/config/')
        self.assertEqual(config_resolve_match.func, views.config)

    def test_Resolve_AJAXGetSites_ReturnsCorrectHandler(self):
        get_sites_resolve_match = resolve('/ajax/get_sites/')
        self.assertEqual(get_sites_resolve_match.func, views.ajax_get_sites)

    def test_Resolve_AJAXSetPublishSite_ReturnsCorrectHandler(self):
        set_site_resolve_match = resolve('/ajax/set_publish_site/')
        self.assertEqual(set_site_resolve_match.func, views.ajax_set_publish_site)

    def test_Resolve_AJAXPublish_ReturnsCorrectHandler(self):
        publish_resolve_match = resolve('/ajax/publish/')
        self.assertEqual(publish_resolve_match.func, views.ajax_publish)


if __name__ == '__main__':
    unittest.main()
