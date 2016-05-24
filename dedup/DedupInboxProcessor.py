import pymongo
import operator

from edge.inbox import InboxProcessorForPackages, InboxProcessorForBuilders, InboxItem, InboxError, anti_ping_pong, \
    drop_envelopes, INBOX_DROP_ENVELOPES
from edge.generic import create_package, EdgeObject
from mongoengine.connection import get_db
from adapters.certuk_mod.validation import ValidationStatus
from adapters.certuk_mod.validation.package.validator import PackageValidationInfo
from .property_finder import capec_finder, cve_finder
from edge.tools import rgetattr
from .edges import dedup_collections
from edge import LOCAL_NAMESPACE

PROPERTY_TYPE = ['api_object', 'obj', 'object_', 'properties', '_XSI_TYPE']
PROPERTY_FILENAME = ['api_object', 'obj', 'object_', 'properties', 'file_name']
PROPERTY_MD5 = ['api_object', 'obj', 'object_', 'properties', 'md5']
PROPERTY_SHA1 = ['api_object', 'obj', 'object_', 'properties', 'sha1']
PROPERTY_SHA224 = ['api_object', 'obj', 'object_', 'properties', 'sha224']
PROPERTY_SHA256 = ['api_object', 'obj', 'object_', 'properties', 'sha256']
PROPERTY_SHA384 = ['api_object', 'obj', 'object_', 'properties', 'sha384']
PROPERTY_SHA512 = ['api_object', 'obj', 'object_', 'properties', 'sha512']
PROPERTY_CAPEC = ['api_object', 'obj', 'behavior', 'attack_patterns']
PROPERTY_CVE = ['api_object', 'obj', 'vulnerabilities']


def _get_sighting_count(obs):
    sighting_count = getattr(obs, 'sighting_count', 1)
    if sighting_count is None:
        sighting_count = 1
    return sighting_count


def _merge_properties(api_object, id_, count, additional_file_hashes):
    api_object.obj.sighting_count = _get_sighting_count(api_object.obj) + count
    if id_ in additional_file_hashes:
        file_properties = rgetattr(api_object, ['obj', 'object_', 'properties'], None)
        for hash_type, hash_value in additional_file_hashes[id_].iteritems():
            if getattr(file_properties, hash_type, None) is None:
                setattr(file_properties, hash_type, hash_value)


def _update_existing_properties(additional_sightings, additional_file_hashes, user):
    inbox_processor = InboxProcessorForBuilders(user=user)
    for id_, count in additional_sightings.iteritems():
        edge_object = EdgeObject.load(id_)
        api_object = edge_object.to_ApiObject()
        _merge_properties(api_object, id_, count, additional_file_hashes)
        inbox_processor.add(InboxItem(
            api_object=api_object,
            etlp=edge_object.etlp,
            etou=edge_object.etou,
            esms=edge_object.esms
        ))
    inbox_processor.run()


def _coalesce_duplicates(contents, map_table):
    def add_missing_file_hash(inbox_object, file_hashes, property_name):
        hash_type = property_name[-1]
        if hash_type not in file_hashes:
            hash_value = rgetattr(inbox_object, property_name, None)
            if hash_value is not None:
                file_hashes[hash_type] = hash_value

    out = {}
    additional_sightings = {}
    additional_file_hashes = {}
    for id_, io in contents.iteritems():
        if id_ not in map_table:
            io.api_object = io.api_object.remap(map_table)
            out[id_] = io
        elif io.api_object.ty == 'obs':
            existing_id = map_table[id_]
            sightings_for_duplicate = _get_sighting_count(io.api_object.obj)
            additional_sightings[existing_id] = additional_sightings.get(existing_id, 0) + sightings_for_duplicate
            if rgetattr(io, PROPERTY_TYPE, None) == 'FileObjectType':
                if existing_id not in additional_file_hashes:
                    additional_file_hashes[existing_id] = {}
                add_missing_file_hash(io, additional_file_hashes[existing_id], PROPERTY_MD5)
                add_missing_file_hash(io, additional_file_hashes[existing_id], PROPERTY_SHA1)
                add_missing_file_hash(io, additional_file_hashes[existing_id], PROPERTY_SHA224)
                add_missing_file_hash(io, additional_file_hashes[existing_id], PROPERTY_SHA256)
                add_missing_file_hash(io, additional_file_hashes[existing_id], PROPERTY_SHA384)
                add_missing_file_hash(io, additional_file_hashes[existing_id], PROPERTY_SHA512)
    return out, additional_sightings, additional_file_hashes


