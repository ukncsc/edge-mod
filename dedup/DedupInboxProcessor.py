from edge.inbox import InboxProcessorForPackages, anti_ping_pong


def existing_hash_dedup(contents, hashes, user):
    return contents


def new_hash_dedup(contents, hashes, user):
    return contents


class DedupInboxProcessor(InboxProcessorForPackages):
    filters = [
        anti_ping_pong,         # removes existing STIX objects matched by id
        existing_hash_dedup,    # removes existing STIX objects matched by hash
        new_hash_dedup          # removes new STIX objects matched by hash
    ]
