from audit import setup as audit_setup
import builder.customizations as cert_builder
from cron import setup as cron_setup
from patch import remap_patch

audit_setup.configure_publisher_actions()
cert_builder.apply_customizations()
remap_patch.apply_patch()
cron_setup.create_jobs()