def _generate_message(template_text, contents, out):
    removed = len(contents) - len(out)
    message = (template_text % removed) if removed else None
    return message


def _find_matching_db_file_obs(db, new_file_obs):
    def extract_properties(inbox_items, property_path):
        return list({str(rgetattr(inbox_item, property_path, None)) for inbox_item in inbox_items.itervalues()
                     if rgetattr(inbox_item, property_path, None) is not None})

    new_filenames = extract_properties(new_file_obs, PROPERTY_FILENAME)
    new_md5s = extract_properties(new_file_obs, PROPERTY_MD5)
    new_sha1s = extract_properties(new_file_obs, PROPERTY_SHA1)
    new_sha224s = extract_properties(new_file_obs, PROPERTY_SHA224)
    new_sha256s = extract_properties(new_file_obs, PROPERTY_SHA256)
    new_sha384s = extract_properties(new_file_obs, PROPERTY_SHA384)
    new_sha512s = extract_properties(new_file_obs, PROPERTY_SHA512)
    existing_file_obs = db.stix.find({
        'type': 'obs',
        'data.api.object.properties.xsi:type': 'FileObjectType',
        '$or': [
            {
                'data.api.object.properties.file_name': {'$in': new_filenames}
            }, {
                '$and': [
                    {'data.api.object.properties.hashes.type': 'MD5'},
                    {'data.api.object.properties.hashes.simple_hash_value': {'$in': new_md5s}}
                ]
            }, {
                '$and': [
                    {'data.api.object.properties.hashes.type': 'SHA1'},
                    {'data.api.object.properties.hashes.simple_hash_value': {'$in': new_sha1s}}
                ]
            }, {
                '$and': [
                    {'data.api.object.properties.hashes.type': 'SHA224'},
                    {'data.api.object.properties.hashes.simple_hash_value': {'$in': new_sha224s}}
                ]
            }, {
                '$and': [
                    {'data.api.object.properties.hashes.type': 'SHA256'},
                    {'data.api.object.properties.hashes.simple_hash_value': {'$in': new_sha256s}}
                ]
            }, {
                '$and': [
                    {'data.api.object.properties.hashes.type': 'SHA384'},
                    {'data.api.object.properties.hashes.simple_hash_value': {'$in': new_sha384s}}
                ]
            }, {
                '$and': [
                    {'data.api.object.properties.hashes.type': 'SHA512'},
                    {'data.api.object.properties.hashes.simple_hash_value': {'$in': new_sha512s}}
                ]
            }
        ]
    }).sort('created_on', pymongo.DESCENDING)
    return existing_file_obs


def _is_matching_file(existing_file, new_file):
    def matches(existing, new, property_path):
        # NOTE: need to ignore the `api_object` part of the property path here - hence `[1:]`
        existing_value = rgetattr(existing, property_path[1:], None)
        new_value = rgetattr(new, property_path[1:], None)
        return existing_value is not None and new_value is not None and existing_value == new_value

    return matches(existing_file, new_file, PROPERTY_FILENAME) and (
        matches(existing_file, new_file, PROPERTY_MD5) or
        matches(existing_file, new_file, PROPERTY_SHA1) or
        matches(existing_file, new_file, PROPERTY_SHA224) or
        matches(existing_file, new_file, PROPERTY_SHA256) or
        matches(existing_file, new_file, PROPERTY_SHA384) or
        matches(existing_file, new_file, PROPERTY_SHA512)
    )


def _add_matching_file_observables(db, map_table, contents):
    # identify file observables in contents excluding any which are already in map_table
    new_file_obs = {id_: inbox_item for (id_, inbox_item) in contents.iteritems()
                    if inbox_item.api_object.ty == 'obs' and
                    id_ not in map_table and  # exclude perfect matches which have already been discovered via data hash
                    rgetattr(inbox_item, PROPERTY_TYPE, 'Unknown') == 'FileObjectType'}
    if not new_file_obs:
        # if we have no new file observables, we can bail out
        return

    existing_file_obs = _find_matching_db_file_obs(db, new_file_obs)
    if not existing_file_obs:
        # if we have no matching existing file observables, we can bail out
        return

    for existing_file in existing_file_obs:
        for (new_id, new_file) in new_file_obs.iteritems():
            if _is_matching_file(EdgeObject(existing_file).to_ApiObject(), new_file.api_object):
                map_table[new_id] = existing_file['_id']


