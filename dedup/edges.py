#
# edges
# removes duplicate entries from edges such as indicated_ttps, suggested_coas, etc
#

from edge.generic import coalesce
from edge.tools import rgetattr


def dedup(collection, idref_path='item.idref'):
    if not collection or len(collection) == 0:
        return
    seen = set()
    idx = 0
    for edge in collection:
        idref = rgetattr(edge, idref_path.split('.'))
        if idref not in seen:
            seen.add(idref)
            collection[idx] = edge
            idx += 1
    del collection[idx:]


def dedup_collections_ind(o):
    dedup(coalesce(o, 'composite_indicator_expression'), idref_path='idref')
    dedup(coalesce(o, 'indicated_ttps'))
    dedup(coalesce(o, 'related_indicators'))
    dedup(coalesce(o, 'suggested_coas'))
    dedup(coalesce(o, 'observables'))


def dedup_collections_obs(o):
    if o.observable_composition is not None:
        dedup(coalesce(o.observable_composition, 'observables'), idref_path='idref')


def dedup_collections_inc(o):
    dedup(coalesce(o, 'attributed_threat_actors'))
    dedup(coalesce(o, 'leveraged_ttps'))
    dedup(coalesce(o, 'related_incidents'))
    dedup(coalesce(o, 'related_indicators'))
    dedup(coalesce(o, 'related_observables'))
    dedup(coalesce(o, 'coa_taken'), idref_path='idref')


def dedup_collections_coa(o):
    dedup(coalesce(o, 'related_coas'))
    dedup(coalesce(o, 'related_packages'))
    dedup(coalesce(o.parameter_observables, 'observables'), idref_path='idref')


def dedup_collections_ttp(o):
    dedup(coalesce(o, 'exploit_targets'))
    dedup(coalesce(o, 'related_ttps'))


def dedup_collections_cam(o):
    dedup(coalesce(o, 'associated_campaigns'), idref_path='idref')
    dedup(coalesce(o, 'related_packages'))
    dedup(coalesce(o, 'related_incidents'))
    dedup(coalesce(o, 'related_indicators'))
    dedup(coalesce(o, 'related_ttps'))
    for at in coalesce(o, 'attribution'):
        dedup(at)


def dedup_collections_act(o):
    dedup(coalesce(o, 'related_packages'))
    dedup(coalesce(o, 'associated_actors'))
    dedup(coalesce(o, 'associated_campaigns'))
    dedup(coalesce(o, 'observed_ttps'))


def dedup_collections_tgt(o):
    dedup(coalesce(o, 'potential_coas'))
    dedup(coalesce(o, 'related_packages'))
    dedup(coalesce(o, 'related_exploit_targets'))


def dedup_collections_pkg(o):
    dedup(coalesce(o.observables, 'observables'), idref_path='idref')
    dedup(coalesce(o, 'campaigns'), idref_path='idref')
    dedup(coalesce(o, 'courses_of_action'), idref_path='idref')
    dedup(coalesce(o, 'exploit_targets'), idref_path='idref')
    dedup(coalesce(o, 'incidents'), idref_path='idref')
    dedup(coalesce(o, 'indicators'), idref_path='idref')
    dedup(coalesce(o, 'threat_actors'), idref_path='idref')
    dedup(coalesce(o, 'ttps'), idref_path='idref')
    dedup(coalesce(o, 'related_packages'))


DEDUP_COLLECTION_DISPATCH = {
    'ind': dedup_collections_ind,
    'obs': dedup_collections_obs,
    'inc': dedup_collections_inc,
    'coa': dedup_collections_coa,
    'ttp': dedup_collections_ttp,
    'cam': dedup_collections_cam,
    'act': dedup_collections_act,
    'tgt': dedup_collections_tgt,
    'pkg': dedup_collections_pkg,
}


def dedup_collections(ty, apiobject):
    DEDUP_COLLECTION_DISPATCH[ty](apiobject)
