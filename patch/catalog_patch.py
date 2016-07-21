from django.core.urlresolvers import get_resolver


def apply_patch():
    res = get_resolver(None)
    for url_pattern in res.url_patterns:
        if hasattr(url_pattern, 'name') and url_pattern.name is 'catalog_detail':
            url_pattern._callback_str = 'adapters.certuk_mod.views.views.review'