def _existing_hash_dedup(contents, hashes, user):
    db = get_db()

    existing_items = db.stix.find({
        'type': 'obs',
        'data.hash': {
            '$in': hashes.values()
        }
    }, {
        '_id': 1,
        'data.hash': 1
    }).sort('created_on', pymongo.DESCENDING)

    hash_to_existing_ids = {doc['data']['hash']: doc['_id'] for doc in existing_items}

    map_table = {
        id_: hash_to_existing_ids[hash_] for id_, hash_ in hashes.iteritems() if hash_ in hash_to_existing_ids
        }

    # file observable have more complex rules for duplicates, so simple hash matching isn't good enough
    _add_matching_file_observables(db, map_table, contents)

    out, additional_sightings, additional_file_hashes = _coalesce_duplicates(contents, map_table)

    if additional_sightings:
        _update_existing_properties(additional_sightings, additional_file_hashes, user)

    message = _generate_message("Remapped %d observables to existing observables based on hashes", contents, out)

    return out, message


def _new_hash_dedup(contents, hashes, user):
    hash_to_ids = {}
    for id_, hash_ in sorted(hashes.iteritems()):
        if rgetattr(contents.get(id_, None), ['api_object', 'ty'], '') == 'obs':
            hash_to_ids.setdefault(hash_, []).append(id_)

    map_table = {}
    for hash_, ids in hash_to_ids.iteritems():
        if len(ids) > 1:
            master = ids[0]
            for dup in ids[1:]:
                map_table[dup] = master

    out, additional_sightings, additional_file_hashes = _coalesce_duplicates(contents, map_table)

    for id_, count in additional_sightings.iteritems():
        inbox_item = contents.get(id_, None)
        if inbox_item is not None:
            api_object = inbox_item.api_object
            _merge_properties(api_object, id_, count, additional_file_hashes)

    message = _generate_message("Merged %d observables in the supplied package based on hashes", contents, out)

    for id_, io in out.iteritems():
        dedup_collections(io.api_object.ty, io.api_object.obj)

    return out, message


def _coalesce_non_observable_duplicates(contents, map_table):
    out = {}
    for id_, io in contents.iteritems():
        if id_ not in map_table:
            io.api_object = io.api_object.remap(map_table)
            out[id_] = io
    return out


def _create_capec_title_key(title, capec_ids):
    capec_join = ",".join(sorted(capec_ids))
    return title.strip().lower() + ": " + capec_join


def _get_map_table(contents, key_to_ids):
    map_table = {}
    for key, ids in key_to_ids.iteritems():
        if len(ids) <= 1:
            continue

        id_to_description_length = {}
        for id in ids:
            if contents[id].api_object.obj.description is not None:
                id_to_description_length[id] = len(contents[id].api_object.obj.description.value)
        if id_to_description_length == {}:
            master = ids[0]
        else:
            master = sorted(id_to_description_length.items(), key = operator.itemgetter(1))[-1][0]
        ids.remove(master)
        for dup in ids:
            map_table[dup] = master
    return map_table


def _package_ttps_to_consider(contents, local):
    ids_to_objects_to_consider = {}
    for id_, io in contents.iteritems():
        is_local = rgetattr(contents.get(id_, None), ['api_object', 'obj', 'id_ns'], '') == LOCAL_NAMESPACE
        correct_ns = is_local if local else (not is_local)
        if not correct_ns:
            continue
        if rgetattr(contents.get(id_, None), ['api_object', 'ty'], '') == 'ttp' and len(
                rgetattr(contents.get(id_, None), PROPERTY_CAPEC, '')) > 0:
            ids_to_objects_to_consider.setdefault(id_, []).append(io)

    title_capec_string_to_ids = {}
    for id_, ttps in ids_to_objects_to_consider.iteritems():
        for ttp in ttps:
            capec_ids = [capecs.capec_id for capecs in ttp.api_object.obj.behavior.attack_patterns if capecs.capec_id]
            title = ttp.api_object.obj.title
            if len(capec_ids) != 0:
                key = _create_capec_title_key(title, capec_ids)
                title_capec_string_to_ids.setdefault(key, []).append(id_)
    return title_capec_string_to_ids


