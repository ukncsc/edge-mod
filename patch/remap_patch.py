import edge.remap as remap


# fixes a EDGE bug. registered as MOD#20
def remap_tgt(src, maptable):
    n = remap.copywrapper(src)

    for ref in remap.coalesce(n, 'potential_coas'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'related_packages'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'related_exploit_targets'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)

    return n


def remap_ind(src, maptable):
    n = remap.copywrapper(src)

    for ref in remap.coalesce(n, 'composite_indicator_expression'):
        ref.idref = remap.maybe_remap(ref.idref, maptable)
    for ref in remap.coalesce(n, 'indicated_ttps'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'suggested_coas'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'related_indicators'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'observables'):
        ref.idref = remap.maybe_remap(ref.idref, maptable)

    return n


# Fix EDGE bug. MOD#254 (missing .item for the RelatedCampaigns)
def remap_cam(src, maptable):
    n = remap.copywrapper(src)

    for ref in remap.coalesce(n, 'associated_campaigns'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'related_packages'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'related_incidents'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'related_indicators'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)
    for ref in remap.coalesce(n, 'related_ttps'):
        ref.item.idref = remap.maybe_remap(ref.item.idref, maptable)

    for atr in n.attribution:
        for rta in atr:
            rta.item.idref = remap.maybe_remap(rta.item.idref, maptable)

    return n


def apply_patch():
    remap.REMAP_DISPATCH['tgt'] = remap_tgt
    remap.REMAP_DISPATCH['ind'] = remap_ind
    remap.REMAP_DISPATCH['cam'] = remap_cam

