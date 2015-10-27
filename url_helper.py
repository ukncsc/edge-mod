
from django.core.urlresolvers import RegexURLPattern
from django.conf.urls import url


def replace_patterns(original_patterns, prefix, replacement_patterns):
    for t in replacement_patterns:
        if isinstance(t, (list, tuple)):
            t = url(prefix=prefix, *t)
        elif isinstance(t, RegexURLPattern):
            t.add_prefix(prefix)

        _item_to_replace = next((item for item in original_patterns if item.regex.pattern == t.regex.pattern), None)
        if _item_to_replace is None:
            original_patterns.append(t)
        else:
            _replace_item_idx = original_patterns.index(_item_to_replace)
            original_patterns.pop(_replace_item_idx)
            original_patterns.insert(_replace_item_idx, t)
    return original_patterns