def _existing_title_and_capecs(local):
    existing_ttps = capec_finder(local)

    existing_title_capec_string_to_id = {}
    for found_ttp in existing_ttps:
        capec_ids = [found_capec['capec'] for found_capec in found_ttp['capecs']]
        key = _create_capec_title_key(found_ttp['title'], capec_ids)
        existing_title_capec_string_to_id[key] = found_ttp['_id']
    return existing_title_capec_string_to_id


def _existing_ttp_capec_dedup(contents, hashes, user, local):
    existing_title_capec_string_to_id = _existing_title_and_capecs(local)

    ttp_title_capec_string_to_ids = _package_ttps_to_consider(contents, local)

    map_table = {
        id_[0]: existing_title_capec_string_to_id[key] for key, id_ in ttp_title_capec_string_to_ids.iteritems() if
        key in existing_title_capec_string_to_id
        }

    out = _coalesce_non_observable_duplicates(contents, map_table)

    message = _generate_message("Remapped %d " + ('local' if local else 'external') +
                                " namespace TTPs to existing TTPs based on CAPEC-IDs and title"
                                , contents, out)
    return out, message


def _new_ttp_capec_dedup(contents, hashes, user, local):
    ttp_title_capec_string_to_ids = _package_ttps_to_consider(contents, local)

    map_table = _get_map_table(contents, ttp_title_capec_string_to_ids)

    out = _coalesce_non_observable_duplicates(contents, map_table)

    message = _generate_message("Merged %d " + ('local' if local else 'external') +
                                " namespace TTPs in the supplied package based on CAPEC-IDs and title", contents, out)
    return out, message


def _new_ttp_local_ns_capec_dedup(contents, hashes, user):
    return _new_ttp_capec_dedup(contents, hashes, user, True)


def _new_ttp_external_ns_capec_dedup(contents, hashes, user):
    return _new_ttp_capec_dedup(contents, hashes, user, False)


def _existing_ttp_local_ns_capec_dedup(contents, hashes, user):
    return _existing_ttp_capec_dedup(contents, hashes, user, True)


def _existing_ttp_external_ns_capec_dedup(contents, hashes, user):
    return _existing_ttp_capec_dedup(contents, hashes, user, False)

def _package_tgts_to_consider(contents, local):
    package_tgts_to_consider = {}
    for id_, io in contents.iteritems():
        is_local = rgetattr(contents.get(id_, None), ['api_object', 'obj', 'id_ns'], '') == LOCAL_NAMESPACE
        correct_ns = is_local if local else (not is_local)
        if not correct_ns:
            continue
        if rgetattr(contents.get(id_, None), ['api_object', 'ty'], '') == 'tgt' and len(
                rgetattr(contents.get(id_, None), PROPERTY_CVE, '')) > 0:
            package_tgts_to_consider.setdefault(id_, []).append(io)

    cves_to_ids = {}
    for id_, tgts in package_tgts_to_consider.iteritems():
        for tgt in tgts:
            cves = [cve.cve_id for cve in tgt.api_object.obj.vulnerabilities if cve.cve_id]
            if len(cves) != 0:
                key = ",".join(sorted(cves))
                cves_to_ids.setdefault(key, []).append(id_)
    return cves_to_ids

def _existing_tgts_with_cves(local):
    existing_cves = cve_finder(local)

    existing_cves_to_ids = {}
    for found_tgt in existing_cves:
        cve_ids = [found_cve['cve'] for found_cve in found_tgt['cves']]
        key = ",".join(sorted(cve_ids))
        existing_cves_to_ids[key] = found_tgt['_id']
    return existing_cves_to_ids


