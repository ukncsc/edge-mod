import unittest

from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse, resolve

from adapters.certuk_mod.tests.support import view_loader
from adapters.certuk_mod.views.urls import publisher_urls

views = view_loader.get_views_module()
publisher_url_patterns = [url(item[0], item[1], name=item[2]) for item in publisher_urls]
urlpatterns = patterns('adapters.certuk_mod.views', *publisher_url_patterns)


class URLConfTests(unittest.TestCase):

    urls = 'adapters.certuk_mod.tests.unit.urlconf_tests'

    def test_Resolve_PublisherDiscover_ReturnsCorrectHandler(self):
        review_resolve_match = resolve('/review/', URLConfTests.urls)
        self.assertEqual(review_resolve_match.func, views.discover)

    def test_Reverse_PublisherReview_ReturnsCorrectURL(self):
        review_url = reverse('publisher_review', URLConfTests.urls,
                             kwargs={"id_": "example:incident-02468346-fdf2-4095-a905-f3731fccd58d"})
        self.assertEqual(review_url, '/review/example%3Aincident-02468346-fdf2-4095-a905-f3731fccd58d')

    def test_Resolve_PublisherReview_ReturnsCorrectHandler(self):
        review_resolve_match = resolve('/review/example:incident-02468346-fdf2-4095-a905-f3731fccd58d',
                                       URLConfTests.urls)
        self.assertEqual(review_resolve_match.func, views.review)

    def test_Reverse_PublisherNotFound_ReturnsCorrectURL(self):
        not_found_url = reverse('publisher_not_found', URLConfTests.urls)
        self.assertEqual(not_found_url, '/missing/')

    def test_Resolve_PublisherNotFound_ReturnsCorrectHandler(self):
        not_found_resolve_match = resolve('/missing/', URLConfTests.urls)
        self.assertEqual(not_found_resolve_match.func, views.not_found)

    def test_Reverse_PublisherConfig_ReturnsCorrectURL(self):
        config_url = reverse('publisher_config', URLConfTests.urls)
        self.assertEqual(config_url, '/config/')

    def test_Resolve_PublisherConfig_ReturnsCorrectHandler(self):
        config_resolve_match = resolve('/config/', URLConfTests.urls)
        self.assertEqual(config_resolve_match.func, views.config)

    def test_Resolve_AJAXGetSites_ReturnsCorrectHandler(self):
        get_sites_resolve_match = resolve('/ajax/get_sites/', URLConfTests.urls)
        self.assertEqual(get_sites_resolve_match.func, views.ajax_get_sites)

    def test_Resolve_AJAXSetPublishSite_ReturnsCorrectHandler(self):
        set_site_resolve_match = resolve('/ajax/set_publish_site/', URLConfTests.urls)
        self.assertEqual(set_site_resolve_match.func, views.ajax_set_publish_site)

    def test_Resolve_AJAXPublish_ReturnsCorrectHandler(self):
        publish_resolve_match = resolve('/ajax/publish/', URLConfTests.urls)
        self.assertEqual(publish_resolve_match.func, views.ajax_publish)


if __name__ == '__main__':
    unittest.main()
