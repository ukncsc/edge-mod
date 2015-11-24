
import imp
import mock


def get_views_module(requesting_module=''):
    # This is a totally shit hack that we need to mock decorators...
    # Decorators are applied at class definition time, which means we have to patch them before we import any modules
    # that use them. But this also means that the decorators remain patched forever..! So, we need to import multiple
    # 'instances' of the modules that use the decorators, so that patching one 'instance' doesn't patch another.
    # So why not use classes instead of functional views (so we can have multiple instances in a sane way)? Because the
    # decorators are applied at class definition time, so all class instances will be affected by patching anyway!
    # Aaarrgghh!
    with mock.patch('adapters.certuk_mod.audit.setup.configure_publisher_actions'):
        views_package_path = imp.load_module('views', *imp.find_module('views')).__path__
        views = imp.load_module(requesting_module + 'adapters.certuk_mod.views.views', *imp.find_module('views', views_package_path))
        return views