def _new_tgt_cve_dedup(contents, hashes, user, local):
    cve_to_tgt_ids = _package_tgts_to_consider(contents, local)

    map_table = _get_map_table(contents, cve_to_tgt_ids)

    out = _coalesce_non_observable_duplicates(contents, map_table)

    message = _generate_message("Merged %d " + ('local' if local else 'external') +
                                " namespace Exploit Targets in the supplied package based on CVE-IDs", contents, out)

    return out, message

def _existing_tgt_cve_dedup(contents, hashes, user, local):
    existing_cve_ids_to_id = _existing_tgts_with_cves(local)
    cve_to_tgt_ids = _package_tgts_to_consider(contents, local)

    map_table = {
        id_[0]: existing_cve_ids_to_id[key] for key, id_ in cve_to_tgt_ids.iteritems() if key in existing_cve_ids_to_id
    }

    out = _coalesce_non_observable_duplicates(contents, map_table)

    message = _generate_message("Remapped %d " + ('local' if local else 'external') +
                                " namespace Exploit Targets to existing Targets based on CVE-IDs", contents, out)

    return out, message

def _new_tgt_local_ns_cve_dedup(contents, hashes, user):
    return _new_tgt_cve_dedup(contents, hashes, user, True)

def _existing_tgt_local_ns_cve_dedup(contents, hashes, user):
    return _existing_tgt_cve_dedup(contents, hashes, user, True)

class DedupInboxProcessor(InboxProcessorForPackages):
    filters = ([drop_envelopes] if INBOX_DROP_ENVELOPES else []) + [
        _new_hash_dedup,  # removes new STIX objects matched by hash
        _existing_hash_dedup,  # removes existing STIX objects matched by hash
        _new_ttp_local_ns_capec_dedup,  # removes new TTPs matched by CAPEC-IDs and Title in local NS
        _existing_ttp_local_ns_capec_dedup,  # dedup against existing TTPs matched by CAPEC-IDs and Title in local NS
        _new_tgt_local_ns_cve_dedup, # removes new tgts matched by CVE-ID in incoming package in local NS
        _existing_tgt_local_ns_cve_dedup, # dedup against existing tgts matched by CVE-ID in local NS
        anti_ping_pong,  # removes existing STIX objects matched by id
    ]

    def __init__(self, user, trustgroups=None, streams=None, validate=True):
        super(DedupInboxProcessor, self).__init__(user, trustgroups, streams)
        self.validation_result = {}
        self.package_header = DedupInboxProcessor.get_package_header(self.contents)
        self.validate = validate

    @staticmethod
    def get_package_header(contents):
        if contents:
            package_items = {id_: inbox_item for id_, inbox_item in contents.iteritems() if
                             inbox_item.api_object.ty == 'pkg'}

            related_package_ids = set()
            for package_item in package_items.values():
                if package_item.api_object.obj.related_packages:
                    related_packages = package_item.api_object.obj.related_packages
                    related_package_ids = related_package_ids.union(
                        {related_package.item.idref for related_package in related_packages})

            top_level_package_ids = set(package_items.keys()).difference(related_package_ids)
            if len(top_level_package_ids) > 1:
                raise InboxError("Multiple top level packages are not expected")
            if len(top_level_package_ids) == 0:
                return None

            top_level_package_item = package_items[top_level_package_ids.pop()]
            return top_level_package_item.api_object.obj.stix_header

        return None

    @staticmethod
    def _validate(contents, package_header):
        if not contents:
            return None
        # At this point, only things that don't already exist in the database will be in contents...
        # We can exclude packages, as they only serve as containers for other objects.
        contents_to_validate = {
            id_: inbox_item.api_object for id_, inbox_item in contents.iteritems() if inbox_item.api_object.ty != 'pkg'
            }
        # Wrap the contents in a package for convenience so they can be easily validated:
        package_for_validation = create_package(contents_to_validate)
        package_for_validation.stix_header = package_header
        validation_result = PackageValidationInfo.validate(package_for_validation)

        return validation_result.validation_dict

    def apply_filters(self):
        super(DedupInboxProcessor, self).apply_filters()
        if not self.contents or not self.validate:
            return
        self.validation_result = DedupInboxProcessor._validate(self.contents, self.package_header)
        for id_, object_fields in self.validation_result.iteritems():
            for field_name in object_fields:
                if object_fields[field_name]['status'] == ValidationStatus.ERROR:
                    raise InboxError('Validation failed')
