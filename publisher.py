
import dateutil.tz
from datetime import datetime
import libtaxii
from publisher_config import PublisherConfig
from peers.models import PeerSite
from peers.push import send_message, discover_inbox_url


class Publisher(object):

    @staticmethod
    def push_package(package):
        config = PublisherConfig.get_config()
        namespace_info = {
            config['namespace_id']: config['namespace_alias']
        }
        xml_data = package.to_xml(ns_dict=namespace_info, include_idgen=False, include_schemalocs=False)
        output_block = libtaxii.tm11.ContentBlock(
            content_binding=libtaxii.CB_STIX_XML_111,
            content=xml_data,
            timestamp_label=datetime.now(dateutil.tz.tzutc())
        )
        message_id = libtaxii.tm11.generate_message_id()
        message = libtaxii.tm11.InboxMessage(message_id=message_id)
        message.content_blocks.append(output_block)
        site = PeerSite.objects.get(id=config['site_id'])
        url = discover_inbox_url(site)
        send_message(site, url, message)
