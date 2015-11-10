
import os
import sys
import dummy_settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.unit.dummy_settings')
sys.modules['repository.settings'] = sys.modules['tests.unit.dummy_settings']
